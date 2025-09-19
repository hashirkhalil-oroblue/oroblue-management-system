from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.login_pg,name='login_pg'),
    path('logout/',views.logout_pg,name='logout_pg'),
]