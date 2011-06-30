from django.http import HttpResponseRedirect

from flowgram import localsettings
from flowgram.core.require import permissionscheckers, transformers
from flowgram.core.response import data_response, error_response

from functools import wraps


class RedirectException(Exception):
    def __init__(self, url):
        self.url = url


def parse_required_arg(required_arg):
    """Parses a required_arg string like: <name>(:<value>)?(=<default_value>)?"""
    required_arg_parts = required_arg.split('=')
    default_value = required_arg_parts[1] if len(required_arg_parts) == 2 else None
    required_arg = required_arg_parts[0]

    required_arg_parts = required_arg.split(':')
    type = required_arg_parts[1] if len(required_arg_parts) == 2 else None
    required_arg = required_arg_parts[0]

    return (required_arg, type, default_value)


def require(method, required_args=[], permissions=[]):
    def check(func):
        @wraps(func)
        def wrapper_func(request, *args, **kwargs):
            method_args = request.GET if request.method == 'GET' else request.POST

            default_enc = 'json'

            parsed_required_args = []
            for required_arg in required_args:
                (required_arg, type, default_value) = parse_required_arg(required_arg)
                parsed_required_args.append([required_arg, type, default_value])

                if required_arg == 'enc':
                    default_enc = default_value

            enc = method_args.get('enc', default_enc)

            # Checking method.
            if method and request.method != method:
                return error_response.create(enc, '%s method not allowed.' % request.method)

            transformed_values = {}
            
            try:
                # Checking required arguments.
                for (required_arg, type, default_value) in parsed_required_args:
                    if default_value == None and \
                            not required_arg in method_args and \
                            not required_arg in kwargs:
                        return error_response.create(enc, 'Missing required field %s.' % required_arg)

                    try:
                        value = method_args.get(required_arg, kwargs.get(required_arg, default_value))
                        new_name = required_arg
                        if type in transformers.transform_funcs:
                            (new_name, value) = transformers.transform_funcs[type](request, value)
                        if required_arg in transformers.transform_funcs:
                            (new_name, value) = \
                                transformers.transform_funcs[required_arg](request, value)
                        args += (value,)
                        transformed_values[new_name or required_arg] = value
                    except transformers.TransformError, (errMessage):
                        return error_response.create(enc, str(errMessage))

                # Checking permissions
                for permission in permissions:
                    if not permissionscheckers.permission_funcs[permission](request,
                                                                            method_args,
                                                                            transformed_values):
                        return error_response.create(enc, 'Does not have %s permission.' % permission \
                                                              if localsettings.DEBUG \
                                                              else 'Permission violation')
            except RedirectException, e:
                return HttpResponseRedirect(e.url)

            kwargs = {}
            return func(request, *args, **kwargs) or data_response.create(enc, 'ok', {})
        return wrapper_func
    return check
