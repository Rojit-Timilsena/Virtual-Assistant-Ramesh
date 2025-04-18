from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('debug/', views.debug_view, name='debug'),
    path('jarvis/', views.jarvis_api, name='jarvis_api'),
    path('test_gemini/', views.test_gemini, name='test_gemini'),
]
