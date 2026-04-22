'''as_view() Internally:

Takes your class(since PostAPIView is a class based view)
Handles GET, POST methods
Returns a callable function'''

'''post_id → group of comments
pk → single comment'''

from django.urls import path
from .views import CommentAPIView, CommunityPostAPIView, LoginAPI
from .views import CommunityPostDetailAPIView
urlpatterns = [ 
    path('posts/', CommunityPostAPIView.as_view(), name='community-posts'),
    path('posts/<int:pk>/', CommunityPostDetailAPIView.as_view(), name='community-post-detail'),
    path('posts/<int:pk>/', CommunityPostDetailAPIView.as_view(), name='post-detail'),
    path('comments/<int:post_id>/', CommentAPIView.as_view(), name='comment-list'),
    path('comments/create/', CommentAPIView.as_view(), name='comment-create'),
    path('comments/delete/<int:pk>/', CommentAPIView.as_view(), name='comment-delete'),
    path('login/', LoginAPI.as_view()),


]