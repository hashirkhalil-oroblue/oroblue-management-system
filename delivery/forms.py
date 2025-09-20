from django import forms
from .models import Customer, Delivery, Transaction, BottlePrice


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["name", "phone", "address", "bottles_at_site", "is_active"]


class DeliveryForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        widget=forms.Select(attrs={"class": "form-control searchable-select"})
    )

    date = forms.DateField(
        required=False,  # user can leave it empty -> auto-fills with today
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date"  # HTML5 date picker
            }
        )
    )

    class Meta:
        model = Delivery
        fields = [
            "customer",
            "bottles_delivered",
            "bottles_returned",
            "amount_received",
            "date",
        ]


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["customer", "amount", "transaction_type", "description"]


class BottlePriceForm(forms.ModelForm):
    class Meta:
        model = BottlePrice
        fields = ["price_per_bottle"]


class CustomerBalanceForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["balance", "pending_balance"]


class BottleUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["bottles_at_site"]
