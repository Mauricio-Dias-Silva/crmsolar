# notifications/admin.py
from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'verb', 'notification_type', 'timestamp', 'read', 'target')
    list_filter = ('read', 'notification_type', 'timestamp') # Estes filtros agora serão válidos
    search_fields = ('recipient__username', 'message', 'verb')
    raw_id_fields = ('recipient',)