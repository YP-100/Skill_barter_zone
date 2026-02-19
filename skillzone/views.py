from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from .models import Barter, Feedback

from .models import Skill, Barter, Feedback, Message
from users.models import ProfileModel


def home(request):
    """
    Dashboard listing skills with simple search.

    - If the user is logged in, show their own skills separately from
      skills offered by other users.
    - Anonymous users see the combined list of all skills.
    - Supports search on skill name, description and user name.
    """
    query = request.GET.get("q", "").strip()

    all_skills = Skill.objects.select_related("user")

    if query:
        all_skills = all_skills.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(user__username__icontains=query)
            | Q(user__profilemodel__full_name__icontains=query)
        )

    my_skills = None
    other_skills = None

    if request.user.is_authenticated:
        my_skills = all_skills.filter(user=request.user)
        other_skills = all_skills.exclude(user=request.user)
    else:
        other_skills = all_skills

    context = {
        "skills": other_skills,   # skills from other users / all skills
        "my_skills": my_skills,   # skills belonging to the logged-in user
        "query": query,
    }
    return render(request, "skillzone/home.html", context)


@login_required
def my_profile(request):
    """
    Simple profile page for the currently logged-in user.
    Shows profile info, skills and quick stats.
    """
    profile = getattr(request.user, "profilemodel", None)
    my_skills = Skill.objects.filter(user=request.user)
    # my_barters = Barter.objects.filter(
    #     Q(user_from=request.user) | Q(user_to=request.user)
    # ).order_by("-date_requested")
    my_barters = Barter.objects.filter(
    Q(user_from=request.user) |
    Q(
        user_to=request.user,
        status__in=[
            Barter.STATUS_ADMIN_APPROVED,
            Barter.STATUS_ACCEPTED,
            Barter.STATUS_REJECTED,
            Barter.STATUS_COMPLETED,
        ],
    )
).order_by("-date_requested")


    avg_rating = Feedback.objects.filter(
        barter__user_to=request.user
    ).aggregate(avg=Avg("rating"))["avg"]

    context = {
        "profile": profile,
        "my_skills": my_skills,
        "my_barters": my_barters,
        "avg_rating": avg_rating,
    }
    return render(request, "skillzone/profile.html", context)


@login_required
def add_skill(request):
    """
    Allow the user to add a new skill they can offer.
    """
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        if not name:
            messages.error(request, "Skill name is required.")
        else:
            Skill.objects.create(
                user=request.user,
                name=name,
                description=description,
            )
            messages.success(request, "Skill added successfully.")
            return redirect("skillzone:home")
    return render(request, "skillzone/add_skill.html")


@login_required
def send_barter_request(request, skill_id, user_to_id):
    """
    Create a barter request with:
    - A dropdown to choose WHICH skill of the other user you want to learn
    - A dropdown to choose WHICH of your own skills you want to offer
    """

    user_to = get_object_or_404(User, id=user_to_id)

    if user_to == request.user:
        messages.error(request, "You cannot create a barter with yourself.")
        return redirect("skillzone:home")

    # All skills of the user receiving the request
    user_to_skills = Skill.objects.filter(user=user_to)

    # The logged-in user's skills
    my_skills = Skill.objects.filter(user=request.user)

    if not my_skills.exists():
        messages.error(
            request,
            "You must add at least one skill before you can request a barter.",
        )
        return redirect("skillzone:add_skill")

    if request.method == "POST":
        try:
            skill_to_id = int(request.POST.get("skill_to"))
            skill_from_id = int(request.POST.get("skill_from"))

            skill_to = user_to_skills.get(id=skill_to_id)
            skill_from = my_skills.get(id=skill_from_id)

        except (Skill.DoesNotExist, ValueError, TypeError):
            messages.error(request, "Please choose valid skills from dropdowns.")
            return redirect("skillzone:send_barter_request", skill_id=skill_id, user_to_id=user_to_id)

        barter = Barter.objects.create(
            skill_from=skill_from,
            skill_to=skill_to,
            user_from=request.user,
            user_to=user_to,
        )

        messages.success(request, f"Barter request #{barter.id} sent successfully.")
        return redirect("skillzone:my_barters")

    # skill_id can be preselected, but now user chooses from dropdown
    preselected_skill = Skill.objects.filter(id=skill_id).first()

    return render(
        request,
        "skillzone/send_barter_request.html",
        {
            "user_to": user_to,
            "user_to_skills": user_to_skills,
            "my_skills": my_skills,
            "preselected_skill": preselected_skill,
        },
    )


@login_required
def my_barters(request):
    # barters = Barter.objects.filter(
    #     Q(user_to=request.user) | Q(user_from=request.user)
    # ).select_related("user_from", "user_to", "skill_from", "skill_to").order_by("-date_requested")
    barters = Barter.objects.filter(
    Q(user_from=request.user) |
    Q(
        user_to=request.user,
        status__in=[
            Barter.STATUS_ADMIN_APPROVED,
            Barter.STATUS_ACCEPTED,
            Barter.STATUS_REJECTED,
            Barter.STATUS_COMPLETED,
        ],
    )).select_related("user_from", "user_to", "skill_from", "skill_to").order_by("-date_requested")

    feedback_map = {}

    for b in barters:
        fb = b.feedback_set.filter(user=request.user).first()
        feedback_map[b.id] = fb if fb else None

    return render(
        request,
        "skillzone/barters.html",
        {
            "barters": barters,
            "feedback_map": feedback_map
        },
    )
 

@login_required
def update_barter_status(request, barter_id, new_status):
    """
    Update the status of a barter with simple rules:

    - Only the receiver (user_to) can Accept or Reject a Pending barter.
    - Either participant (user_from or user_to) can mark an Accepted barter as Completed.
    - Only valid status values from Barter.STATUS_CHOICES are allowed.
    """
    barter = get_object_or_404(Barter, id=barter_id)

    valid_statuses = dict(Barter.STATUS_CHOICES).keys()
    if new_status not in valid_statuses:
        messages.error(request, "Invalid status.")
        return redirect("skillzone:my_barters")

    # Pending -> Accepted / Rejected (only receiver)
    if (
    barter.status == Barter.STATUS_ADMIN_APPROVED
    and request.user == barter.user_to):
        if new_status in [Barter.STATUS_ACCEPTED, Barter.STATUS_REJECTED]:
            barter.status = new_status
            barter.save()
            messages.success(request, f"Barter #{barter.id} updated to {new_status}.")
            return redirect("skillzone:my_barters")
        else:
            messages.error(request, "You can only accept or reject a pending barter.")
            return redirect("skillzone:my_barters")

    # Accepted -> Completed (either participant)
    # if (
    #     barter.status == Barter.STATUS_ACCEPTED
    #     and new_status == Barter.STATUS_COMPLETED
    #     and request.user in [barter.user_from, barter.user_to]
    # ):
    #     barter.status = Barter.STATUS_COMPLETED
    #     barter.save()
    #     messages.success(request, f"Barter #{barter.id} marked as completed.")
    #     return redirect("skillzone:my_barters")
    
    # Accepted -> Completed (needs BOTH users)
    if barter.status == Barter.STATUS_ACCEPTED and new_status == Barter.STATUS_COMPLETED:
        if request.user == barter.user_from:
            barter.completed_by_from = True
            messages.success(request, "You marked this barter as completed.")
        elif request.user == barter.user_to:
            barter.completed_by_to = True
            messages.success(request, "You marked this barter as completed.")
        else:
            messages.error(request, "You are not allowed to do this.")
            return redirect("skillzone:my_barters")

    # If both confirmed → complete barter
    if barter.completed_by_from and barter.completed_by_to:
        barter.status = Barter.STATUS_COMPLETED
        messages.success(request, f"Barter #{barter.id} is now fully completed!")

    barter.save()
    return redirect("skillzone:my_barters")


    messages.error(request, "You are not allowed to update this barter.")
    return redirect("skillzone:my_barters")


@login_required
def give_feedback(request, barter_id):
    barter = get_object_or_404(Barter, id=barter_id)

    if request.user not in [barter.user_from, barter.user_to]:
        messages.error(request, "You cannot give feedback for this barter.")
        return redirect("skillzone:completed_barters")

    if request.method == "POST":
        rating = float(request.POST.get("rating"))
        comment = request.POST.get("comment")

        fb, created = Feedback.objects.get_or_create(
            barter=barter,
            user=request.user,
            defaults={"rating": rating, "comment": comment},
        )

        if not created:
            fb.rating = rating
            fb.comment = comment
            fb.save()
            messages.success(request, "Feedback updated!")
        else:
            messages.success(request, "Feedback submitted!")

        return redirect("skillzone:completed_barters")

    return redirect("skillzone:completed_barters")


@login_required
def completed_barters(request):
    barters = Barter.objects.filter(status="Completed")

    feedback_map = {}
    already_feedback_ids = []

    for b in barters:
        fb = b.feedback_set.filter(user=request.user).first()
        feedback_map[b.id] = fb if fb else None
        if fb:
            already_feedback_ids.append(b.id)

    return render(
        request,
        "skillzone/completed_barters.html",
        {
            "barters": barters,
            "feedback_map": feedback_map,
            "already_feedback_ids": already_feedback_ids,
        },
    )


@login_required
def user_list(request):
    """
    Browse and search other users.
    """
    query = request.GET.get("q", "").strip()
    users = User.objects.all().select_related("profilemodel")

    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(profilemodel__full_name__icontains=query)
            | Q(skills__name__icontains=query)
        ).distinct()

    return render(
        request,
        "skillzone/user_list.html",
        {"users": users, "query": query},
    )


@login_required
def user_detail(request, user_id):
    """
    View another user's public profile + skills and overall rating.
    """
    other_user = get_object_or_404(User.objects.select_related("profilemodel"), id=user_id)
    skills = Skill.objects.filter(user=other_user)

    avg_rating = Feedback.objects.filter(
        barter__user_to=other_user
    ).aggregate(avg=Avg("rating"))["avg"]

    return render(
        request,
        "skillzone/user_detail.html",
        {
            "other_user": other_user,
            "skills": skills,
            "avg_rating": avg_rating,
        },
    )


# messaging system


@login_required
def inbox(request):
    """
    Very simple inbox: list of latest messages received.
    """
    messages_qs = Message.objects.filter(recipient=request.user).select_related(
        "sender"
    ).order_by("-created_at")
    return render(
        request,
        "skillzone/inbox.html",
        {"messages": messages_qs},
    )


@login_required
def conversation(request, user_id):
    """
    One-to-one conversation between the current user and another user.
    """
    other_user = get_object_or_404(User, id=user_id)

    messages_qs = Message.objects.filter(
        Q(sender=request.user, recipient=other_user)
        | Q(sender=other_user, recipient=request.user)
    ).select_related("sender", "recipient").order_by("created_at")

    # Mark incoming messages as read
    Message.objects.filter(
        sender=other_user, recipient=request.user, is_read=False
    ).update(is_read=True)

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        if body:
            Message.objects.create(
                sender=request.user,
                recipient=other_user,
                body=body,
            )
            return redirect("skillzone:conversation", user_id=other_user.id)

    return render(
        request,
        "skillzone/conversation.html",
        {"other_user": other_user, "messages": messages_qs},
    )
