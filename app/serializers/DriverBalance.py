from app.serializers.UserExtended import UserExtendedSerializer
from rest_framework import serializers
from app.models import DriverBalance, DriverBalanceDetail


class DriverBalanceSerializer(serializers.ModelSerializer):
    driver = UserExtendedSerializer(many=False)

    class Meta:
        model = DriverBalance
        fields = ("id", "driver", "total")


class DriverBalanceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverBalanceDetail
        fields = ("id", "created_at", "driver_balance", "value", "type")
