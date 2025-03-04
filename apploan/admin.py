from django.contrib import admin
from .models import CustomUser, Loan, OTP, PaymentSchedule

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_verified')
    search_fields = ('username', 'email')

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'amount', 'tenure', 'interest_rate', 
                    'monthly_installment', 'total_amount', 'status', 'created_at')
    
    search_fields = ('loan_id', 'borrower__username', 'borrower__email', 'amount')
    list_filter = ('status', 'created_at')

    def get_borrower(self, obj):
        """Return the borrower's username or email"""
        return obj.borrower.username if obj.borrower else "No Borrower"

    get_borrower.short_description = "Borrower"
    get_borrower.admin_order_field = "borrower__username"

    def get_queryset(self, request):
        """Superusers see all loans, regular users see only their loans."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Show all loans
        return qs.filter(borrower=request.user)

    
@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ('loan', 'get_loan_id', 'installment_no', 'due_date', 'amount')
    search_fields = ('loan__loan_id',)

    def get_loan_id(self, obj):
        """Retrieve the loan ID from the related Loan model."""
        return obj.loan.loan_id if obj.loan else "No Loan"

    get_loan_id.short_description = "Loan ID"  # Set column name in admin
    get_loan_id.admin_order_field = "loan__loan_id"  # Enable sorting by loan_id

