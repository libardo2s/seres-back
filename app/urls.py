from django.urls import path
from .views import login, register, loginAdmin, pdfDownload, tokerUserFmc, sendMessage, getServiceWithoutDriver, updateServiceDriver, deleteTokenFmc, UsersApi, ServiceAPi, getServiceClient, getServiceDriver, ValueKilometerApi, updateServiceClient, CommentApi, BasePriceApi

urlpatterns = [
    path('login/', login),
    path('login-admin/', loginAdmin),
    path('register/', register),
    path('users/', UsersApi.as_view()),
    path('users/<int:id>/', UsersApi.as_view()),
    path('service/', ServiceAPi.as_view()),
    path('service/available/', getServiceWithoutDriver),
    path('service/client/<int:id_client>/', getServiceClient),
    path('service/driver/<int:id_driver>/', getServiceDriver),
    path('service/update/driver/<int:id>/', updateServiceDriver),
    path('service/update/client/<int:id>/', updateServiceClient),
    path('cost/kilometer/', ValueKilometerApi.as_view()),
    path('flag/price/', BasePriceApi.as_view()),
    path('comments/driver/', CommentApi.as_view()),
    path('comments/driver/<int:id>/', CommentApi.as_view()),
    path('token/fmc/', tokerUserFmc),
    path('token/fmc/delete/<int:id>/', deleteTokenFmc),
    path('terminos/', pdfDownload),
    path('messages/', sendMessage),
]
