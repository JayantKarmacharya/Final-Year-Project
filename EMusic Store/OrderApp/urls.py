from django.urls import path
from OrderApp.views import(
    Add_to_Shoping_cart, cart_detials, cart_delete,
    OrderCart, Order_showing, Order_Product_showing,
    user_oder_details, useroderproduct_details, EsewaRequestView, EsewaVerifyView,verify_payment

)
urlpatterns = [
    path('addingcart/<int:id>/', Add_to_Shoping_cart, name='Add_to_Shoping_cart'),
    path('cart_details/', cart_detials, name='cart_detials'),
    path('cart_delete/<int:id>/', cart_delete, name='cart_delete'),

    path('oder_cart/', OrderCart, name="OrderCart"),

    path('orderlist/', Order_showing, name="orderlist"),
    path('OrderProduct/', Order_Product_showing, name="orderproduct"),
    path('OrderDetails/<int:id>/', user_oder_details, name="user_oder_details"),
    path('OrderProductDetails/<int:id>/<int:oid>/', useroderproduct_details, name="useroderproduct_details"),

    path("esewa-request/", EsewaRequestView.as_view(), name="esewarequest"),
    path("esewa-verify/", EsewaVerifyView.as_view(), name="esewaverify"),
    path('verify_payment',verify_payment,name='verify_payment')



    # path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    # path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    ]
