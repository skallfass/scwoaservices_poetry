"""
Inside this module all basic options for a service a defined inside the
`create_base_options`-function. For additional options you can define your own
`create_service_options`-function with additional parser which then can be
passed to the `create_base_options` as the `parser`-parameter.
To create additional flags or parameters the functions `add_flag` and
`add_param` should be used.
"""

from argparse import ArgumentParser
from argparse import Namespace
from typing import List
from typing import Optional
from typing import NoReturn
from typing import Union


def add_flag(*,
             parser: ArgumentParser,
             flag: str,
             help_str: Optional[str] = None) -> NoReturn:
    """
    Function to be used to add additional flag to an
    ``ArgumentParser``-instance.

    # Note
        This function modifies the passed ``parser``.

    # Parameters
        parser (ArgumentParser): The ArgumentParser-instance to add the flag
        flag (str): The name for the flag
        help_str (Optional[str]): Optional adding the help-string for the param
    """
    parser.add_argument(f'-{flag[0]}',
                        f'--{flag}',
                        help=help_str,
                        action='store_true')


def add_param(*,
              parser: ArgumentParser,
              short: str,
              name: str,
              param_type: Union[str, int, float],
              required: bool = False,
              default: Optional[Union[str, int, float]] = None,
              choices: Optional[List[Union[str, int, float]]] = None,
              help_str: Optional[str] = None) -> NoReturn:
    """
    Function to be used to add additional argument to an
    ``ArgumentParser``-instance.

    # Note
        This function modifies the passed ``parser``.

    # Parameters
        parser (ArgumentParser): The ArgumentParser to add the param
        short (str): Short name for the param
        name (str): Full name for the param
        param_type (Union[str, int, float]): The type of the param
        required (bool): Flag if the parameter is required.
        default (Optional[Union[str, int, float]): Optional setting the
            default-value to use for this param
        choices (Optional[List[Union[str, int, float]): Optional setting the
            choices for the possible values of the param
        help_str (Optional[str]): Optional adding the help-string for the param
    """
    args = dict(type=param_type, help=help_str)
    if default:
        args['default'] = default
    if choices:
        args['choices'] = choices
    if required:
        args['required'] = True
    parser.add_argument(f'-{short}', f'--{name}', **args)


def create_base_options(parser: Optional[ArgumentParser] = None) -> Namespace:
    """
    Builds the default arguments for a service.
    To use additional arguments create a ArgumentParser add your arguments
    using the functions :func:`add_param` or :func:`add_flag` and pass the
    resulting parser-object to this function.

    # Parameters
        parser (Optional[ArgumentParser]): Optional passed parser containing
            additional arguments

    # Returns
        args (Namespace): The parsed arguments parsed as Namespace-object
    """
    if not parser:
        parser = ArgumentParser()
    add_param(parser=parser,
              short='m',
              name='mode',
              param_type=str,
              choices=['devl', 'staging', 'prod'],
              default='devl')
    add_param(parser=parser, short='p', name='port', param_type=int)
    add_param(parser=parser, short='l', name='logfile', param_type=str)
    add_param(parser=parser, short='ho', name='hostname', param_type=str)
    add_param(parser=parser, short='w', name='workers', param_type=int)
    add_flag(parser=parser, flag='debugmode')
    args = parser.parse_args()
    return args
