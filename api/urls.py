from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [

    path('goods/search/', views.goods_search, name='goods_search'),
    path('goods/detail/<int:goodsId>/', views.goods_detail, name='goods_detail'),
    path('category/list/', views.category_list, name='category_list'),

    path('index/', views.index_info, name='index_info'),

    path('order/<str:orderNo>/cancel/', views.order_cancel, name='order_cancel'),
    path('order/list/', views.order_list, name='order_list'),
    path('order/save/', views.order_save, name='order_save'),
    path('order/detail/<str:orderNo>/', views.order_detail, name='order_detail'),
    path('order/<str:orderNo>/finish/', views.order_finish, name='order_finish'),
    path('order/paysuccess/', views.order_paysuccess, name='order_paysuccess'),

    path('user/logout/', views.user_logout, name='user_logout'),
    path('user/login/', views.user_login, name='user_login'),
    path('user/modify/', views.user_modify, name='user_modify'),
    path('user/register/', views.user_register, name='user_register'),
    path('user/info/', views.user_info, name='user_info'),

    path('cart/page/', views.cart_list_page, name='cart_list_page'),
    path('cart/modify/', views.cart_modify, name='cart_modify'),
    path('cart/remove/<int:cartItemId>/', views.cart_remove, name='cart_remove'),
    path('cart/settle/', views.cart_settle, name='cart_settle'),
    path('cart/save/', views.cart_save, name='cart_save'),
    path('cart/list/', views.cart_list, name='cart_list'),

    path('addr/default/', views.addr_default, name='addr_default'),
    path('addr/modify/', views.addr_modify, name='addr_modify'),
    path('addr/remove/<int:addressId>/', views.addr_remove, name='addr_remove'),
    path('addr/detail/<int:addressId>/', views.addr_info, name='addr_info'),
    path('addr/save/', views.addr_save, name='addr_save'),
    path('addr/list/', views.addr_list, name='addr_list'),

    path('manage/carousel/list/', views.manage_carousel_list, name='manage_carousel_list'),
    path('manage/carousel/save/', views.manage_carousel_save, name='manage_carousel_save'),
    path('manage/carousel/modify/', views.manage_carousel_modify, name='manage_carousel_modify'),
    path('manage/category/list/', views.manage_category_list, name='manage_category_list'),
    path('manage/category/list4select/', views.manage_category_listForSelect, name='manage_category_listForSelect'),
    path('manage/category/save/', views.manage_category_save, name='manage_category_save'),
    path('manage/category/modify/', views.manage_category_modify, name='manage_category_modfy'),
    path('manage/category/info/<int:id>/', views.manage_category_info, name='manage_category_info'),
    path('manage/category/remove/', views.manage_category_remove, name='manage_category_remove'),

    path('manage/goods/list/', views.manage_goods_list, name='manage_goods_list'),
    path('manage/goods/save/', views.manage_goods_save, name='manage_goods_save'),
    path('manage/goods/modify/', views.manage_goods_modify, name='manage_goods_modify'),
    path('manage/goods/info/<int:id>/', views.manage_goods_info, name='manage_goods_info'),
    path('manage/goods/change/<int:sellStatus>/', views.manage_goods_changeStatus, name='manage_goods_changeStatus'),

    path('manage/cfg/list/', views.manage_index_list, name='manage_index_list'),
    path('manage/cfg/save/', views.manage_index_save, name='manage_index_save'),
    path('manage/cfg/modify/', views.manage_index_modify, name='manage_index_modify'),
    path('manage/cfg/info/<int:id>/', views.manage_index_info, name='manage_index_info'),
    path('manage/cfg/remove/', views.manage_index_remove, name='manage_index_remove'),

    path('manage/index/list/', views.manage_index_list, name='manage_index_list'),
    path('manage/index/save/', views.manage_index_save, name='manage_index_save'),
    path('manage/index/modify/', views.manage_index_modify, name='manage_index_modify'),
    path('manage/index/info/<int:id>/', views.manage_index_info, name='manage_index_info'),
    path('manage/index/remove/', views.manage_index_remove, name='manage_index_remove'),

    path('manage/admin/login/', views.manage_admin_login, name='manage_admin_login'),
    path('manage/admin/profile/', views.manage_admin_profile, name='manage_admin_profile'),
    path('manage/admin/logout/', views.manage_admin_logout, name='manage_admin_logout'),
    path('manage/admin/password/', views.manage_admin_password, name='manage_admin_password'),
    path('manage/admin/name/', views.manage_admin_name, name='manage_admin_name'),

    path('manage/order/list/', views.manage_order_list, name='manage_order_list'),
    path('manage/order/totalprice/', views.manage_order_modify_totalprice, name='manage_order_modify_totalprice'),
    path('manage/order/info/<int:id>/', views.manage_order_info, name='manage_order_info'),
    path('manage/order/detail/<int:id>/', views.manage_order_detail, name='manage_order_detail'),
    path('manage/order/close/', views.manage_order_close, name='manage_order_close'),
    path('manage/order/done/', views.manage_order_done, name='manage_order_done'),
    path('manage/order/out/', views.manage_order_out, name='manage_order_out'),

    path('manage/user/list/', views.manage_user_list, name='manage_user_list'),
    path('manage/user/lock/<int:lockStatus>/', views.manage_user_lock, name='manage_user_lock'),

]
