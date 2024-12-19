from django.contrib import admin
from .models import User, Team, Player, Coach, Invitation, InviteLink, Match

admin.site.register(User)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Coach)
admin.site.register(Invitation)
admin.site.register(InviteLink)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('team_a', 'team_b', 'date', 'status', 'winner')
    list_filter = ('status', 'date')
    search_fields = ('team_a__name', 'team_b__name')