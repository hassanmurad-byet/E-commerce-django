from django import forms
from django.shortcuts import get_object_or_404, render,redirect,HttpResponseRedirect
from django.views import View
from django.urls import reverse
from django.http import HttpResponse , JsonResponse
from django.utils import timezone
from datetime import timedelta
from shoppinglyx import settings
from .models import Customer, Product, Cart, OrderPlaced
from django.contrib import messages
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from .forms import AddProductForm,OrderplacedForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView,UpdateView
from django.db.models import Q
from django.db.models import Sum


def custom_login_redirect(request):
  if request.user.is_authenticated:
    if request.user.is_superuser:
      return HttpResponseRedirect(reverse(settings.ADMIN_DASHBOARD_URL)  )
    else:
      return HttpResponseRedirect(reverse(settings.LOGIN_REDIRECT_URL))
  else:
    return redirect(settings.LOGIN_URL)




# def home(request):
#  return render(request, 'app/home.html') 

class ProductView(View):
 def get(self, request):
  totalitem = 0
  product = Product.objects.all()
  AirPods = Product.objects.filter(category='AP')
  Accessories = Product.objects.filter(category= 'AC')
  mobiles = Product.objects.filter(category='M')
  laptops = Product.objects.filter(category='L')
  if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))

  return render(request, 'app/home.html',{'AirPods':AirPods,
    'Accessories':Accessories, 'mobiles': mobiles ,'laptops':laptops,'totalitem':totalitem,'products':product})
  

# product List
def product_list(request):
  product = Product.objects.all()
  return render(request, 'app/Product_list.html', {'products': product})

# Add Product 

class AddProduct(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'app/add_product.html'
    fields = ('title','spec','description','category','brand', 'selling_price','availability','product_image')
    
    def form_valid(self, form):
        prod_obj = form.save(commit=False)
        prod_obj.user =self.request.user
        prod_obj.save()
        return HttpResponseRedirect(reverse('productlist'))

# Update Product
@login_required
def UpdateProduct(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('productlist')  # Redirect to the product detail page
    else:
        form = AddProductForm(instance=product)
    
    return render(request, 'app/add_product.html', {'form': form})


# delete product
# def deleteproduct(request,del_id):
#     product = Product.objects.get(pk=del_id).delete()
#     messages.success(request, 'Congratulations..! Registration Successful')
#     return render(request, 'app/dashboard.html')
@login_required
def deleteproduct(request, del_id):
    product = get_object_or_404(Product, pk=del_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        # return redirect('productlist') 
    return render(request, 'app/product_del.html', {'product': product})


# Customer List 
@login_required
def Customer_list(request):
  customer = Customer.objects.all()
  return render(request, 'app/customer_list.html', {'customers': customer})


@login_required
def user_list(request):
  user = User.objects.all()
  return render(request, 'app/user_list.html', {'users': user})


@login_required
def Order_list(request):
  order = OrderPlaced.objects.all()
  return render(request, 'app/Order_list.html', {'orders': order})



@login_required
def updaeOrderPlace(request, pk):
    order = get_object_or_404(OrderPlaced, pk=pk)
    
    if request.method == 'POST':
        form = OrderplacedForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('orderlist')  # Redirect to the product detail page
    else:
        form = OrderplacedForm(instance=order)
    
    return render(request, 'app/orderplaced.html', {'form': form})


def Orderproduct_detail(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    return render(request, 'app/Orderproduct_detail.html', {'products': product })






def Ordercustomer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)


     # Fetching all orders of the customer
    orders = OrderPlaced.objects.filter(customer=customer)

    total_price = 0
    order_list = []

    # Calculating total price and preparing order list
    for order in orders:
        order_total = order.quantity * order.product.selling_price
        total_price += order_total
        order_list.append({
            'product': order.product.title,
            'cate': order.product.category,
            'brand': order.product.brand,

            'img': order.product.product_image,

            'quantity': order.quantity,
            'status': order.status,

            'unit_price': order.product.selling_price,
            'order_total': order_total
        })
    return render(request, 'app/ordercust_info.html', {'customers': customer, 'order_list': order_list,'total_price': total_price })













# srearch bar ........
def product_search(request):
  query = request.GET.get('q')
  if query:
    products = Product.objects.filter(title__icontains=query)
  else:
    products = Product.objects.all()
  return render(request, 'app/home.html', {'products': products, 'query': query})



class ProductDetailView(View):
 def get(self, request, pk):
  totalitem = 0
  product = Product.objects.get(pk=pk)
  item_already_in_cart = False
  if request.user.is_authenticated:
    totalitem =len(Cart.objects.filter(user=request.user))
    item_already_in_cart =Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
  return render(request, 'app/productdetail.html', {'product':product, 'item_already_in_cart':item_already_in_cart,'totalitem':totalitem})
 
@login_required
def add_to_cart(request):
 user = request.user
 product_id = request.GET.get('prod_id')
 product = Product.objects.get(id=product_id)
 Cart(user=user, product=product).save()
 return redirect('/cart')

@login_required
def show_cart(request):
 totalitem =0 
 if request.user.is_authenticated:
  totalitem =len(Cart.objects.filter(user=request.user))
  user = request.user
  cart =Cart.objects.filter(user=user)
  amount = 0.0
  shipping_amount = 70.0
  totalamount = 0.0
  cart_product = [ p for p in Cart.objects.all() if p.user == user ]
  if cart_product:
    for p in cart_product:
     tempamount = (p.quantity * p.product.selling_price)
     amount += tempamount
    totalamount = amount + shipping_amount
    return render(request, 'app/addtocart.html', {'carts':cart, 'totalamount':totalamount, 'amount':amount,'totalitem':totalitem})
  else:
     return render(request, 'app/emptycart.html')
 

def plus_cart(request):
  if request.method == "GET":
   prod_id = request.GET['prod_id']
   c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
   c.quantity+=1
   c.save()
   amount = 0.0
   shipping_amount = 70.0
   totalamount =0.0
   cart_product = [ p for p in Cart.objects.all() if p.user ==request.user ]
   for p in cart_product:
    tempamount = (p.quantity * p.product.selling_price)
    amount += tempamount
    
 
    
    
    data = {
     'quantity': c.quantity,
     'amount' : amount,
     'totalamount': amount + shipping_amount
     }
    return JsonResponse(data)
   

def minus_cart(request):
  if request.method == "GET":
   prod_id = request.GET['prod_id']
   c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
   c.quantity-=1
   c.save()
   amount = 0.0
   shipping_amount = 70.0
   cart_product = [ p for p in Cart.objects.all() if p.user ==request.user ]
   for p in cart_product:
    tempamount = (p.quantity * p.product.selling_price)
    amount += tempamount
    
    
    data = {
     'quantity': c.quantity,
     'amount' : amount,
     'totalamount': amount + shipping_amount
     }
    return JsonResponse(data)
   
def remove_cart(request):
  if request.method == "GET":
   prod_id = request.GET['prod_id']
   c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
   c.delete()
   amount = 0.0
   shipping_amount = 70.0
   cart_product = [ p for p in Cart.objects.all() if p.user ==request.user ]
   for p in cart_product:
    tempamount = (p.quantity * p.product.selling_price)
    amount += tempamount
    
    data = {
     'amount' : amount,
     'totalamount': amount + shipping_amount
     }
    return JsonResponse(data)


@login_required
def buy_now(request):
 return render(request, 'app/buynow.html')

@login_required
def profile(request):
 return render(request, 'app/profile.html')

@login_required
def address(request):
 add = Customer.objects.filter(user=request.user)
 return render(request, 'app/address.html', {'add':add, 'active':'btn-primary'})

@login_required
def orders(request):
 op = OrderPlaced.objects.filter(user=request.user)
 return render(request, 'app/orders.html',{'order_placed':op})

# def change_password(request):
#  return render(request, 'app/changepassword.html')
 

def mobile(request, data=None):
 if data == None:
  mobiles = Product.objects.filter(category='M')
 elif data == 'Redmi' or data == 'Samsung':
  mobiles = Product.objects.filter(category = 'M').filter(brand=data)
 elif data =='below':
  mobiles = Product.objects.filter(category = 'M').filter(discounted_price__lt=10000)
 elif data =='above':
  mobiles = Product.objects.filter(category = 'M').filter(discounted_price__gt=10000)

 return render(request, 'app/mobile.html', {'mobiles':mobiles})



# laptop----------------:

def Laptop(request, data=None):
 if data == None:
  laptop = Product.objects.filter(category='L')
 elif data == 'Apple' or data == 'HP' or data == 'Dell':
  laptop = Product.objects.filter(category = 'L').filter(brand=data)
 return render(request, 'app/laptop.html', {'laptop':laptop})



# laptop----------):

def airpod(request, data=None):
 if data == None:
  airpod = Product.objects.filter(category='AP')
  return render(request, 'app/airpods.html', {'airpod':airpod})

#  return render(request, 'app/customerregistration.html')
def acces(request, data=None):
 if data == None:
  acce = Product.objects.filter(category='AC')
  return render(request, 'app/access.html', {'acce':acce})






class CustomerRegistrationView(View):
  def get(self, request):
    form = CustomerRegistrationForm()
    return render(request, 'app/customerregistration.html', {'form': form})
  
  def post(self, request):
    form = CustomerRegistrationForm(request.POST)
    if form.is_valid():
      messages.success(request, 'Congratulations..! Registration Successful')
      form.save()
    return render(request, 'app/customerregistration.html', {'form': form})


class UserLogoutView(LoginRequiredMixin,View):
 def get(self,request):
  logout(request)
  return redirect('login') 
 

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
 def get(self, request):
  form = CustomerProfileForm
  return render(request,'app/profile.html', {'form':form, 'active':'btn-primary'})
 
 def post(self, request):
  form = CustomerProfileForm(request.POST)
  if form.is_valid():
   usr = request.user
   name = form.cleaned_data['name']
   locality = form.cleaned_data['locality']
   city = form.cleaned_data['city']
   state = form.cleaned_data['state']
   zipcode = form.cleaned_data['zipcode']
   reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
   reg.save()
   messages.success(request, 'Congratulations!! Profile Update Successfully')
   return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})
  


#  admin login -----------------------------
@login_required
def dashboard(request):
  total_products = Product.objects.count()
  customer = Customer.objects.all()
  order = OrderPlaced.objects.all()
  total_order = OrderPlaced.objects.count()
  total_customer = Customer.objects.count()

  shipping_complete_orders = OrderPlaced.objects.filter(status='Delivery completed')
    
 # Count the number of shipping complete orders
  shipping_complete = shipping_complete_orders.count()

  # Calculate total revenue
  total_revenue = sum(order.product.selling_price * order.quantity for order in shipping_complete_orders)
    


   # Get the current datetime
  current_datetime = timezone.now()
    # Calculate datetime 24 hours ago
  datetime_24_hours_ago = current_datetime - timezone.timedelta(hours=24)

    # Filter OrderPlaced objects with "Shipping Complete" status within the last 24 hours
  todays_shipping_complete_orders = OrderPlaced.objects.filter(status='Delivery completed', ordered_date__gte=datetime_24_hours_ago) 
    # Calculate total price of products marked as "Shipping Complete" today
  total_price_today = sum(order.product.selling_price * order.quantity for order in todays_shipping_complete_orders)
    

  return render(request, 'app/dashboard.html',{'customers': customer,'orders':order,'total_product':total_products,'total_order':total_order, 
    'total_customer':total_customer,'shipping_complete':shipping_complete,'total_revenue':total_revenue,'total_price_today':total_price_today,'todays_shipping_complete_orders':todays_shipping_complete_orders})






@login_required
def shipping_complete(request):
  shipping_complete_orders = OrderPlaced.objects.filter(status='Delivery completed')

  return render(request, 'app/shipping_done.html', {'shipping_complete_orders':shipping_complete_orders})
 




# checkout-------------------
@login_required
def checkout(request):
 user = request.user
 add = Customer.objects.filter(user=user)
 cart_item = Cart.objects.filter(user=user )
 amount = 0.0
 shipping_amount = 70.0
 totalamount = 0.0
 cart_product = [ p for p in Cart.objects.all() if p.user ==request.user ]
 if cart_product:
  for p in cart_product:
    tempamount = (p.quantity * p.product.selling_price)
    amount += tempamount
  totalamount= amount+ shipping_amount
  return render(request, 'app/checkout.html',{'add':add, 'totalamount':totalamount,'cart_items':cart_item})

@login_required
def payment_done(request):
  user = request.user
  custid = request.GET.get('custid')
  customer = Customer.objects.get(id= custid)
  cart = Cart.objects.filter(user=user)
  for c in cart:
    OrderPlaced(user=user, customer=customer, product=c.product, quantity = c.quantity).save()
    c.delete()
  return redirect("orders")





@login_required
def order_report(request):
    # Fetching today's orders within the last 24 hours
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    today_orders = OrderPlaced.objects.filter(ordered_date__range=(today_start, today_end))

    # Fetching monthly orders
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_end = today_end
    monthly_orders = OrderPlaced.objects.filter(ordered_date__range=(month_start, month_end))



    shipping_complete_orders = OrderPlaced.objects.filter(status='Delivery completed')
 # Count the number of shipping complete orders
 

    # # Aggregate total cost for all products
    total_cost_all_products = shipping_complete_orders.aggregate(total_cost=Sum('product__selling_price'))


      # Get the current datetime
    current_datetime = timezone.now()
    # Calculate datetime 24 hours ago
    datetime_24_hours_ago = current_datetime - timezone.timedelta(hours=24)

    # Filter OrderPlaced objects with "Shipping Complete" status within the last 24 hours
    todays_shipping_complete_orders = OrderPlaced.objects.filter(status='Delivery completed', ordered_date__gte=datetime_24_hours_ago) 
    # Calculate total price of products marked as "Shipping Complete" today
    total_price_today = sum(order.product.selling_price * order.quantity for order in todays_shipping_complete_orders)
    
    
    context = {
        'today_orders': today_orders,
        'monthly_orders': monthly_orders,
        'shipping_complete_orders':shipping_complete_orders,
        'total_cost_all_products':total_cost_all_products,
        'todays_shipping_complete_orders':todays_shipping_complete_orders,
        'total_price_today':total_price_today

    }
    return render(request, 'app/report.html', context)





def Bkash(request):
 user = request.user
 add = Customer.objects.filter(user=user)
 cart_item = Cart.objects.filter(user=user )
 amount = 0.0
 shipping_amount = 70.0
 totalamount = 0.0
 cart_product = [ p for p in Cart.objects.all() if p.user ==request.user ]
 if cart_product:
  for p in cart_product:
    tempamount = (p.quantity * p.product.selling_price)
    amount += tempamount
  totalamount= amount+ shipping_amount
  return render(request, 'app/index.html',{'add':add, 'totalamount':totalamount,'cart_items':cart_item})