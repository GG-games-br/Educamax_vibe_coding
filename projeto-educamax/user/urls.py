from . import views
from django.contrib import admin
from django.urls import path, include


"""app_name = 'user'"""

urlpatterns = [ 
    path('', views.login),
    path('login', views.login),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls'))
]
