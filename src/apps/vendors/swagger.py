from drf_yasg import openapi
from rest_framework import status

vendor_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['first_name', 'last_name', 'email', 'password', 'confirm_password', 'phone_number'],
    properties={
        'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя'),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Фамилия пользователя'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Почта пользователя'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль пользователя'),
        'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Подтверждение пароля'),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='номер телефона')
    }
)

vendor_response = {
    status.HTTP_200_OK: openapi.Response(
        description='Токен верификации',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'verification_token': openapi.Schema(type=openapi.TYPE_STRING, description='verify token'),
            },
        ),
    ),
    status.HTTP_422_UNPROCESSABLE_ENTITY: openapi.Response(
        description='Вендор уже существует',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Проверка на существование'),
            },
        ),
    ),
    status.HTTP_400_BAD_REQUEST: openapi.Response(
        description='Валидации с паролем',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'password': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description='валидации пароля',
                    items=openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description='Сообщение валидации'
                    )
                ),
            },
        ),
    ),
}

vendor_confirm_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['code', 'token'],
    properties={
        'code': openapi.Schema(type=openapi.TYPE_STRING, description='код подтверждение для сброса'),
        'token': openapi.Schema(type=openapi.TYPE_STRING, description='уникальный токен для сброса'),
    }
)
vendor_confirm_response = {
    status.HTTP_201_CREATED: openapi.Response(
        description='вендор успешно создан',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='refresh_token'),
                'access': openapi.Schema(type=openapi.TYPE_STRING, description='access_token'),
            },
        ),
    ),
    status.HTTP_401_UNAUTHORIZED: openapi.Response(
        description='Срок токена истек',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, default='Token lifetime has expired'),
            },
        ),
    ),
    status.HTTP_400_BAD_REQUEST: openapi.Response(
        description='Введенные коды не совпадают',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, default='Invalid code'),
            },
        ),
    ),
}

vendor_login_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'password'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Почта вендора'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль вендора'),
    }
)
vendor_login_response = {
    status.HTTP_200_OK: openapi.Response(
        description='Вендор успешно авторизовался',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='refresh_token'),
                'access': openapi.Schema(type=openapi.TYPE_STRING, description='access_token'),
            },
        ),
    )
}

send_vendor_reset_code_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='email для сброса'),
    }
)
send_vendor_reset_code_response = {
    status.HTTP_200_OK: openapi.Response(
        description='В ответе приходит токен для сброса',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reset_code_token': openapi.Schema(type=openapi.TYPE_STRING, description='reset_token'),
            },
        ),
    )
}

check_vendor_reset_code_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['token', 'code'],
    properties={
        'token': openapi.Schema(type=openapi.TYPE_STRING, description='уникальный токен для сброса'),
        'code': openapi.Schema(type=openapi.TYPE_STRING, description='введенный код от юзера'),
    }
)
check_vendor_reset_code_response = {
    status.HTTP_200_OK: openapi.Response(
        description='В ответе приходит токен для сброса',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'access': openapi.Schema(type=openapi.TYPE_STRING, description='access_token'),
            },
        ),
    ),
    status.HTTP_400_BAD_REQUEST: openapi.Response(
        description='Введенный код не верный',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, default='code is not match'),
            },
        ),
    ),
    status.HTTP_401_UNAUTHORIZED: openapi.Response(
        description='Срок токена истек',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, default='Token lifetime is expired'),
            },
        ),
    )
}

change_vendor_password_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['new_password', 'confirm_password'],
    properties={
        'new_password': openapi.Schema(type=openapi.TYPE_STRING),
        'confirm_password': openapi.Schema(type=openapi.TYPE_STRING),
    }
)
change_vendor_password_response = {
    status.HTTP_200_OK: openapi.Response(
        description='В ответе приходит токен для сброса',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, default='success'),
            },
        ),
    ),
    status.HTTP_400_BAD_REQUEST: openapi.Response(
        description='Введенный код не верный',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, default='code is not match'),
            },
        ),
    ),
    status.HTTP_401_UNAUTHORIZED: openapi.Response(
        description='Срок токена истек',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, default='Token lifetime is expired'),
            },
        ),
    )
}

vendor_google_auth_request = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['google_token'],
        properties={
            'google_token': openapi.Schema(type=openapi.TYPE_STRING, description='Токен от гугла'),
        }
    )
vendor_google_auth_response = {
        status.HTTP_201_CREATED: openapi.Response(
            description='Вендор успешно создался',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='refresh_token'),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='access_token'),
                },
            ),
        ),
        status.HTTP_200_OK: openapi.Response(
            description='Вендор успешно авторизовался',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='refresh_token'),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='access_token'),
                },
            ),
        )
    }
