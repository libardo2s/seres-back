# -*- coding: utf-8 -*-
import os
import base64
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
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# DJANGO REST FRAMEWORK
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
# MODELS
from .models import UserExtended, Service, TokenPhoneFCM, ValueKilometer, Comment, BasePrice, MessageService
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


@api_view(['POST'])
def loginAdmin(request):
    try:
        if request.method == 'POST':
            username = request.data.get('usuario')
            password = request.data.get('contrasena')

            authentication = authenticate(username=username, password=password)

            if authentication is not None:
                if authentication.is_active:
                    user_extended = UserExtended.objects.get(
                        user__id=authentication.id)
                    user_extended_serializer = UserExtendedSerializer(
                        user_extended, many=False)
                    response = {
                        'content': user_extended_serializer.data,
                        'isOk': True,
                        'message': '',
                    }
                else:
                    response = {
                        'content': [],
                        'isOk': False,
                        'message': 'El usuario no se encuentra activo',
                    }
            else:
                response = {
                    'content': [],
                    'isOk': False,
                    'message': 'El usuario no se encuentra registrado',
                }
        return Response(response, status=status.HTTP_200_OK)
    except UserExtended.DoesNotExist:
        response = {
            'content': [],
            'isOk': False,
            'message': 'El usuario no se encuentra registrado',
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {
            'content': [],
            'isOk': False,
            'message': str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


# Create your views here.
@api_view(['POST'])
def login(request):
    try:
        if request.method == 'POST':
            phone = request.data.get('telefono')

            user_extended = UserExtended.objects.get(phone=phone)

            if user_extended.is_active:
                    user_extended_serializer = UserExtendedSerializer(user_extended, many=False)
                    response = {
                        'content': user_extended_serializer.data,
                        'isOk': True,
                        'message': '',
                    }
            else:
                response = {
                    'content': [],
                    'isOk': False,
                    'message': 'El usuario no se encuentra activo',
                }
        return Response(response, status=status.HTTP_200_OK)
    except UserExtended.DoesNotExist:
        response = {
            'content': [],
            'isOk': False,
            'message': 'El usuario no se encuentra registrado',
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {
            'content': [],
            'isOk': False,
            'message': str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request):
    try:
        if request.method == 'POST':
            email = request.data.get('correo')
            phone = request.data.get('telefono')
            name = request.data.get('nombres')
            last_name = request.data.get('apellidos')
            is_driver = request.data.get('conductor')
            license_plate = request.data.get('placa')

            new_user = User.objects.create_user(
                username=email,
                password=phone,
                email=email,
                first_name=name,
                last_name=last_name
            )
            new_user.is_active = True
            new_user.is_superuser = False
            new_user.save()

            user_extended = UserExtended.objects.create(
                phone=phone,
                is_driver=is_driver,
                user=new_user,
                license_plate=license_plate
            )
            user_extended_serializer = UserExtendedSerializer(  user_extended, many=False)

            response = {
                'content': user_extended_serializer.data,
                'isOk': True,
                'message': 'Usuario creado exitosamente',
            }
            return Response(response, status=status.HTTP_200_OK)
                
    except Exception as e:
        response = {
            'content': [],
            'isOk': False,
            'message': str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
def getServiceClient(request, id_client=None):
    try:
        services_client = Service.objects.filter(client__id=id_client).order_by('-date')
        services_client_serializer = ServiceSerializer(
            services_client, many=True)
        response = {
            'content': services_client_serializer.data,
            'isOk': True,
            'message': '',
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {
            'content': [],
            'isOk': False,
            'message': str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
def getServiceDriver(request, id_driver=None):
    try:
        services_driver = Service.objects.filter(driver__id=id_driver).order_by('-date')
        services_driver_serializer = ServiceSerializer(
            services_driver, many=True)
        response = {
            'content': services_driver_serializer.data,
            'isOk': True,
            'message': '',
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {
            'content': [],
            'isOk': False,
            'message': str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
def tokerUserFmc(request):
    try:
        if request.method == 'POST':
            user_id = request.data.get('user_id')
            token_fmc = request.data.get('token')

            user = UserExtended.objects.get(id=user_id)
            if TokenPhoneFCM.objects.filter(user=user).exists():
                token = TokenPhoneFCM.objects.get(user=user)
                token.toke_phone = token_fmc
                token.save()
            else:
                TokenPhoneFCM.objects.create(user=user, toke_phone=token_fmc)

            response = {
                'content': [],
                'isOk': True,
                'message': '',
            }
            return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
        response = {
            'content': [],
            'isOk': False,
            'message': str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def deleteTokenFmc(request, id=None):
    try:
        if request.method == 'DELETE':
            user = UserExtended.objects.get(id=id)
            token = TokenPhoneFCM.objects.filter(user=user)
            token.delete()

            response = {
                'content': [],
                'isOk': True,
                'message': '',
            }
            return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
        response = {
            'content': [],
            'isOk': False,
            'message': str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(['GET'])
def getServiceWithoutDriver(request):
    try:
        services = Service.objects.filter(state="servicio creado").order_by('-date')
        print(services)
        services_serializer = ServiceSerializer(services, many=True)
        response = {
            'content': services_serializer.data,
            'isOk': True,
            'message': '',
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {
            'content': [],
            'isOk': False,
            'message': str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(['PUT'])
def updateServiceDriver(request, id=None):
    try:
        driver_id = request.data.get('conductor')
        state = request.data.get('estado')

        driver = UserExtended.objects.get(id=driver_id)
        service = Service.objects.get(id=id)

        if service.driver is None:
            service.driver = driver
            service.state = state
            service.save()
            services_serializer = ServiceSerializer(service, many=False)
            response = {
                'content': services_serializer.data,
                'isOk': True,
                'message': '',
            }
            sendNotificationClient(services_serializer.data, service.client.id, 'update')
            return Response(response, status=status.HTTP_200_OK)
        elif service.driver == driver:
            service.state = state
            service.save()
            services_serializer = ServiceSerializer(service, many=False)
            response = {
                'content': services_serializer.data,
                'isOk': True,
                'message': '',
            } 
            if state == 'Servicio terminado':
               sendNotificationClient(services_serializer.data, service.client.id, 'finished')
            elif state == 'Servicio cancelado':
                 sendNotificationClient(services_serializer.data, service.client.id, 'canceled')
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {
                'content': [],
                'isOk': False,
                'message': 'El servicio ya tiene un conductor asignado',
            }   
            return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        response = {
            'content': [],
            'isOk': False,
            'message': str(e),
        }   
        return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
def sendMessage(request):
    try:
        service_id = request.data.get('servicio')
        message = request.data.get('message')

        service = Service.objects.get(id=service_id)

        message_servicio = MessageService.objects.create(
            service=service,
            message=message
        )

        message_servicio_serializer = MessageSerializer(message_servicio, many=False)
        sendNotificationClient(message_servicio_serializer.data, service.client.id, 'add_message')

        response = {
            'content': message_servicio_serializer.data,
            'isOk': True,
            'message': '',
        }
        return Response(response, status=status.HTTP_200_OK)        


    except Exception as e:
        response = {
            'content': [],
            'isOk': False,
            'message': str(e),
        }
        return Response(response, status=status.HTTP_200_OK)


'''
actualizacion: 0 -> cancelar servicio
actualizacion: 1 -> actualizar, tiempo y distancia
'''
@api_view(['PUT'])
def updateServiceClient(request, id=None):
    try:
        #client_id = request.data.get('cliente')
        state = request.data.get('estado')
        time = request.data.get('tiempo')
        distance = request.data.get('distancia')
        cancel_reason = request.data.get('motivo')
        update = request.data.get('actualizacion')

        #client = UserExtended.objects.get(id=client_id)
        service = Service.objects.get(id=id)
        cost = ValueKilometer.objects.all().order_by('-id')[0]
        base = BasePrice.objects.all().order_by('-id')[0]
 
        if update == "0":
            service.state = state
            service.cancel_reason = cancel_reason
            service.save()
            service_serializer = ServiceSerializer(service, many=False)
            sendNotificationDriver(service_serializer.data, "delete")
        elif update == "1":
            service.distance = distance
            service.time = time
            if distance > base.count_after:
                service.value = distance*cost.cost+base.base
            else:
                service.value = base.base

            service.save()
            service_serializer = ServiceSerializer(service, many=False)
        
        response = {
            'content': service_serializer.data,
            'isOk': True,
            'message': '',
        }
        return Response(response, status=status.HTTP_200_OK)
        
    except Exception as e:
        response = {
            'content': [],
            'isOk': False,
            'message': str(e),
        }   
        return Response(response, status=status.HTTP_200_OK)


def pdfDownload(request):
    with open('/home/habitapp/webapps/seresapp_statics/terminos_y_condiciones.pdf', 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=terminos.pdf'
        return response
    pdf.closed


def activate(self, request, uidb64=None, token=None):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        # activate user and login:
        user.is_active = True
        user.save()
        #login(request, user)
        return HttpResponse('Activación valida!')
    else:
        return HttpResponse('Activación inválida!')


'''
actualizacion: 0 -> Todos los datos
actualizacion: 1 -> Foto de perfil
actualizacion: 2 -> Estado
'''
class UsersApi(APIView):
    def get(self, request, format=None):
        try:
            user_extended = UserExtended.objects.filter(
                user__is_superuser=False)
            user_extended_serializer = UserExtendedSerializer(
                user_extended, many=True)
            response = {
                'content': user_extended_serializer.data,
                'isOk': True,
                'message': '',
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                'content': [],
                'isOk': False,
                'message': str(e),
            }
            return Response(response, status=status.HTTP_200_OK)

    def put(self, request, id=None, format=None):
        try:
            actualizacion = request.data.get('actualizacion')
            user_extended = UserExtended.objects.get(id=id)

            if actualizacion == "0":
                user_extended.user.first_name = request.data.get('nombre')
                user_extended.user.last_name = request.data.get('apellido')
                user_extended.user.save()
                user_extended.birth_date = request.data.get('fecha_nacimiento')
                user_extended.phone = request.data.get('telefono')
            elif actualizacion == "1":
                format, imgstr = request.data.get(
                    'foto_perfil').split(';base64,')
                ext = format.split('/')[-1]
                user_extended.photo_profile.save(
                    str(user_extended.id)+'.'+ext, ContentFile(base64.b64decode(imgstr)), save=True)
            elif actualizacion == "2":
                user_extended.user.is_active = not user_extended.user.is_active
                user_extended.user.save()

            user_extended.save()
            user_extended_serializer = UserExtendedSerializer(
                user_extended, many=False)
            response = {
                'content': user_extended_serializer.data,
                'isOk': True,
                'message': 'Información actualizada correctamente',
            }
            return Response(response, status=status.HTTP_200_OK)

        except UserExtended.DoesNotExist:
            response = {
                'content': [],
                'isOk': False,
                'message': 'Usuario no encontrado',
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                'content': [],
                'isOk': False,
                'message': str(e),
            }
            return Response(response, status=status.HTTP_200_OK)


class ServiceAPi(APIView):
    def get(self, request, format=None):
        try:
            services = Service.objects.all().order_by('-date')
            services_serializer = ServiceSerializer(services, many=True)
            response = {
                'content': services_serializer.data,
                'isOk': True,
                'message': '',
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                'content': [],
                'isOk': False,
                'message': str(e),
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            client_id = request.data.get('usuario')
            origin = request.data.get('origen')
            origin_lat = request.data.get('origin_lat')
            origin_lan = request.data.get('origin_lan')
            destiny = request.data.get('destino')
            destiny_lat = request.data.get('destiny_lat')
            destiny_lan = request.data.get('destiny_lan')
            type_service = request.data.get('tipo_servicio')
            disability = request.data.get('discapacidad')
            charge = request.data.get('carga')
            pet = request.data.get('mascota')
            passengers = request.data.get('pasajeros')
            description = request.data.get('descripcion')

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
                description=description
            )

            service_serializers = ServiceSerializer(service, many=False)
            sendNotificationDriver(service_serializers.data, 'add')
            response = {
                'content': service_serializers.data,
                'isOk': True,
                'message': '',
            }
            return Response(response, status=status.HTTP_200_OK)

        except UserExtended.DoesNotExist:
            response = {
                'content': [],
                'isOk': False,
                'message': 'Cliente no encontrado',
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                'content': [],
                'isOk': False,
                'message': str(e),
            }
            return Response(response, status=status.HTTP_200_OK)


class ValueKilometerApi(APIView):
    def get(self, request, format=None):
        try:
            costs = ValueKilometer.objects.all()
            cost_serializers = ValueKilometerSerializer(costs, many=True)
            response = {
                'content': cost_serializers.data,
                'isOk': True,
                'message': '',
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                'content': [],
                'isOk': False,
                'message': str(e),
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            price = request.data.get('precio')
            cost = ValueKilometer.objects.create(cost=price)
            cost_serializers = ValueKilometerSerializer(cost, many=False)
            response = {
                'content': cost_serializers.data,
                'isOk': True,
                'message': '',
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                'content': [],
                'isOk': False,
                'message': str(e),
            }
            return Response(response, status=status.HTTP_200_OK)       


class BasePriceApi(APIView):
    def get(self, request, format=None):
        try:
            prices = BasePrice.objects.all()
            prices_serializers = BasePriceSerializer(prices, many=True)
            response = {
                'content': prices_serializers.data,
                'isOk': True,
                'message': '',
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                'content': [],
                'isOk': False,
                'message': str(e),
            }
            return Response(response, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            price = request.data.get('precio')
            count_after = request.data.get('kilometros')
            cost = BasePrice.objects.create(base=price, count_after=count_after)
            cost_serializers = ValueKilometerSerializer(cost, many=False)
            response = {
                'content': cost_serializers.data,
                'isOk': True,
                'message': '',
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                'content': [],
                'isOk': False,
                'message': str(e),
            }
            return Response(response, status=status.HTTP_200_OK)


class CommentApi(APIView):
    def get(self, request, id=None,format=None):
        try:
            
            comments = Comment.objects.filter(driver__id=id)
            count_comments = len(comments)
            avg_comments_p = 0
            avg_comments_c = 0
            avg_comments_a = 0
            if count_comments != 0:
                sum_comments_p = Comment.objects.filter(driver__id=id).aggregate(Sum('score_personalPresentation'))
                avg_comments_p = sum_comments_p.get('score_personalPresentation__sum')/count_comments
                sum_comments_c = Comment.objects.filter(driver__id=id).aggregate(Sum('score_carCondition'))
                avg_comments_c = sum_comments_c.get('score_carCondition__sum')/count_comments
                sum_comments_a = Comment.objects.filter(driver__id=id).aggregate(Sum('score_attitude'))
                avg_comments_a = sum_comments_a.get('score_attitude__sum')/count_comments
            comments_serializer = CommentSerializer(comments, many=True)
            response = {
                'content': comments_serializer.data,
                'avg_personal_presentation': avg_comments_p,
                'avg_score_carCondition': avg_comments_c,
                'avg_score_attitude': avg_comments_a,
                'isOk': True,
                'message': '',
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                'content': [],
                'isOk': False,
                'message': str(e),
            }
            return Response(response, status=status.HTTP_200_OK)
    
    def post(self, request, id=None,format=None):
        try:
            drive_id = request.data.get('conductor')
            client_id = request.data.get('cliente')
            comment = request.data.get('comentario')
            score_personalPresentation = request.data.get('presentacionPersonal')
            score_carCondition = request.data.get('condicionCarro')
            score_attitude = request.data.get('actitud')

            driver = UserExtended.objects.get(id=drive_id)
            client = UserExtended.objects.get(id=client_id)

            if not Comment.objects.filter(driver__id=drive_id, client__id=id).exists():
                comments = Comment.objects.create(client=client, driver=driver, comment=comment, 
                    score_personalPresentation=score_personalPresentation, score_carCondition=score_carCondition,
                    score_attitude=score_attitude)
            
            comments_serializer = CommentSerializer(comments, many=False)
            response = {
                'content': comments_serializer.data,
                'isOk': True,
                'message': '',
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            response = {
                'content': [],
                'isOk': False,
                'message': '',
            }
            return Response(response, status=status.HTTP_200_OK)



def sendNotificationDriver(data, action):
    registration_ids = []
    data_message = {
        'data': data,
        'action': action,
        'type_user': 'driver'
    }
    message_title = "Nuevo Servicio"
    message_body = "SeresApp, tienes un nuevo servicio"
    tokens = TokenPhoneFCM.objects.filter(user__is_driver=True)
    for token_fmc in tokens:
        registration_ids.append(token_fmc.toke_phone)

    push_service = FCMNotification(
        api_key="AAAACLbce_k:APA91bHj61GTr9duB6hW3QR9EwgRgjBOsgukOO7shDAf1Z_ZDxt1SMuYDOamWq1Ma_p2pT7ONCQ7aoAphA_T16e_x_wW0L-i6XveZNtqlEFek8UVhX2vFqt1xNo81IhVm-Uoho-mPP7G")
    try:
        result = push_service.notify_multiple_devices(
            registration_ids=registration_ids, message_title=message_title, message_body=message_body, data_message=data_message)
        print(result)
    except Exception as e:
        print(e)


def sendNotificationClient(data, id_client, action):
    registration_ids = []
    message_title = "Actualización de servicio"
    message_body = "SeresApp, tu servicio ha cambiado"
    tokens = TokenPhoneFCM.objects.filter(user__id=id_client)
    data_message = {
        'data': data,
        'action': action,
        'type_user': 'client'
    }
    for token_fmc in tokens:
        registration_ids.append(token_fmc.toke_phone)

    push_service = FCMNotification(
        api_key="AAAACLbce_k:APA91bHj61GTr9duB6hW3QR9EwgRgjBOsgukOO7shDAf1Z_ZDxt1SMuYDOamWq1Ma_p2pT7ONCQ7aoAphA_T16e_x_wW0L-i6XveZNtqlEFek8UVhX2vFqt1xNo81IhVm-Uoho-mPP7G")
    try:
        result = push_service.notify_multiple_devices(
            registration_ids=registration_ids, message_title=message_title, message_body=message_body, data_message=data_message)
        print(result)
    except Exception as e:
        print(e)
