from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

def create_notification(recipient, verb, actor=None, target=None, notification_type='info'):
    notif = Notification.objects.create(
        recipient=recipient,
        verb=verb,
        actor=actor,
        target=target,
        notification_type=notification_type
    )

    # Enviar via WebSocket
    channel_layer = get_channel_layer()
    group_name = f"user_{recipient.id}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_notification",
            "id": notif.id,
            "verb": notif.verb,
            "actor": getattr(notif.actor, 'get_full_name', lambda: "Sistema")(),
            "timestamp": notif.timestamp.isoformat(),
            "read": notif.read,
            "notification_type": notif.notification_type,
        }
    )
    return notif