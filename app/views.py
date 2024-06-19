# -*- coding: utf-8 -*-
import os
import json
import base64
import hashlib
import requests
from datetime import datetime

# DJANGO
from django.db.models import Sum
from django.shortcuts import render
from django.db import IntegrityError
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode

# DJANGO REST FRAMEWORK
from app.serializers.DriverBalance import (
    DriverBalanceDetailSerializer,
    DriverBalanceSerializer,
)
from app.serializers.DriverPayment import DriverPaymentSerializer
from firebase_config import FIREBASE_CONFIG
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

# MODELS
from .models import (
    DiscountService,
    DriverBalance,
    DriverBalanceDetail,
    DriverPayment,
    UserExtended,
    Service,
    TokenPhoneFCM,
    ValueKilometer,
    Comment,
    BasePrice,
    MessageService,
)
from django.contrib.auth.models import User

# SERIALIZERS
from app.serializers.UserExtended import UserExtendedSerializer
from app.serializers.Service import ServiceSerializer
from app.serializers.Price import ValueKilometerSerializer
from app.serializers.Comment import CommentSerializer
from app.serializers.BasePrice import BasePriceSerializer
from app.serializers.Message import MessageSerializer

# TOKEN
from .token import account_activation_token
from pyfcm import FCMNotification

import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate(FIREBASE_CONFIG)
firebase_admin.initialize_app(cred)


@api_view(["POST"])
def loginAdmin(request):
    try:
        if request.method == "POST":
            username = request.data.get("usuario")
            password = request.data.get("contrasena")

            authentication = authenticate(username=username, password=password)

            if authentication is not None:
                if authentication.is_active:
                    user_extended = UserExtended.objects.get(user__id=authentication.id)
                    user_extended_serializer = UserExtendedSerializer(
                        user_extended, many=False
                    )
                    response = {
                        "content": user_extended_serializer.data,
                        "isOk": True,
                        "message": "",
                    }
                else:
                    response = {
                        "content": [],
                        "isOk": False,
                        "message": "El usuario no se encuentra activo",
                    }
            else:
                response = {
                    "content": [],
                    "isOk": False,
                    "message": "El usuario no se encuentra registrado",
                }
        return Response(response, status=status.HTTP_200_OK)
    except UserExtended.DoesNotExist:
        response = {
            "content": [],
            "isOk": False,
            "message": "El usuario no se encuentra registrado",
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {
            "content": [],
            "isOk": False,
            "message": str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


# Create your views here.
@api_view(["POST"])
def login(request):
    try:
        if request.method == "POST":
            phone = request.data.get("telefono")

            user_extended = UserExtended.objects.get(phone=phone)

            if user_extended.is_active:
                user_extended_serializer = UserExtendedSerializer(
                    user_extended, many=False
                )
                response = {
                    "content": user_extended_serializer.data,
                    "isOk": True,
                    "message": "",
                }
            else:
                response = {
                    "content": [],
                    "isOk": False,
                    "message": "El usuario no se encuentra activo",
                }
        return Response(response, status=status.HTTP_200_OK)
    except UserExtended.DoesNotExist:
        response = {
            "content": [],
            "isOk": False,
            "message": "El usuario no se encuentra registrado",
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {
            "content": [],
            "isOk": False,
            "message": str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(["POST"])
def register(request):
    try:
        if request.method == "POST":
            email = request.data.get("correo")
            phone = request.data.get("telefono")
            name = request.data.get("nombres")
            last_name = request.data.get("apellidos")
            is_driver = request.data.get("conductor")
            license_plate = request.data.get("placa")

            new_user = User.objects.create_user(
                username=email,
                password=phone,
                email=email,
                first_name=name,
                last_name=last_name,
            )
            new_user.is_active = True
            new_user.is_superuser = False
            new_user.save()

            user_extended = UserExtended.objects.create(
                phone=phone,
                is_driver=is_driver,
                user=new_user,
                license_plate=license_plate,
            )
            user_extended_serializer = UserExtendedSerializer(user_extended, many=False)

            response = {
                "content": user_extended_serializer.data,
                "isOk": True,
                "message": "Usuario creado exitosamente",
            }
            return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
        response = {
            "content": [],
            "isOk": False,
            "message": str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(["GET"])
def getServiceClient(request, id_client=None):
    try:
        services_client = Service.objects.filter(client__id=id_client).order_by("-date")
        services_client_serializer = ServiceSerializer(services_client, many=True)
        response = {
            "content": services_client_serializer.data,
            "isOk": True,
            "message": "",
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {
            "content": [],
            "isOk": False,
            "message": str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(["GET"])
def getServiceDriver(request, id_driver=None):
    try:
        services_driver = Service.objects.filter(driver__id=id_driver).order_by("-date")
        services_driver_serializer = ServiceSerializer(services_driver, many=True)
        response = {
            "content": services_driver_serializer.data,
            "isOk": True,
            "message": "",
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {
            "content": [],
            "isOk": False,
            "message": str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(["POST"])
def tokerUserFmc(request):
    try:
        if request.method == "POST":
            user_id = request.data.get("user_id")
            token_fmc = request.data.get("token")
            print(f"token fmc: {token_fmc}")
            if token_fmc == "":
                response = {
                    "content": [],
                    "isOk": True,
                    "message": "Token vacio",
                }
                return Response(response, status=status.HTTP_200_OK)

            user = UserExtended.objects.get(id=user_id)
            if TokenPhoneFCM.objects.filter(user=user).exists():
                token = TokenPhoneFCM.objects.get(user=user)
                token.toke_phone = token_fmc
                token.save()
            else:
                TokenPhoneFCM.objects.create(user=user, toke_phone=token_fmc)

            response = {
                "content": [],
                "isOk": True,
                "message": "",
            }
            return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
        response = {
            "content": [],
            "isOk": False,
            "message": str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(["DELETE"])
def deleteTokenFmc(request, id=None):
    try:
        if request.method == "DELETE":
            user = UserExtended.objects.get(id=id)
            token = TokenPhoneFCM.objects.filter(user=user)
            token.delete()

            response = {
                "content": [],
                "isOk": True,
                "message": "",
            }
            return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
        response = {
            "content": [],
            "isOk": False,
            "message": str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(["GET"])
def getServiceWithoutDriver(request):
    try:
        services = Service.objects.filter(state="servicio creado").order_by("-date")
        print(services)
        services_serializer = ServiceSerializer(services, many=True)
        response = {
            "content": services_serializer.data,
            "isOk": True,
            "message": "",
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {
            "content": [],
            "isOk": False,
            "message": str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(["PUT"])
def updateServiceDriver(request, id=None):
    try:
        driver_id = request.data.get("conductor")
        state = request.data.get("estado")

        driver = UserExtended.objects.get(id=driver_id)
        driver_balance = DriverBalance.objects.get(driver_id=driver_id)
        service = Service.objects.get(id=id)
        discount = DiscountService.objects.all().first()

        if service.driver is None:
            if driver_balance.total < discount.cost:
                response = {
                    "content": [],
                    "isOk": False,
                    "message": "Saldo insuficiente. Por favor, recargue para poder aceptar servicios.",
                }

                return Response(response, status=status.HTTP_200_OK)

            service.driver = driver
            service.state = state
            service.save()

            driver_balance.total -= discount.cost
            driver_balance.save()

            DriverBalanceDetail.objects.create(
                driver_balance=driver_balance,
                value=discount.cost,
                type=DriverBalanceDetail.SE,
            )

            services_serializer = ServiceSerializer(service, many=False)
            response = {
                "content": services_serializer.data,
                "isOk": True,
                "message": "",
            }
            sendNotificationClient(
                services_serializer.data, service.client.id, "update"
            )
            return Response(response, status=status.HTTP_200_OK)
        elif service.driver == driver:
            service.state = state
            service.save()
            services_serializer = ServiceSerializer(service, many=False)
            response = {
                "content": services_serializer.data,
                "isOk": True,
                "message": "",
            }
            if state == "Servicio terminado":
                sendNotificationClient(
                    services_serializer.data, service.client.id, "finished"
                )
            elif state == "Servicio cancelado":
                sendNotificationClient(
                    services_serializer.data, service.client.id, "canceled"
                )
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {
                "content": [],
                "isOk": False,
                "message": "El servicio ya tiene un conductor asignado",
            }
            return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {
            "content": [],
            "isOk": False,
            "message": str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(["POST"])
def sendMessage(request):
    try:
        service_id = request.data.get("servicio")
        message = request.data.get("message")

        service = Service.objects.get(id=service_id)

        message_servicio = MessageService.objects.create(
            service=service, message=message
        )

        message_servicio_serializer = MessageSerializer(message_servicio, many=False)
        sendNotificationClient(
            message_servicio_serializer.data, service.client.id, "add_message"
        )

        response = {
            "content": message_servicio_serializer.data,
            "isOk": True,
            "message": "",
        }
        return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
        response = {
            "content": [],
            "isOk": False,
            "message": str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


"""
actualizacion: 0 -> cancelar servicio
actualizacion: 1 -> actualizar, tiempo y distancia
"""


@api_view(["PUT"])
def updateServiceClient(request, id=None):
    try:
        # client_id = request.data.get('cliente')
        state = request.data.get("estado")
        time = request.data.get("tiempo")
        distance = request.data.get("distancia")
        cancel_reason = request.data.get("motivo")
        update = request.data.get("actualizacion")

        # client = UserExtended.objects.get(id=client_id)
        service = Service.objects.get(id=id)

        if update == "0":
            service.state = state
            service.cancel_reason = cancel_reason
            service.save()
            service_serializer = ServiceSerializer(service, many=False)
            sendNotificationDriver(service_serializer.data, "delete")
        elif update == "1":
            cost = ValueKilometer.objects.all().order_by("-id")[0]
            base = BasePrice.objects.all().order_by("-id")[0]
            service.distance = distance
            service.time = time
            if distance > base.count_after:
                service.value = distance * cost.cost + base.base
            else:
                service.value = base.base

            service.save()
            service_serializer = ServiceSerializer(service, many=False)

        response = {
            "content": service_serializer.data,
            "isOk": True,
            "message": "",
        }
        return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
        response = {
            "content": [],
            "isOk": False,
            "message": str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


def pdfDownload(request):
    with open(
        "/home/habitapp/webapps/seresapp_statics/terminos_y_condiciones.pdf", "rb"
    ) as pdf:
        response = HttpResponse(pdf.read(), content_type="application/pdf")
        response["Content-Disposition"] = "inline;filename=terminos.pdf"
        return response
    pdf.closed


def activate(self, request, uidb64=None, token=None):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        # activate user and login:
        user.is_active = True
        user.save()
        # login(request, user)
        return HttpResponse("Activación valida!")
    else:
        return HttpResponse("Activación inválida!")


"""
actualizacion: 0 -> Todos los datos
actualizacion: 1 -> Foto de perfil
actualizacion: 2 -> Estado
"""


@api_view(["GET"])
def get_bank_list_pse(request):
    try:
        url = (
            os.environ.get("PAYU_TEST_API")
            if os.environ.get("PAYU_ENV") == "Test"
            else os.environ.get("PAYU_PROD_API")
        )
        data = {
            "language": "es",
            "command": "GET_BANKS_LIST",
            "merchant": {
                "apiLogin": os.environ.get("PAYU_API_LOGIN"),
                "apiKey": os.environ.get("PAYU_API_KEY"),
            },
            "test": True if os.environ.get("PAYU_ENV") == "Test" else False,
            "bankListInformation": {"paymentMethod": "PSE", "paymentCountry": "CO"},
        }
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json",
            "Content-Length": "length",
        }

        response_data = requests.post(url, headers=headers, data=json.dumps(data))

        if response_data.status_code == 200:
            # Parse the JSON response
            response_data = response_data.json()

            # Process the response data
            banks = response_data.get("banks", [])

            response = {
                "content": banks,
                "isOk": True,
                "message": "",
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {
                "content": [],
                "isOk": False,
                "message": response_data.text,
            }
            return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {
            "content": [],
            "isOk": False,
            "message": str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


class UsersApi(APIView):
    def get(self, request, format=None):
        try:
            user_extended = UserExtended.objects.filter(user__is_superuser=False)
            user_extended_serializer = UserExtendedSerializer(user_extended, many=True)
            response = {
                "content": user_extended_serializer.data,
                "isOk": True,
                "message": "",
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                "content": [],
                "isOk": False,
                "message": str(e),
            }
            return Response(response, status=status.HTTP_200_OK)

    def put(self, request, id=None, format=None):
        try:
            print(request.data)
            actualizacion = request.data.get("actualizacion")
            user_extended = UserExtended.objects.get(id=id)

            if actualizacion == "0":
                user_extended.user.first_name = request.data.get("nombre")
                user_extended.user.last_name = request.data.get("apellido")
                if request.data.get("fecha_nacimiento"):
                    user_extended.birth_date = request.data.get("fecha_nacimiento")
                user_extended.phone = request.data.get("telefono")
                user_extended.address = request.data.get("address")
                user_extended.document_number = request.data.get("document")
                user_extended.user.save()
            elif actualizacion == "1":
                format, imgstr = request.data.get("foto_perfil").split(";base64,")
                ext = format.split("/")[-1]
                user_extended.photo_profile.save(
                    str(user_extended.id) + "." + ext,
                    ContentFile(base64.b64decode(imgstr)),
                    save=True,
                )
            elif actualizacion == "2":
                user_extended.user.is_active = not user_extended.user.is_active
                user_extended.user.save()
            elif actualizacion == "3":
                estado = request.data.get("estado")
                user_extended.status = estado

            user_extended.save()
            user_extended_serializer = UserExtendedSerializer(user_extended, many=False)
            response = {
                "content": user_extended_serializer.data,
                "isOk": True,
                "message": "Información actualizada correctamente",
            }
            return Response(response, status=status.HTTP_200_OK)

        except UserExtended.DoesNotExist:
            response = {
                "content": [],
                "isOk": False,
                "message": "Usuario no encontrado",
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                "content": [],
                "isOk": False,
                "message": str(e),
            }
            return Response(response, status=status.HTTP_200_OK)


class ServiceAPi(APIView):
    def get(self, request, format=None):
        try:
            services = Service.objects.all().order_by("-date")
            services_serializer = ServiceSerializer(services, many=True)
            response = {
                "content": services_serializer.data,
                "isOk": True,
                "message": "",
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                "content": [],
                "isOk": False,
                "message": str(e),
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            client_id = request.data.get("usuario")
            origin = request.data.get("origen")
            origin_lat = request.data.get("origin_lat")
            origin_lan = request.data.get("origin_lan")
            destiny = request.data.get("destino")
            destiny_lat = request.data.get("destiny_lat")
            destiny_lan = request.data.get("destiny_lan")
            type_service = request.data.get("tipo_servicio")
            disability = request.data.get("discapacidad")
            charge = request.data.get("carga")
            pet = request.data.get("mascota")
            passengers = request.data.get("pasajeros")
            description = request.data.get("descripcion")
            valor = request.data.get("valor")
            fecha_hora_reserva = request.data.get("reserva_fecha_hora")

            reservation_date_time = datetime.strptime(
                fecha_hora_reserva, "%Y-%m-%dT%H:%M:%S.%fZ"
            )

            client = UserExtended.objects.get(id=client_id)

            service = Service.objects.create(
                client=client,
                origin_name=origin,
                origin_lat=origin_lat,
                origin_lan=origin_lan,
                destiny_name=destiny,
                destiny_lat=destiny_lat,
                destiny_lan=destiny_lan,
                type_service=type_service,
                disability=disability,
                charge=charge,
                pet=pet,
                passengers=passengers,
                description=description,
                value=valor,
                date_reservation=reservation_date_time.date(),
                reservation_time=reservation_date_time.time(),
            )

            service_serializers = ServiceSerializer(service, many=False)
            sendNotificationDriver(service_serializers.data, "add")
            response = {
                "content": service_serializers.data,
                "isOk": True,
                "message": "",
            }
            return Response(response, status=status.HTTP_200_OK)

        except UserExtended.DoesNotExist:
            response = {
                "content": [],
                "isOk": False,
                "message": "Cliente no encontrado",
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                "content": [],
                "isOk": False,
                "message": str(e),
            }
            return Response(response, status=status.HTTP_200_OK)


class ValueKilometerApi(APIView):
    def get(self, request, format=None):
        try:
            costs = ValueKilometer.objects.all()
            cost_serializers = ValueKilometerSerializer(costs, many=True)
            response = {
                "content": cost_serializers.data,
                "isOk": True,
                "message": "",
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                "content": [],
                "isOk": False,
                "message": str(e),
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            price = request.data.get("precio")
            cost = ValueKilometer.objects.create(cost=price)
            cost_serializers = ValueKilometerSerializer(cost, many=False)
            response = {
                "content": cost_serializers.data,
                "isOk": True,
                "message": "",
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                "content": [],
                "isOk": False,
                "message": str(e),
            }
            return Response(response, status=status.HTTP_200_OK)


class BasePriceApi(APIView):
    def get(self, request, format=None):
        try:
            prices = BasePrice.objects.all()
            prices_serializers = BasePriceSerializer(prices, many=True)
            response = {
                "content": prices_serializers.data,
                "isOk": True,
                "message": "",
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                "content": [],
                "isOk": False,
                "message": str(e),
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            price = request.data.get("precio")
            count_after = request.data.get("kilometros")
            cost = BasePrice.objects.create(base=price, count_after=count_after)
            cost_serializers = ValueKilometerSerializer(cost, many=False)
            response = {
                "content": cost_serializers.data,
                "isOk": True,
                "message": "",
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                "content": [],
                "isOk": False,
                "message": str(e),
            }
            return Response(response, status=status.HTTP_200_OK)


class CommentApi(APIView):
    def get(self, request, id=None, format=None):
        try:

            comments = Comment.objects.filter(driver__id=id)
            count_comments = len(comments)
            avg_comments_p = 0
            avg_comments_c = 0
            avg_comments_a = 0
            if count_comments != 0:
                sum_comments_p = Comment.objects.filter(driver__id=id).aggregate(
                    Sum("score_personalPresentation")
                )
                avg_comments_p = (
                    sum_comments_p.get("score_personalPresentation__sum")
                    / count_comments
                )
                sum_comments_c = Comment.objects.filter(driver__id=id).aggregate(
                    Sum("score_carCondition")
                )
                avg_comments_c = (
                    sum_comments_c.get("score_carCondition__sum") / count_comments
                )
                sum_comments_a = Comment.objects.filter(driver__id=id).aggregate(
                    Sum("score_attitude")
                )
                avg_comments_a = (
                    sum_comments_a.get("score_attitude__sum") / count_comments
                )
            comments_serializer = CommentSerializer(comments, many=True)
            response = {
                "content": comments_serializer.data,
                "avg_personal_presentation": avg_comments_p,
                "avg_score_carCondition": avg_comments_c,
                "avg_score_attitude": avg_comments_a,
                "isOk": True,
                "message": "",
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                "content": [],
                "isOk": False,
                "message": str(e),
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, id=None, format=None):
        try:
            drive_id = request.data.get("conductor")
            client_id = request.data.get("cliente")
            comment = request.data.get("comentario")
            score_personalPresentation = request.data.get("presentacionPersonal")
            score_carCondition = request.data.get("condicionCarro")
            score_attitude = request.data.get("actitud")

            driver = UserExtended.objects.get(id=drive_id)
            client = UserExtended.objects.get(id=client_id)

            if not Comment.objects.filter(driver__id=drive_id, client__id=id).exists():
                comments = Comment.objects.create(
                    client=client,
                    driver=driver,
                    comment=comment,
                    score_personalPresentation=score_personalPresentation,
                    score_carCondition=score_carCondition,
                    score_attitude=score_attitude,
                )

            comments_serializer = CommentSerializer(comments, many=False)
            response = {
                "content": comments_serializer.data,
                "isOk": True,
                "message": "",
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            response = {
                "content": [],
                "isOk": False,
                "message": "",
            }
            return Response(response, status=status.HTTP_200_OK)


class DriverBalanceApi(APIView):
    def get(self, request, driver_id=None, format=None):
        try:
            driver_balance = DriverBalance.objects.get(driver_id=driver_id)
            driver_balance_detail = DriverBalanceDetail.objects.filter(
                driver_balance__driver_id=driver_id
            )
            driver_balance_serializer = DriverBalanceSerializer(
                driver_balance, many=False
            )
            driver_balance_detail_serializer = DriverBalanceDetailSerializer(
                driver_balance_detail, many=True
            )
            response = {
                "content": {
                    "balance": driver_balance_serializer.data,
                    "details": driver_balance_detail_serializer.data,
                },
                "isOk": True,
                "message": "",
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                "content": [],
                "isOk": False,
                "message": str(e),
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            driver_id = request.data.get("driveId")
            bank = request.data.get("bank")
            amount = request.data.get("amount")

            driver = UserExtended.objects.get(id=driver_id)
            driver_payment = DriverPayment.objects.create(
                amount=amount, driver=driver, status=DriverPayment.created
            )
            tax_amount = amount * 0.19
            amount_with_tax = amount + tax_amount
            reference_code = f"payment_driver_{driver_payment.id}_{datetime.now()}"
            signature = hashlib.md5(
                str(
                    f"{os.environ.get('PAYU_API_KEY')}~{os.environ.get('MERCHAN_ID')}~{reference_code}~{amount_with_tax}~COP"
                ).encode("utf-8")
            )
            session_id = hashlib.md5(
                str(request.session._get_or_create_session_key()).encode("utf-8")
            )

            url = (
                os.environ.get("PAYU_TEST_API")
                if os.environ.get("PAYU_ENV") == "Test"
                else os.environ.get("PAYU_PROD_API")
            )

            data = {
                "language": "es",
                "command": "SUBMIT_TRANSACTION",
                "merchant": {
                    "apiLogin": os.environ.get("PAYU_API_LOGIN"),
                    "apiKey": os.environ.get("PAYU_API_KEY"),
                },
                "transaction": {
                    "order": {
                        "accountId": os.environ.get("PAYU_ACCOUNT_ID"),
                        "referenceCode": reference_code,
                        "description": "Recarga saldo conductor",
                        "language": "es",
                        "signature": signature.hexdigest(),
                        "buyer": {
                            "fullName": f"{driver.user.first_name} {driver.user.last_name}",
                            "emailAddress": driver.user.email,
                            "contactPhone": driver.phone,
                            "dniNumber": driver.document_number,
                            "shippingAddress": {
                                "street1": driver.address,
                                "street2": driver.address,
                                "city": "Valledupar",
                                "state": "Cesar",
                                "country": "CO",
                                "postalCode": "200005",
                                "phone": driver.phone,
                            },
                        },
                        "additionalValues": {
                            "TX_VALUE": {
                                "value": amount_with_tax,
                                "currency": "COP",
                            },
                            "TX_TAX": {"value": tax_amount, "currency": "COP"},
                            "TX_TAX_RETURN_BASE": {"value": amount, "currency": "COP"},
                        },
                        "shippingAddress": {
                            "street1": driver.address,
                            "street2": driver.address,
                            "city": "Valledupar",
                            "state": "Cesar",
                            "country": "CO",
                            "postalCode": "200005",
                            "phone": driver.phone,
                        },
                    },
                    "payer": {
                        "fullName": f"{driver.user.first_name} {driver.user.last_name}",
                        "emailAddress": driver.user.email,
                        "contactPhone": driver.phone,
                        "dniNumber": driver.document_number,
                        "billingAddress": {
                            "street1": driver.address,
                            "street2": driver.address,
                            "city": "Valledupar",
                            "state": "Cesar",
                            "country": "CO",
                            "postalCode": "200005",
                            "phone": driver.phone,
                        },
                    },
                    "extraParameters": {
                        "RESPONSE_URL": "http://www.payu.com/response",
                        "PSE_REFERENCE1": "127.0.0.1",
                        "FINANCIAL_INSTITUTION_CODE": bank.get("pseCode"),
                        "USER_TYPE": "N",
                        "PSE_REFERENCE2": "CC",
                        "PSE_REFERENCE3": driver.document_number,
                    },
                    "type": "AUTHORIZATION_AND_CAPTURE",
                    "paymentMethod": "PSE",
                    "paymentCountry": "CO",
                    "deviceSessionId": session_id.hexdigest(),
                    "ipAddress": get_client_ip(request),
                    "cookie": request.META.get("HTTP_COOKIE"),
                    "userAgent": request.META["HTTP_USER_AGENT"],
                },
                "test": True if os.environ.get("PAYU_ENV") != "Test" else False,
            }

            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
                "Content-Length": "length",
            }

            response_data = requests.post(
                url, headers=headers, data=json.dumps(data, indent=4)
            )
            print(response_data)

            if response_data.status_code == 200:
                # Parse the JSON response
                response_data = response_data.json()
                print(response_data)
                driver_payment.payment_id = response_data.get(
                    "transactionResponse"
                ).get("transactionId")
                driver_payment.status = (
                    response_data.get("transactionResponse").get("state").lower()
                )
                driver_payment.order_id = response_data.get("transactionResponse").get(
                    "orderId"
                )
                driver_payment.pse_url = (
                    response_data.get("transactionResponse")
                    .get("extraParameters")
                    .get("BANK_URL")
                )
                driver_payment.save()

                serializer = DriverPaymentSerializer(driver_payment, many=False)

                response = {
                    "content": serializer.data,
                    "isOk": True,
                    "message": "",
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "content": [],
                    "isOk": False,
                    "message": response_data.text,
                }
                return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            response = {
                "content": [],
                "isOk": False,
                "message": str(e),
            }
            return Response(response, status=status.HTTP_200_OK)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def sendNotificationDriver(data, action):
    registration_ids = []
    data = {key: str(value) for key, value in data.items()}
    message_title = "Nuevo Servicio"
    message_body = "SeresApp, tienes un nuevo servicio"
    tokens = TokenPhoneFCM.objects.filter(
        user__is_driver=True, user__status="Disponible"
    )
    data["action"] = action
    data["type_user"] = "driver"
    for token_fmc in tokens:
        registration_ids.append(token_fmc.toke_phone)
    try:
        message = messaging.MulticastMessage(
            data=data,
            tokens=registration_ids,
            notification=messaging.Notification(title=message_title, body=message_body),
        )
        response = messaging.send_multicast(message)

        print(f" success {response}")
    except Exception as e:
        print(f"error {str(e)}")


def sendNotificationClient(data, id_client, action):
    registration_ids = []
    message_title = "Actualización de servicio"
    message_body = "SeresApp, tu servicio ha cambiado"
    tokens = TokenPhoneFCM.objects.filter(user__id=id_client)
    data = {key: str(value) for key, value in data.items()}
    data["action"] = action
    data["type_user"] = "client"
    for token_fmc in tokens:
        registration_ids.append(token_fmc.toke_phone)
    try:
        message = messaging.MulticastMessage(
            data=data,
            tokens=registration_ids,
            notification=messaging.Notification(title=message_title, body=message_body),
        )
        response = messaging.send_multicast(message)

        print(response)
    except Exception as e:
        print(e)
