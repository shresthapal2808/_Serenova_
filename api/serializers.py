
from rest_framework import serializers
from serenova.models import Comment, Post
from django.contrib.auth.models import User
from django.utils.timezone import now

class PostSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')  # to display the username instead of user ID
    is_owner = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['id','content', 'mood', 'created_at', 'username', 'is_owner']
    
    def get_is_owner(self, obj):
        request = self.context.get("request")
        if request and request.user == obj.user:
            return True
        return False
    
class CommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)  # to display the username instead of user ID
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'text', 'created_at']
        read_only_fields = ['user']  # make user field read-only