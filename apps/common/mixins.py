from rest_framework.response import Response
from rest_framework import status


class SuccessResponseMixin:
    """Mixin that wraps view responses in the standard envelope."""

    def success(self, data=None, message='', status_code=status.HTTP_200_OK):
        return Response(
            {'status': 'success', 'data': data, 'message': message},
            status=status_code,
        )

    def created(self, data=None, message=''):
        return self.success(data=data, message=message, status_code=status.HTTP_201_CREATED)

    def error(self, message='', data=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response(
            {'status': 'error', 'data': data, 'message': message},
            status=status_code,
        )
