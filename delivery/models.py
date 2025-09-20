from django.db import models
from decimal import Decimal
from django.db.models import F
from datetime import date


class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # Balances
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pending_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Bottles tracking
    bottles_at_site = models.IntegerField(default=0)

    # Status flags
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.phone if self.phone else 'No Phone'})"

    @property
    def net_balance(self):
        return self.balance - self.pending_balance

    def save(self, *args, **kwargs):
        """Ensure balance and pending_balance auto-adjust."""
        super().save(*args, **kwargs)  # ✅ save first (apply F() updates)

        # ✅ refresh with real values from DB (so not CombinedExpression)
        self.refresh_from_db(fields=["balance", "pending_balance"])

        # Now adjust with pure numbers
        if self.balance > 0 and self.pending_balance > 0:
            if self.balance >= self.pending_balance:
                self.balance = self.balance - self.pending_balance
                self.pending_balance = Decimal("0.00")
            else:
                self.pending_balance = self.pending_balance - self.balance
                self.balance = Decimal("0.00")

            # save again after adjustment
            super().save(update_fields=["balance", "pending_balance"])




class BottlePrice(models.Model):
    price_per_bottle = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Price: {self.price_per_bottle}"


class Delivery(models.Model):
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE)
    date = models.DateField(blank=True, null=True)

    bottles_delivered = models.IntegerField(default=0)
    bottles_returned = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        creating = self.pk is None

        # ✅ Ensure date is always set
        if not self.date:
            self.date = date.today()

        # Convert to Decimal
        self.amount_received = Decimal(self.amount_received)
        self.total_amount = Decimal(self.total_amount)

        if not creating:
            old = Delivery.objects.get(pk=self.pk)
            self.customer.bottles_at_site -= old.bottles_delivered
            self.customer.bottles_at_site += old.bottles_returned

        # Update bottle counts
        self.customer.bottles_at_site += self.bottles_delivered
        self.customer.bottles_at_site -= self.bottles_returned

        # Handle payments
        if self.amount_received >= self.total_amount:
            self.is_paid = True
            extra = self.amount_received - self.total_amount
            if extra > Decimal("0"):
                self.customer.balance = F("balance") + extra
                Transaction.objects.create(
                    customer=self.customer,
                    amount=self.amount_received,
                    transaction_type="payment",
                    description=f"Full payment received with extra {extra} added to advance",
                    date=self.date  # ✅ transaction gets same date as delivery
                )
            else:
                Transaction.objects.create(
                    customer=self.customer,
                    amount=self.amount_received,
                    transaction_type="payment",
                    description="Full delivery payment",
                    date=self.date  # ✅ match delivery date
                )
        else:
            self.is_paid = False
            pending = self.total_amount - self.amount_received
            self.customer.pending_balance = F("pending_balance") + pending
            Transaction.objects.create(
                customer=self.customer,
                amount=self.amount_received,
                transaction_type="partial",
                description=f"Partial payment, pending {pending}",
                date=self.date  # ✅ match delivery date
            )

        self.customer.save()
        super().save(*args, **kwargs)




class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("advance", "Advance"),
        ("payment", "Payment"),
        ("pending", "Pending"),
        ("partial", "Partial"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    # ✅ allow manual setting, default is now.today if not given
    date = models.DateField(blank=True, null=True)  
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES, default="payment")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.customer.name} - {self.transaction_type} ({self.amount}) on {self.date.strftime('%Y-%m-%d')}"
