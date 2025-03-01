from twilio.rest import Client
import os


AUTH_TOKEN= os.getenv('TWILIO_AUTH_TOKEN')
ACCOUNT_SID= os.getenv('TWILIO_ACCOUNT_SID')


client = Client(ACCOUNT_SID, AUTH_TOKEN)


# llamada = client.calls.create(
#     to="+573216790777",
#     from_="+17603321951",
#     url="http://demo.twilio.com/docs/voice.xml"
# )


llamada = client.calls.create(
    to="+573216790777",
    from_="+15076688527",
    url="http://demo.twilio.com/docs/voice.xml"
)


print(f"Llamada iniciada con SID: {llamada.sid}")

