from app.serializers.UserExtended import UserExtendedSerializer
from rest_framework import serializers
from app.models import DriverPayment


class DriverPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverPayment
        fields = ("id", "amount", "status", "pse_url", "driver")
