from django.urls import path
from . import views

app_name = 'backup'

urlpatterns = [
    # Страница со списком бэкапов и формой создания нового
    path('', views.admin_backup, name='index'),
    # Скачивание файла бэкапа
    path('download/<str:filename>/', views.admin_backup_download, name='download'),
    # Восстановление базы данных из бэкапа
    path('restore/<str:filename>/', views.admin_backup_restore, name='restore'),
    # Удаление файла бэкапа
    path('delete/<str:filename>/', views.admin_backup_delete, name='delete'),
]
