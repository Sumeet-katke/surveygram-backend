from rest_framework import serializers
from .models import CustomUser, role

class CustomUserSerializer(serializers.ModelSerializer):
    roleId = serializers.PrimaryKeyRelatedField(queryset=role.objects.all())
    password = serializers.CharField(write_only=True)  # Hide the password field in response

    class Meta:
        model = CustomUser
        fields = ['email', 'userId', 'first_name', 'last_name', 'password', 'roleId']

    def create(self, validated_data):
        user = CustomUser.objects.create(
            email=validated_data['email'],
            userId=validated_data['userId'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            roleId=validated_data['roleId']  # Use the validated roleId
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
