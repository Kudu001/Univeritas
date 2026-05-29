from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'status': 'error',
            'data': None,
            'message': _extract_message(response.data),
        }

    return response


def _extract_message(data):
    if isinstance(data, str):
        return data
    if isinstance(data, list) and data:
        return _extract_message(data[0])
    if isinstance(data, dict):
        for key in ('detail', 'non_field_errors', *data.keys()):
            if key in data:
                val = data[key]
                if isinstance(val, list) and val:
                    return str(val[0])
                return str(val)
    return 'An error occurred.'
