import requests
from datetime import datetime
from django.conf import settings
from app.models import PaymentRecord


def create_payment_link(user, amount):
    hotel = getattr(user, 'staffof', None)
    if not hotel:
        raise ValueError("User is not linked to a hotel.")

    order_id = f"hotel_{hotel.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    phone = str(getattr(user, 'phone', '') or '9999999999')
    customer_name = (user.first_name + " " + user.last_name).strip() or user.username

    url = "https://sandbox.cashfree.com/pg/links"
    headers = {
        "x-client-id": settings.CASHFREE_CLIENT_ID,
        "x-client-secret": settings.CASHFREE_CLIENT_SECRET,
        "x-api-version": "2025-01-01",
        "Content-Type": "application/json",
    }
    
    data = {
        "link_id": order_id,
        "link_amount": amount,
        "link_currency": "INR",
        "link_purpose": "Subscription Payment",
        "customer_details": {
            "customer_name": customer_name,
            "customer_email": user.email or f"{user.username}@example.com",
            "customer_phone": phone,
        },
        "link_notify": {
            "send_email": True,
            "send_sms": True,
        },
        "link_meta": {
            "return_url": "https://hotelsoftware.pythonanywhere.com/owner/",
            "notify_url": "https://hotelsoftware.pythonanywhere.com/owner/cashfree_webhook",
        },
    }
    response = requests.post(url, headers=headers, json=data, verify=False).json()

    # Save PaymentRecord
    PaymentRecord.objects.create(
        user=user,
        hotel=hotel,
        order_id=order_id,
        amount=amount,
        status="PENDING"
    )

    return response
