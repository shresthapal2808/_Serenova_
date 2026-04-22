
from django.shortcuts import render
from httpx import post, request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from serenova.models import Comment, Post
from .serializers import PostSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate


class CommunityPostAPIView(APIView):      #this class handles API requests for posts using APIView
    permission_classes = [IsAuthenticatedOrReadOnly]  # Ensure only authenticated users can access this view
    def get(self, request):
        # 1. Get all posts (latest first)
        posts = Post.objects.all().order_by('-created_at') 

        # 2. Apply mood filter if provided
        mood = request.query_params.get('mood')
        if mood:
            posts = posts.filter(mood=mood)

        # 3. Apply pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10

        result_page = paginator.paginate_queryset(posts, request)

        # 4. Serialize with request context (IMPORTANT for is_owner)
        serializer = PostSerializer(
            result_page,
            many=True,
            context={"request": request}
        )

        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        #only logged in users are allowed to create posts, otherwise return 403 error
        if not request.user.is_authenticated:
            return Response({"error": "Login required"}, status=403)

        serializer = PostSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)   # ✅ ONLY THIS
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#API for a single post detail, update, delete
class CommunityPostDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]          # Only authenticated users can access this view

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return None

    def get(self, request, pk):
        post = self.get_object(pk)

        if not post:
            return Response({"error": "Post not found"}, status=404)

        serializer = PostSerializer(post, context={"request": request})
        return Response(serializer.data)

    def delete(self, request, pk):
        post = self.get_object(pk)

        if not post:
            return Response({"error": "Post not found"}, status=404)

        #if not the owner of the post, return 403 error 
        if post.user != request.user:
            return Response({"error": "Permission denied"}, status=403)

        #if the user is the owner, delete the post and return a success message with 204 status code (no content)    
        post.delete()
        return Response({"message": "Post deleted"}, status=status.HTTP_204_NO_CONTENT)
    
    def patch(self, request, pk):
        post = self.get_object(pk)

        if not post:
            return Response({"error": "Post not found"}, status=404)
        
        #ownership check
        if post.user != request.user:
            return Response({"error": "Permission denied"}, status=403)
        
        content =  request.data.get('content')
        if not content:
            return Response({"error": "Content is required"}, status=400)
        
        serializer = PostSerializer(post, data=request.data, partial=True, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        print("PATCH USER:", request.user)
        print("POST OWNER:", post.user)

        return Response(serializer.errors, status=400)
    

#Comments
class CommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id=None, pk=None):
        if post_id is None:
            return Response({"error": "post_id required"}, status=400)
        comments = Comment.objects.filter(post_id=post_id).order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk, user=request.user)
            comment.delete()
            return Response({"message": "Deleted"}, status=204)
        except Comment.DoesNotExist:
            return Response({"error": "Not found"}, status=404)
    

class LoginAPI(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})

        return Response({"error": "Invalid credentials"}, status=400)