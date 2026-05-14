from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>АИС Общепит</h1><p>Сервер работает!</p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
]
