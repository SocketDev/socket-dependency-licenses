import requests
from urllib.parse import urlencode
import glob
import sys
import base64
import json


class APIKeyMissing(Exception):
    """Raised when the api key is not passed and the headers are empty"""
    pass


class Dependency:
    branch: str
    id: int
    name: str
    type: str
    version: str
    namespace: str
    repository: str

    def __init__(self, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def __str__(self):
        output = {
            "branch": self.branch,
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "version": self.version,
            "namespace": self.namespace,
            "repository": self.repository
        }
        return json.dumps(output)


class Org:
    id: int
    image: str
    name: str
    plan: str

    def __init__(self, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def __str__(self):
        output = {
            "id": self.id,
            "image": self.image,
            "name": self.name,
            "plan": self.plan
        }
        return json.dumps(output)


class Response:
    text: str
    error: bool
    status_code: int

    def __init__(self, text: str, error: bool, status_code: int):
        self.text = text
        self.error = error
        self.status_code = status_code


class DependGetData:
    url: str
    headers: dict
    payload: str

    def __init__(self, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)


class SocketDev:
    key: str
    url: str

    def __init__(
            self,
            key: str = None,
            url: str = "https://api.socket.dev/v0"
    ):
        self.key = key
        api_key_str = f"{self.key}:"
        self.encoded_key = base64.b64encode(api_key_str.encode()).decode('ascii')
        self.url = url

    @staticmethod
    def do_request(
            url: str,
            key: str = None,
            headers: dict = None,
            payload: str = None,
            files: list = None,
            method: str = "GET",
    ):
        if key is None and headers is None:
            raise APIKeyMissing

        if key is not None and headers is None:
            headers = {
                'Authorization': f"Basic {key}",
                'User-Agent': 'SocketPythonScript/0.0.1',
            }

        try:
            response = requests.request(
                method.upper(),
                url,
                headers=headers,
                data=payload,
                files=files
            )
        except Exception as error:
            response = Response(
                text=f"{error}",
                error=True,
                status_code=500
            )
        return response

    def post_dependencies(self, files: list, params: dict) -> [None, str]:
        loaded_files = []
        loaded_files = SocketDev.load_files(files, loaded_files)
        url = f"{self.url}/dependencies/upload?"
        url = url + urlencode(params)
        response = SocketDev.do_request(
            url=url,
            key=self.encoded_key,
            files=loaded_files,
            method="POST",
            headers=None,
            payload=None
        )
        if response.status_code == 200:
            result = response.json()
            result_id = result.get("id")
        else:
            result_id = None
            print("Error posting dependency to the API")
            print(response.text)
        return result_id

    def get_dependencies(
            self,
            limit: int = 50,
            offset: int = 0
    ) -> [list, dict]:
        api_url = f"{self.url}/dependencies/search"
        payload = {
            "limit":  limit,
            "offset": offset
        }
        payload_str = json.dumps(payload)
        response = SocketDev.do_request(
            url=api_url,
            key=self.encoded_key,
            method="POST",
            headers=None,
            payload=payload_str
        )
        if response.status_code == 200:
            result = response.json()
            rows = result.get("rows")
            dependencies = SocketDev.process_dependencies(rows)
        else:
            dependencies = []
            print("Unable to retrieve Dependencies")
            print(response.text)
        return dependencies

    @staticmethod
    def process_dependencies(rows) -> list:
        dependencies = []
        if rows is not None:
            for row in rows:
                dependency = Dependency(**row)
                if dependency.namespace == "\"" or dependency.namespace == "":
                    dependency.namespace = None
                dependencies.append(dependency)
        return dependencies

    def get_org_ids(self, org_name: str = None) -> dict:
        orgs = self.get_organizations()
        org_results = orgs.get("organizations")
        org_ids = {}
        if org_results is not None:
            for org in org_results:
                org_obj = Org(**org_results[org])
                if org_name is None or org_name == org_obj.name:
                    org_ids[org_obj.id] = org_obj
        else:
            org_ids = orgs
        return org_ids

    def get_organizations(self) -> dict:

        url = f"{self.url}/organizations"
        headers = None
        payload = None

        response = SocketDev.do_request(
            url=url,
            key=self.encoded_key,
            headers=headers,
            payload=payload
        )
        if response.status_code == 200:
            result = response.json()
        else:
            result = {
                "msg": "Error posting dependency to the API",
                "error": response.text
            }
        return result

    @staticmethod
    def find_package_files(folder: str, file_types: list):
        files = []

        for file_type in file_types:
            search_pattern = f"{folder}/**/{file_type}"
            result = glob.glob(search_pattern, recursive=True)
            if sys.platform.lower() == "win32":
                result = SocketDev.fix_file_path(result)
            files.extend(result)
        return files

    @staticmethod
    def fix_file_path(files) -> list:
        fixed_files = []
        for file in files:
            file = file.replace("\\", '/')
            fixed_files.append(file)
        return fixed_files

    @staticmethod
    def load_files(files: list, loaded_files: list):
        for file in files:
            if "/" in file:
                _, file_name = file.rsplit("/", 1)
            elif "\\" in file:
                _, file_name = file.rsplit("/", 1)
            else:
                file_name = file
            try:
                file_tuple = (file_name, (file_name, open(file, 'rb'), 'text/plain'))
                loaded_files.append(file_tuple)
            except Exception as error:
                print(f"Unable to open {file}")
                print(error)
                exit(1)
        return loaded_files

    @staticmethod
    def prepare_for_csv(dependencies: list, packages: dict) -> list:
        output = []
        for dependency in dependencies:
            if dependency.name in packages:
                for package in packages[dependency.name]:
                    output_object = [
                        dependency.repository,
                        dependency.branch,
                        package.name,
                        package.version,
                        package.license,
                        package.repository
                    ]
                    output.append(output_object)
        return output


