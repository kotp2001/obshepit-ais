from django.urls import path
from . import views

app_name = 'backup'

urlpatterns = [
    path('', views.admin_backup, name='index'),
    path('download/<str:filename>/', views.admin_backup_download, name='download'),
    path('restore/<str:filename>/', views.admin_backup_restore, name='restore'),
    path('delete/<str:filename>/', views.admin_backup_delete, name='delete'),
]
