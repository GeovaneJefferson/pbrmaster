from django.urls import path
from app import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='home'),  # This should render your index.html
    path('generate-maps/', views.generate_maps, name='generate_maps'),
    path('export-textures/', views.export_textures, name='export_textures'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)