import datetime
import json
import requests
import xmltodict
import xml.etree.ElementTree as ET
import urllib.parse
__version__ = '1.1'
# 0.2 moves create_xml to internal method
# 0.3 implements xmltodict and json for more complex returned xml
# 1.0 Add class methods, matching the API
# 1.1 updated technician_get_all


class API:
    """
    The main sending class for the Manage Service Engine Rest API
    # https://www.manageengine.com/products/service-desk/help/adminguide/api/request-operations.html
    """
    def __init__(self, api_key, api_url_base):
        """
        Initiate values
        :param api_key: technician key
        :param api_url_base: should be base of sdplus api e.g. http://sdplus/sdpapi/
        """
        self.api_key = api_key
        self.api_url_base = api_url_base

    @staticmethod
    def _create_xml(fields, sub_elements=None):
        """
        Makes xml out of parameters
        :param fields: dict of main values e.g.  {'isPublic': 'false', 'notesText': 'Simon Crouch'...}
        :param starting_element: string
        :param sub_elements: list of elements to put in xml between the default <Details> and <parameter>
        :return:
        """
        sub_elements = [] if sub_elements is None else sub_elements
        xml_string = ET.Element('Operation')  # Standard as part of the API
        details = ET.SubElement(xml_string, 'Details')  # Standard as part of the API
        current_parent = details
        for sub in sub_elements:
            current_parent = ET.SubElement(current_parent, sub)
        for key, value in fields.items():
            param = ET.SubElement(current_parent, 'parameter')
            ET.SubElement(param, 'name').text = key
            ET.SubElement(param, 'value').text = value
        return ET.tostring(xml_string)

    @staticmethod
    def output_params_to_list(response):
        """
        Outputs a list of parameters in a list of dict values
        :param response: output response from API in json
        :return: list: [{'key': 'value'}, {'key': 'value'}, ...
        """
        all_params = []
        try:
            records = response['API']['response']['operation']['Details']['record']
        except KeyError:
            return []
        if isinstance(records, dict):  # 1 record
            parameters_dict = {}
            for param in records['parameter']:
                parameters_dict[param['name']] = param['value']
            all_params.append(parameters_dict)
        elif isinstance(records, list):  # > 1 record
            for record in records:
                parameters_dict = {}
                for param in record['parameter']:
                    parameters_dict[param['name']] = param['value']
                all_params.append(parameters_dict)
        return all_params

    def send(self, url_append, operation, input_fields=None, attachment='', sub_elements=None, bypass=False):
        """
        Send through details into API
        :param url_append: string to append to end of base API url e.g. 21 but not /21
        :param operation: operation name param as specified in ManageEngine API spec
        :param input_fields: dictionary of fields e.g. {'subject': 'EDITED ...' }
        :param attachment: file path to attachment
        :param sub_elements: list of elements to put in xml between the default <Details> and <parameter>
        :param bypass: True/False as to whether to bypass manual processing and use xmltodict module
        :return: {'response_key': 'response value', ...}
        """
        sub_elements = [] if sub_elements is None else sub_elements
        params = {'TECHNICIAN_KEY': self.api_key,
                  'OPERATION_NAME': operation}
        if input_fields:
            xml_input = self._create_xml(input_fields, sub_elements)
            params.update({'INPUT_DATA': xml_input})
        if attachment:
            file = {'file': open(attachment, 'rb')}
            response_text = requests.post(urllib.parse.urljoin(self.api_url_base, url_append), params=params, files=file).text
        else:
            response_text = requests.get(urllib.parse.urljoin(self.api_url_base, url_append), params).text
        if bypass:  # needed when xml response is more complex
            return json.loads(json.dumps(xmltodict.parse(response_text)))
        response = ET.fromstring(response_text)
        result = {}
        for status_item in response.iter('result'):
            result = {
                'response_status': status_item.find('status').text,
                'response_message': status_item.find('message').text
            }
        if result['response_status'] == 'Success':
            for param_tags in response.iter('Details'):
                # Assumes xml: parameter, name & value
                if param_tags.findall('parameter'):
                    result.update(dict([(details_params.find('name').text, details_params.find('value').text)
                                        for details_params in param_tags.findall('parameter')
                                        if details_params is not None]))
        return result

    # Request Operations
    def request_add(self, fields):
        return self.send('request/', 'ADD_REQUEST', fields)

    def request_edit(self, request_id, fields):
        return self.send('request/' + request_id, 'EDIT_REQUEST', fields)

    def request_view(self, request_id):
        return self.send('request/' + request_id, 'GET_REQUEST')

    def request_delete(self, request_id):
        return self.send('request/' + request_id, 'DELETE_REQUEST')

    def request_close(self, request_id, accepted=False, comment=''):
        """
        Closes request. ***NOTE: You can't use this unless call has been assigned***
        :param request_id: id of request
        :param accepted: 'Accepted' or ''
        :param comment: Comment to put in the closure comments box
        :return: response
        """
        if accepted:
            accepted_text = 'Accepted'
        else:
            accepted_text = ''
        fields = {'closeAccepted': accepted_text, 'closeComment': comment}
        return self.send('request/' + request_id, 'CLOSE_REQUEST', fields)

    def request_get_conversations(self, request_id):
        result = self.send('request/' + request_id + '/conversation', 'GET_CONVERSATIONS', bypass=True)
        return self.output_params_to_list(result)

    def request_get_conversation(self, request_id, conversation_id):
        result = self.send('request/' + request_id + '/conversation/' + conversation_id, 'GET_CONVERSATION', bypass=True)
        return self.output_params_to_list(result)

    def request_add_attachment(self, request_id, attachment_path):
        return self.send('request/' + request_id + '/attachment', 'ADD_ATTACHMENT', attachment=attachment_path)

    def request_adding_resolution(self, request_id, text=''):
        return self.send('request/' + request_id + '/resolution', 'ADD_RESOLUTION', {'resolutiontext': text}, sub_elements='resolution')

    def request_editing_resolution(self, request_id, text=''):
        return self.send('request/' + request_id + '/resolution', 'EDIT_RESOLUTION', {'resolutiontext': text}, sub_elements='resolution')

    def request_get_resolution(self, request_id):
        return self.send('request/' + request_id, 'GET_RESOLUTION', bypass=True)

    def request_pickup(self, request_id):
        return self.send('request/' + request_id, 'PICKUP_REQUEST')

    def request_assign(self, request_id, technician_id):
        return self.send('request/' + request_id, 'ASSIGN_REQUEST', {'technicianid': technician_id})

    def request_reply(self, request_id, fields):
        # fields: {'to': 'simon.crouch@nbt.nhs.uk', 'cc': 'simoncrouch@nhs.net', 'subject': 'subj test', 'description':
        return self.send('request/' + request_id, 'REPLY_REQUEST', fields, bypass=True)

    # "Operation ADD_CONVERSATION is not supported."
    # def request_add_conversation(self, request_id, subject='', description=''):
    #     return self.send('request/' + request_id, 'ADD_CONVERSATION', {'subject': subject, 'description': description},
    #                      bypass=True)

    def request_get_requests(self, filter_by='All_Requests', limit='1000', frm='0'):
        """
        Get all call details from sdplus - works by returning MOST RECENT calls first
        Will translate epoch createdtime to datetime object
        :param filter_by: Queue name (not value) to search - seems to return only OPEN calls
        :param frm: 0=most recent logged call, ... 10=10th oldest call from present etc.
        :param limit: limit returned results
        :return: list of dicts for each call
        e.g. [{'duebytime': '-1', 'subject': 'Smartcard Request [Lorenzo Access ]',
        'createdby': 'Yasmin Daniels', 'requester': 'Harriet Barnard', 'PRIORITY': None, 'workorderid': '184699',
        'isoverdue': 'false', 'status': 'Open', 'TECHNICIAN': None, 'createdtime': '1465832199994'}, ...]
        """
        # api = API(os.environ['SDPLUS_ADMIN'], 'http://sdplus/sdpapi/request/')
        fields = {'from': frm, 'limit': limit, 'filterby': filter_by}
        calls_from_sdplus = self.send('request/', 'GET_REQUESTS', fields, bypass=True)
        calls_from_sdplus = self.output_params_to_list(calls_from_sdplus)
        for call in calls_from_sdplus:
            call['createdtime'] = self.epoch_to_datetime(call['createdtime'])
        return calls_from_sdplus

    def request_get_notification(self, request_id, notification_id):
        return self.send('request/' + request_id + '/notification/' + notification_id, 'GET_NOTIFICATION', bypass=True)

    def request_get_notifications(self, request_id):
        return self.send('request/' + request_id + '/notification/', 'GET_NOTIFICATIONS', bypass=True)

    def request_get_all_conversations(self, request_id):
        all_conversations = self.send('request/' + request_id + '/allconversation/', 'GET_ALL_CONVERSATIONS', bypass=True)
        all_conversations = self.output_params_to_list(all_conversations)
        for conversation in all_conversations:
            conversation['createddate'] = self.epoch_to_datetime(conversation['createddate'])
        return all_conversations

    def request_get_request_filters(self):
        # WARNING: request_get_request_filters() DOESN'T RETURN ALL FILTERS! EXCELLENT(!) API BROKEN.
        return self.send('request/', 'GET_REQUEST_FILTERS', bypass=True)

    # Notes Related Operations
    def note_add(self, request_id, is_public='False', text=''):
        fields = {'isPublic': is_public, 'notesText': text}
        return self.send('request/' + request_id + '/notes', 'ADD_NOTE', fields, sub_elements=['Notes', 'Note'])

    def note_edit(self, request_id, note_id, text=''):
        return self.send('request/' + request_id + '/notes/' + note_id, 'EDIT_NOTE', {'notesText': text},
                         sub_elements=['Notes', 'Note'])

    def note_view(self, request_id, note_id):
        return self.send('request/' + request_id + '/notes/' + note_id, 'GET_NOTE')

    def note_view_all(self, request_id):
        return self.send('request/' + request_id + '/notes/', 'GET_NOTES')

    def note_delete(self, request_id, note_id):
        return self.send('request/' + request_id + '/notes/' + note_id, 'DELETE_NOTE')

    # Technician Operations
    def technician_get_all(self, site_name='', group_id=''):
        fields = {'siteName': site_name, 'groupid': group_id}
        people_raw = self.send('technician/', 'GET_ALL', fields, bypass=True)
        people = {}
        for record in people_raw['API']['response']['operation']['Details']['record']:
            people[record['parameter'][1]['value']] = record['parameter'][0]['value']
        return people

    # Custom API Calls
    def request_assign_name(self, full_name, request_id):
        """
        Assigns a call to a person by full name
        :param full_name: Simon Crouch
        :param request_id: 1851234
        :return: -
        """
        names = self.technician_get_all()
        technician_id = names.get(full_name)
        return self.request_assign(request_id, technician_id)

    def get_queue_ids(self, queue_name_list: list):
        """
        WARNING: request_get_request_filters() DOESN'T RETURN ALL FILTERS! EXCELLENT(!) API BROKEN.
        Takes in a list of displayed queue names and returns a list of dicts with queue name, id
        :param queue_name_list: [displayed queue names]
        :return: [{'name': 'displayed queue name', 'id': 'queue id in sdplus'}, ...]
        """
        filters = self.request_get_request_filters()
        sdplus_queue_value_name = filters['operation']['Details']['Filters']['parameter']  # value=display, name=id
        queues_all = []
        queue = {}
        for queue_name in queue_name_list:
            queue['name'] = queue_name
            for sdplus_queue in sdplus_queue_value_name:
                if sdplus_queue['value'] == queue_name:
                    queue_id = queue.copy()
                    queue_id['id'] = sdplus_queue['name']
                    queues_all.append(queue_id)
        return queues_all

    @staticmethod
    def epoch_to_datetime(epoch):
        return datetime.datetime.fromtimestamp(float(epoch) / 1000)
