from rest_framework import serializers
from .UserExtended import UserExtendedSerializer
from app.models import Service


class ServiceSerializer(serializers.ModelSerializer):
    client = UserExtendedSerializer(many=False)
    driver = UserExtendedSerializer(many=False)

    class Meta:
        model = Service
        fields = (
            "id",
            "date",
            "client",
            "driver",
            "origin_name",
            "origin_lat",
            "origin_lan",
            "destiny_name",
            "destiny_lat",
            "destiny_lan",
            "distance",
            "time",
            "type_service",
            "disability",
            "charge",
            "pet",
            "passengers",
            "state",
            "description",
            "value",
            "cancel_reason",
            "date_reservation",
            "reservation_time",
        )
