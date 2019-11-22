from rest_framework import serializers
from app.models import MessageService
from .Service import ServiceSerializer

class MessageSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(many=False)
    class Meta:
        model = MessageService
        fields = ('id', 'service','message')