import requests
from datetime import datetime
from django.conf import settings
from app.models import PaymentRecord

def create_payment_link(user, amount=499):
    url = "https://sandbox.cashfree.com/pg/links"

    headers = {
        "x-client-id": settings.CASHFREE_CLIENT_ID,
        "x-client-secret": settings.CASHFREE_CLIENT_SECRET,
        "x-api-version": "2025-01-01",
        "Content-Type": "application/json",
    }

    # unique order id linked to your user/hotel
    order_id = f"hotel_{user.hotel.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    data = {
        "link_id": order_id,
        "link_amount": amount,
        "link_currency": "INR",
        "link_purpose": "Subscription Payment",
        "customer_details": {
            "customer_name": user.get_full_name(),
            "customer_email": user.email,
            "customer_phone": user.profile.phone,  # assuming you store phone
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

    response = requests.post(url, headers=headers, json=data).json()

    PaymentRecord.objects.create(
        user=user,
        hotel=user.hotel,
        order_id=order_id,
        amount=amount,
        status="PENDING"
    )

    return response
