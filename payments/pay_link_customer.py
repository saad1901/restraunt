import requests
from datetime import datetime
from django.conf import settings
from app.models import PaymentRecord

def create_payment_link(user, amount):
    hotel = getattr(user, 'staffof', None)
    if not hotel:
        raise ValueError("User is not linked to a hotel.")

    order_id = f"hotel_{hotel.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    phone = str(getattr(user, 'phone', '') or '8799878583')
    customer_name = (user.first_name + " " + user.last_name).strip() or user.username

    url = settings.CASHFREE_BASE_URL
    headers = {
        "x-client-id": settings.CASHFREE_CLIENT_ID,
        "x-client-secret": settings.CASHFREE_CLIENT_SECRET,
        "x-api-version": "2022-09-01",
        "Content-Type": "application/json",
    }

    data = {
        "link_id": order_id,
        "link_amount": float(amount),
        "link_currency": "INR",
        "link_purpose": "Subscription Payment",
        "link_partial_payments": False,
        "link_auto_reminders": True,
        "customer_details": {
            "customer_name": customer_name,
            "customer_email": user.email or f"{user.username}@NEtastybits.com",
            "customer_phone": phone,
        },
        "link_notify": {
            "send_email": True,
            "send_sms": True,
        },
        "link_meta": {
            "return_url": settings.CASHFREE_RETURN_URL,
            "notify_url": settings.CASHFREE_NOTIFY_URL,
        },
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        # print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        res_json = response.json()
        print('test1')
    except Exception as e:
        print('test2')
        res_json = {"status": "failed", "reason": str(e)}

    payment_link = res_json.get("link_url")
    PaymentRecord.objects.create(
        user=user,
        hotel=hotel,
        order_id=order_id,
        amount=amount,
        status="PENDING",
        payment_link=payment_link
    )
    return 

