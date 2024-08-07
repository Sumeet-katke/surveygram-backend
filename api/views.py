from django.shortcuts import render
from rest_framework.views import APIView
from api.serializers import (surveySerializer, questionsSerializer,CompanySerializer, responseSerializer, surveyHistorySerializer,
                            Userserializer, surveyHistorySerializer)
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from api.models import (questions,
                        Company,
                        rewards,
                        survey, 
                        questions, 
                        response, 
                        surveyHistory, 
                        typeOfQuestion)
from rest_framework import status, viewsets
from django.db import transaction
from datetime import datetime
import logging
from django.http import HttpResponseBadRequest, HttpResponseServerError

User = get_user_model()
from .models import CustomUser as User, role
# Create your views here.

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from api.serializers import CustomUserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser
from django.core.exceptions import ValidationError

class CustomUserCreate(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(type(request.data['roleId']))
        serializer.is_valid(raise_exception=True)
        # Ensure role is provided and valid during registration
        role_id = serializer.validated_data.pop('roleId', None)  # Assuming you pass roleId in the request
        try:
            role_obj = role.objects.get(id=role_id.id)
        except role.DoesNotExist:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save(roleId=role_obj)  # Pass the roleId to the serializer's save method

        # Generate tokens (adjust as needed for your simpleJWT setup)
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

from django.utils import timezone


class CompanyRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]  # Allow anyone to register a company

    def post(self, request, *args, **kwargs):
        user_serial = CustomUserSerializer(data=request.data)
        company_serial = CompanySerializer(data=request.data)

        user_serializer = user_serial.is_valid()
        company_serializer = company_serial.is_valid()

        if user_serializer and company_serializer:

            # Create the user first
            user = user_serial.save(roleId=role.objects.get(id=2))  # Assuming role ID 2 is for companies

            # Now create the company and associate it with the user
            company = company_serial.save(userId=user)

            # Generate tokens
            refresh = RefreshToken.for_user(user)

            # Include company details in the response
            response_data = {
                'user': user_serial.data,
                'company': company_serial.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        else:

            # Combine errors from both serializers
            errors = {**user_serial.errors, **company_serial.errors}
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.first_name
        token['email'] = user.email
        # ...
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)

        # Include additional data in the response
        data['user_info'] = {
            'user': self.user.id,
            'email' : self.user.email,
            'role': self.user.roleId.id,
            'first_name':self.user.first_name,
            'last_login':self.user.last_login
            # Add more user details here
        }
        User.objects.filter(id=self.user.id).update(last_login=timezone.now())
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(serializer)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.response import Response
from rest_framework import status

class CookieTokenRefreshSerializer(TokenRefreshSerializer):
  refresh = None

class CookieTokenRefreshView(TokenRefreshView):
  serializer_class = CookieTokenRefreshSerializer

  def finalize_response(self, request, response, *args, **kwargs):
      if response.data.get("access"):
          response.set_cookie(
              "access_token",
              response.data["access"],
              httponly=True,
          )
          del response.data["access"]
      return super().finalize_response(request, response, *args, **kwargs)


class getQuestionDetails(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = questionsSerializer
    def get(self, request):
        try:
            querySet = survey(isActive = True)
            print(querySet)
            data = questionsSerializer(data=querySet)
            print(data.is_valid())
            return Response(data=data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data= str(e), status=status.HTTP_400_BAD_REQUEST)

# class RegisterCompany(APIView, TokenObtainPairView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         try:
#             response = request.body
#             print(response)
#             return Response(data='Done', status=status.HTTP_201_CREATED)
        
#         except Exception as e:
#             return Response(data=str(e), status=status.HTTP_400_BAD_REQUEST)

import json

# Set up a logger for error tracking
logger = logging.getLogger(__name__) 
from datetime import datetime, timedelta

class PostSurvey(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try :
            with transaction.atomic():
                data = json.loads(request.body)
                # print("Data: ",data)
                


                required_fields = ['title', "TypeOfQuestion", "age_groupFrom", 'rewardType', "startdate", "deadLine",
                                    "description", "no_of_question", "questions"]
                missing_fields = [field for field in required_fields if not data.get(field)]
                
                if missing_fields :
                    error = {'Error':'Missing Fields',
                             'Missing Fields': f'{missing_fields}'}
                    return Response(data=json.dumps(error), status=status.HTTP_400_BAD_REQUEST)
                
                title = data["title"]
                TypeOfQuestion = data['TypeOfQuestion']
                age_groupFrom = data['age_groupFrom']
                age_groupTo = data['age_groupTo']
                rewardType = data['rewardType']
                startdate = datetime.strptime(data['startdate'], "%Y-%m-%d").date()
                deadLine = datetime.strptime(data['deadLine'], "%Y-%m-%d").date()
                description = data.get('description', '')
                no_of_questions = int(data['no_of_question'])
                # question = data.get('questions', [])
                Questions = data['questions']


                if (len(data.get("title", ''))>250):
                    return Response(data=json.dumps({"error":"Title length greater than 200"}), status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    Reward = rewards.objects.get(name=rewardType)
                except rewards.DoesNotExist:
                    return Response(data="Reward doesn't exists", status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    Qtype = typeOfQuestion.objects.get(name=data.get('TypeOfQuestion', ''))
                except typeOfQuestion.DoesNotExist:
                    return Response(data="Wrong Question type", status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    companyUser = Company.objects.get(userId = request.user)
                except Company.DoesNotExist:
                    return Response(data="UnAuthorised Company. Doesn't exists in Database", status=status.HTTP_401_UNAUTHORIZED)
                reward_quantity = Qtype.reward * no_of_questions
                print("Reward: ",no_of_questions)
                print(Qtype.time)
                # from datetime import datetime, timedelta
                # hours = Qtype.time.hour
                # minutes = Qtype.time.minute
                # seconds = Qtype.time.second
                # total_seconds = (hours * 3600) + (minutes * 60) + seconds
                # total_timedelta = timedelta(seconds=total_seconds)
                # timeTofinish = (datetime.min + total_timedelta).time()

                time_delta = timedelta(hours=Qtype.time.hour, minutes=Qtype.time.minute, seconds=Qtype.time.second)
                timeTofinish = time_delta * no_of_questions
                print(timeTofinish)
                # print(type())
                # total_seconds = (Qtype.time.hour * 3600 + Qtype.time.minute * 60 + Qtype.time.second) * no_of_questions
                # timeTofinish = (datetime.min + timedelta(seconds=total_seconds)).time()


                # timeTofinish = (datetime.min + (timedelta(hours=Qtype.time.hour, minutes=Qtype.time.minute, seconds=Qtype.time.second) * no_of_questions)).time()

                # timeTofinish = Qtype.time *no_of_questions
                print(type(age_groupFrom))
                try:
                    new_survey = survey.objects.create(
                        title = title,
                        reward = Reward,
                        rewardQuantity = reward_quantity,
                        startDate = startdate,
                        endDate = deadLine,
                        ageFrom = age_groupFrom,
                        ageTo = age_groupTo,
                        company = companyUser,
                        typeOf = Qtype,
                        timeToFinish = str(timeTofinish),
                        description = description,
                    )
                    print("Creating survey")

                    for question_data in Questions:
                        print(question_data)
                        questions.objects.create(
                            question = question_data['question'],
                            options = json.dumps(question_data['options']),
                            surveyId = new_survey
                        )

                except ValidationError as e:
                    error_data = e.message_dict if hasattr(e, 'message_dict') else e.messages
                    return Response(data=error_data, status=status.HTTP_400_BAD_REQUEST)
                        
                except Exception as e:  # Catch other database errors
                    logger.error(f"Error creating survey or questions: {e}")
                    return HttpResponseServerError({'status': 'error', 'message': 'Failed to create survey or questions'})

                return Response(data="Survery Created Successfully", status=status.HTTP_201_CREATED)
            
        except json.JSONDecodeError:
            return HttpResponseBadRequest({'status': 'error', 'message': 'Invalid JSON data'})
        
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class UserSurveyFetch(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = surveySerializer

    def get(self, request):
        try:
            # Pagination setup
            paginator = PageNumberPagination()
            paginator.page_size = 3  # Set the number of surveys per page

            last_viewed_survey_id = request.session.get('last_viewed_survey_id', 0) 

            # Retrieve inactive surveys for the current user, sorted by endDate
            # user_company = Company.objects.get(userId=request.user)
            answered_survey_ids = surveyHistory.objects.filter(
                userId=request.user
            ).values_list('surveyID', flat=True)

            # Retrieve inactive surveys excluding those already answered by the user
            surveys_query = survey.objects.filter(
                isActive=True,
                id__gt=last_viewed_survey_id
            ).exclude(
                id__in=answered_survey_ids 
            ).order_by('endDate')
            # print(surveys_query)
            # Paginate the queryset
            paginated_surveys = paginator.paginate_queryset(surveys_query, request)

            # Serialize the paginated surveys
            surveys_serialized = surveySerializer(paginated_surveys, many=True)

            response_data = []
            for survey_data in surveys_serialized.data:
                company_id = survey_data['company']

                try:
                    company_obj = Company.objects.get(id=company_id)
                    user_obj = company_obj.userId
                except Company.DoesNotExist:
                    continue

                company_serialized = CompanySerializer(company_obj)
                user_serialized = Userserializer(user_obj)

                survey_id = survey_data['id']
                question_instances = questions.objects.filter(surveyId=survey_id)
                questions_serialized = questionsSerializer(question_instances, many=True)

                survey_with_details = {
                    'survey': survey_data,
                    'company_url': company_serialized.data['url'],
                    'user': user_serialized.data,
                    'questions': questions_serialized.data
                }
                response_data.append(survey_with_details)

            # Get the paginated response
            paginated_response = paginator.get_paginated_response(response_data)

            return paginated_response 

        except Exception as e:
            logger.error(f"Error fetching surveys or companies: {e}")
            return HttpResponseServerError({'status': 'error', 'message': 'An error occurred'})


class Responses(APIView):
    permission_classes= [IsAuthenticated]

    def post(self, request):
        try:
            with transaction.atomic():

                data = request.data

                # questionId = data['questionId']
                userObj = request.user
                # userResponse = data

                for questionIdData, responses in data.items():
                    try:
                        questionObj = questions.objects.get(id=questionIdData)
                        print(questionObj.surveyId.id)
                        surveyObj = survey.objects.get(id=questionObj.surveyId.id)
                    except questions.DoesNotExist:
                        return Response(data=f"question Id {questionIdData} doesn't exists in the database", status=status.HTTP_400_BAD_REQUEST)
                    
                    responsesObj = response.objects.create(
                        questionId = questionObj,
                        userID = userObj,
                        userResponse = responses,
                        surveyId = questionObj.surveyId
                    )
                    print(surveyObj.company)
                    responsesObj.save()
                surveyHistObj = surveyHistory.objects.create(
                    userId = userObj,
                    companyId = surveyObj.company,
                    surveyID = surveyObj
                )

                surveyHistObj.save()
                return Response(data=f"Response collectd with ID {responsesObj.id}", status=status.HTTP_202_ACCEPTED)
        except Exception as e:
                return Response(data=f"{str(e)} Response", status=status.HTTP_400_BAD_REQUEST)
                

class SurveyHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            try:    
                surveys = surveyHistory.objects.filter(userId=request.user.id)
            except surveyHistory.DoesNotExist:
                return Response(data=None, status=status.HTTP_204_NO_CONTENT)
            
            surveyData = surveyHistorySerializer(surveys, many=True)
            return Response(data=surveyData.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(data=f"{str(e)}")
        

class CompanySurveyHistory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            comapnyId = Company.objects.get(userId=request.user.id)
            print(comapnyId.id)
            surveys = surveyHistory.objects.filter(companyId = comapnyId.id)
            responsedata = surveyHistorySerializer(surveys, many=True).data
            return Response(data=responsedata, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data=str(e))