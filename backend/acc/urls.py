from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("auth/login", views.auth_login, name="auth_login"),
    path("auth/callback", views.auth_callback, name="auth_callback"),
    path("auth/logout", views.auth_logout, name="auth_logout"),
    path("auth/me", views.me, name="me"),

    # ACC browsing
    path("hubs", views.list_hubs, name="list_hubs"),
    path("projects/<str:hub_id>", views.list_projects, name="list_projects"),
    path("top-folders/<str:project_id>", views.list_top_folders, name="list_top_folders"),
    path("folders/<str:project_id>/<path:folder_id>", views.list_folder_contents, name="list_folder_contents"),

    # Permissions
    path("permissions/<str:project_id>/<path:folder_id>", views.folder_permissions, name="folder_permissions"),
]
