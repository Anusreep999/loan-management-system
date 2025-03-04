from django.shortcuts import render
import random
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import CustomUser, OTP
from .serializers import UserSerializer, LoanSerializer ,OTPSerializer
from django.core.mail import send_mail
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import serializers, viewsets, status
from apploan.models import Loan 
from django.shortcuts import get_object_or_404
from decimal import Decimal
from rest_framework import viewsets, permissions


ACCESS_TOKEN_SECRET = 'access_secret_key'
REFRESH_TOKEN_SECRET = 'refresh_secret_key'

class IsAdmin(permissions.BasePermission):
    """Custom permission to allow only admins to access certain actions."""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff  # Only admins


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate OTP
            otp_code = str(random.randint(100000, 999999))
            OTP.objects.create(user=user, otp=otp_code)

            # Debugging: Print OTP and user email
            print(f"Generated OTP: {otp_code} for {user.email}")

            # Send OTP via NodeMailer
            email_data = {"email": user.email, "otp": otp_code}

            try:
                response = requests.post("http://127.0.0.1:5001/send-otp", json=email_data)
                
                # Debugging: Print Node.js response
                print(f"Node.js response: {response.status_code} - {response.text}")
                
                response.raise_for_status()  # Raise an error for failed requests
            except requests.exceptions.RequestException as e:
                print(f"Error sending OTP: {e}")
                return Response(
                    {"message": "User registered, but OTP could not be sent.", "error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({"message": "OTP sent to email."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    def post(self, request):
        serializer = OTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        otp_code = serializer.validated_data["otp"]
        user = serializer.validated_data["user"]

        # Fetch latest OTP for the user
        otp = OTP.objects.filter(user=user).order_by('-created_at').first()
        if not otp:
            return Response({"error": "No OTP found. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate OTP
        if otp.otp != otp_code:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # Mark user as verified
        user.is_verified = True
        user.save()
        otp.delete()  # Delete OTP after successful verification

        return Response({"message": "Account verified successfully."}, status=status.HTTP_200_OK)


class Loginview(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data['refresh']
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True, secure=True)
        response.data['message'] = 'Login successful!'
        return response


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    lookup_field = 'loan_id'

    def get_permissions(self):
        """Grant different permissions based on the action"""
        if self.action in ['list', 'retrieve']:  # Allow all users to view
            return [permissions.IsAuthenticated()]
        elif self.action == 'destroy':  # Only admins can delete
            return [IsAdmin()]
        return super().get_permissions()


class LoanForeclosureView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # Ensure only authenticated users can foreclose

    def post(self, request, loan_id):
        loan = get_object_or_404(Loan, loan_id=loan_id)

        # Ensure loan is active before foreclosure
        if loan.status != "ACTIVE":
            return Response({"status": "error", "message": "Loan is already closed."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure loan details are complete
        if loan.total_amount is None or loan.total_interest is None:
            return Response({"status": "error", "message": "Loan details are incomplete."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate foreclosure discount
        foreclosure_discount = loan.total_amount * Decimal("0.05")  # 5% discount
        final_settlement_amount = loan.total_amount - foreclosure_discount

        # Update loan status
        loan.status = "CLOSED"
        loan.save()

        # Response data
        response_data = {
            "status": "success",
            "message": "Loan foreclosed successfully.",
            "data": {
                "loan_id": loan.loan_id,
                "amount_paid": loan.total_amount,
                "foreclosure_discount": round(foreclosure_discount, 2),
                "final_settlement_amount": round(final_settlement_amount, 2),
                "status": loan.status
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)