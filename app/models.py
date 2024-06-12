from django.db import models
from django.contrib.auth.models import User


TYPE_BALANCE_DETAIL = (("recarga", "Recarga"), ("servicio", "Servicio"))
STATUS_PAYMENTS = (
    ("approved", "Transacción aprobada"),
    ("failed", "Transacción fallida"),
    ("declined", "Transacción rechazada"),
    ("pending", "Transacción pendiente"),
)


# Create your models here.
class UserExtended(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField("Dirección", max_length=60, null=True, blank=True)
    phone = models.CharField("Telefono", max_length=10, unique=True)
    birth_date = models.DateField("Fecha de nacimiento", null=True, blank=True)
    is_driver = models.BooleanField("Es conductor", default=False, null=True)
    photo_profile = models.ImageField(
        "Foto de Perfil", upload_to="fotos_de_perfil", null=True, blank=True
    )
    license_plate = models.CharField("Placa", max_length=6, null=True, blank=True)
    is_active = models.BooleanField("Activo", default=True)
    status = models.CharField("Estado del conductor", default="Disponible")

    def __str__(self):
        return "%s - %s %s" % (self.id, self.user.first_name, self.user.last_name)


class DriverBalance(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    driver = models.ForeignKey(
        UserExtended, related_name="balance_driver", on_delete=models.CASCADE
    )
    total = models.FloatField("Total Balance Conductor", default=0.0)


class DriverBalanceDetail(models.Model):
    RC = "recarga"
    SE = "servicio"
    created_at = models.DateTimeField(auto_now=True)
    driver_balance = models.ForeignKey(
        DriverBalance, related_name="driver_balance", on_delete=models.CASCADE
    )
    value = models.FloatField("Valor recarga - uso", default=0.0)
    type = models.CharField("Tipo de balance", choices=TYPE_BALANCE_DETAIL, default=RC)


class Service(models.Model):
    date = models.DateTimeField(auto_now=True)
    client = models.ForeignKey(
        UserExtended, related_name="service_client", on_delete=models.CASCADE
    )
    driver = models.ForeignKey(
        UserExtended, related_name="service_drive", on_delete=models.CASCADE, null=True
    )
    origin_name = models.CharField("Origen", max_length=100)
    origin_lat = models.FloatField(default=0.0)
    origin_lan = models.FloatField(default=0.0)
    destiny_name = models.CharField("Destino", max_length=100)
    destiny_lat = models.FloatField(default=0.0)
    destiny_lan = models.FloatField(default=0.0)
    distance = models.CharField("Distancia", null=True, max_length=30)
    time = models.CharField("Tiempo estimado", null=True, max_length=30)
    type_service = models.CharField("Tipo de servicio", max_length=100)
    disability = models.BooleanField("Discapacidad", default=False)
    charge = models.BooleanField("Carga", default=False)
    pet = models.BooleanField("Mascota", default=False)
    passengers = models.BooleanField("Pasajeros", default=False)
    description = models.TextField("Description", default="Sin descripción")
    state = models.CharField("Estado", max_length=100, default="servicio creado")
    value = models.FloatField(default=0.0)
    cancel_reason = models.CharField(
        "Motivo cancelacion servicio", max_length=100, default=""
    )
    date_reservation = models.DateField("Fecha de reserva", null=True, blank=True)
    reservation_time = models.TimeField("Hora de reserva", null=True, blank=True)

    def __str__(self):
        return "%s - %s" % (str(self.id), self.client.user.first_name)


class MessageService(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    message = models.CharField("Origen", max_length=100)

    def __str__(self):
        return self.message


class TokenPhoneFCM(models.Model):
    user = models.ForeignKey(UserExtended, on_delete=models.CASCADE)
    toke_phone = models.CharField("Token FMC", max_length=250)

    def __str__(self):
        return "%s - %s" % (self.user.user.first_name, self.toke_phone)


class ValueKilometer(models.Model):
    cost = models.FloatField(default=0.0)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s ---- %s" % (self.cost, self.last_update)


class DiscountService(models.Model):
    cost = models.FloatField("Costo a descontara por servicio", default=0.0)


class BasePrice(models.Model):
    base = models.FloatField(default=0.0)
    count_after = models.FloatField(default=0.0)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s ---- %s" % (self.base, self.last_update)


class Comment(models.Model):
    client = models.ForeignKey(
        UserExtended, related_name="comment_client", on_delete=models.CASCADE
    )
    driver = models.ForeignKey(
        UserExtended, related_name="comment_drive", on_delete=models.CASCADE
    )
    comment = models.CharField("Comentario", max_length=150)
    score_personalPresentation = models.FloatField(default=0.0)
    score_carCondition = models.FloatField(default=0.0)
    score_attitude = models.FloatField(default=0.0)

    def __str__(self):
        return self.comment


class DriverPayment(models.Model):
    approved = "approved"
    failed = "failed"
    declined = "rechazado"
    pending = "pending"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    amount = models.FloatField("Total pagado", default=0.0)
    driver = models.ForeignKey(
        UserExtended, related_name="payment_drive", on_delete=models.CASCADE
    )
    status = models.CharField(
        "Estado", choices=STATUS_PAYMENTS, default=STATUS_PAYMENTS[pending]
    )
    payment_id = models.CharField("Id payU", max_length=100, default="")
