from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('words/', include('words.urls')),
    path('admin/', admin.site.urls),
]
