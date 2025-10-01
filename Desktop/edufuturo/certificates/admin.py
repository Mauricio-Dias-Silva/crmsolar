from django.contrib import admin
from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'issue_date', 'certificate_id', 'is_valid')
    list_filter = ('issue_date', 'is_valid', 'course')
    search_fields = ('student__user__username', 'course__name', 'certificate_id')
    readonly_fields = ('issue_date', 'certificate_id', 'verification_hash')