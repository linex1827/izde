from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.exceptions import InvalidToken


def unified_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, InvalidToken):
        return Response({"detail": "Given token not valid for any token type"}, status=status.HTTP_401_UNAUTHORIZED)

    if response is not None:
        error_messages = {}
        for key, value in response.data.items():
            if isinstance(value, list):
                error_messages[key] = ", ".join(value)
            else:
                error_messages[key] = value

        response.data = error_messages

    return response
