# from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, PlayerSerializer, TeamSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Player, Team, Invitation, User, Coach

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