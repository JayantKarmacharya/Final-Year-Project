import code

from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect, reverse
from django.views.generic import View , CreateView
# from OrderApp.forms import CouponForm, RefundForm
from Product.models import Category, Product, Images
from django.contrib import messages
from OrderApp.models import ShopCart, ShopingCartForm, OderForm, Order, OderProduct, CheckoutForm
from EcomApp.models import Setting, ContactMessage, ContactForm
from UserApp.models import UserProfile
# from OrderApp.forms import CheckoutForm
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.urls import reverse_lazy, reverse

import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.


@login_required(login_url='/user/login')
def Add_to_Shoping_cart(request, id):
    url = request.META.get('HTTP_REFERER')
    current_user = request.user
    checking = ShopCart.objects.filter(
        product_id=id, user_id=current_user.id)
    if checking:
        control = 1
    else:
        control = 0

    if request.method == "POST":
        form = ShopingCartForm(request.POST)
        if form.is_valid():
            if control == 1:
                data = ShopCart.objects.filter(
                    product_id=id, user_id=current_user.id)
                data.quantity += form.cleaned_data['quantity']
                data.save()
            else:
                data = ShopCart()
                data.user_id = current_user.id
                data.product_id = id
                data.quantity = form.cleaned_data['quantity']
                data.save()
        messages.success(request, 'Your Product  has been added')
        return HttpResponseRedirect(url)
    else:
        if control == 1:
            data = ShopCart.objects.filter(
                product_id=id, user_id=current_user.id)
            data.quantity += 1
            data.save()
        else:
            data = ShopCart()
            data.user_id = current_user.id
            data.product_id = id
            data.quantity = 1
            data.save()
        messages.success(request, 'Your  product has been added')
        return HttpResponseRedirect(url)


def cart_detials(request):
    current_user = request.user
    category = Category.objects.all()
    setting = Setting.objects.get(id=1)
    cart_product = ShopCart.objects.filter(user_id=current_user.id)
    total_amount = 0
    for p in cart_product:
        total_amount += p.product.new_price*p.quantity

    context = {
        'category': category,
        'setting': setting,
        'cart_product': cart_product,
        'total_amount': total_amount,

    }
    return render(request, 'cart_details.html', context)


def cart_delete(request, id):
    url = request.META.get('HTTP_REFERER')
    current_user = request.user
    cart_product = ShopCart.objects.filter(id=id, user_id=current_user.id)
    cart_product.delete()
    messages.warning(request, 'Your product has been deleted.')
    return HttpResponseRedirect(url)


@login_required(login_url='/user/login')
def OrderCart(request):
    current_user = request.user
    shoping_cart = ShopCart.objects.filter(user_id=current_user.id)
    totalamount = 0
    for rs in shoping_cart:
        totalamount += rs.quantity*rs.product.new_price
    if request.method == "POST":
        form = OderForm(request.POST, request.FILES)
        if form.is_valid():
            dat = Order()
            # get product quantity from form
            dat.first_name = form.cleaned_data['first_name']
            dat.last_name = form.cleaned_data['last_name']
            dat.address = form.cleaned_data['address']
            dat.city = form.cleaned_data['city']
            dat.phone = form.cleaned_data['phone']
            dat.country = form.cleaned_data['country']
            dat.transaction_id = form.cleaned_data['transaction_id']
            dat.transaction_image = form.cleaned_data['transaction_image']
            dat.user_id = current_user.id
            dat.total = totalamount
            dat.ip = request.META.get('REMOTE_ADDR')
            ordercode = get_random_string(5).upper()  # random cod
            dat.code = ordercode
            dat.save()

            # moving data shortcart to product cart
            for rs in shoping_cart:
                data = OderProduct()
                data.order_id = dat.id
                data.product_id = rs.product_id
                data.user_id = current_user.id
                data.quantity = rs.quantity
                data.price = rs.product.new_price
                data.amount = rs.amount
                data.save()

                product = Product.objects.get(id=rs.product_id)
                product.amount -= rs.quantity
                product.save()
            # Now remove all oder data from the shoping cart
            ShopCart.objects.filter(user_id=current_user.id).delete()
            # request.session['cart_item']=0
            messages.success(request, 'Your oder has been completed')
            category = Category.objects.all()
            setting = Setting.objects.get(id=1)
            context = {
                # 'category':category,
                'ordercode': ordercode,
                'category': category,
                'setting': setting,
            }

            return render(request, 'oder_completed.html', context)
        else:
            messages.warning(request, form.errors)
          #  return HttpResponseRedirect("/order/oder_cart")
    form = OderForm()
    profile = UserProfile.objects.get(user_id=current_user.id)
    total_amount = 0
    for p in shoping_cart:
        total_amount += p.product.new_price*p.quantity
    category = Category.objects.all()
    setting = Setting.objects.get(id=1)

    context = {
        # 'category':category,
        'shoping_cart': shoping_cart,
        'totalamount': totalamount,
        'profile': profile,
        'form': form,
        'category': category,
        'setting': setting,
        'total_amount': total_amount
    }
    return render(request, 'order_form.html', context)


def Order_showing(request):
    category = Category.objects.all()
    setting = Setting.objects.get(id=1)
    current_user = request.user
    orders = Order.objects.filter(user_id=current_user.id)
    context = {
        'category': category,
        'setting': setting,
        'orders': orders

    }

    return render(request, 'user_order_showing.html', context)


@login_required(login_url='/user/login')
def user_oder_details(request, id):
    category = Category.objects.all()
    setting = Setting.objects.get(id=1)
    current_user = request.user
    order = Order.objects.get(user_id=current_user.id, id=id)
    order_products = OderProduct.objects.filter(order_id=id)
    context = {

        'order': order,
        'order_products': order_products,
        'category': category,
        'setting': setting,
    }
    return render(request, 'user_order_details.html', context)


def Order_Product_showing(request):
    category = Category.objects.all()
    setting = Setting.objects.get(id=1)
    current_user = request.user
    order_product = OderProduct.objects.filter(user_id=current_user.id)
    context = {
        'category': category,
        'setting': setting,
        'order_product': order_product

    }

    return render(request, 'OrderProducList.html', context)


@login_required(login_url='/user/login')
def useroderproduct_details(request, id, oid):
    category = Category.objects.all()
    setting = Setting.objects.get(id=1)
    current_user = request.user
    order = Order.objects.get(user_id=current_user.id, id=oid)
    order_products = OderProduct.objects.get(user_id=current_user.id, id=id)
    context = {

        'order': order,
        'order_products': order_products,
        'category': category,
        'setting': setting,
    }
    return render(request, 'user_order_pro_details.html', context)

class EsewaRequestView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get("o_id")
        order = Order.objects.get(id=o_id)
        context = {
            "order": order
        }
        return render(request, "esewarequest.html", context)

class EsewaVerifyView(View):
    def get(self, request, *args, **kwargs):
        import xml.etree.ElementTree as ET
        oid = request.GET.get("oid")
        amt = request.GET.get("amt")
        refId = request.GET.get("refId")

        url = "https://uat.esewa.com.np/epay/transrec"
        d = {
            'amt': amt,
            'scd': 'epay_payment',
            'rid': refId,
            'pid': oid,
        }
        resp = request.post(url, d)
        root = ET.fromstring(resp.content)
        status = root[0].text.strip()

        order_id = oid.split("_")[1]
        order_obj = Order.objects.get(id=order_id)
        if status == "Success":
            order_obj.payment_completed = True
            order_obj.save()
            return redirect("/")
        else:

            return redirect("/esewa-request/?o_id="+order_id)

class CheckoutView(CreateView):
    template_name = "user_order_details.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("EcomApp:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)



    def form_valid(self, ckform):
        cart_id = self.request.session.get("cart_id")
        if cart_id:

            pm = ckform.cleaned_data.get("payment_method")
            order = ckform.save()
            if pm == "Esewa":
                return redirect(reverse("ecomapp:khaltirequest") + "?o_id=" + str(order.id))
            elif pm == "Esewa":
                return redirect(reverse("ecomapp:esewarequest") + "?o_id=" + str(order.id))
        else:
            return redirect("EcomApp:home")
        return super().form_valid(ckform)


@csrf_exempt
def verify_payment(request):
    data = request.POST
    product_id = data['product_identity']
    token = data['token']
    amount = data['amount']

    url = "https://khalti.com/api/v2/payment/verify/"
    payload = {
        "token": token,
        "amount": amount
    }
    headers = {
        "Authorization": "Key test_secret_key_165ce92d5e9646e7b945e9f9fcaff883"
    }

    response = requests.post(url, payload, headers=headers)

    response_data = json.loads(response.text)
    status_code = str(response.status_code)

    if status_code == '400':
        response = JsonResponse({'status': 'false', 'message': response_data['detail']}, status=500)
        return response

    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(response_data)

    return JsonResponse(f"Payment Done !! With IDX. {response_data['user']['idx']}", safe=False)



# def get_coupon(request, id):
#     try:
#         coupon = Coupon.objects.get(code=code)
#         return coupon
#     except ObjectDoesNotExist:
#         messages.info(request, "This coupon does not exist")
#         return redirect("core:checkout")
#
# class AddCouponView(login_required()):
#     def post(self, *args, **kwargs):
#         form = CouponForm(self.request.POST or None)
#         if form.is_valid():
#             try:
#                 code = form.cleaned_data.get('code')
#                 order = Order.objects.get(
#                     user=self.request.user, ordered=False)
#                 order.coupon = get_coupon(self.request, code)
#                 order.save()
#                 messages.success(self.request, "Successfully added coupon")
#                 return redirect("core:checkout")
#             except ObjectDoesNotExist:
#                 messages.info(self.request, "You do not have an active order")
#                 return redirect("core:checkout")
#
#
# class RequestRefundView(login_required()):
#     def get(self, *args, **kwargs):
#         form = RefundForm()
#         context = {
#             'form': form
#         }
#         return render(self.request, "request_refund.html", context)
#
#     def post(self, *args, **kwargs):
#         form = RefundForm(self.request.POST)
#         if form.is_valid():
#             ref_code = form.cleaned_data.get('ref_code')
#             message = form.cleaned_data.get('message')
#             email = form.cleaned_data.get('email')
#             # edit the order
#             try:
#                 order = Order.objects.get(ref_code=ref_code)
#                 order.refund_requested = True
#                 order.save()
#
#                 # store the refund
#                 refund = Refund()
#                 refund.order = order
#                 refund.reason = message
#                 refund.email = email
#                 refund.save()
#
#                 messages.info(self.request, "Your request was received.")
#                 return redirect("OrderApp:request-refund")
#
#             except ObjectDoesNotExist:
#                 messages.info(self.request, "This order does not exist.")
#                 return redirect("core:request-refund")
