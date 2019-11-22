from rest_framework import serializers
from app.models import ValueKilometer

class ValueKilometerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValueKilometer
        fields = ('id', 'cost','last_update')