from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response


class UnifiedErrorResponse(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A server error occurred.'
    default_code = 'error'

    def __init__(self, detail=None, code=None):
        if detail is not None:
            self.detail = {'error': {'message': detail, 'code': code or self.status_code}}
        else:
            self.detail = {'error': {'message': self.default_detail, 'code': self.default_code}}
