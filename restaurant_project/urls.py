from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>АИС Общепит</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
            h1 { font-size: 48px; }
            .container { background: rgba(255,255,255,0.1); padding: 30px; border-radius: 20px; display: inline-block; }
            .status { color: #4CAF50; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>АИС Общепит</h1>
            <p>Система автоматизации для ресторана</p>
            <p class="status">Сервер работает успешно</p>
            <p>База данных подключена</p>
            <hr>
            <p><a href="/admin">Админ-панель</a></p>
        </div>
    </body>
    </html>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
]
