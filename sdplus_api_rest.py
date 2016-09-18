import json
import os
import requests
import xmltodict
import xml.etree.ElementTree as ET
__version__ = 0.3
# 0.2 moves create_xml to internal method
# 0.3 implements xmltodict and json for more complex returned xml


class API:
    """
    The main sending class for the Manage Service Engine Rest API
    # https://www.manageengine.com/products/service-desk/help/adminguide/api/request-operations.html
    """
    def __init__(self, api_key, api_url_base):
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
        records = response['API']['response']['operation']['Details']['record']
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
            response_text = requests.post(os.path.join(self.api_url_base, url_append), params=params, files=file).text
        else:
            response_text = requests.get(os.path.join(self.api_url_base, url_append), params).text
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


def eg_add_request():
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    fields = {
        'reqtemplate': 'Default Request',  # or 'General IT Request' which has supplier ref, but also Due by Date,
        'requesttype': 'Service Request',
        'status': 'Hold - Awaiting Third Party',
        'requester': 'Simon Crouch',
        'mode': '@Southmead Retained Estate',  # site
        'best contact number': '-',
        'Exact Location': 'white room',
        'group': 'Back Office',
        'subject': 'This is a test call only - please ignore',
        'description': 'This is a test call only (description) - please ignore',
        'service': '.Lorenzo/Galaxy - IT Templates',    # Service Category
        'category': 'Clinical Applications Incident',  # Self Service Incident
        'subcategory': 'Lorenzo',
        'impact': '3 Impacts Department',
        'urgency': '3 Business Operations Slightly Affected - Requires response within 8 hours of created time'
    }
    result = api.send('', 'ADD_REQUEST', fields)
    print(result)


def eg_edit_request():
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    fields = {'subject': 'EDITED EDITED ignore this request'}
    result = api.send('154820', 'EDIT_REQUEST', fields)
    print(result)


def eg_view_request():
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    result = api.send('154594', 'GET_REQUEST')
    print(result)


def eg_delete_request():
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    result = api.send('154820', 'DELETE_REQUEST')
    print(result)


# eg_close_request


def eg_get_conversations():
    """
    Gets ONLY incoming conversations (incoming emails usually)
    :return: e.g. [{'createdtime': '1472553622289', 'TYPE': None, 'conversationid': '573946', 'from': 'IT Third Party...

    """
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    result = api.send('196392/conversation', 'GET_CONVERSATIONS', bypass=True)
    print(api.output_params_to_list(result))


def eg_get_conversation():
    """
    Gets the conversation item contents (usually incoming email) from sdplus ref and conversation id
    :return: e.g. [{'conversationid': '573946', 'title': 'FW: Helpdesk case HD0000001088813  ...
    """
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    result = api.send('196392/conversation/573946', 'GET_CONVERSATION', bypass=True)
    # print(result)
    print(api.output_params_to_list(result))


def eg_get_all_conversation_detail(sdplus_ref):
    """
    ***Don't use - instead use eg_get_all_conversations()***
    Gets all conversation items and their details from an sdplus call (usually incoming email)
    Combines GET_CONVERSATIONS and GET_CONVERSATION commands.
    :param sdplus_ref: sdplus reference number
    :return: list of dicts e.g. [{'description': 'To r...',  'toaddress': '..', 'title': 'FW: Helpdesk ...
             note: description will be in html
    """
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    conversations = api.send(sdplus_ref + '/conversation', 'GET_CONVERSATIONS', bypass=True)
    conversations = api.output_params_to_list(conversations)
    full_detail = []
    for conversation in conversations:
        one_detail = api.send(sdplus_ref + '/conversation/' + conversation['conversationid'], 'GET_CONVERSATION',
                              bypass=True)
        one_detail = api.output_params_to_list(one_detail)
        full_detail.append(one_detail[0])
    return full_detail


def eg_add_attachment():
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    result = api.send('137216/attachment', 'ADD_ATTACHMENT', attachment=r'C:\Users\nbf1707\Desktop\test.txt')
    print(result)


# eg_adding_resolution
# eg_edit_resolution
# eg_get_resolution
# eg_pickup_request

def eg_assign_request():
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    fields = {'technicianid': '25261'}  # 25261 = Simon Crouch
    result = api.send('165741', 'ASSIGN_REQUEST', fields)
    print(result)


def eg_assign_request_name(full_name, sdplus_ref):
    """
    Assigns a call to a person by full name
    :param full_name: Simon Crouch
    :param sdplus_ref: 1851234
    :return: -
    """
    names = eg_get_all_technicians()
    id = names.get(full_name)
    if not id:
        raise LookupError('full_name not found')
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    fields = {'technicianid': id}
    result = api.send(sdplus_ref, 'ASSIGN_REQUEST', fields)
    print(result)


def eg_reply():
    """
    Uses Manage Engine to send an email to the To recipient, then places against the call as a conversation
    :return:
    """
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    fields = {'to': 'simon.crouch@nbt.nhs.uk', 'cc': 'simoncrouch@nhs.net', 'subject': 'subj test',
              'description': 'd test'}
    result = api.send('197019', 'REPLY_REQUEST', fields, bypass=True)
    print(result)


def eg_get_requests(limit='25', frm='0', filter_by='All_Requests'):
    """
    Get all call details from sdplus - works by returning MOST RECENT calls first
    :param frm: 0=most recent logged call, ... 10=10th oldest call from present etc.
    :param limit: limit returned results
    :return: list of dicts for each call
    e.g. [{'duebytime': '-1', 'subject': 'Smartcard Request [Lorenzo Access ]',
    'createdby': 'Yasmin Daniels', 'requester': 'Harriet Barnard', 'PRIORITY': None, 'workorderid': '184699',
    'isoverdue': 'false', 'status': 'Open', 'TECHNICIAN': None, 'createdtime': '1465832199994'}, ...]
    """
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    fields = {'from': frm, 'limit': limit, 'filterby': filter_by}
    calls_from_sdplus = api.send('', 'GET_REQUESTS', fields, bypass=True)
    return api.output_params_to_list(calls_from_sdplus)


def eg_get_notification():
    """
    Gets the notification item contents (usually outgoing email) from sdplus ref and notification id
    :return: list of dicts e.g.
    """
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    result = api.send('196392/notification/848547', 'GET_NOTIFICATION', bypass=True)
    # print(result)
    print(api.output_params_to_list(result))


def eg_get_notifications():
    """
    Get replies to the customer from a resolver or sdplus automated email
    :return: list of dicts e.g. [{'type': 'Notification', 'subtype': 'REQ_IN_QUEUE', 'notifyid': '848547',
    """
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    result = api.send('196392/notification/', 'GET_NOTIFICATIONS', bypass=True)
    # print(result)
    print(api.output_params_to_list(result))


def eg_get_all_conversations():
    """
    Gets all incoming and outgoing communications for a call, with their contents
    :return: list of dicts e.g. [{'from': 'System', 'description': '<font face= ...
    """
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    result = api.send('196392/allconversation/', 'GET_ALL_CONVERSATIONS', bypass=True)
    # print(result)
    return api.output_params_to_list(result)


def eg_get_request_filters():
    """
    Gets all the request View Menu items - e.g. "Back Office Third Party/CSC"
    or {'name': '131707_MyView', 'value': 'Projects - Paper Light'},
    :return: list of dicts
    """
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    result = api.send('', 'GET_REQUEST_FILTERS', bypass=True)
    print(result)


def eg_add_note():
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    fields = {'isPublic': 'false', 'notesText': 'Simon Crouch: Logged to CSC'}
    result = api.send('165741/notes', 'ADD_NOTE', fields, sub_elements=['Notes', 'Note'])
    print(result)


def eg_get_all_technicians():
    """
    Returns all IDs and technicians
    :return: {'full name': id, 'full name': id, ...}
    """
    api = API(os.environ['SLACK_SIMONC'], 'http://sdplus/sdpapi/technician/')
    fields = {'siteName': '', 'groupid': ''}
    peoples = api.send('', 'GET_ALL', fields, bypass=True)

    people = {}
    for record in peoples['API']['response']['operation']['Details']['record']:
        people[record['parameter'][1]['value']] = record['parameter'][0]['value']
    return people
