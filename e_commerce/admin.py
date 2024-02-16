from django.contrib import admin
from . import models
# Register your models here.



admin.site.register(models.Cart)
admin.site.register(models.Category)
admin.site.register(models.Item)
admin.site.register(models.ItemCart)
admin.site.register(models.ItemOrder)
admin.site.register(models.Wishlist)
admin.site.register(models.Order)