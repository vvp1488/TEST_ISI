from django.urls import path
from .views import (
    RegisterUserAPIView,
    ThreadCreateAPIView,
    MessageListAPIView,
    ThreadListAPIView,
    UnreadMessagesCountAPIView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterUserAPIView.as_view()),
    path('new_thread/', ThreadCreateAPIView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('messages/<int:thread_id>/', MessageListAPIView.as_view()),
    path('threads/', ThreadListAPIView.as_view()),
    path('unread_msgs/', UnreadMessagesCountAPIView.as_view()),

]

