
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import(Customer, Product,Cart,OrderPlaced)



@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id','user','name','locality', 'city','zipcode','state']



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','title','selling_price','description','spec', 'brand', 'category','availability','product_image']




@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id','user','product','quantity']



@admin.register(OrderPlaced)
class OrderPlacedAdmin(admin.ModelAdmin):
    list_display = ['id','user','customer','product' ,'quantity','ordered_date','status']
    # readonly_fields = ('customerinfo',)


# def customerinfo(self, obj):
#     link = reverse(f"admin:app_customer_change", args=[obj.customer.pk])
#     return format_html('<a href="{}"> {} </a>', link, obj.customer.name)
# customer_info.short_description = "Customer"



MIDDLEWARE = [

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'app.middleware.custom_login_redirect',

]