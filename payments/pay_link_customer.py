import requests
from datetime import datetime
from django.conf import settings

def create_payment_link(amount=100):
    url = "https://sandbox.cashfree.com/pg/links"

    headers = {
        "x-client-id": settings.CASHFREE_CLIENT_ID,
        "x-client-secret": settings.CASHFREE_CLIENT_SECRET,
        "x-api-version": "2025-01-01",  # from docs you pasted
        "Content-Type": "application/json",
    }

    data = {
        "link_id": f"sub_1011_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "link_amount": amount,
        "link_currency": "INR",
        "link_purpose": "Subscription Payment",
        "customer_details": {
            "customer_name":"Test User",
            "customer_email": "saadiqbal1921@gmail.com",
            "customer_phone": "8799878583",  # ideally from user profile
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
    return response
