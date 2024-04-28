from rest_framework import generics
from rest_framework.response import Response
from apps.common.exceptions import UnifiedErrorResponse
from apps.houserent.permissions import IsVendor, IsVendorOwnerOrReadOnly
from apps.profiles.services import user
from apps.profiles.services import user as user_service
from apps.profiles.serializers import user as user_serializers
from apps.profiles.views.user import authorization_header
from apps.vendors import serializers as v_serializers
from apps.vendors import services as v_services
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import mixins, views
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from apps.vendors import swagger
from apps.profiles.swaggers import swagger as vendor_confirm
from apps.profiles.models import user as models
from apps.vendors.serializers import OrderSerializer, CurrentOccupancySerializer, DetailCurrentOccupancySerializer
from apps.vendors.utils import send_sms_code_from_nikita


class RegisterVendorAPIView(generics.CreateAPIView):
    serializer_class = v_serializers.RegisterVendorSerializer

    @swagger_auto_schema(
        tags=['Регистрация и Авторизация вендора'],
        request_body=swagger.vendor_request_body,
        responses=swagger.vendor_response,
    )
    def post(self, request, *args, **kwargs):
        temporary_user_id, error = user_service.register(self)
        if error:
            exception = UnifiedErrorResponse(
                detail=error,
                code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
            return Response(exception.detail, status=exception.detail['error']['code'])

        return Response({'verification_token': temporary_user_id})


class VerifyVendorAPIView(generics.CreateAPIView):
    serializer_class = user_serializers.VerifyUserSerializer

    @swagger_auto_schema(
        tags=['Подтверждение'],
        request_body=swagger.vendor_confirm_request,
        responses=swagger.vendor_confirm_response,
    )
    def post(self, request, *args, **kwargs):
        token = self.request.data.get('token')
        code = self.request.data.get('code')
        tokens, error = user_service.create_verified_user_type(token, code, models.Vendor.objects)

        if error:
            exception = UnifiedErrorResponse(
                detail=error,
                code=status.HTTP_400_BAD_REQUEST if error == 'Invalid code' else status.HTTP_401_UNAUTHORIZED
            )
            return Response(exception.detail, status=exception.detail['error']['code'])

        return Response(tokens, status=status.HTTP_201_CREATED)


class SendVendorResetCode(generics.CreateAPIView):
    serializer_class = user_serializers.SendResetCodeSerializer

    @swagger_auto_schema(
        tags=['Сброс пароля вендора'],
        request_body=swagger.send_vendor_reset_code_request,
        responses=swagger.send_vendor_reset_code_response,
    )
    def post(self, request, *args, **kwargs):
        vendor = get_object_or_404(models.Vendor, email=request.data.get('email'))
        unique_reset_code_token = user.send_reset_code(vendor.email, models.Vendor.objects)
        return Response({"reset_code_token": unique_reset_code_token})


class SendVendorNewResetCodeAPIView(mixins.UpdateModelMixin, generics.GenericAPIView):
    serializer_class = user_serializers.CheckVerifyTokenSerializer

    @swagger_auto_schema(
        tags=['Подтверждение'],
        request_body=vendor_confirm.send_verify_token_request,
        responses=vendor_confirm.send_verify_token_response,
    )
    def put(self, request, *args, **kwargs):
        verification_token = self.request.data.get('verification_token')
        status_result = user_service.send_new_reset_code(verification_token, models.Vendor.objects)
        return Response(status_result)


class CheckVendorResetCodeAPIView(mixins.UpdateModelMixin, generics.GenericAPIView):
    serializer_class = user_serializers.VerifyUserSerializer

    @swagger_auto_schema(
        tags=['Сброс пароля вендора'],
        request_body=swagger.check_vendor_reset_code_request,
        responses=swagger.check_vendor_reset_code_response,
    )
    def put(self, request, *args, **kwargs):
        reset_code = self.request.data.get('code')
        reset_code_token = self.request.data.get('token')
        access_token, error = user_service.check_reset_code(reset_code, reset_code_token, models.Vendor.objects)

        if error:
            exception = UnifiedErrorResponse(
                detail=error,
                code=status.HTTP_400_BAD_REQUEST if error == "Invalid code" else status.HTTP_401_UNAUTHORIZED
            )
            return Response(exception.detail, status=exception.detail['error']['code'])

        return Response(access_token)


class ChangeVendorPasswordAPIView(mixins.UpdateModelMixin, generics.GenericAPIView):
    serializer_class = user_serializers.ChangeUserPasswordSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Сброс пароля вендора'],
        manual_parameters=[authorization_header],
        request_body=swagger.change_vendor_password_request,
        responses=swagger.change_vendor_password_response,
    )
    def patch(self, request, *args, **kwargs):
        new_password = self.request.data.get('new_password')
        confirming_password = self.request.data.get('confirm_password')
        status_response, error = user_service.check_user_password(self.request.user, new_password, confirming_password)

        if error:
            exception = UnifiedErrorResponse(
                detail=error,
                code=status.HTTP_400_BAD_REQUEST
            )
            return Response(exception.detail, status=exception.detail['error']['code'])
        return Response({'status': status_response})


class LoginVendorAPIView(generics.CreateAPIView):
    serializer_class = user_serializers.LoginSerializer

    @swagger_auto_schema(
        tags=['Регистрация и Авторизация вендора'],
        request_body=swagger.vendor_login_request,
        responses=swagger.vendor_login_response,
    )
    def post(self, request, *args, **kwargs):
        tokens, error = user_service.authenticate(
            email=request.data.get('email'),
            password=request.data.get('password'),
            user_object=models.Vendor.objects
        )

        if error:
            exception = UnifiedErrorResponse(
                detail=error,
                code=status.HTTP_404_NOT_FOUND if error == 'User type does not exist' else status.HTTP_401_UNAUTHORIZED
            )
            return Response(exception.detail, status=exception.detail['error']['code'])
        user = models.Vendor.objects.get(email=request.data.get('email'))
        if user.twofa:
            return Response(data={'message': 'two-factor is enabled'}, status=status.HTTP_204_NO_CONTENT)
        return Response(tokens)


class TwoFactorLoginAPIView(generics.CreateAPIView):
    serializer_class = v_serializers.TwoFactorLoginSerializer

    def post(self, request, *args, **kwargs):
        tokens, error = v_services.TwoFactorService.twofactor_login(
            email=request.data.get('email'),
            password=request.data.get('password'),
            code=request.data.get('code'),
        )

        if error:
            exception = UnifiedErrorResponse(
                detail=error,
                code=status.HTTP_400_BAD_REQUEST if error == 'Wrong code' else status.HTTP_401_UNAUTHORIZED
            )
            return Response(exception.detail, status=exception.detail['error']['code'])
        return Response(tokens)


class GoogleOAuthAPIView(generics.CreateAPIView):
    serializer_class = user_serializers.GoogleOAuthSerializer

    @swagger_auto_schema(
        tags=['OAUTH авторизация'],
        request_body=swagger.vendor_google_auth_request,
        responses=swagger.vendor_google_auth_response,
    )
    def post(self, request, *args, **kwargs):
        google_token = self.request.data.get('google_token')
        tokens = user_service.get_or_create_from_google(google_token, models.Vendor.objects)
        status_code = status.HTTP_201_CREATED if tokens.get('user_created') else status.HTTP_200_OK

        return Response({
            'access': tokens['access'],
            'refresh': tokens['refresh'],
        }, status=status_code)


class TwoFactorSetupAPIView(generics.GenericAPIView):
    serializer_class = v_serializers.TwoFactorSetupSerializer
    permission_classes = [IsVendor]

    def get(self, request, *args, **kwargs):
        user = request.user
        user_object = models.Vendor.objects.filter(email=user.email).first()
        service = v_services.TwoFactorService.twofactor_setup(user_object)
        if service:
            return Response(service, status=status.HTTP_200_OK)


class TwoFactorVerifyAPIView(generics.GenericAPIView):
    serializer_class = v_serializers.TwoFACodeSerializer
    permission_classes = [IsVendor]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        service = v_services.TwoFactorService.twofactor_verify(serializer.validated_data['code'], email=user.email)
        if service:
            return Response(data={'2fa successfully activated'}, status=status.HTTP_200_OK)
        if service is not None:
            return Response({'2fa is disabled'}, status=status.HTTP_202_ACCEPTED)
        if not service:
            return Response(data={'wrong code'}, status=status.HTTP_400_BAD_REQUEST)


class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsVendor]

    def get_queryset(self):
        return v_services.OrderListService.get_vendor_orders(self.request.user.vendor)


class ApprovedOrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsVendor]

    def get_queryset(self):
        return v_services.OrderListService.approved_vendor_orders(self.request.user.vendor)


class CurrentOccupancyAPIView(generics.ListAPIView):
    serializer_class = CurrentOccupancySerializer
    permission_classes = [IsVendor]

    def get_queryset(self):
        return v_services.OrderListService.get_current_occupancy(self.request.user.vendor)


class DetailCurrentOccupancy(generics.RetrieveAPIView):
    serializer_class = DetailCurrentOccupancySerializer
    permission_classes = [IsVendor]
    lookup_field = 'order_id'

    def get_object(self):
        return v_services.OrderListService.detail_current_occupancy(self.kwargs['order_id'], self.request.user.vendor)


'''AGREEMENT VIEW'''


class AgreementListAPIView(generics.ListAPIView):
    serializer_class = v_serializers.AgreementSerializer
    queryset = v_services.AgreementService.filter(is_deleted=False).order_by("-created_at")
    pagination_class = None
    permission_classes = [IsVendor]


class VendorContractCreateAPIView(generics.CreateAPIView):
    serializer_class = v_serializers.VendorContractSerializer
    queryset = v_services.VendorContractService.filter(is_deleted=False)
    permission_classes = [IsVendor]


class QuestionBlockListAPIView(generics.ListAPIView):
    serializer_class = v_serializers.QuestionBlockSerializer
    queryset = v_services.QuestionBlockService.filter(is_deleted=False)
    pagination_class = None
    permission_classes = [IsVendor]


'''Profiles'''


class VendorDetailAPIView(generics.GenericAPIView):
    serializer_class = v_serializers.VendorDetailSerializer
    permission_classes = [IsVendorOwnerOrReadOnly]

    def get_object(self):
        queryset = v_services.VendorService.get_queryset(
            id=self.request.user.id,
            is_deleted=False
        )
        return generics.get_object_or_404(queryset)

    def get(self, request, *args, **kwargs):
        vendor = self.get_object()
        serializer = self.get_serializer(vendor)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        vendor = self.get_object()
        serializer = self.get_serializer(vendor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(data=serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class PhoneNumberChangeRequestCodeAPIView(views.APIView):
    serializer_class = v_serializers.PhoneChangeSerializer
    permission_classes = [IsVendor]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        v_services.VendorService.send_change_phone_code(
            vendor_id=request.user.id,
            phone_number=serializer.validated_data["phone_number"]
        )
        return Response(
            data={
                "message": "Code sended!",
                "code": "ok"
            },
            status=status.HTTP_201_CREATED
        )


class PhoneNumberChangeVerifyCodeAPIView(views.APIView):
    vendor_serializer = v_serializers.VendorDetailSerializer
    code_serializer = v_serializers.PhoneCodeSerializer
    permission_classes = [IsVendor]

    def post(self, request, *args, **kwargs):
        serializer = self.code_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vendor = v_services.VendorService.check_change_phone_code(
            vendor_id=request.user.id,
            code=serializer.validated_data["code"],
            phone_number=serializer.validated_data["phone_number"]
        )
        return Response(
            data={
                "message": "Phone successfully changed!",
                "code": "ok",
                "data": self.vendor_serializer(vendor).data
            },
            status=status.HTTP_200_OK
        )


class PhoneNumberChangeResendCodeAPIView(views.APIView):
    serializer = v_serializers.PhoneChangeSerializer
    permission_classes = [IsVendor]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        v_services.VendorService.resend_change_phone_code(
            vendor_id=request.user.id,
            phone_number=serializer.validated_data["phone_number"]
        )
        return Response(
            data={
                "message": "Code sended!",
                "code": "ok"
            },
            status=status.HTTP_201_CREATED
        )


class EmailChangeRequestCodeAPIView(views.APIView):
    permission_classes = [IsVendor]
    serializer = v_serializers.EmailChangeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        v_services.VendorService.send_change_email_code(
            vendor_id=request.user.id,
            email=serializer.validated_data["email"]
        )
        return Response(
            data={
                "message": "Code sended!",
                "code": "ok"
            },
            status=status.HTTP_201_CREATED
        )


class EmailChangeVerifyCodeAPIView(views.APIView):
    vendor_serializer = v_serializers.VendorDetailSerializer
    code_serializer = v_serializers.EmailCodeSerializer
    permission_classes = [IsVendor]

    def post(self, request, *args, **kwargs):
        serializer = self.code_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vendor = v_services.VendorService.check_change_email_code(
            vendor_id=request.user.id,
            code=serializer.validated_data["code"],
            email=serializer.validated_data["email"]
        )
        return Response(
            data={
                "message": "Email successfully changed!",
                "code": "ok",
                "data": self.vendor_serializer(vendor).data
            },
            status=status.HTTP_200_OK
        )


class EmailChangeResendCodeAPIView(views.APIView):
    serializer = v_serializers.EmailChangeSerializer
    permission_classes = [IsVendor]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        v_services.VendorService.resend_change_email_code(
            vendor_id=request.user.id,
            email=serializer.validated_data["email"]
        )
        return Response(
            data={
                "message": "Code sended!",
                "code": "ok"
            },
            status=status.HTTP_201_CREATED
        )


class PasswordChangeAPIView(views.APIView):
    permission_classes = [IsVendor]
    serializer_class = v_serializers.ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        v_services.VendorService.change_password(
            vendor=request.user,
            old_password=serializer.validated_data["old_password"],
            new_password=serializer.validated_data["new_password1"]
        )
        return Response(data={
            "message": "Password successfully changed!",
            "code": "ok"
        }, status=status.HTTP_202_ACCEPTED)

