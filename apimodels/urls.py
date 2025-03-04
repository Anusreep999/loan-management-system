from django.urls import path
from apploan.views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('login/', Loginview.as_view(), name='login'),
    path('loans/', LoanViewSet.as_view({'get': 'list', 'post': 'create'}), name='loan_list_create'),
    path('loans/<str:loan_id>/', LoanViewSet.as_view({'get': 'retrieve'}), name='loan_detail'),
    path('loans/<str:loan_id>/foreclose/', LoanForeclosureView.as_view(), name='loan_foreclosure'),
]
