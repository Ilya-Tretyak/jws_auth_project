from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    UserProfileView,
    NewFeedView
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/', UserProfileView.as_view(), name='user'),
    path('feed/', NewFeedView.as_view(), name='feed'),
    path('feed/<int:post_id>/', NewFeedView.as_view(), name='feed_id')
]