from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum , Q
from .models import Customer, Delivery, Transaction, BottlePrice
from .forms import CustomerForm, BottleUpdateForm, DeliveryForm, TransactionForm, BottlePriceForm, CustomerBalanceForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
def dashboard(request):
    total_customers = Customer.objects.count()
    total_bottles = Customer.objects.aggregate(total=Sum("bottles_at_site"))["total"] or 0

    today = timezone.localdate()  # ✅ local timezone aware
    first_day_month = today.replace(day=1)

    # Daily total
    daily_total = Transaction.objects.filter(date__date=today).aggregate(total=Sum("amount"))["total"] or 0

    # Monthly total
    monthly_total = Transaction.objects.filter(date__date__gte=first_day_month).aggregate(total=Sum("amount"))["total"] or 0

    context = {
        "total_customers": total_customers,
        "total_bottles": total_bottles,
        "daily_total": daily_total,
        "monthly_total": monthly_total,
    }
    return render(request, "delivery/dashboard.html", context)



# Customer Management
@login_required
def customer_list(request):
    query = request.GET.get("q", "")
    customers = Customer.objects.all()

    if query:
        customers = customers.filter(
            Q(name__icontains=query) | Q(phone__icontains=query)
        )

    return render(request, "delivery/customers.html", {
        "customers": customers,
        "query": query,
    })

@login_required
def customer_add(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm()
    return render(request, "delivery/customer_add.html", {"form": form})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    deliveries = Delivery.objects.filter(customer=customer)
    transactions = Transaction.objects.filter(customer=customer)

    # Handle bottle update directly on detail page
    if request.method == "POST":
        form = BottleUpdateForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Bottles at site updated successfully.")
            return redirect("customer_detail", pk=pk)
    else:
        form = BottleUpdateForm(instance=customer)

    return render(request, "delivery/customer_detail.html", {
        "customer": customer,
        "deliveries": deliveries,
        "transactions": transactions,
        "form": form,
    })

@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect("customer_detail", pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, "delivery/customer_form.html", {"form": form})

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.delete()
        return redirect("customer_list")
    return render(request, "delivery/customer_confirm_delete.html", {"customer": customer})

@login_required
def customer_balance_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerBalanceForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect("customer_detail", pk=customer.pk)
    else:
        form = CustomerBalanceForm(instance=customer)

    return render(request, "delivery/customer_balance_edit.html", {
        "form": form,
        "customer": customer,
    })


# Delivery Management

@login_required
def delivery_list(request):
    deliveries = Delivery.objects.all()
    return render(request, "delivery/deliveries.html", {"deliveries": deliveries})

@login_required
def delivery_add(request):
    if request.method == "POST":
        form = DeliveryForm(request.POST)
        if form.is_valid():
            delivery = form.save(commit=False)
            try:
                bottle_price = BottlePrice.objects.last().price_per_bottle
            except AttributeError:
                bottle_price = 0
            delivery.total_amount = delivery.bottles_delivered * bottle_price
            delivery.save()
            return redirect("delivery_list")
    else:
        form = DeliveryForm()
    return render(request, "delivery/delivery_add.html", {"form": form})


# Transaction Management

@login_required
def transaction_list(request):
    transactions = Transaction.objects.all()
    return render(request, "delivery/transactions.html", {"transactions": transactions})

@login_required
def transaction_add(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("transaction_list")
    else:
        form = TransactionForm()
    return render(request, "delivery/transaction_add.html", {"form": form})


# Bottle Price

@login_required
def bottle_price(request):
    if request.method == "POST":
        form = BottlePriceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("bottle_price")
    else:
        form = BottlePriceForm()
    prices = BottlePrice.objects.all().order_by("-updated_at")
    return render(request, "delivery/bottle_price.html", {"form": form, "prices": prices})
