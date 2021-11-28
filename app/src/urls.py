from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('login.urls')),
    # path('sendmail/', include('sendmail.urls')),
    path('', include('farmsapp.urls')),
    path('', include('healthapp.urls')),
    # path('', include('dssapp.urls')),
]
