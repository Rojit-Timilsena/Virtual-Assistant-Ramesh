from django.contrib import admin
from django.urls import path, include  # 👈 include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('assistant.urls')),  # 👈 route to assistant app
]
