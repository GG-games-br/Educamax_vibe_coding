from django.contrib.auth.views import LoginView, LogoutView
from .forms import EmailAuthenticationForm
from django.urls import path, include
from . import views


"""app_name = 'user'"""

urlpatterns = [ 
    path('login/', LoginView.as_view(
        template_name='user/login.html',
        authentication_form=EmailAuthenticationForm
    ), name='login'),

    path('logout/', LogoutView.as_view(), name='logout'),

    path('redirect/', views.login_redirect_view, name='login_redirect')
]
