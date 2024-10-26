# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('<int:chatid>/', views.chat.as_view(), name='chat'),
    path('<int:chat_id>/response/', views.get_response, name='get_response'),
    path('new/', views.create_chat.as_view(), name='create_chat'),
    path('', views.index, name='chat_page')
]