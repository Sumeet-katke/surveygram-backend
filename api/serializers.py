from rest_framework import serializers
from .models import CustomUser, role, survey, questions,Company,  response, surveyHistory

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

from .models import survey, rewards, Company, typeOfQuestion

class RewardSerializer(serializers.ModelSerializer):  # Nested serializer for 'reward'
    class Meta:
        model = rewards
        fields = ['name']  # Or other fields you want to include

class CompanySerializer(serializers.ModelSerializer):  # Nested serializer for 'company'
    class Meta:
        model = Company
        fields = ('id', 'userId')  # Or other relevant fields

class TypeOfQuestionSerializer(serializers.ModelSerializer):  # Nested serializer for 'typeOf'
    class Meta:
        model = typeOfQuestion
        fields = ('id', 'name')  # Or other relevant fields

class surveySerializer(serializers.ModelSerializer):
    reward = RewardSerializer()
    # company = CompanySerializer()
    typeOf = TypeOfQuestionSerializer()
    timeToFinish = serializers.TimeField(format="%H:%M:%S")  # Format the time

    class Meta:
        model = survey
        fields = ["id", "title", "reward", "rewardQuantity", "company", "startDate", "endDate", "timeToFinish", "description", "ageFrom", "ageTo", "typeOf"]  # Include all relevant fieldse", "reward", "rewardQuantity", "company", "startDate", "timeToFinish", "description"]

class questionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = questions
        fields = "__all__"

class responseSerializer(serializers.ModelSerializer):

    class Meta:
        model = response
        fields = "__all__"

class surveyHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = surveyHistory
        fields = "__all__"

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"

class Userserializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["first_name", "email"]