"""
This module contains decorators to be used for api-endpoints.
The default decorator to be used is `service_endpoint`.

## Example usage
```python
from sanic.blueprints import Blueprint
from sanic.log import logger
from sanic.request import Request
from sanic.response import HTTPResponse

from scwoaservices.decorators import api_documentation
from scwoaservices.decorators import api_inputmodel
from scwoaservices.decorators import api_outputmodel

from exampleservice.models.example_api import InputModel
from exampleservice.models.example_api import OutputModel
from exampleservice.rules import SERVICERULES


NAME = 'Example'
API = '/example'
BLUEPRINT = Blueprint(NAME, API)


@BLUEPRINT.post('', strict_slashes=True)
@api_documentation(api=API, summary='example api', in_model=InputModel,
                   out_model=OutputModel,
                   out_description='the output for the example request.')
@api_inputmodel(api=API, model=InputModel,
                servicename=SERVICERULES.servicename, service_logger=logger)
@api_outputmodel(api=API, model=OutputModel,
                 servicename=SERVICERULES.servicename, service_logger=logger)
async def api_example(request: Request,
                      service_params: InputModel) -> HTTPResponse:
    return OutputModelExample(message=service_params.param)
```
"""

from dataclasses import make_dataclass
from functools import wraps
from typing import Callable
from typing import Optional

from pydantic import BaseModel
from pydantic import ValidationError
from sanic import response
from sanic.blueprints import Blueprint
from sanic.exceptions import ServerError
from sanic.log import logger
from sanic_openapi import doc

from scwoaservices.errors import PreconditionFailed
from scwoaservices.rules import BaseServiceRules


def api_documentation(api: str, summary: str, in_model: BaseModel,
                      out_model: BaseModel, out_description: str) -> Callable:
    """
    Decorator to be used in api-methods to serve the swagger-documentation for
    this api.

    # Parameters
        api (str): the route to the api.
        summary (str): the summary-description for the api.
        in_model (BaseModel): the InputModel to be used to transform the
            request-data.
        out_model (BaseModel): the OutputModel to be used to transform the
            output of the api for the client.
        out_description (str): description for the output returned by the api.

    # Returns
        decorator: decorated version of the function
    """
    for model, name in ((in_model, 'Input'), (out_model, 'Output')):
        doc.Object(
            make_dataclass(
                f'Api{api[1:].title()}{name}',
                [(key, val.type_, val.type_)
                 for key, val in model.__dict__['__fields__'].items()]))
    im_returns = doc.JsonBody({
        key: val.type_
        for key, val in in_model.__dict__['__fields__'].items()
    })

    om_returns = {
        key: val.type_
        for key, val in out_model.__dict__['__fields__'].items()
    }

    def decorator(func):
        @doc.summary(summary)
        @doc.response(412,
                      'Error: Precondition Failed',
                      description='The passed request-parameters are invalid')
        @doc.response(500,
                      'Error: Server-Error occured',
                      description='An internal error occured')
        @doc.consumes(im_returns,
                      content_type='application/json',
                      location='body')
        @doc.produces(om_returns,
                      content_type='application/json',
                      description=out_description)
        @wraps(func)
        async def function_wrapper(request, *args, **kwargs):
            return await func(request=request, *args, **kwargs)

        return function_wrapper

    return decorator


def api_inputmodel(api: str, model: BaseModel, servicename: str,
                   service_logger: logger) -> Callable:
    """
    Decorator to be used in api-methods to convert the request-data
    to an instance of the passed `model`. This instance is passed to the
    decorated api-endpoint as the parameter `service_params`.

    # Parameters
        model (BaseModel): The pydantic-model to use to convert the
            request-data passed to the decorated api-method.

    # Returns
        decorator: decorated version of the function
    """

    def decorator(func):
        @wraps(func)
        async def function_wrapper(request, *args, **kwargs):
            try:
                service_params = model.parse_raw(request.body)
            except ValidationError as err:
                msg = (f'API: {api} - invalid params ({request.json}) passed '
                       f'to {servicename}: {err}')
                service_logger.warning(msg)
                raise PreconditionFailed(msg, status_code=412)
            result = await func(request=request,
                                service_params=service_params,
                                service_logger=service_logger,
                                *args,
                                **kwargs)
            return result

        return function_wrapper

    return decorator


def api_outputmodel(api: str, model: BaseModel, servicename: str,
                    service_logger: logger) -> Callable:
    """
    Decorator to be used in api-methods to convert the response-data of the
    decorated api-method to a json based on the passed `model`.

    # Parameters
        model (BaseModel): The pydantic-model to use to convert the
            response data of the decorated api-method.

    # Returns
        decorator: decorated version of the function
    """

    def decorator(func):
        @wraps(func)
        async def function_wrapper(request, *args, **kwargs):
            service_result = await func(request, *args, **kwargs)
            try:
                if isinstance(service_result, model):
                    result = service_result
                else:
                    result = model(**service_result)
                output = response.json(result.dict())
            except Exception as err:
                msg = ('an internal error occured (service: '
                       f'{servicename}, api: {api}): {err}')
                raise ServerError(msg)
            service_logger.info(f'processed result {result} => '
                                f'{output.content_type} [{output.status}] '
                                f'{output.body}')
            return output

        return function_wrapper

    return decorator
