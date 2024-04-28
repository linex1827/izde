from django.urls import path
from apps.vendors import views

urlpatterns = [
    path('register/', views.RegisterVendorAPIView.as_view()),
    path('login/', views.LoginVendorAPIView.as_view()),
    path('twofa_login/', views.TwoFactorLoginAPIView.as_view()),
    path('verify/', views.VerifyVendorAPIView.as_view()),
    path('send_reset_code/', views.SendVendorResetCode.as_view()),
    path('send_new_reset_code/', views.SendVendorNewResetCodeAPIView.as_view()),
    path('check_reset_code/', views.CheckVendorResetCodeAPIView.as_view()),
    path('change_password/', views.ChangeVendorPasswordAPIView.as_view()),
    path('twofa/', views.TwoFactorSetupAPIView.as_view()),
    path('twofa/verify', views.TwoFactorVerifyAPIView.as_view()),
    path('orders/', views.OrderListAPIView.as_view()),
    path('approved_orders/', views.ApprovedOrderListAPIView.as_view()),
    path('current_occupancies/', views.CurrentOccupancyAPIView.as_view()),
    path('detail_current_occupancy/<uuid:order_id>/', views.DetailCurrentOccupancy.as_view()),


    path('vendor_contract/', views.VendorContractCreateAPIView.as_view(), name="create-contract"),
    path('agreements/', views.AgreementListAPIView.as_view(), name="agreement-list"),
    path('profile/', views.VendorDetailAPIView.as_view(), name="vendor-detail"),
    path('question_block/', views.QuestionBlockListAPIView.as_view(), name="question-block"),

    path(
        'phone_number/change/request_code/',
        views.PhoneNumberChangeRequestCodeAPIView.as_view(),
        name="request_code_change_phone"
    ),
    path(
        'phone_number/change/verify_code/',
        views.PhoneNumberChangeVerifyCodeAPIView.as_view(),
        name="verify_code_change_phone"
    ),
    path(
        'phone_number/change/resend_code/',
        views.PhoneNumberChangeResendCodeAPIView.as_view(),
        name="resend_code_change_phone"
    ),

    path(
        'email/change/request_code/',
        views.EmailChangeRequestCodeAPIView.as_view(),
        name="request_code_change_email"
    ),
    path(
        'email/change/verify_code/',
        views.EmailChangeVerifyCodeAPIView.as_view(),
        name="verify_code_change_email"
    ),
    path(
        'email/change/resend_code/',
        views.EmailChangeResendCodeAPIView.as_view(),
        name="resend_code_change_email"
    ),
    path(
        'password/change/',
        views.PasswordChangeAPIView.as_view(),
        name="password_change"
    )

]
