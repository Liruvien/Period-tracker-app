from rest_framework import serializers
from .models import UserProfile
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'weight']