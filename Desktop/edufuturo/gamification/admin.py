from django.contrib import admin
from .models import Badge, Achievement, UserXP

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'xp_value', 'icon')
    search_fields = ('name',)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at', 'course')
    list_filter = ('earned_at', 'badge')
    search_fields = ('user__username', 'badge__name')

@admin.register(UserXP)
class UserXPAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_xp', 'level')
    readonly_fields = ('level',)