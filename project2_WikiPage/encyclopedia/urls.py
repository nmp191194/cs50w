from django.urls import path

from . import views

app_name = 'encyclopedia'
urlpatterns = [
    path("", views.index, name="index"),
    path("entry/<str:title>", views.entry_page, name="entry_page"),
    path("add_entry", views.add, name="add_entry"),
    path("edit_entry/<str:title>", views.edit, name="edit_entry"),
    path("random", views.random, name="random")
]
