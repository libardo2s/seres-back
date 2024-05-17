from rest_framework import serializers
from .User import UserSerializer
from app.models import UserExtended


class UserExtendedSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)

    class Meta:
        model = UserExtended
        fields = (
            "id",
            "user",
            "address",
            "phone",
            "birth_date",
            "is_driver",
            "photo_profile",
            "license_plate",
            "status",
        )
