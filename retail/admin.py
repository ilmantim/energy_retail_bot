from django.contrib import admin

from retail.models import Mro, Customer, Bill, Address


# Register your models here.
@admin.register(Mro)
class MroAdmin(admin.ModelAdmin):
    list_filter = ('name', )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('chat_id', )


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('value', )