from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import NoReturn
from pkg_resources import get_distribution

from sanic import Sanic
from sanic_openapi import swagger_blueprint

from scwoaservices.errors import ServiceErrorHandler


@dataclass
class BaseServiceRules:
    servicename: str
    host: str
    port: int
    debug: bool
    title: str
    description: str
    contact_email: str
    version: str = None
    app: Sanic = None
    produces_content_types: List[str] = field(
        default_factory=lambda: ['application/json'])
    workers: int = 1
    mode: str = 'devl'

    def __post_init__(self) -> NoReturn:
        """
        Sets the more complex attributes of this class like the swagger-config.
        """
        try:
            self.version = get_distribution(self.servicename).version
        except:
            self.version = ''
        self.app = Sanic()
        self.app.blueprint(swagger_blueprint)
        self.app.config.API_VERSION = self.version
        self.app.config.API_TITLE = self.title
        self.app.config.API_DESCRIPTION = self.description
        self.app.config.API_PRODUCES_CONTENT_TYPES = self.produces_content_types
        self.app.config.API_CONTACT_EMAIL = self.contact_email
        self.app.config.API_HOST = f'{self.host}:{self.port}'
        self.app.error_handler = ServiceErrorHandler(self)

    def reconfig(self, host, port, mode) -> NoReturn:
        """
        Reconfigures the host- and port-attributes and also sets the api-host
        definition of the swagger-config.

        # Parameters
            host (str): the host where the service runs.
            port (int): the port on which the service can be accessed.
        """
        self.host = host
        self.port = port
        self.mode = mode
        self.app.config.API_HOST = f'{self.host}:{self.port}'
