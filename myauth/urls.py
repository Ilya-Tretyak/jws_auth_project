from django.urls import path


from .views import (
    RegisterView,
    LoginView,
    RefreshTokenView,
    LogoutView,
    UserProfileView,
    NewFeedView,
    UserRoleManagementView
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('user/', UserProfileView.as_view(), name='user'),
    path('user/<int:user_id>/roles/', UserRoleManagementView.as_view(), name='user-role-management'),

    path('feed/', NewFeedView.as_view(), name='feed'),
    path('feed/<int:post_id>/', NewFeedView.as_view(), name='feed_id')
]