# Manage Engine Service Desk Plus Rest API Python Module
## Background
Currently, the [Manage Engine Service Desk Plus Rest API](https://www.manageengine.com/products/service-desk/help/adminguide/api/rest-api.html) is xml based.

This python module eases the interaction with the API by translating the xml into a more pythonic structure.

## Usage
### Required Modules
* requests
* xmltodict

# Use
The main class "API" is used with your manage engine API key to access the common commands. The API key can be obtained via the sdplus section: Admin, Assignees, Edit Assignee (other than yourself), Generate API Key.
*Recommended: Setup your API key as a windows environment variable (e.g. SDPLUS_API_KEY).*
All interactions with the API require a "base" url - the url of how you usually access Service Desk Plus, with '/sdpapi/request/' appended at the end.

For example, to view a request, and return a list of dictionary items:
```python
import sdplus_api_rest

def eg_view_request():
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    result = api.send('154594', 'GET_REQUEST')
    print(result)
```

Most code you will write using this module will be similar to the above. 
E.g. to edit a request and change the subject line:
```python
def eg_edit_request():
    api = API(os.environ['SDPLUS_API_KEY'], 'http://sdplus/sdpapi/request/')
    fields = {'subject': 'EDITED EDITED ignore this request'}
    result = api.send('154820', 'EDIT_REQUEST', fields)
    print(result)
```

However, sometimes the xml returned is not standard to the common return structure from Manage Engine. In these cases, you can bypass this module's internal processing with the following "bypass=True" parameter:
```python
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
```