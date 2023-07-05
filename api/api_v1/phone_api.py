'''
普通用户接口
'''
from django.utils import timezone
from logger import logger

from api import services
from utils.app_decorators import user_token_decorator
from utils.commons import get_request_params, Constants, ResultGenerator, ServiceResultEnum, IndexConfigTypeEnum, \
    NumberUtil, ParseRequestData
from utils.exceptions import AppViewException


class GoodsAPI:
    '''
    商城商品相关接口
    '''
    @staticmethod
    @user_token_decorator()
    def search(request, *args, **kwargs):
        # 商品搜索接口，根据关键字和分类id进行搜索
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        keyword = params_data.get('keyword')  # 搜索关键字
        goodsCategoryId = params_data.get('goodsCategoryId')  # 分类id
        orderBy = params_data.get('orderBy')  # orderBy
        pageNumber = params_data.get('pageNumber')  # 页码
        loginUser = params_data.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        logger.debug(
            "[Debug] goods search api,keyword={},goodsCategoryId={},orderBy={},pageNumber={},userId={}".format(keyword, goodsCategoryId, orderBy, pageNumber, loginUser))
        # 两个搜索参数都为空，直接返回异常
        if goodsCategoryId == None and (keyword == None or keyword == ''):
            raise AppViewException('非法的搜索参数')
        if pageNumber == None or pageNumber < 1:
            pageNumber = 1
        params = {
            'page': pageNumber,
            'pageSize': Constants.GOODS_SEARCH_PAGE_LIMIT.value,
            'goodsSellingStatus': Constants.SELL_STATUS_UP.value,  # 搜索上架状态下的商品
        }
        if goodsCategoryId != None and goodsCategoryId != '':
            params['goodsCategoryId'] = goodsCategoryId
        if keyword != None and keyword != '':
            params['keyword'] = keyword
        if orderBy != None and orderBy != '':
            params['orderBy'] = orderBy
        data = services.GoodsService.searchGoods(**params)
        return ResultGenerator.genJsonResponseSuccessResult(data=data)

    @staticmethod
    @user_token_decorator()
    def detail(request, goodsId=None, *args, **kwargs):
        # 商品详情接口，传参为商品id
        loginUser = kwargs.get(Constants.Token_To_User.value, None)  # 当前用户信息
        if goodsId == None or goodsId < 1:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        goods = services.GoodsService.getGoodsById(goodsId)
        if goods == None:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        data = {k: v for k, v in goods.__dict__.items() if k in ['goodsId', 'goodsName', 'goodsIntro', 'goodsCoverImg', 'sellingPrice', 'tag', 'goodsCarouselList', 'originalPrice', 'goodsDetailContent', 'goodsCarousel']}
        if data.get('goodsCarousel') != None and data.get('goodsCarousel') != '':
            data['goodsCarouselList'] = data.get('goodsCarousel').split(',')
            del data['goodsCarousel']
        return ResultGenerator.genJsonResponseSuccessResult(data=data)

class CategoryAPI:
    '''
    商品分类页面接口
    '''
    @staticmethod
    @user_token_decorator()
    def list(request, *args, **kwargs):
        # 获取分类数据，分类页面使用
        data = services.CategoryService.getCategoriesForIndex()
        if len(data) < 1:
            raise AppViewException(ServiceResultEnum.DATA_NOT_EXIST.value)
        return ResultGenerator.genJsonResponseSuccessResult(data=data)

class IndexAPI:
    '''
    商城首页接口
    '''
    @staticmethod
    @user_token_decorator()
    def index(request, *args, **kwargs):
        # 获取首页数据，轮播图，新品，推荐等
        data = {}
        carousels = services.CarouselService.getCarouselsForIndex(number=Constants.INDEX_CAROUSEL_NUMBER.value)
        hotGoodses = services.IndexConfigService.getConfigGoodsForIndex(IndexConfigTypeEnum.INDEX_GOODS_HOT.value[0], Constants.INDEX_GOODS_HOT_NUMBER.value)
        newGoodses = services.IndexConfigService.getConfigGoodsForIndex(IndexConfigTypeEnum.INDEX_GOODS_NEW.value[0], Constants.INDEX_GOODS_NEW_NUMBER.value)
        recommendGoodses = services.IndexConfigService.getConfigGoodsForIndex(IndexConfigTypeEnum.INDEX_GOODS_RECOMMOND.value[0], Constants.INDEX_GOODS_RECOMMOND_NUMBER.value)
        data = {
            'carousels': carousels,
            'hotGoodses': hotGoodses,
            'newGoodses': newGoodses,
            'recommendGoodses': recommendGoodses
        }
        return ResultGenerator.genJsonResponseSuccessResult(data=data)

class OrderAPI:
    '''
    商城订单操作相关接口
    '''
    @staticmethod
    @user_token_decorator()
    def save(request, *args, **kwargs):
        # 生成订单接口，传参为地址id和待结算的购物项id数组
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        cartItemIds = params_data.get('cartItemIds')
        addressId = params_data.get('addressId')
        if cartItemIds != None and not isinstance(cartItemIds, list):
            if isinstance(cartItemIds, str):
                cartItemIds = cartItemIds.split(',')
        if cartItemIds != None and not isinstance(cartItemIds, list):
            cartItemIds = [cartItemIds]
        loginUser = kwargs.get(Constants.Token_To_User.value, None)  # 当前用户信息
        if cartItemIds == None or len(cartItemIds) < 1:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        itemsForSave = services.ShoppingCartService.getCartItemsForSettle(cartItemIds, loginUser.get('userId'))
        if itemsForSave == None or len(itemsForSave) < 1:
            raise AppViewException(ServiceResultEnum.PARAM_ERROR.value)
        priceTotal = sum([item.get('goodsCount') * item.get('sellingPrice') for item in itemsForSave])
        if priceTotal <= 0:
            raise AppViewException('价格异常')
        address = services.UserAddressService.getUserAddressById(addressId)
        if address == None:
            raise AppViewException(ServiceResultEnum.PARAM_ERROR.value)
        if address.userId != loginUser.get('userId'):
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.REQUEST_FORBIDEN_ERROR.value)
        # 保存订单并返回订单号
        address = {k: v for k, v in address.__dict__.items() if k != '_state'}
        try:
            saveOrderResult = services.OrderService.saveOrder(loginUser.get('userId'), address, itemsForSave)
            return ResultGenerator.genJsonResponseSuccessResult(data=saveOrderResult)
        except Exception as ex:
            return ResultGenerator.genJsonResponseFailResult(message=ex)

    @staticmethod
    @user_token_decorator()
    def detail(request, orderNo=None, *args, **kwargs):
        # 订单详情接口，传参为订单号
        loginUser = kwargs.get(Constants.Token_To_User.value, None)  # 当前用户信息
        if orderNo == None:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        data = services.OrderService.getOrderDetailByOrderNo(orderNo, loginUser.get('userId'))
        return ResultGenerator.genJsonResponseSuccessResult(data=data)

    @staticmethod
    @user_token_decorator()
    def list(request, *args, **kwargs):
        # 订单列表接口，传参为页码
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        pageNumber = params_data.get('pageNumber', 1)
        status = params_data.get('status', 0)
        loginUser = kwargs.get(Constants.Token_To_User.value, None)  # 当前用户信息
        if pageNumber == None or pageNumber < 1:
            pageNumber = 1
        # 封装分页请求参数
        params = {
            'userId': loginUser.get('userId'),
            'orderStatus': status,
            'page': pageNumber,
            'pageSize': Constants.ORDER_SEARCH_PAGE_LIMIT.value
        }
        data = services.OrderService.getMyOrders(**params)
        return ResultGenerator.genJsonResponseSuccessResult(data=data)

    @staticmethod
    @user_token_decorator()
    def cancel(request, ordeNo, *args, **kwargs):
        # 订单取消接口，传参为订单号
        loginUser = kwargs.get(Constants.Token_To_User.value, None)  # 当前用户信息
        if ordeNo == None or ordeNo == '':
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        cancelOrderResult = services.OrderService.cancelOrder(ordeNo, loginUser.get('userId'))
        if cancelOrderResult == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=cancelOrderResult)

    @staticmethod
    @user_token_decorator()
    def finish(request, ordeNo, *args, **kwargs):
        # 确认收货接口，传参为订单号
        loginUser = kwargs.get(Constants.Token_To_User.value, None)  # 当前用户信息
        if ordeNo == None or ordeNo == '':
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        result = services.OrderService.finishOrder(ordeNo, loginUser.get('userId'))
        if result == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=result)

    @staticmethod
    @user_token_decorator()
    def paysuccess(request, *args, **kwargs):
        # 模拟支付成功回调的接口，传参为订单号和支付方式
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        orderNo = params_data.get('orderNo', '')
        payType = params_data.get('payType')
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        if orderNo == '':
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        result = services.OrderService.paySuccess(orderNo, payType)
        if result == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=result)

class PersonalAPI:
    '''
    商城用户操作相关接口
    '''
    @staticmethod
    def login(request, *args, **kwargs):
        # 商城用户操作相关接口
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        loginName = params_data.get('loginName')
        passwordMd5 = params_data.get('passwordMd5')
        if not NumberUtil.isPhone(loginName):
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.LOGIN_NAME_IS_NOT_PHONE.value)
        loginResult = services.UserService.login(loginName, passwordMd5)
        logger.info("login api,loginName={},loginResult={}".format(loginName, loginResult))
        # 登录成功
        if len(loginResult) == Constants.TOKEN_LENGTH.value:
            return ResultGenerator.genJsonResponseSuccessResult(data=loginResult)
        return ResultGenerator.genJsonResponseFailResult(message=loginResult)

    @staticmethod
    @user_token_decorator()
    def logout(request, *args, **kwargs):
        # 登出接口，清除token
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value,None)  # 当前用户信息
        logoutResult = services.UserService.logout(loginUser.get('userId'))
        if logoutResult:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message='logout error')

    @staticmethod
    def register(request, *args, **kwargs):
        # 用户注册
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        loginName = params_data.get('loginName')
        password = params_data.get('password')
        if not NumberUtil.isPhone(loginName):
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.LOGIN_NAME_IS_NOT_PHONE.value)
        registerResult = services.UserService.register(loginName, str(password))
        logger.info("register api,loginName={},loginResult={}".format(loginName, registerResult))
        if registerResult == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=registerResult)

    @staticmethod
    @user_token_decorator()
    def modify(request, *args, **kwargs):
        # 修改用户信息
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        nickName = params_data.get('nickName')
        passwordMd5 = params_data.get('passwordMd5')
        introduceSign = params_data.get('introduceSign')
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        flag = services.UserService.updateUserInfo(loginUser.get('userId'), nickName, introduceSign, passwordMd5)
        if flag:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message='修改失败')

    @staticmethod
    @user_token_decorator()
    def info(request, *args, **kwargs):
        # 获取用户信息
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        # 已登录则直接返回
        vo = {k: v for k, v in loginUser.items() if k in ['loginName', 'nickName', 'introduceSign']}
        return ResultGenerator.genJsonResponseSuccessResult(data=vo)

class ShoppingCartAPI:
    '''
    商城购物车相关接口
    '''

    @staticmethod
    @user_token_decorator()
    def list_page(request, *args, **kwargs):
        # 购物车列表(每页默认5条)，传参为页码
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        pageNumber = params_data.get('pageNumber', 1)
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        if pageNumber == None or pageNumber < 1:
            pageNumber = 1
        params = {
            'page': pageNumber,
            'userId': loginUser.get('userId'),
            'pageSize': Constants.SHOPPING_CART_PAGE_LIMIT.value
        }
        data = services.ShoppingCartService.getShoppingCartItems(**params)
        return ResultGenerator.genJsonResponseSuccessResult(data=data)

    @staticmethod
    @user_token_decorator()
    def list(request, *args, **kwargs):
        # 购物车列表(网页移动端不分页)
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        data = services.ShoppingCartService.getShoppingCartItems(userId=loginUser.get('userId'))
        return ResultGenerator.genJsonResponseSuccessResult(data=data.list)

    @staticmethod
    @user_token_decorator()
    def save(request, *args, **kwargs):
        # 添加商品到购物车接口，传参为商品id、数量
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        goodsId = params_data.get('goodsId')
        goodsCount = params_data.get('goodsCount')
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        saveResult = services.ShoppingCartService.saveCartItem(goodsId, goodsCount, loginUser.get('userId'))
        if saveResult == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=saveResult)

    @staticmethod
    @user_token_decorator()
    def modify(request, *args, **kwargs):
        # 修改购物项数据，传参为购物项id、数量
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        cartItemId = params_data.get('cartItemId')
        goodsCount = params_data.get('goodsCount')
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        updateResult = services.ShoppingCartService.updateNewBeeMallCartItem(loginUser.get('userId'), cartItemId, goodsCount)
        if updateResult == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=updateResult)

    @staticmethod
    @user_token_decorator()
    def remove(request, cartItemId, *args, **kwargs):
        # 删除购物项，传参为购物项id
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        cartItem = services.ShoppingCartService.getCartItemById(cartItemId)
        if cartItem.userId != loginUser.get('userId'):
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.REQUEST_FORBIDEN_ERROR.value)
        deleteResult = services.ShoppingCartService.deleteById(cartItemId)
        if deleteResult:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.OPERATE_ERROR.value)

    @staticmethod
    @user_token_decorator()
    def settle(request, *args, **kwargs):
        # 根据购物项id数组查询购物项明细，确认订单页面使用
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        cartItemIds = params_data.get('cartItemIds')
        if cartItemIds != None and not isinstance(cartItemIds, list):
            if isinstance(cartItemIds, str):
                cartItemIds = cartItemIds.split(",")
        if cartItemIds != None and not isinstance(cartItemIds, list):
            cartItemIds = [cartItemIds]
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        if cartItemIds == None or len(cartItemIds) < 1:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        itemsForSettle = services.ShoppingCartService.getCartItemsForSettle(cartItemIds, loginUser.get('userId'))
        if len(itemsForSettle) < 1:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        priceTotal = sum([item.get('goodsCount') * item.get('sellingPrice') for item in itemsForSettle])
        if priceTotal < 1:
            return ResultGenerator.genJsonResponseFailResult(message='价格异常')
        return ResultGenerator.genJsonResponseSuccessResult(data=itemsForSettle)

class UserAddressAPI:
    '''
    商城个人地址相关接口
    '''
    @staticmethod
    @user_token_decorator()
    def list(request, *args, **kwargs):
        # 我的收获地址列表
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        data = services.UserAddressService.getAddressesByUserId(loginUser.get('userId'))
        return ResultGenerator.genJsonResponseSuccessResult(data=[item for item in data])

    @staticmethod
    @user_token_decorator()
    def save(request, *args, **kwargs):
        # 添加地址
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        params = {k: v for k, v in params_data.items() if k not in ['BODY', Constants.TOKEN_TO_USER.value]}
        params.update({
            'userId': loginUser.get('userId')
        })
        saveResult = services.UserAddressService.saveUserAddress(params)
        if saveResult:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message='添加失败')

    @staticmethod
    @user_token_decorator()
    def modify(request, *args, **kwargs):
        # 修改地址
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        addressId = params_data.get('addressId')
        userName = params_data.get('userName')
        userPhone = params_data.get('userPhone')
        defaultFlag = params_data.get('defaultFlag')
        provinceName = params_data.get('provinceName')
        cityName = params_data.get('cityName')
        regionName = params_data.get('regionName')
        detailAddress = params_data.get('detailAddress')
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        params = {
            'addressId': addressId,
            'updateTime': timezone.now(),
            'userId': loginUser.get('userId')
        }
        if userName != None:
            params['userName'] = userName
        if userPhone != None:
            params['userPhone'] = userPhone
        if defaultFlag != None:
            params['defaultFlag'] = defaultFlag
        if provinceName != None:
            params['provinceName'] = provinceName
        if cityName != None:
            params['cityName'] = cityName
        if regionName != None:
            params['regionName'] = regionName
        if detailAddress != None:
            params['detailAddress'] = detailAddress
        address = services.UserAddressService.getUserAddressById(addressId)
        if address == None:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.DATA_NOT_EXIST.value)
        if address.userId != loginUser.get('userId'):
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.REQUEST_FORBIDEN_ERROR.value)

        updateResult = services.UserAddressService.updateUserAddress(params)
        if updateResult:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message='更新失败')

    @staticmethod
    @user_token_decorator()
    def info(request, addressId, *args, **kwargs):
        # 获取收货地址详情，传参为地址id
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        address = services.UserAddressService.getUserAddressById(addressId)
        if address == None:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.DATA_NOT_EXIST.value)
        if address.userId != loginUser.get('userId'):
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.REQUEST_FORBIDEN_ERROR.value)
        return ResultGenerator.genJsonResponseSuccessResult(data={k: v for k, v in address.__dict__.items() if k != '_state'})

    @staticmethod
    @user_token_decorator()
    def default(request, *args, **kwargs):
        # 获取默认收货地址，无传参
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value,None)  # 当前用户信息
        address = services.UserAddressService.getDefaultAddressByUserId(loginUser.get('userId'))
        if address == None:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseSuccessResult(data={k: v for k, v in address.__dict__.items() if k != '_state'})

    @staticmethod
    @user_token_decorator()
    def remove(request, addressId, *args, **kwargs):
        # 删除收货地址，传参为地址id
        loginUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        address = services.UserAddressService.getUserAddressById(addressId)
        if address == None:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.DATA_NOT_EXIST.value)
        if address.userId != loginUser.get('userId'):
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.REQUEST_FORBIDEN_ERROR.value)
        deleteResult = services.UserAddressService.deleteById(addressId)
        if deleteResult:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message='删除失败')

