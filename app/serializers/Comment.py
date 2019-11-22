from rest_framework import serializers
from .UserExtended import UserExtendedSerializer
from app.models import Comment

class CommentSerializer(serializers.ModelSerializer):
    client = UserExtendedSerializer(many=False)
    driver = UserExtendedSerializer(many=False)
    class Meta:
        model = Comment
        fields = ('id', 'comment', 'client', 'driver', 'score_personalPresentation', 
                    'score_carCondition', 'score_attitude')

