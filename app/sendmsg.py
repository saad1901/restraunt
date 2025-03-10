from twilio.rest import Client

def sendbill(amount, orderid):
    pass
    # account_sid = 'ACdf184ee0812e7da7e72f40de2507df07'
    # auth_token = 'ce7c34823660d063c5a8375a929f6049'
    # client = Client(account_sid, auth_token)

    # # Custom message
    # custom_message = f"Your order with order id {orderid} has been placed successfully. Your bill amount is {amount}"
    # # custom_message = f"{amount} is your bill amount. Please pay it as soon as possible."

    # # Sending WhatsApp message
    # message = client.messages.create(
    #   from_='whatsapp:+14155238886',  # Twilio Sandbox/Business Number
    #   body=custom_message,  # Custom text message
    #   to='whatsapp:+918799878583'  # Recipient's WhatsApp number
    # )