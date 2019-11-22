from rest_framework import serializers
from app.models import BasePrice

class BasePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasePrice
        fields = ('id', 'base','last_update', 'count_after')