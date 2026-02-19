from django.contrib import admin
from .models import Skill, Barter, Feedback


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'description')
    search_fields = ('name', 'description', 'user__username')


# @admin.register(Barter)
# class BarterAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user_from', 'user_to', 'skill_from', 'skill_to', 'status', 'date_requested')
#     list_filter = ('status', 'date_requested')
    
#     search_fields = ('user_from__username', 'user_to__username')
#     date_hierarchy = 'date_requested'

@admin.register(Barter)
class BarterAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_from', 'user_to',
        'skill_from', 'skill_to',
        'status', 'date_requested'
    )
    list_filter = ('status',)
    actions = ['approve_barters']

    def approve_barters(self, request, queryset):
        queryset.filter(status="Pending").update(
            status="Admin Approved",
            admin=request.user
        )
    approve_barters.short_description = "Approve selected barters"

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'barter', 'user', 'rating', 'date')
    list_filter = ('rating', 'date')
    search_fields = ('user__username', 'barter__id')
