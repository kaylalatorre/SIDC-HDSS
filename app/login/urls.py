from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name="home"),
    path('home', views.home_view, name="home"),

    path('login', views.login, name="login"),
    path('login', views.check_group, name="check_group"),

    path('logout', views.logout_view, name="logout"),
    path('error', views.error, name="error"),
]