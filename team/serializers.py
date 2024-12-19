from .models import Team, Player, Coach, Match
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username', 'password', 'email', 'role' ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class TeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Team
        fields = ['url', 'id',  'name', 'logo', 'abbr', 'bio', 'num_roaster']

class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source="name.username", read_only=True)
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Player
        fields = ['url', 'id', 'name', 'team', 'role', 'image', 'bio']
        extra_kwargs = {
                'url': {'view_name': 'player-detail', 'lookup_field': 'pk'},  
            }
        
class CoachSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField()
    team = TeamSerializer(read_only=True)

    class Meta:
        model = Coach
        fields = ['id', 'name', 'image', 'team', 'bio']
        

class MatchSerializer(serializers.ModelSerializer):
    team_a = TeamSerializer(read_only=True)
    team_b = TeamSerializer(read_only=True)
    winner = TeamSerializer(read_only=True)

    class Meta:
        model = Match
        fields = [
            'id', 'team_a', 'team_b', 'date', 'status', 'team_a_score',
            'team_b_score', 'winner', 'created_by', 'created_at'
        ]

class LeagueTableSerializer(serializers.ModelSerializer):
    kd_ratio = serializers.FloatField(read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'logo', 'wins', 'loses', 'points', 'kd_ratio']
