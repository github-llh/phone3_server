from datetime import datetime
from django.http import JsonResponse
from api import services
from api.api_v1 import phone_api, admin_api


# Create your views here.
from utils.commons import ParseRequestData, ResultGenerator


# def test(request):
#     # r = services.CarouselService.getCarouselPage(page=2, pageSize=3)
#     r = services.GoodsService.getGoodsPage()
#     return JsonResponse(r.__dict__, safe=False)

    # r = services.CategoryService.getCategoriesForIndex()
    # return JsonResponse(r, safe=False)

goods_search = phone_api.GoodsAPI.search
goods_detail = phone_api.GoodsAPI.detail
category_list = phone_api.CategoryAPI.list
index_info = phone_api.IndexAPI.index

order_detail = phone_api.OrderAPI.detail
order_list = phone_api.OrderAPI.list
order_paysuccess = phone_api.OrderAPI.paysuccess
order_cancel = phone_api.OrderAPI.cancel
order_finish = phone_api.OrderAPI.finish
order_save = phone_api.OrderAPI.save

user_register = phone_api.PersonalAPI.register
user_logout = phone_api.PersonalAPI.logout
user_login = phone_api.PersonalAPI.login
user_info = phone_api.PersonalAPI.info
user_modify = phone_api.PersonalAPI.modify

cart_list = phone_api.ShoppingCartAPI.list
cart_modify = phone_api.ShoppingCartAPI.modify
cart_save = phone_api.ShoppingCartAPI.save
cart_list_page = phone_api.ShoppingCartAPI.list_page
cart_remove = phone_api.ShoppingCartAPI.remove
cart_settle = phone_api.ShoppingCartAPI.settle

addr_default = phone_api.UserAddressAPI.default
addr_list = phone_api.UserAddressAPI.list
addr_modify = phone_api.UserAddressAPI.modify
addr_remove = phone_api.UserAddressAPI.remove
addr_info = phone_api.UserAddressAPI.info
addr_save = phone_api.UserAddressAPI.save

manage_carousel_list = admin_api.CarouselAPI.list
manage_carousel_save = admin_api.CarouselAPI.save
manage_carousel_modify = admin_api.CarouselAPI.modify
manage_carousel_info = admin_api.CarouselAPI.info
manage_carousel_remove = admin_api.CarouselAPI.remove

manage_category_list = admin_api.CategoryAPI.list
manage_category_listForSelect = admin_api.CategoryAPI.listForSelect
manage_category_save = admin_api.CategoryAPI.save
manage_category_modify = admin_api.CategoryAPI.modify
manage_category_info = admin_api.CategoryAPI.info
manage_category_remove = admin_api.CategoryAPI.remove

manage_goods_list = admin_api.GoodsAPI.list
manage_goods_save = admin_api.GoodsAPI.save
manage_goods_modify = admin_api.GoodsAPI.modify
manage_goods_info = admin_api.GoodsAPI.info
manage_goods_changeStatus = admin_api.GoodsAPI.changeStatus

manage_index_list = admin_api.IndexConfigAPI.list
manage_index_save = admin_api.IndexConfigAPI.save
manage_index_info = admin_api.IndexConfigAPI.info
manage_index_modify = admin_api.IndexConfigAPI.modify
manage_index_remove = admin_api.IndexConfigAPI.remove

manage_admin_login = admin_api.AdminUserAPI.login
manage_admin_profile = admin_api.AdminUserAPI.profile
manage_admin_logout = admin_api.AdminUserAPI.logout
manage_admin_name = admin_api.AdminUserAPI.name
manage_admin_password = admin_api.AdminUserAPI.password

manage_order_list = admin_api.OrderAPI.list
manage_order_modify_totalprice = admin_api.OrderAPI.modify
manage_order_info = admin_api.OrderAPI.info
manage_order_detail = admin_api.OrderAPI.detail
manage_order_close = admin_api.OrderAPI.closeOrder
manage_order_done = admin_api.OrderAPI.checkDone
manage_order_out = admin_api.OrderAPI.checkOut

manage_user_list = admin_api.UserAPI.list
manage_user_lock = admin_api.UserAPI.lock

if __name__ == '__main__':
    print(datetime.now())

def test(request):
    data = ParseRequestData(request).get_request_data(param_type=ParseRequestData.ParamType.GET_POST_BODY, typecls=dict)
    print('=====', data)
    if 'BODY' in data:
        data['BODY'] = data['BODY'].decode('utf-8')
    return ResultGenerator.genJsonResponseSuccessResult(data=data)


