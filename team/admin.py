from django.contrib import admin
from .models import User, Team, Player, Coach, Invitation, InviteLink

admin.site.register(User)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Coach)
admin.site.register(Invitation)
admin.site.register(InviteLink)
