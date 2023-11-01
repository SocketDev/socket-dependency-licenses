import json
import requests
from core.socket_dev import Dependency


class Package:
    name: str
    description: str
    keywords: list
    version: str
    homepage: str
    bugs: dict
    license: str
    licenses: list
    main: str
    exports: dict
    repository: dict
    engines: dict
    dependencies: dict
    browserify: dict
    gitHead: str
    _id: str
    _nodeVersion: str
    _npmVersion: str
    dist: dict
    _npmUser: dict
    directories: dict
    maintainers: list
    _npmOperationalInternal: list
    _hasShrinkwrap: bool

    def __init__(self, **kwargs):
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def __str__(self):
        output = json.dumps(self.__dict__)
        return json.dumps(output)


class Search:
    base_url: str

    def __init__(self, base_url: str = "https://registry.npmjs.com"):
        self.base_url = base_url

    def do_request(
            self,
            path: str,
            headers: dict = None,
            payload: str = None,
            files: list = None,
            method: str = "GET",
    ) -> [requests.request, None]:

        url = f"{self.base_url}/{path}"
        if headers is None:
            headers = {
                'User-Agent': 'NpmSearch/0.0.1',
            }

        try:
            response = requests.request(
                method.upper(),
                url,
                headers=headers,
                data=payload,
                files=files
            )
            return response
        except Exception as error:
            print(f"Failed to perform request for {url} with method {method}")
            print(error)
            return None

    def get_package_details(self, dependency: Dependency) -> [Package, None, bool, int]:
        pkg_name_search = f"{dependency.name}@{dependency.version}"
        pkg_url = f"{dependency.name}/{dependency.version}"
        response = self.do_request(path=pkg_url)
        retry_wait = 0
        package = None
        not_found = False
        if response.status_code == 200:
            pkg_json = response.json()
            package = Package(**pkg_json)
            if not hasattr(package, "version"):
                package.version = dependency.version
            if not hasattr(package, "repository"):
                package.repository = ""
            package.repository = Search.get_package_repo(package)
            package.license = Search.get_license(package)
        elif response.status_code == 404:
            print(
                f"{pkg_name_search} not found on the NPM registry, trying base package"
            )
            package, not_found, retry_wait = self.get_package(dependency)
        elif response.status_code == 429:
            retry_wait = response.headers.get("Retry-After")
            retry_wait = int(retry_wait)
            print(f"npm rate limit hit try after {retry_wait}")
        elif response.status_code == 503:
            print("NPM Service availability issue")
            retry_wait = 15
        return package, not_found, retry_wait

    @staticmethod
    def get_package_repo(package: Package) -> str:
        if type(package.repository) is dict:
            repo = package.repository.get("url")
            repo = repo.replace("git+", "")
            repo = repo.replace("git://github.com", "https://github.com")
            repo = repo.replace("ssh://git@github.com", "https://github.com")
            repo = repo.rstrip(".git")
            if repo == "npm/security-holder":
                repo = ""
        else:
            repo = package.repository
        return repo

    @staticmethod
    def get_license(package: Package) -> str:
        license_type = None
        if hasattr(package, "licenses"):
            for info in package.licenses:
                info_type = info.get("type")
                if license_type is None:
                    license_type = info_type
                else:
                    license_type = license_type + f";{info_type}"
        elif hasattr(package, "license"):
            license_type = package.license
        else:
            license_type = ""
        return license_type

    def get_package(self, dependency: Dependency) -> ([Package, None], bool, int):
        pkg_name_search = f"{dependency.name}"
        response = self.do_request(path=dependency.name)
        retry_wait = 0
        package = None
        not_found = False
        if response.status_code == 200:
            pkg_json = response.json()
            package = Package(**pkg_json)
            if not hasattr(package, "version"):
                package.version = dependency.version
            package.license = Search.get_license(package)
            if not hasattr(package, "repository"):
                package.repository = ""
            package.repository = Search.get_package_repo(package)
        elif response.status_code == 404:
            not_found = True
            package = Package(
                name=dependency.name,
                version=dependency.version,
                license="",
                repository=""
            )
            print(f"{pkg_name_search} not found on the NPM registry")
        elif response.status_code == 429:
            retry_wait = response.headers.get("Retry-After")
            retry_wait = int(retry_wait)
            print(f"npm rate limit hit try after {retry_wait}")
        elif response.status_code == 503:
            print("NPM Service availability issue")
            retry_wait = 15
        return package, not_found, retry_wait
