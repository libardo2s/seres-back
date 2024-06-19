from django.contrib import admin
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

# Register your models here.
admin.site.register(UserExtended)
admin.site.register(Service)
admin.site.register(TokenPhoneFCM)
admin.site.register(ValueKilometer)
admin.site.register(Comment)
admin.site.register(BasePrice)
admin.site.register(MessageService)
admin.site.register(DriverBalance)
admin.site.register(DriverBalanceDetail)
admin.site.register(DiscountService)
admin.site.register(DriverPayment)
