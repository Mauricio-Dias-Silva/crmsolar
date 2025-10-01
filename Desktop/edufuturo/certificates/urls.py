from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('emitir/<int:course_id>/', views.issue_certificate, name='issue'),
    path('baixar/<uuid:verification_hash>/', views.download_certificate, name='download'),
    path('verificar/<uuid:verification_hash>/', views.verify_certificate, name='verify'),
]