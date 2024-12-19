from django.urls import path, include
from .views import route, RegisterView, ProtectedView, TeamView, PlayerView, create_invite, register_coach, GenerateInviteLinkView, accept_invite, get_current_user, get_player_profile, get_coach_profile,  get_team_player, player_marketplace, MatchDetailView, MatchListCreateView, upcoming_matches, match_played, league_table

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

# Create a router and register the viewset

router = DefaultRouter()
router.register(r'team', TeamView, basename='team')
router.register(r'players', PlayerView, basename='player')

urlpatterns = [
    path('', include(router.urls)),   # Includes all router URLs
    path('route/', route),        # Corrected path format
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', RegisterView.as_view(), name='register'),
    path('protected', ProtectedView.as_view()),
    path('invite/', create_invite, name="create_invite"),
    path('register/<uuid:token>/', register_coach, name='register_coach'),
    path('generate-invite/<int:team_id>/', GenerateInviteLinkView.as_view(), name='generate_invite'),
    path('invite/<uuid:token>/', accept_invite, name='accept_invite'),
    path('user_me/', get_current_user, name="current_user"),
    path('player_profile/', get_player_profile, name="player_profile"),
    path('coach_profile/', get_coach_profile, name='coach_profile'),
    path('team_player/<int:team_id>/players/', get_team_player, name='player_team'),
    path('player-marketplace/', player_marketplace, name="player-marketplace"),

    # Matches
    path('matches/all/', MatchListCreateView.as_view(), name='match-list-create'),
    path('matches/<int:pk>/', MatchDetailView.as_view(), name='match-detail'),
    path('matches/upcoming/', upcoming_matches, name='upcoming-matches'),
    path('matches/played/', match_played, name="match_played"),

    # League Table
    path("league-table/", league_table, name="league-table")


]
