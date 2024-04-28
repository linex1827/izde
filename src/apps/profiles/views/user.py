from rest_framework.generics import CreateAPIView, GenericAPIView
from apps.common.exceptions import UnifiedErrorResponse
from apps.profiles.models.user import User, TemporaryUser, Vendor
from django.shortcuts import get_object_or_404

from apps.profiles.serializers.user import CancelOfferSerializer
from apps.profiles.services import user
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from drf_yasg import openapi
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from apps.profiles.services.payment import PaymentService
from apps.profiles.swaggers import swagger
from rest_framework.response import Response
from rest_framework import mixins, generics, status
from drf_yasg.utils import swagger_auto_schema
from apps.profiles.serializers import user as user_serializers
from apps.profiles.services import user as user_services

# Create your views here.

authorization_header = openapi.Parameter(
    'Authorization', in_=openapi.IN_HEADER,
    description="JWT токен для авторизации в формате: 'Bearer <токен>'",
    type=openapi.TYPE_STRING,
    required=True
)


class ProfileUserAPIView(RetrieveAPIView):
    serializer_class = user_serializers.ProfileUserSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Профиль пользователя'], manual_parameters=[authorization_header])
    def get(self, request, *args, **kwargs):
        serialized_data = self.get_serializer(self.request.user).data
        return Response(serialized_data)


class ChangeUserPasswordAPIView(mixins.UpdateModelMixin, generics.GenericAPIView):
    serializer_class = user_serializers.ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Профиль пользователя'],
        manual_parameters=[authorization_header],
        request_body=swagger.profile_change_password_request,
        responses=swagger.profile_change_password_response,
    )
    def patch(self, request, *args, **kwargs):
        user_status = user_services.change_user_password(self.request)

        if user_status == 'Password is not match':
            return Response({'status': user_status}, status=status.HTTP_400_BAD_REQUEST)
        elif user_status == 'Password is not correct':
            return Response({'status': user_status}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({'status': user_status}, status=status.HTTP_200_OK)


class UpdateUserProfileAPIView(mixins.UpdateModelMixin, generics.GenericAPIView):
    serializer_class = user_serializers.UpdateUserProfileSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Профиль пользователя'],
        manual_parameters=[authorization_header],
        request_body=swagger.update_profile_request,
        responses=swagger.update_profile_response,
    )
    def patch(self, request, *args, **kwargs):
        user_status = user_services.update_user_profile(self.request)
        return Response({'status': user_status}, status=status.HTTP_200_OK)


class RegisterUserAPIView(CreateAPIView):
    serializer_class = user_serializers.RegisterUserSerializer

    @swagger_auto_schema(
        tags=['Аутентификация и Авторизация пользователя'],
        request_body=swagger.user_request_body,
        responses=swagger.user_response,
    )
    def post(self, request, *args, **kwargs):
        user_id, error = user_services.register(self)

        if error:
            exception = UnifiedErrorResponse(
                detail=error,
                code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            return Response(exception.detail, status=exception.detail['error']['code'])
        return Response({'verification_token': user_id})


class VerifyUserAPIView(CreateAPIView):
    serializer_class = user_serializers.VerifyUserSerializer

    @swagger_auto_schema(
        tags=['Подтверждение'],
        request_body=swagger.user_confirm_request,
        responses=swagger.user_confirm_response,
    )
    def post(self, request, *args, **kwargs):
        token = self.request.data.get('token')
        code = self.request.data.get('code')
        tokens, error = user_services.create_verified_user_type(token, code, User.objects)

        if error:
            exception = UnifiedErrorResponse(
                detail=error,
                code=status.HTTP_400_BAD_REQUEST if error == 'Invalid code' else status.HTTP_401_UNAUTHORIZED
            )
            return Response(exception.detail, status=exception.detail['error']['code'])

        return Response(tokens, status=status.HTTP_201_CREATED)


class LoginUserAPIView(CreateAPIView):
    serializer_class = user_serializers.LoginSerializer

    @swagger_auto_schema(
        tags=['Аутентификация и Авторизация пользователя'],
        request_body=swagger.user_login_request,
        responses=swagger.user_login_response,
    )
    def post(self, request, *args, **kwargs):
        tokens, error = user_services.authenticate(
            email=request.data.get('email'),
            password=request.data.get('password'),
            user_object=User.objects
        )
        if error:
            exception = UnifiedErrorResponse(
                detail=error,
                code=status.HTTP_404_NOT_FOUND if error == 'User type does not exist' else status.HTTP_401_UNAUTHORIZED
            )
            return Response(exception.detail, status=exception.detail['error']['code'])
        return Response(tokens)


class SendResetCodeAPIView(CreateAPIView):
    serializer_class = user_serializers.SendResetCodeSerializer

    @swagger_auto_schema(
        tags=['Сброс пароля пользователя'],
        request_body=swagger.send_reset_code_request,
        responses=swagger.send_reset_code_response,
    )
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, email=request.data.get('email'))
        unique_reset_code_token = user_services.send_reset_code(user.email, User.objects)
        return Response({"reset_code_token": unique_reset_code_token})


class CheckResetCodeAPIView(mixins.UpdateModelMixin, GenericAPIView):
    serializer_class = user_serializers.VerifyUserSerializer

    @swagger_auto_schema(
        tags=['Сброс пароля пользователя'],
        request_body=swagger.check_reset_code_request,
        responses=swagger.check_reset_code_response,
    )
    def put(self, request, *args, **kwargs):
        reset_code = self.request.data.get('code')
        reset_code_token = self.request.data.get('token')
        access_token, error = user_services.check_reset_code(reset_code, reset_code_token, User.objects)
        if error:
            exception = UnifiedErrorResponse(
                detail=error,
                code=status.HTTP_400_BAD_REQUEST if error == "Invalid code" else status.HTTP_401_UNAUTHORIZED
            )
            return Response(exception.detail, status=exception.detail['error']['code'])
        return Response(access_token)


class ChangePasswordAPIView(mixins.UpdateModelMixin, GenericAPIView):
    serializer_class = user_serializers.ChangeUserPasswordSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Сброс пароля пользователя'],
        manual_parameters=[authorization_header],
        request_body=swagger.change_password_request,
        responses=swagger.change_password_response,
    )
    def patch(self, request, *args, **kwargs):
        new_password = self.request.data.get('new_password')
        confirming_password = self.request.data.get('confirm_password')
        status_response, error = user_services.check_user_password(self.request.user, new_password, confirming_password)

        if error:
            exception = UnifiedErrorResponse(
                detail=error,
                code=status.HTTP_400_BAD_REQUEST
            )
            return Response(exception.detail, status=exception.detail['error']['code'])

        return Response({'status': status_response})


class SendUserNewResetCodeAPIView(mixins.UpdateModelMixin, GenericAPIView):
    serializer_class = user_serializers.CheckVerifyTokenSerializer

    @swagger_auto_schema(
        tags=['Подтверждение'],
        request_body=swagger.send_verify_token_request,
        responses=swagger.send_verify_token_response,
    )
    def put(self, request, *args, **kwargs):
        verification_token = self.request.data.get('verification_token')
        status_result = user_services.send_new_reset_code(verification_token, User.objects)
        return Response(status_result)


class SendNewRegisterCodeAPIView(mixins.UpdateModelMixin, GenericAPIView):
    serializer_class = user_serializers.CheckVerifyTokenSerializer

    @swagger_auto_schema(
        tags=['Подтверждение'],
        request_body=swagger.send_verify_token_request,
        responses=swagger.send_verify_token_response,
    )
    def put(self, request, *args, **kwargs):
        verification_token = self.request.data.get('verification_token')
        token_status, result_status = user_services.send_new_register_code(verification_token, TemporaryUser.objects)
        if token_status:
            exception = UnifiedErrorResponse(
                detail=token_status,
                code=status.HTTP_401_UNAUTHORIZED
            )
            return Response(exception.detail, status=exception.detail['error']['code'])
        return Response(result_status)


class GoogleOAuthAPIView(CreateAPIView):
    serializer_class = user_serializers.GoogleOAuthSerializer

    @swagger_auto_schema(
        tags=['OAUTH авторизация'],
        request_body=swagger.google_auth_request,
        responses=swagger.google_auth_response,
    )
    def post(self, request, *args, **kwargs):
        google_token = self.request.data.get('google_token')
        tokens = user_services.get_or_create_from_google(google_token, User.objects)
        return Response(
            {'access': tokens['access'], 'refresh': tokens['refresh']},
            status=status.HTTP_201_CREATED if tokens.get('user_created') else status.HTTP_200_OK
        )


class CancelSearchAPIView(generics.DestroyAPIView):
    serializer_class = user_serializers.ProfileUserSerializer
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        return user_services.SearchService.cancel_search(self.request.user)


class CancelOfferAPIView(mixins.UpdateModelMixin, GenericAPIView):
    serializer_class = user_serializers.CancelOfferSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        return user_services.SearchService.cancel_offer(request.data.get('id'))


class AcceptOfferAPIView(mixins.UpdateModelMixin, GenericAPIView):
    serializer_class = CancelOfferSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        return user_services.SearchService.accept_offer(kwargs['offer_id'])


class AppleOAuthAPIView(CreateAPIView):
    serializer_class = user_serializers.AppleOAuthSerializer

    def post(self, request, *args, **kwargs):
        return user_services.get_or_create_from_apple(self)


class CustomTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(tags=['JWT токены'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenVerifyView(TokenVerifyView):
    @swagger_auto_schema(tags=['JWT токены'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CurrencyListAPIView(generics.ListAPIView):
    serializer_class = user_serializers.CurrencySerializer
    queryset = user_services.CurrencyService.filter(is_deleted=False)
    pagination_class = None
