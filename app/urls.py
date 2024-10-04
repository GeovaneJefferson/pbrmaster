# app/urls.py
from django.urls import path
from . import views  # This imports all views from the current app

urlpatterns = [
    path('generate-textures', views.generate_textures, name='generate_textures'),  # Define the URL for the texture generation

]
