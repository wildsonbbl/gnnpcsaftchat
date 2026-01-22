"Module for url config."

from django.urls import path, re_path

from . import views

urlpatterns = [
    path("about/", views.about, name="about"),
    path("", views.chat, name="chat"),
    path("api/sessions/", views.get_sessions, name="get_sessions"),
    path("api/sessions/create/", views.create_session, name="create_session"),
    path(
        "api/sessions/<uuid:session_id>/delete/",
        views.delete_session,
        name="delete_session",
    ),
    re_path(r"^serviceworker\.js$", views.service_worker, name="serviceworker"),
]
