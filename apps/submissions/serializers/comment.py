from rest_framework import serializers
from ..models import SubmissionComment


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = SubmissionComment
        fields = ('id', 'author', 'author_name', 'body', 'resolved', 'created_at')

    def get_author_name(self, obj):
        return obj.author.full_name if obj.author else None


class CommentCreateSerializer(serializers.Serializer):
    body = serializers.CharField()
