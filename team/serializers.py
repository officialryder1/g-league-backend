from .models import Team, Player, Coach
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
        
       