from django.urls import path
from . import views

app_name = "skillzone"

urlpatterns = [
    path("", views.home, name="home"),
    path("profile/", views.my_profile, name="profile"),
    path("skills/add/", views.add_skill, name="add_skill"),

    # Barter flows
    path("barters/", views.my_barters, name="my_barters"),
    path(
        "barters/request/<int:skill_id>/<int:user_to_id>/",
        views.send_barter_request,
        name="send_barter_request",
    ),

    # ⚠ FEEDBACK ROUTE MUST BE ABOVE STATUS ROUTE
    path(
        "barters/<int:barter_id>/feedback/",
        views.give_feedback,
        name="give_feedback",
    ),

    path(
        "barters/<int:barter_id>/<str:new_status>/",
        views.update_barter_status,
        name="update_barter_status",
    ),

    path("barters/completed/", views.completed_barters, name="completed_barters"),

    # User directory
    path("users/", views.user_list, name="user_list"),
    path("users/<int:user_id>/", views.user_detail, name="user_detail"),

    # Messaging
    path("inbox/", views.inbox, name="inbox"),
    path("messages/<int:user_id>/", views.conversation, name="conversation"),
]
