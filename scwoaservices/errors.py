"""
This module includes additional errors and the `ServiceErrorHandler` required
by services based on sanicbaseservice.
"""

from sanic.exceptions import SanicException
from sanic.handlers import ErrorHandler
from sanic.log import logger
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic.exceptions import ServerError


class PreconditionFailed(SanicException):
    """
    Exception to be used for invalid request-data.
    """


class ServiceErrorHandler(ErrorHandler):
    """
    this error-handler handles the errors occuring inside services based on
    scwoaservices.
    """

    def __init__(self, rules, *args, **kwargs):
        self.rules = rules
        super().__init__(*args, **kwargs)

    def default(self, request: Request, exception: Exception) -> HTTPResponse:
        """
        this method defines how errors occuring inside the service should be
        handled.

        # Parameters
            request (Request): the request-object for the requested api.
            exception (Exceeption): the exception raised during runtime.

        # Returns
            the httpresponse to return to the caller of the api.
        """
        logger.error(exception)

        if isinstance(exception, SanicException):
            return super().default(request, exception)

        location = (f'{self.rules.servicename}/'
                    f'{"".join(request.endpoint.split(".")[1:])}')
        msg = f'in api {location}: {str(exception)}'
        return super().default(request, ServerError(msg))
