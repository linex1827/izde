import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("apps/notification/serviceAccountKey.json")
firebase_admin.initialize_app(cred)


def push_notifications(title, message, tokens):
    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=message),
        data=None,
        tokens=tokens
    )
    response = messaging.send_multicast(message)
    return response
