import uuid
from rest_framework import serializers
from .models import CustomUser, OTP
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework import serializers, viewsets, status
import math
from apploan.models import PaymentSchedule, Loan

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, help_text="Enter your registered email")
    otp = serializers.CharField(write_only=True, help_text="Enter the OTP received")

    def validate(self, data):
        """
        Validate email existence and map it to the user.
        """
        email = data.get('email')
        user = CustomUser.objects.filter(email__iexact=email).first()
        
        if not user:
            raise serializers.ValidationError({"email": "User with this email does not exist."})

        data['user'] = user  
        return data

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = CustomUser.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError({"email": "User not found."})
        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Invalid credentials."})
        
        data['user'] = user
        return data  

class PaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSchedule
        fields = ['installment_no', 'due_date', 'amount']

class LoanSerializer(serializers.ModelSerializer):
    payment_schedule = PaymentScheduleSerializer(many=True, read_only=True)
    interest_rate_display = serializers.SerializerMethodField()  # Custom formatted field

    class Meta:
        model = Loan
        fields = ['loan_id', 'amount', 'tenure', 'interest_rate', 'interest_rate_display', 'monthly_installment', 'total_interest', 'total_amount', 'payment_schedule']
    
    def get_interest_rate_display(self, obj):
        """Formats interest rate as '10% yearly'."""
        return f"{obj.interest_rate}% yearly"
    
    def to_representation(self, instance):
        """Removes 'interest_rate' from the API response but keeps it for input."""
        data = super().to_representation(instance)
        data.pop('interest_rate', None)  
        return data

    def validate(self, data):
        if 'amount' not in data:
            raise serializers.ValidationError({"amount": "This field is required."})
        if 'tenure' not in data:
            raise serializers.ValidationError({"tenure": "This field is required."})
        if 'interest_rate' not in data:
            raise serializers.ValidationError({"interest_rate": "This field is required."})

        if data['amount'] < 1000 or data['amount'] > 100000:
            raise serializers.ValidationError({"amount": "Amount must be between ₹1,000 and ₹100,000"})
        if data['tenure'] < 3 or data['tenure'] > 24:
            raise serializers.ValidationError({"tenure": "Tenure must be between 3 and 24 months"})
        return data

    def create(self, validated_data):
        amount = validated_data['amount']
        tenure = validated_data['tenure']
        interest_rate = validated_data['interest_rate']

        monthly_rate = (interest_rate / 100) / 12
        total_interest = amount * ((1 + monthly_rate) ** tenure - 1)
        total_amount = amount + total_interest
        monthly_installment = total_amount / tenure

        loan = Loan.objects.create(
            amount=amount,
            tenure=tenure,
            interest_rate=interest_rate,
            monthly_installment=round(monthly_installment, 2),
            total_interest=round(total_interest, 2),
            total_amount=round(total_amount, 2)
        )

        for i in range(1, tenure + 1):
            PaymentSchedule.objects.create(
                loan=loan,
                installment_no=i,
                due_date=timezone.now().date().replace(day=24) + timezone.timedelta(days=(i - 1) * 30),
                amount=round(monthly_installment, 2)
            )

        return loan