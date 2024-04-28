from drf_yasg import openapi
from rest_framework import status


profile_change_password_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['old_password', 'new_password', 'confirm_password'],
    properties={
        'old_password': openapi.Schema(type=openapi.TYPE_STRING, description='Текущий пароль'),
        'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='Новый пароль'),
        'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Подтверждение пароля')
    }
)

profile_change_password_response = {
    status.HTTP_200_OK: openapi.Response(
        description='Пароль успешно изменен',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, default='success'),
            },
        ),
    ),
    status.HTTP_400_BAD_REQUEST: openapi.Response(
        description='Пароли не совпадают',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, default='Password is not match'),
            },
        ),
    ),
    status.HTTP_401_UNAUTHORIZED: openapi.Response(
        description='Текущий пароль не верный',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING,default='Password is not correct'),
            },
        ),
    ),
}

update_profile_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['first_name', 'last_name'],
    properties={
        'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Имя юзера'),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Фамилия юзера'),
    }
)

update_profile_response = {
    status.HTTP_200_OK: openapi.Response(
        description='Имя и фамилия успешно изменены',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, default='success'),
            },
        ),
    ),
}

from drf_yasg import openapi
from rest_framework import status

# REGISTER
user_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['first_name', 'last_name', 'email', 'password', 'confirm_password'],
    properties={
        'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя'),
        'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Фамилия пользователя'),
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Почта пользователя'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль пользователя'),
        'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Подтверждение пароля')
    }
)
user_response = {
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
        description='Пользователь уже существует',
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

# CONFIRMATION
user_confirm_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['code', 'token'],
    properties={
        'code': openapi.Schema(type=openapi.TYPE_STRING, description='код подтверждение для сброса'),
        'token': openapi.Schema(type=openapi.TYPE_STRING, description='уникальный токен для сброса'),
    }
)
user_confirm_response = {
    status.HTTP_201_CREATED: openapi.Response(
        description='Пользователь успешно создан',
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

# LOGIN
user_login_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email', 'password'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='Почта пользователя'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль пользователя'),
    }
)
user_login_response = {
    status.HTTP_200_OK: openapi.Response(
        description='Пользователь успешно авторизовался',
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='refresh_token'),
                'access': openapi.Schema(type=openapi.TYPE_STRING, description='access_token'),
            },
        ),
    )
}

# SEND RESET CODE
send_reset_code_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['email'],
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='email для сброса'),
    }
)
send_reset_code_response = {
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

# CHECK RESET CODE
check_reset_code_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['token', 'code'],
    properties={
        'token': openapi.Schema(type=openapi.TYPE_STRING, description='уникальный токен для сброса'),
        'code': openapi.Schema(type=openapi.TYPE_STRING, description='введенный код от юзера'),
    }
)
check_reset_code_response = {
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

# CHANGE PASSWORD
change_password_request = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['new_password', 'confirming_password'],
    properties={
        'new_password': openapi.Schema(type=openapi.TYPE_STRING),
        'confirm_password': openapi.Schema(type=openapi.TYPE_STRING),
    }
)
change_password_response = {
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

# SEND VERIFICATION TOKEN
send_verify_token_request = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['verification_token'],
        properties={
            'verification_token': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )
send_verify_token_response = {
        status.HTTP_200_OK: openapi.Response(
            description='В ответе приходит уникальный токен для подтверждения юзера',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'verification_token': openapi.Schema(type=openapi.TYPE_STRING),
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

# OAUTH GOOGLE
google_auth_request = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['google_token'],
        properties={
            'google_token': openapi.Schema(type=openapi.TYPE_STRING, description='Токен от гугла'),
        }
    )
google_auth_response = {
        status.HTTP_201_CREATED: openapi.Response(
            description='Пользователь успешно создался',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='refresh_token'),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='access_token'),
                },
            ),
        ),
        status.HTTP_200_OK: openapi.Response(
            description='Пользователь успешно авторизовался',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='refresh_token'),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='access_token'),
                },
            ),
        )
    }


