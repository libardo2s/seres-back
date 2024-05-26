from app.serializers.UserExtended import UserExtendedSerializer
from rest_framework import serializers
from app.models import DriverBalance


class DriverBalanceSerializer(serializers.ModelSerializer):
    driver = UserExtendedSerializer(many=False)

    class Meta:
        model = DriverBalance
        fields = ("id", "driver", "total")
