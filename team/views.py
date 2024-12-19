# from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, PlayerSerializer, TeamSerializer, CoachSerializer, MatchSerializer, LeagueTableSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Player, Team, Invitation, User, Coach, InviteLink, Match
from django.utils.timezone import now, timedelta
from django.shortcuts import get_object_or_404

def route(request):
    data = {
        "message": "hello world",
        "status": "success"
    }
    return JsonResponse(data)


    
class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role', 'normal')

        user = get_user_model().objects.create_user(
            username=username, email=email, password=password, role=role
        )
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class ProtectedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected route"})
    

class TeamView(viewsets.ModelViewSet):
    queryset = Team.objects.all().order_by('-created_at')
    serializer_class = TeamSerializer

class PlayerView(viewsets.ModelViewSet):
    queryset = Player.objects.all().order_by('-date_joined')
    serializer_class = PlayerSerializer

@api_view(['POST'])
def create_invite(request):
    email = request.data.get('email')
    team_id = request.data.get('team_id')

    # Handle create invite
    invitation = Invitation.objects.create(email=email, team_id=team_id)
    invite_link = f"{request.get_host()}/register/{invitation.token}/"

    return Response({"invite_link": invite_link}, status=201)

@api_view(['POST'])
def register_coach(request, token):
    try:
        invitation = Invitation.objects.get(token=token, is_used=False)
        username = request.data.get('username')
        password = request.data.get('password')

        # Create user and coach profile
        user = get_user_model().objects.create_user(username=username, password=password, email=invitation.email, role='coach')
        Coach.objects.create(name=user, team=invitation.team)

        # Set the invitation as used
        invitation.is_used = True
        invitation.save()

        return Response({"message": "Registration successful"}, status=201)
    except Invitation.DoesNotExist:
        return Response({"error": "Invalid or expired token."}, status=400)
    
class GenerateInviteLinkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, team_id):
        try:
            team = Team.objects.get(id=team_id)
            
            # Ensure the logged-in user is a coach of the team
            coach = Coach.objects.filter(name=request.user, team=team).first()
            if not coach:
                return Response({"error": "You are not the coach of this team"}, status=403)
            
            # Create invite link
            invite = InviteLink.objects.create(
                team=team, 
                created_by=request.user, 
                expires_at=now() + timedelta(days=5)
            )

            # invite_url = f"{request.build_absolute_uri('/api/invite/')}{invite.token}/"

            invite_url = invite.token
            return Response({"invite_link": invite_url}, status=201)
        
        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)
        
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_invite(request, token):
    try:
        invite = InviteLink.objects.get(token=token, is_active = True)

        # check if the is expired
        if invite.expires_at < now():
            return Response({"error": "Invite link has expired"}, status=400)
        
        # create the team player
        user = request.user
        if user.role != "player":
            return Response({"error": "Only players can accept team invites"}, status=400)
        
        if hasattr(user, 'player'):
            player = user.player
        else:
            player = Player(name=user)

        player.team = invite.team
        player.save()

        # Deactivate the invite link after use
        invite.is_active = False
        invite.save()

        return Response({"success": "You have successfully joined the team"}, status=200)
    except InviteLink.DoesNotExist:
        return Response({"error": "Invalid invite link"}, status=404)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_current_user(request):
    try:
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_player_profile(request):
    try:
        # Ensure the logged-in user has a player profile
        player = get_object_or_404(Player, name=request.user)
        serializer = PlayerSerializer(player, context={'request': request})
        return Response({
            'success': True,
            'data': serializer.data
        }, status=200)
    except Player.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Player profile not found.'
        }, status=404)
    
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_coach_profile(request):
    coach = get_object_or_404(Coach, name=request.user)
    serializer = CoachSerializer(coach, context={'request': request})
    return Response({
        'success': True,
        'data': serializer.data
    }, status=200)

@api_view(['GET'])
def get_team_player(request, team_id):
   try:
        team = Team.objects.get(id=team_id)
        players = Player.objects.filter(team=team)
        serializer = PlayerSerializer(players, many=True, context={'request': request})
        return Response({
            'success': True,
            'data': serializer.data
        }, status=200)
   except Team.DoesNotExist:
       return Response({
           'success': False,
           'error': "Team not found"
       }, status=404)
   
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def player_marketplace(request):
    """
    Get all users with role "player" who are not in the Player model.
    """
    registered_players = Player.objects.values_list('name_id', flat=True)
    free_agents = User.objects.filter(role="player").exclude(id__in=registered_players)

    if free_agents.exists():
        serializer = UserSerializer(free_agents, many=True, context={'request': request})
        return Response({
            "success": True,
            "data": serializer.data
        }, status=200)
    
    return Response({
        "success": False,
        "message": "No free agents available"
    }, status=404)


# List and Create matches view
class MatchListCreateView(generics.ListCreateAPIView):
    queryset = Match.objects.all().order_by('-date')
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# Retrieve, Update, and Delete Match Details
class MatchDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# Get incoming matches
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def upcoming_matches(request):
    matches = Match.objects.filter(status="pending").order_by('date')
    serializer = MatchSerializer(matches, many=True, context={"request": request})
    return Response({
        "success": True,
        "data": serializer.data},
        status=200
    )
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def match_played(request):
    matches = Match.objects.filter(status="completed")
    serializer = MatchSerializer(matches, many=True, context={'request':request})
    return Response({
        "success": True,
        "data": serializer.data
    }, status=200)

@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def league_table(request):
    teams = Team.objects.all().order_by('-points', '-wins', '-loses')
    serializer = LeagueTableSerializer(teams, many=True, context={'request': request})

    return Response({
        "success": True,
        "data": serializer.data
    }, status=200)
