from django.urls import path, include
from .views import route, RegisterView, ProtectedView, TeamView, PlayerView, create_invite, register_coach, GenerateInviteLinkView, accept_invite, get_current_user, get_player_profile

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
    path('player_profile/', get_player_profile, name="player_profile")
]