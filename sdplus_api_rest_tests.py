import os
import unittest
from custom_modules.sdplus_api_rest import API

sdplus_base_url = 'http://sdplus/sdpapi/'
sdplus_api_key = os.environ['SDPLUS_ADMIN']


class RequestAddTest(unittest.TestCase):
    def setUp(self):
        self.sdplus_api = API(sdplus_api_key, sdplus_base_url)

    def test_request_add(self):
        fields = {
            'reqtemplate': 'Default Request',
            'requesttype': 'Service Request',
            'status': 'Hold - Awaiting Third Party',
            'requester': 'Simon Crouch',
            'mode': '@Southmead Retained Estate',  # site
            'best contact number': '-',
            'Exact Location': 'white room',
            'group': 'Back Office Third Party/CSC',
            'assignee': 'Simon Crouch',
            'subject': 'This is a test call only - please ignore',
            'description': 'This is a test call only (description) - please ignore',
            'service': '.Lorenzo/Galaxy - IT Templates',  # Service Category
            'category': 'Clinical Applications Incident',  # Self Service Incident
            'subcategory': 'Lorenzo',
            'impact': '3 Impacts Department',
            'urgency': '3 Business Operations Slightly Affected - Requires response within 8 hours of created time'
        }
        result = self.sdplus_api.request_add(fields)
        self.request_id = result['workorderid']
        print('(Created call ' + self.request_id + ')')
        self.assertEqual(result['response_status'], 'Success')

    def tearDown(self):
        result = self.sdplus_api.request_delete(self.request_id)
        print(result['response_status'])


class RequestDeleteTest(unittest.TestCase):
    def setUp(self):
        self.sdplus_api = API(sdplus_api_key, sdplus_base_url)
        fields = {
            'reqtemplate': 'Default Request',
            'requesttype': 'Service Request',
            'status': 'Hold - Awaiting Third Party',
            'requester': 'Simon Crouch',
            'mode': '@Southmead Retained Estate',  # site
            'best contact number': '-',
            'Exact Location': 'white room',
            'group': 'Back Office Third Party/CSC',
            'assignee': 'Simon Crouch',
            'subject': 'This is a test call only - please ignore',
            'description': 'This is a test call only (description) - please ignore',
            'service': '.Lorenzo/Galaxy - IT Templates',  # Service Category
            'category': 'Clinical Applications Incident',  # Self Service Incident
            'subcategory': 'Lorenzo',
            'impact': '3 Impacts Department',
            'urgency': '3 Business Operations Slightly Affected - Requires response within 8 hours of created time'
        }
        result = self.sdplus_api.request_add(fields)
        self.request_id = result['workorderid']
        print('(Created call ' + self.request_id + ')')

    def test_request_delete(self):
        print('Deleting call: ' + self.request_id)
        result = self.sdplus_api.request_delete(self.request_id)
        print(result['response_status'])


class RequestSpecificTest(unittest.TestCase):
    def setUp(self):
        self.sdplus_api = API(sdplus_api_key, sdplus_base_url)
        self.request_id = '198952'
        self.conversation_id = '577291'
        self.notification_id = '855331'

    def test_request_get_conversation(self):
        result = self.sdplus_api.request_get_conversation(self.request_id, self.conversation_id)
        self.assertEqual(result['response_status'], 'Success')

    def test_request_get_notification(self):
        result = self.sdplus_api.request_get_notification(self.request_id, self.notification_id)
        self.assertEqual(result['response_status'], 'Success')


class RequestTest(unittest.TestCase):
    def setUp(self):
        self.attachment_path = r'c:\file.txt'
        self.technician_id = '12345'
        self.sdplus_api = API(sdplus_api_key, sdplus_base_url)
        fields = {
            'reqtemplate': 'Default Request',  # or 'General IT Request' which has supplier ref, but also Due by Date,
            'requesttype': 'Service Request',
            'status': 'Hold - Awaiting Third Party',
            'requester': 'Simon Crouch',
            'mode': '@Southmead Retained Estate',  # site
            'best contact number': '-',
            'Exact Location': 'white room',
            'group': 'Back Office Third Party/CSC',
            'assignee': 'Simon Crouch',
            'subject': 'This is a test call only - please ignore',
            'description': 'This is a test call only (description) - please ignore',
            'service': '.Lorenzo/Galaxy - IT Templates',  # Service Category
            'category': 'Clinical Applications Incident',  # Self Service Incident
            'subcategory': 'Lorenzo',
            'impact': '3 Impacts Department',
            'urgency': '3 Business Operations Slightly Affected - Requires response within 8 hours of created time'
        }
        result = self.sdplus_api.request_add(fields)
        self.request_id = result['workorderid']
        print('(Created call ' + self.request_id + ')')

    def tearDown(self):
        result = self.sdplus_api.request_delete(self.request_id)
        print(result['response_status'])

    def test_request_close(self):
        self.sdplus_api.request_pickup(self.request_id)
        result = self.sdplus_api.request_close(self.request_id, True)
        self.assertEqual(result['response_status'], 'Success')

    def test_request_edit(self):
        result = self.sdplus_api.request_edit(self.request_id, {'subject': 'Test subject - now edited successfully'})
        self.assertEqual(result['response_status'], 'Success')

    def test_request_view(self):
        result = self.sdplus_api.request_view(self.request_id)
        self.assertEqual(result['response_status'], 'Success')

    def test_request_get_conversations(self):
        result = self.sdplus_api.request_get_conversations(self.request_id)
        self.assertEqual(result['response_status'], 'Success')

    def test_request_add_attachment(self):
        result = self.sdplus_api.request_add_attachment(self.request_id, self.attachment_path)
        self.assertEqual(result['response_status'], 'Success')

    def test_request_add_resolution(self):
        result = self.sdplus_api.request_adding_resolution(self.request_id, 'Resolution test text add')
        self.assertEqual(result['response_status'], 'Success')

    def test_request_pickup(self):
        print(self.test_request_pickup.__name__)
        result = self.sdplus_api.request_pickup(self.request_id)
        self.assertEqual(result['response_status'], 'Success')

    def test_request_assign(self):
        result = self.sdplus_api.request_assign(self.request_id, self.technician_id)
        self.assertEqual(result['response_status'], 'Success')

    def test_request_reply(self):
        fields = {'to': 'simon.crouch@nbt.nhs.uk', 'cc': 'simon.crouch@nbt.nhs.uk', 'subject': 'subject test reply',
                  'description': 'Test description reply'}
        result = self.sdplus_api.request_reply(self.request_id, fields)
        self.assertEqual(result['response_status'], 'Success')

    def test_request_get_notifications(self):
        result = self.sdplus_api.request_get_notifications(self.request_id)
        self.assertEqual(result['response_status'], 'Success')

    def test_request_get_all_conversations(self):
        result = self.sdplus_api.request_get_all_conversations(self.request_id)
        self.assertEqual(result['response_status'], 'Success')

    def test_request_editing_resolution(self):
        self.sdplus_api.request_adding_resolution(self.request_id, 'Resolution text on create')
        result = self.sdplus_api.request_editing_resolution(self.request_id, 'Resolution test text edit')
        self.assertEqual(result['response_status'], 'Success')

    def test_request_get_resolution(self):
        self.sdplus_api.request_adding_resolution(self.request_id, 'Resolution text on create')
        result = self.sdplus_api.request_get_resolution(self.request_id)
        self.assertEqual(result['response_status'], 'Success')


class RequestGeneralTest(unittest.TestCase):
    def setUp(self):
        self.sdplus_api = API(sdplus_api_key, sdplus_base_url)

    def test_requests_get_requests(self):
        result = self.sdplus_api.request_get_requests()
        self.assertEqual(result['response_status'], 'Success')

    def test_request_get_request_filters(self):
        result = self.sdplus_api.request_get_request_filters()
        self.assertEqual(result['response_status'], 'Success')


class NotesTest(unittest.TestCase):
    def setUp(self):
        self.sdplus_api = API(sdplus_api_key, sdplus_base_url)
        fields = {
            'reqtemplate': 'Default Request',  # or 'General IT Request' which has supplier ref, but also Due by Date,
            'requesttype': 'Service Request',
            'status': 'Hold - Awaiting Third Party',
            'requester': 'Simon Crouch',
            'mode': '@Southmead Retained Estate',  # site
            'best contact number': '-',
            'Exact Location': 'white room',
            'group': 'Back Office Third Party/CSC',
            'assignee': 'Simon Crouch',
            'subject': 'This is a test call only - please ignore',
            'description': 'This is a test call only (description) - please ignore',
            'service': '.Lorenzo/Galaxy - IT Templates',  # Service Category
            'category': 'Clinical Applications Incident',  # Self Service Incident
            'subcategory': 'Lorenzo',
            'impact': '3 Impacts Department',
            'urgency': '3 Business Operations Slightly Affected - Requires response within 8 hours of created time'
        }
        result = self.sdplus_api.request_add(fields)
        self.request_id = result['workorderid']
        print('(Created call ' + self.request_id + ')')

    def tearDown(self):
        result = self.sdplus_api.request_delete(self.request_id)
        print(result['response_status'])

    def test_note_add(self):
        result = self.sdplus_api.note_add(self.request_id, text='Test note add')
        self.assertEqual(result['response_status'], 'Success')

    def test_note_view_all(self):
        result = self.sdplus_api.note_view_all(self.request_id)
        self.assertEqual(result['response_status'], 'Success')


class NotesSpecificTest(unittest.TestCase):
    def setUp(self):
        self.sdplus_api = API(sdplus_api_key, sdplus_base_url)
        self.request_id = '198952'
        self.note_id = '855331'

    def test_note_view(self):
        result = self.sdplus_api.note_view(self.request_id, self.note_id)
        self.assertEqual(result['response_status'], 'Success')

    def test_note_view_delete(self):
        result = self.sdplus_api.note_delete(self.request_id, self.note_id)
        self.assertEqual(result['response_status'], 'Success')

    def test_note_edit(self):
        result = self.sdplus_api.note_edit(self.request_id, self.note_id, text='Test note edit')
        self.assertEqual(result['response_status'], 'Success')


class TechnicianTest(unittest.TestCase):
    def setUp(self):
        self.sdplus_api = API(sdplus_api_key, sdplus_base_url)

    def test_technician_get_all(self):
        result = self.sdplus_api.technician_get_all()
        self.assertEqual(result['response_status'], 'Success')


class CustomTest(unittest.TestCase):
    def setUp(self):
        self.sdplus_api = API(sdplus_api_key, sdplus_base_url)
        self.request_id = '198952'

    def test_request_assign_name(self):
        result = self.sdplus_api.request_assign_name('Simon Crouch', self.request_id)
        self.assertEqual(result['response_status'], 'Success')


if __name__ == '__main__':
    unittest.main()
