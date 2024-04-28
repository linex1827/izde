from django.urls import path
from apps.profiles.views import user as views
from apps.profiles.views import payment


urlpatterns = [
    path('user_profile/', views.ProfileUserAPIView.as_view()),
    path('change_profile_password/', views.ChangeUserPasswordAPIView.as_view()),
    path('update_user_profile/', views.UpdateUserProfileAPIView.as_view()),
    path('register/', views.RegisterUserAPIView.as_view()),
    path('verify/', views.VerifyUserAPIView.as_view()),
    path('login/', views.LoginUserAPIView.as_view()),
    path('send_reset_code/', views.SendResetCodeAPIView.as_view()),
    path('check_reset_code/', views.CheckResetCodeAPIView.as_view()),
    path('change_user_password/', views.ChangePasswordAPIView.as_view()),

    path('send_new_reset_code/', views.SendUserNewResetCodeAPIView.as_view()),
    path('send_new_register_code/', views.SendNewRegisterCodeAPIView.as_view()),

    path('cancel_search/', views.CancelSearchAPIView.as_view()),
    path('cancel_offer/', views.CancelOfferAPIView.as_view()),
    path('accept_offer/<uuid:offer_id>/', views.AcceptOfferAPIView.as_view()),

    path('currencies/', views.CurrencyListAPIView.as_view()),

    path('google_oauth/', views.GoogleOAuthAPIView.as_view()),
    path('apple_auth/', views.AppleOAuthAPIView.as_view()),
    path('refresh/', views.CustomTokenRefreshView.as_view()),
    path('verify/', views.CustomTokenVerifyView.as_view()),
]