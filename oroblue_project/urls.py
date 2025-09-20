from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('delivery.urls')),
    path('', include('auth_user.urls'))
]
