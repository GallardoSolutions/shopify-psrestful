import httpx

from . import settings

from .domain import ORDERED_SERVICES

PS_RESTFUL_API_KEY = settings.PS_RESTFUL_API_KEY
PS_REST_API = settings.PS_REST_API


class ServiceHelper:
    def __init__(self):
        self.headers = {'x-api-key': PS_RESTFUL_API_KEY}
        self.suppliers_trans = {}

    def get_latest_code(self, supplier_code: str, service: str) -> str:
        if supplier_code not in self.suppliers_trans:
            self._fill_out_latest_services(supplier_code)
        return self.suppliers_trans[supplier_code][service]

    def _fill_out_latest_services(self, supplier_code: str):
        url = f'{PS_REST_API}services/{supplier_code}'
        response = httpx.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f'Error getting services for supplier {supplier_code}: {response.text}')
        resp = response.json()
        self.suppliers_trans[supplier_code] = {}
        for service in ORDERED_SERVICES:
            srv = resp.get(service)
            if srv:
                versions = srv['versions']
                latest = self._get_latest_from_versions(versions)
                if latest:
                    self.suppliers_trans[supplier_code][service] = latest

    @staticmethod
    def _get_latest_from_versions(versions: list[dict]) -> str | None:
        ret = None
        for v in versions:
            if v['environment'] == 'PROD':
                version = v['version']
                if ret is None or version > ret:
                    ret = version
        return ret
