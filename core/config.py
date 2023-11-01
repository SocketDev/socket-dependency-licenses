import logging
import os
import json


class Api:
    key: str

    def __init__(
            self,
            key: str,
            repo: str,
            branch: str = "dependencies",
            **kwargs
    ):
        self.key = key
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)


class Options:
    output_file: str
    package_files: list
    wait_time: int
    max_wait: int
    limit: int

    def __init__(
            self,
            output_file: str = "dependency_info.csv",
            wait_time: int = 0,
            max_wait: int = 20,
            limit: int = 1000,
            **kwargs
    ) -> None:
        self.output_file = output_file
        self.package_files = [
            "package.json",
            "requirements.txt"
        ]
        self.wait_time = wait_time
        self.max_wait = max_wait
        self.limit = limit
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)


class Config:
    def __init__(self) -> None:
        global SETTINGS
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s: %(funcName)s: %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logging = logging
        self.log = self.logging.getLogger("")
        SETTINGS = self
        self.options = Config.initialize_options("SOCKET_CONFIG")
        self.api = Config.initialize_api("SOCKET_API")
        SETTINGS = self

    @staticmethod
    def load_env_config(name, required) -> dict:
        env_options = os.getenv(name)
        if env_options is None and required:
            settings().log.error(f"env option {name} is required")
            exit(1)
        elif env_options is None and not required:
            settings().log.info(f"env {name} not passed, using defaults")
            config = None
        else:
            try:
                config = json.loads(env_options)
            except Exception as error:
                settings().log.error(f"Unable to parse {name}")
                settings().log.error(error)
                exit(1)
        return config

    @staticmethod
    def initialize_options(option) -> Options:
        config = Config.load_env_config(option, False)
        if config is None:
            options = Options()
        else:
            options = Options(**config)
        return options

    @staticmethod
    def initialize_api(option) -> Api:
        config = Config.load_env_config(option, True)
        api = Api(**config)
        return api


SETTINGS = None


def settings():
    """Wrapper around `SETTINGS` so that they can be lazily initialized"""
    return SETTINGS
