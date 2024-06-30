from datetime import datetime
from app.models import Service
from app.serializers.Service import ServiceSerializer
from django.core.management.base import BaseCommand, CommandError

from app.views import sendNotificationClient, sendNotificationDriver


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:

            now = datetime.now()

            reservations = Service.objects.filter(
                type_service="Reserva", date__gte=now, state="Conductor asignado"
            )

            for service in reservations:
                time_diff = service.date - now
                if time_diff <= 900:
                    service_serializers = ServiceSerializer(service, many=False)
                    service = service_serializers.data
                    driver = service.driver.id
                    cliente = service.driver.id

                    sendNotificationDriver(service, "add", driver_id=driver)
                    sendNotificationClient(service, cliente, "update")

        except CommandError as e:
            print(str(e))
