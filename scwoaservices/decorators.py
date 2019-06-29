"""
This module contains decorators to be used for api-endpoints.
The default decorator to be used is `service_endpoint`.

## Example usage
```python
@service_endpoint(app=SERVICERULES.app,
                  api='/example',
                  summary='example api',
                  in_model=InputModelExample,
                  out_model=OutputModelExample,
                  out_model_description='the output for the example request.')
async def api_example(request: Request,
                      service_params: InputModelExample) -> HTTPResponse:
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


def service_endpoint(*,
                     rules: BaseServiceRules,
                     api: str,
                     blueprint: Blueprint,
                     service_logger: logger,
                     summary: str,
                     in_model: BaseModel,
                     out_model: BaseModel,
                     in_model_location: Optional[str] = 'body',
                     out_model_description: Optional[str] = None) -> Callable:
    """
    Decorator to be used by default APIs. This decorator combines the
    preparation of the swagger-documentation and the transformation of the
    request and the response of the api using pydantic-models.

    # Parameters
        app (Sanic): the app of the service.
        api (str): the uri for the service-api.
        summary (str): the summary-description for the api to show in the
            swagger-documentation.
        in_model (BaseModel): the pydantic model to be used to
            transform the request-data.
        out_model (ServiceModel): the pydantic model to be used to
            transform the response of the api.
        in_model_location (Optional[str]): defines where inside the request
            the data is located.
        out_model_description (Optional[str]): description for the response
            data to show in the swagger-documentation.
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
        @blueprint.post('', strict_slashes=True)
        @doc.summary(summary)
        @doc.consumes(im_returns,
                      content_type='application/json',
                      location=in_model_location)
        @doc.produces(om_returns,
                      content_type='application/json',
                      description=out_model_description)
        @doc.response(412,
                      'Error: Precondition Failed',
                      description='The passed request-parameters are invalid')
        @doc.response(500,
                      'Error: Server-Error occured',
                      description='An internal error occured')
        @api_inputmodel(api=api[1:],
                        model=in_model,
                        rules=rules,
                        service_logger=service_logger)
        @api_outputmodel(api=api[1:],
                         model=out_model,
                         rules=rules,
                         service_logger=service_logger)
        @wraps(func)
        async def function_wrapper(request, *args, **kwargs):
            return await func(request=request, *args, **kwargs)

        return function_wrapper

    return decorator


def api_inputmodel(api: str, model: BaseModel, rules: BaseServiceRules,
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
                       f'to {rules.servicename}: {err}')
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


def api_outputmodel(api: str, model: BaseModel, rules: BaseServiceRules,
                    service_logger: logger) -> Callable:
    """
    Decorator to be used in api-methods to convert the response-data of the
    decorated api-method to a json based on the passed `schema`.

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
                       f'{rules.servicename}, api: {api}): {err}')
                raise ServerError(msg)
            service_logger.info(f'processed result {result} => '
                                f'{output.content_type} [{output.status}] '
                                f'{output.body}')
            return output

        return function_wrapper

    return decorator
