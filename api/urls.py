from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from api.views import (
    getQuestionDetails,
    PostSurvey,
)



from .views import (CustomUserCreate,Responses,
                    MyTokenObtainPairView,
                    UserSurveyFetch,
                    CookieTokenRefreshView,
                    CompanyRegistrationView,
                    SurveyHistory,
                    CompanySurveyHistory,
                    )

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', CustomUserCreate.as_view(), name = "register user"),
    path('login/', MyTokenObtainPairView.as_view(), name='login user'),
    # path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),


    #-------------------------------------User APIEndpoints-----------------------------------------------
    path('questionFetch/', getQuestionDetails.as_view(), name="fetch all questions"),
    path('fetch-survey/', UserSurveyFetch.as_view(), name = "fetch all surveys"),
    path('record-response/', Responses.as_view(), name="Collecting Response"),
    path('user-survey-history/', SurveyHistory.as_view(), name="Getting User Survey History"),






    #----------------------------------------Company APIEndpoints-----------------------------------------
    path('register-company/', CompanyRegistrationView.as_view(), name="register company"),
    path('post-survey/', PostSurvey.as_view(), name="Post Survey"),
    path('company-history/', CompanySurveyHistory.as_view(), name="Get history"),
]