from django.urls import path

from . import views

urlpatterns = [
    path('word_counter', views.word_counter, name="word_counter"),
    path('word_statistics', views.word_statistics, name="word_statistics"),
    path('test.txt', views.test_txt, name="test_txt"),
]