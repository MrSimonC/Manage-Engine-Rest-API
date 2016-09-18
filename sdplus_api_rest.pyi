# Python 3.5 Type Hinting Stub File
from typing import Dict, Optional

class API:
    def __init__(self, api_key:str,
                 api_url_base:str):
        self.api_key = api_key
        self.api_url_base = api_url_base

    @staticmethod
    def _create_xml(fields: Dict(),
                    sub_elements: Optional(list)=None) -> str:
        pass

    def send(self, url_append: str,
             operation_name: str,
             input_fields: Optional(Dict[str, str])=None,
             attachment: str='',
             sub_elements: list=None,
             bypass: bool=False):
        pass
