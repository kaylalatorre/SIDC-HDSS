from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('home', views.home, name="home"),
    path('login', views.login, name="login"),
    path('logout', views.logout_view, name="logout"),
    path('error', views.error, name="error"),
]