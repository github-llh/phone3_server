from datetime import datetime
import time
from hashlib import md5

from django.db import transaction
from django.utils import timezone

from api import daos, models
from utils.commons import NumberUtil, ServiceResultEnum, SystemUtil, Constants, PageResult, CategoryLevelEnum, \
    OrderStatusEnum, PayTypeEnum, PayStatusEnum
from utils.exceptions import AppServiceException

class UserTokenService:
    @staticmethod
    def getUserInfoByToken(token):
        # 获取数据库的token对象的行
        tokenInfo = daos.UserTokenDao.selectByToken(token)
        # 如果存在（用户有登录信息），判断是否登录过期
        if tokenInfo != None and tokenInfo.expireTime != None and tokenInfo.expireTime > timezone.now():
            # 获取用户信息
            user = daos.UserDao.selectByPrimaryKey(tokenInfo.userId)
            if user != None:
                return {
                    'token': {k: v for k, v in tokenInfo.__dict__.items() if k != '_state'},
                    Constants.Token_To_User.value: {k: v for k, v in user.__dict__.items() if k != '_state'}
                }

class AdminUserTokenService:
    @staticmethod
    def getUserInfoByToken(token):
        # 获取数据库的token对象的行
        tokenInfo = daos.AdminUserTokenDao.selectByToken(token)
        # 如果存在（用户有登录信息），判断是否登录过期
        if tokenInfo != None and tokenInfo.expireTime != None and tokenInfo.expireTime > timezone.now():
            # 获取用户信息
            user = daos.AdminUserDao.selectByPrimaryKey(tokenInfo.adminUserId)
            if user != None:
                return {
                    'token': {k: v for k, v in tokenInfo.__dict__.items() if k != '_state'},
                    Constants.Token_To_Admin.value: {k: v for k, v in user.__dict__.items() if k != '_state'},
                }

class AdminUserService:
    @staticmethod
    def __genNewToken(timeStr, userId):
        src = timeStr + str(userId) + str(NumberUtil.genRandomNum(6))
        return SystemUtil.genToken(src)

    @staticmethod
    def login(userName, password):
        loginAdminUser = daos.AdminUserDao.login(userName)
        if loginAdminUser != None:
            if password == loginAdminUser.loginPassword:
                # 登录后执行修改token的操作
                now = time.time()  # 当前时间
                token = AdminUserService.__genNewToken(str(int(now*1000)), loginAdminUser.adminUserId)
                adminUserToken = daos.AdminUserTokenDao.selectByPrimaryKey(loginAdminUser.adminUserId)
                expireTime = now + 2*24*60*60  # 过期时间，48小时
                if adminUserToken == None:
                    adminUserToken = models.AdminUserToken()
                    adminUserToken.adminUserId = loginAdminUser.adminUserId
                    adminUserToken.token = token
                    adminUserToken.updateTime = datetime.fromtimestamp(now)
                    adminUserToken.expireTime = datetime.fromtimestamp(expireTime)
                    # 新增一条token数据
                    if daos.AdminUserTokenDao.insert(adminUserToken) != None:
                        return token
                else:
                    adminUserToken.token = token
                    adminUserToken.updateTime = datetime.fromtimestamp(now)
                    adminUserToken.expireTime = datetime.fromtimestamp(expireTime)
                    # 更新
                    if daos.AdminUserTokenDao.updateByPrimaryKey(adminUserToken) != None:
                        return token
                return ServiceResultEnum.DB_ERROR.value
            else:  # 密码错误
                return ServiceResultEnum.LOGIN_PASSWORD_INVALID.value
        else:  # 用户名不存在
            return ServiceResultEnum.LOGIN_NAME_NOT_EXISTS.value

    @staticmethod
    def getUserDetailById(loginUserId):
        return daos.AdminUserDao.selectByPrimaryKey(loginUserId)

    @staticmethod
    def updatePassword(loginUserId, originalPassword, newPassword):
        adminUser = daos.AdminUserDao.selectByPrimaryKey(loginUserId)
        if adminUser != None:
            if originalPassword == adminUser.loginPassword:
                adminUser.loginPassword = newPassword
                try:
                    with transaction.atomic():  # 事务
                        if daos.AdminUserDao.updateByPrimaryKey(adminUser) != None and daos.AdminUserTokenDao.deleteByPrimaryKey(loginUserId) != None:
                            return True
                        raise AppServiceException(ServiceResultEnum.DB_ERROR.value)
                except:
                    pass
        return False

    @staticmethod
    def updateName(loginUserId, loginUserName, nickName):
        adminUser = daos.AdminUserDao.selectByPrimaryKey(loginUserId)
        if adminUser != None:
            adminUser.loginUserName = loginUserName
            adminUser.nickName = nickName
            if daos.AdminUserDao.updateByPrimaryKey(adminUser) != None:
                return True
        return False

    @staticmethod
    def logout(adminUserId):
        return daos.AdminUserTokenDao.deleteByPrimaryKey(adminUserId) != None

class CarouselService:
    @staticmethod
    def getCarouselPage(*, page=1, pageSize=None):
        if page == None or pageSize < 1:
            page = 1
        if pageSize == None or pageSize < 1:
            pageSize = Constants.DEFAULT_SELECT_LIMIT.value
        start = (page-1)*pageSize
        limit = page*pageSize
        data, total = daos.CarouselDao.findCarouselList(start=start, limit=limit)
        return PageResult([item for item in data.values()], total, pageSize, page)

    @staticmethod
    def saveCarousel(entry):
        if daos.CarouselDao.insert(entry) != None:
            return ServiceResultEnum.SUCCESS.value
        return ServiceResultEnum.DB_ERROR.value

    @staticmethod
    def updateCarousel(entry):
        if isinstance(entry, dict):
            entry = models.Carousel(**entry)
        temp = daos.CarouselDao.selectByPrimaryKey(entry.carouselId)
        if temp == None:
            return ServiceResultEnum.DATA_NOT_EXIST.value
        temp.carouselRank = entry.carouselRank
        temp.redirectUrl = entry.redirectUrl
        temp.carouselUrl = entry.carouselUrl
        temp.updateUser = entry.updateUser
        if daos.CarouselDao.updateByPrimaeyKey(entry) != None:
            return ServiceResultEnum.SUCCESS.value
        return ServiceResultEnum.DB_ERROR.value

    @staticmethod
    def getCarouselById(id):
        return daos.CarouselDao.selectByPrimaryKey(id)

    @staticmethod
    def deleteBath(ids):
        if ids == None or len(ids) < 1:
            return False
        return daos.CarouselDao.deletedBatch(ids) > 0

    @staticmethod
    def getCarouselsForIndex(number):
        data, total = daos.CarouselDao.findCarouselList(limit=number)
        if data.exists():
            return [item for item in data.values('carouselUrl', 'redirectUrl')]
        else:
            return []

class CategoryService:
    @staticmethod
    def saveCategory(entry):
        if isinstance(entry, dict):
            entry = models.GoodsCategory(**entry)
        temp = daos.GoodsCategoryDao.selectByPrimaryKey(entry.categoryId)
        if temp != None:
            return ServiceResultEnum.SAME_CATEGORY_EXIST.value
        if daos.GoodsCategoryDao.insert(entry) != None:
            return ServiceResultEnum.SUCCESS.value
        return ServiceResultEnum.DB_ERROR.value

    @staticmethod
    def updateGoodsCategory(entry):
        if isinstance(entry, dict):
            entry = models.GoodsCategory(**entry)
        temp = daos.GoodsCategoryDao.selectByPrimaryKey(entry.categoryId)
        if temp == None:
            return ServiceResultEnum.DATA_NOT_EXIST.value
        temp2 = daos.GoodsCategoryDao.selectByLevelAndName(categoryName=entry.categoryName, categoryLeve=entry.categoryName)
        # 同名且不同id，不能继续修改
        if temp2 != None and temp2.categoryId != entry.categoryId:
            return ServiceResultEnum.SAME_CATEGORY_EXIST.value
        if daos.GoodsCategoryDao.updateByPrimaryKey(entry) != None:
            return ServiceResultEnum.DB_ERROR.SUCCESS.value
        return ServiceResultEnum.DB_ERROR.value

    @staticmethod
    def getGoodsCategoryById(id):
        return daos.GoodsCategoryDao.selectByPrimaryKey(id)

    @staticmethod
    def deleteBatch(ids):
        if ids == None or len(ids) < 1:
            return False
        return daos.GoodsCategoryDao.deletedBatch(ids) > 0

    @staticmethod
    def getCategoriesForIndex():
        indexCategoryVOS = []
        # 获取一级分类的固定数量的数据
        firstLevelCategories = daos.GoodsCategoryDao.selectByLevelAndParentIdsAndNumber([0], CategoryLevelEnum.LEVEL_ONE.value[0], Constants.INDEX_CATEGORY_NUMBER.value)
        if firstLevelCategories.exists():
            firstLevelCategoryIds = [item['categoryId'] for item in firstLevelCategories.values('categoryId')]
            # 获取二级分类的数据
            secondLevelCategories = daos.GoodsCategoryDao.selectByLevelAndParentIdsAndNumber(firstLevelCategoryIds, CategoryLevelEnum.LEVEL_TWO.value[0])
            if secondLevelCategories.exists():
                secondLevelCategoryIds = [item['categoryId'] for item in secondLevelCategories.values('categoryId')]
                # 获取三级分类的数据
                thirdLevelCategories = daos.GoodsCategoryDao.selectByLevelAndParentIdsAndNumber(secondLevelCategoryIds, CategoryLevelEnum.LEVEL_THREE.value[0])
                if thirdLevelCategories.exists():
                    # 根据 parentId 将 thirdLevelCategories 分组
                    # 处理二级分类
                    secondLevelCategoryVOS = [
                        {
                            'categoryId': item.get('categoryId'),
                            'parentId': item.get('parentId'),
                            'categoryLevel': item.get('categoryLevel'),
                            'categoryName': item.get('categoryName'),
                            'thirdLevelCategoryVOS': [sitem for sitem in thirdLevelCategories.filter(parentId=item['categoryId']).values('categoryId', 'categoryLevel', 'categoryName')]
                        } for item in secondLevelCategories.values('categoryId', 'parentId', 'categoryLevel', 'categoryName')
                    ]
                    # 处理一级分类
                    indexCategoryVOS = [
                        {
                            'categoryId': item.get('categoryId'),
                            'categoryLevel': item.get('categoryLevel'),
                            'categoryName': item.get('categoryName'),
                            'secondLevelCategoryVOS': [sitem for sitem in secondLevelCategoryVOS if sitem.get('parentId') == item.get('categoryId')]
                        } for item in firstLevelCategories.values('categoryId', 'categoryLevel', 'categoryName')
                    ]
        return indexCategoryVOS

    @staticmethod
    def selectByLevelAndParentIdsAndNumber(parentIds, categoryLevel):
        return daos.GoodsCategoryDao.selectByLevelAndParentIdsAndNumber(parentIds=parentIds, categoryLevel=categoryLevel,number=0)

    @staticmethod
    def getCategorisPage(*, page=1, pageSize=None,categoryLevel=None, parentId=None):
        if page == None or page < 1:
            page = 1
        if pageSize == None or pageSize < 1:
            pageSize = Constants.DEFAULT_SELECT_LIMIT.value
            start = (page-1)*pageSize
            limit = page*pageSize
            data, total = daos.GoodsCategoryDao.findGoodsCategoryList(categoryLevel=categoryLevel, parentId=parentId, start=start, limit=limit)
            return PageResult([item for item in data.values()], total, pageSize, page)

class GoodsService:
    @staticmethod
    def getGoodsPage(*, page=1, pageSize=None, goodsName=None, goodsSellingStatus=None, startTime=None, endTime=None):
        if page == None or page < 1:
            page = 1
        if pageSize == None or pageSize < 1:
            pageSize = Constants.DEFAULT_SELECT_LIMIT.value
        start = (page - 1) * pageSize
        limit = page * pageSize
        data, total = daos.GoodsDao.findGoodsList(goodsName=goodsName, goodsSellStatus=goodsSellingStatus, startTime=startTime, endTime=endTime, orderBy='new', start=start, limit=limit)
        return PageResult([item for item in data.values()], total, pageSize, page)

    @staticmethod
    def saveGoods(entry):
        if daos.GoodsDao.insert(entry) != None:
            return ServiceResultEnum.SUCCESS.value
        return ServiceResultEnum.DB_ERROR.value

    @staticmethod
    def batchSaveGoods(goodsList):
        if goodsList != None and len(goodsList) > 0:
            daos.GoodsDao.batchInsert(goodsList)

    @staticmethod
    def updateGoods(entry):
        if isinstance(entry, models.GoodsInfo):
            entry = {k: v for k, v in entry.__dict__.items() if k != '_state' and v != None}
        temp = daos.GoodsDao.selectByPrimaryKey(entry.get('goodsId'))
        if temp == None:
            return ServiceResultEnum.DATA_NOT_EXIST.value
        if daos.GoodsDao.updateByPrimaryKey(entry) != None:
            return ServiceResultEnum.SUCCESS.value
        return ServiceResultEnum.DB_ERROR.value

    @staticmethod
    def getGoodsById(id):
        return daos.GoodsDao.selectByPrimaryKey(id)

    @staticmethod
    def batchUpdateSellStatus(ids, sellStatus):
        return daos.GoodsDao.batchUpdateSellStatus(ids, sellStatus) > 0

    @staticmethod
    def searchGoods(*, page=1, pageSize=None, keyword=None, goodsCategoryId=None, goodsSellingStatus=None, orderBy='new', startTime=None, endTime=None):
        if page == None or page < 1:
            page = 1
        if pageSize == None or pageSize < 1:
            pageSize = Constants.DEFAULT_SELECT_LIMIT.value
        start = (page - 1) * pageSize
        limit = page * pageSize
        data, total = daos.GoodsDao.findGoodsList(keyword=keyword, goodsCategoryId=goodsCategoryId, goodsSellStatus=goodsSellingStatus, startTime=startTime, endTime=endTime, orderBy=orderBy, start=start, limit=limit)
        return PageResult([item for item in data.values('goodsId', 'goodsName', 'goodsIntro', 'goodsCoverImg', 'sellingPrice')], total, pageSize, page)

class IndexConfigService:
    @staticmethod
    def getConfigsPage(*, page=1, pageSize=None, configType=None):
        if page == None or page < 1:
            page = 1
        if pageSize == None or pageSize < 1:
            pageSize = Constants.DEFAULT_SELECT_LIMIT.value
        start = (page-1)*pageSize
        limit = page*pageSize
        data, total = daos.IndexConfigDao.findIndexConfigList(configType=configType, start=start, limit=limit)
        return PageResult([item for item in data.values()], total, pageSize, page)

    @staticmethod
    def saveIndexConfig(entry):
        if daos.IndexConfigDao.insert(entry):
            return ServiceResultEnum.SUCCESS.value
        return ServiceResultEnum.DB_ERROR.value

    @staticmethod
    def updateIndexConfig(entry):
        if isinstance(entry, models.IndexConfig):
            entry = {k: v for k, v in entry.__dict__.items() if k != '_state' and v != None}
        temp = daos.IndexConfigDao.selectByPrimaryKey(entry.get('configId'))
        if temp == None:
            return ServiceResultEnum.DATA_NOT_EXIST.value
        if daos.IndexConfigDao.updateByPrimaryKey(entry) != None:
            return ServiceResultEnum.SUCCESS.value
        return ServiceResultEnum.DB_ERROR.value

    @staticmethod
    def getIndexConfigById(id):
        return daos.IndexConfigDao.selectByPrimaryKey(id)

    @staticmethod
    def getConfigGoodsForIndex(configType, number):
        indexConfigGoodsVO = []
        data, total = daos.IndexConfigDao.findIndexConfigList(configType=configType, limit=number)
        if data.exists():
            # 取出所有的goodsId
            goodsIds = [item.get('goodsId') for item in data.values('goodsId')]
            goodses = daos.GoodsDao.selectByPrimaryKeys(goodsIds)
            if goodses != None and len(goodses) > 0:
                indexConfigGoodsVO = [
                    {
                        'goodsId': item.get('goodsId'),
                        'goodsName': item.get('goodsName')[:30] + '...' if len(item.get('goodsName')) > 30 else item.get('goodsName'),
                        'goodsIntro': item.get('goodsIntro')[:22] + '...' if len(item.get('goodsIntro')) > 22 else item.get('goodsIntro'),
                        'goodsCoverImg': item.get('goodsCoverImg'),
                        'sellingPrice': item.get('sellingPrice'),
                        'tag': item.get('tag'),
                    } for item in goodses.values('goodsId', 'goodsName', 'goodsIntro', 'goodsCoverImg', 'sellingPrice', 'tag')
                ]
            return indexConfigGoodsVO

    @staticmethod
    def deleteBatch(userId, ids):
        if ids == None or len(ids) < 1:
            return False
        return daos.IndexConfigDao.deleteBatch(userId, ids) > 0

class OrderService:
    @staticmethod
    def getOrderDetailByOrderId(orderId):
        order = daos.OrderDao.selectByPrimaryKey(orderId)
        if order != None:
            raise AppServiceException(ServiceResultEnum.DATA_NOT_EXIST.value)
        orderItems = daos.OrderItemDao.selectByOrderId(orderId)
        # 获取订单项数据
        if orderItems.exists():
            orderItemVOS = [item for item in orderItems.values('goodsId', 'goodsCount', 'goodsName', 'goodsCoverImg', 'sellingPrice')]
            orderDetailVO = {k: v for k, v in order.__dict__.items() if k in ['orderNo', 'totalPrice', 'payStatus', 'payType', 'payTypeString', 'payTime', 'orderStatus', 'orderStatusString', 'createTime', 'orderItemVOS']}
            orderDetailVO['orderStatusString'] = OrderStatusEnum.getOrderStatusEnumByCode(orderDetailVO['orderStatus'])
            orderDetailVO['payTypeString'] = PayTypeEnum.getPayTypeEnumByCode(orderDetailVO['payType'])
            orderDetailVO['orderItemVOS'] = orderItemVOS
            return orderDetailVO
        else:
            raise AppServiceException(ServiceResultEnum.ORDER_ITEM_NULL_ERROR.value)
        return []

    @staticmethod
    def getOrderDetailByOrderNo(orderNo, userId):
        temp = daos.OrderDao.selectByOrderNo(orderNo)
        if temp == None:
            raise AppServiceException(ServiceResultEnum.DATA_NOT_EXIST.value)
        if userId != temp.userId:
            raise AppServiceException(ServiceResultEnum.REQUEST_FORBIDEN_ERROR.value)
        items = daos.OrderItemDao.selectByOrderId(temp.orderId)
        if items.exists():
            orderItemVOS = [item for item in items.values('goodsId', 'goodsCount', 'goodsName', 'goodsCoverImg', 'sellingPrice')]
            orderDetailVO = {k: v for k, v in temp.__dict__.items() if k in ['orderNo', 'totalPrice', 'payStatus', 'payType', 'payTypeString', 'payTime', 'orderStatus', 'orderStatusString', 'createTime', 'orderItemVOS']}
            orderDetailVO['orderStatusString'] = OrderStatusEnum.getOrderStatusEnumByCode(orderDetailVO['orderStatus'])
            orderDetailVO['payTypeString'] = PayTypeEnum.getPayTypeEnumByCode(orderDetailVO['payType'])
            orderDetailVO['orderItemVOS'] = orderItemVOS
            return orderDetailVO
        else:
            raise AppServiceException(ServiceResultEnum.ORDER_ITEM_NULL_ERROR.value)

    @staticmethod
    def getMyOrders(*, page=1, pageSize=None, orderNo=None, userId=None, payType=None, orderStatus=None, isDeleted=None, startTime=None, endTime=None):
        if page == None or page < 1:
            page = 1
        if pageSize == None or pageSize < 1:
            pageSize = Constants.DEFAULT_SELECT_LIMIT.value
            start = (page-1)*pageSize
            limit = page*pageSize
            data, total = daos.OrderDao.findOrderList(orderNo=orderNo, userId=userId, payType=payType, orderStatus=orderStatus, isDeleted=isDeleted, startTime=startTime, endTime=endTime)
            if data != None and len(data) > 0:
                # 数据转换 将实体类转成vo    设置订单状态中文显示值
                # orderListVOS=[{
                #     'orderId': item['orderId'],
                #     'orderNo': item['orderNo'],
                #     'totalPrice': item['totalPrice'],
                #     'payStatus': item['payStatus'],
                #     'orderStatus': item['orderStatus'],
                #     'orderStatusString': OrderStatusEmum.getOrderStatusEnumByCode(item['orderStatus']),
                #     'createTime': item['createTime'],
                #     'orderItemVOS': None,
                # } for item in data.values('orderId','orderNo','totalPrice','payStatus','orderStatus','orderStatusString','createTime','orderItemVOS')]
                orderListVOS = [{
                    **item,
                    'orderStatusString': OrderStatusEnum.getOrderStatusEnumByCode(item['orderStatus']),
                    'orderItemVOS': [sitem for sitem in daos.OrderItemDao.selectByOrderId(item.get('orderId')).values('goodsId', 'goodsCount', 'goodsName', 'goodsCoverImg', 'sellingPrice')],
                }for item in data.values('orderId', 'orderNo', 'totalPrice', 'payStatus', 'orderStatus', 'orderStatusString', 'createTime', 'orderItemVOS')]
            return PageResult(orderListVOS, total, pageSize, page)

    @staticmethod
    def cancelOrder(orderNo, userdId):
        temp = daos.OrderDao.selectByOrderNo(orderNo)
        if temp != None:
            # 验证是否是当前userId下的订单，否则报错
            # 订单状态判断
            r = daos.OrderDao.changeStatus(temp.orderId, OrderStatusEnum.ORDER_CLOSED_BY_MALLUSER.value[0])
            if r > 0:
                return ServiceResultEnum.SUCCESS.value
            return ServiceResultEnum.DB_ERROR.value
        return ServiceResultEnum.DATA_NOT_EXIST.value

    @staticmethod
    def finishOrder(orderNo, userId):
        temp = daos.OrderDao.selectByOrderNo(orderNo)
        if temp != None:
            # 验证是否是当前userId下的订单，否则报错
            # 订单状态判断
            r = daos.OrderDao.changeStatus(temp.orderId, OrderStatusEnum.ORDER_SUCCESS.value[0])
            if r > 0:
                return ServiceResultEnum.SUCCESS.value
            return ServiceResultEnum.DB_ERROR.value
        return ServiceResultEnum.DATA_NOT_EXIST.value

    @staticmethod
    def paySuccess(orderNo, payType):
        temp = daos.OrderDao.selectByOrderNo(orderNo)
        if temp == None:
            raise AppServiceException(ServiceResultEnum.DATA_NOT_EXIST.value)
        if temp.payType != OrderStatusEnum.ORDER_PRE_PAY.value[0]:
            raise AppServiceException('非待支付状态下的订单无法支付')
        temp.orderStatus = OrderStatusEnum.OREDER_PAID.value[0]
        temp.payType = payType
        temp.payStatus = PayStatusEnum.PAY_SUCCESS.value[0]
        temp.payTime = datetime.now()
        if daos.OrderDao.updateByPrimaryKey(temp) != None:
            return ServiceResultEnum.SUCCESS.value
        return ServiceResultEnum.DB_ERROR.value

    @staticmethod
    # @transaction.atomic()
    def saveOrder(loginUser, address, shoppingCartItems):
        '''
        将购物车数据生成订单
        :param loginUser: 用户dict
        :param address: 地址dict
        :param shoppingCartItems: 购物车数据dict
        :return:
        '''
        itemIdList = [item.get('cartItemId') for item in shoppingCartItems]
        goodsIds = [item.get('goodsId') for item in shoppingCartItems]
        goodsList = daos.GoodsDao.selectByPrimaryKeys(goodsIds)
        # 检查是否包含已下架商品
        goodsListNotSelling = [item for item in goodsList.values() if item.get('goodsSellStatus') != Constants.SELL_STATUS_UP.value]
        if goodsListNotSelling != None and len(goodsListNotSelling) > 0:
            raise AppServiceException(goodsListNotSelling[0].get('goodsName') + "已下架，无法生成订单")
        goodsMap = {sitem.get('goodId'): sitem for sitem in [item for item in goodsList.values()]}
        # 判断商品库存
        for shoppingCartItemVO in shoppingCartItems:
            # 查出的商品中不存在购物车中的这条关联商品数据，直接返回错误提醒
            if not shoppingCartItemVO.get('goodsId') in goodsMap:
                raise AppServiceException(ServiceResultEnum.SHOPPING_ITEM_ERROR.value)
            # 存在数量大于库存的情况，直接返回错误提醒
            if shoppingCartItemVO.get('goodCount') > goodsMap.get(shoppingCartItemVO.get('goodsId')).get('stockNum'):
                raise AppServiceException(ServiceResultEnum.SHOPPING_ITEM_COUNT_ERROR.value)
        # 删除购物项
        if itemIdList != None and len(itemIdList) > 0 and goodsIds != None and len(goodsIds) > 0 and goodsList.exists():
            try:
                with transaction.atomic():  # 事务
                    if daos.ShoppingCartItemDao.deleteBatch(itemIdList) > 0:
                        stockNumDTOS = [{item.get('goodsId'): item.get('goodsCount')} for item in shoppingCartItems]
                        updateStockNumResult = daos.GoodsDao.updateStockNum(stockNumDTOS)
                        if updateStockNumResult < 1:
                            raise AppServiceException(ServiceResultEnum.SHOPPING_ITEM_COUNT_ERROR.value)
                        # 生成订单号
                        orderNo = NumberUtil.genOrderNo()
                        # 保存订单
                        # order = models.Order(orderNo=orderNo, userId=loginUser.get('userId'), extraInfo='')
                        order = {
                            'orderNo': orderNo,
                            'usesrId': loginUser.get('userId'),
                            'extraInfo': ''
                        }
                        priceTotal = sum([item.get('goodsCount') * item.get('sellingPrice') for item in shoppingCartItems])
                        if priceTotal <= 0:
                            raise AppServiceException(ServiceResultEnum.ORDER_PRICE_ERROR.value)
                        # order.totalPrice = priceTotal
                        order.update({
                            'totalPrice': priceTotal,
                            'payStatus': 0,
                            'payType': 0,
                            'orderStatus': 0,
                            'isDeleted': 0,
                            'createTime': timezone.now(),
                            'updateTime': timezone.now()
                        })
                        # 生成订单项并保存订单项纪录
                        order = daos.OrderDao.insert(order)
                        if order != None:
                            # 生成订单收货地址快照，并保存至数据库
                            address = {k: v for k, v in address.items() if k in ['userName', 'userPhone', 'provinceName', 'cityName', 'regionName', 'detailAddress', 'orderId']}
                            address.update({
                                'orderId': order.orderId
                            })
                            orderAddress = models.OrderAddress(**address)
                            # 生成所有的订单项快照，并保存至数据库
                            orderItems = []
                            for shoppingCartItemVO in shoppingCartItems:
                                # orderItem = models.OrderItem(**shoppingCartItemVO, orderId=order.orderId)
                                orderItem = {k: v for k, v in shoppingCartItemVO.items() if k in ['goodsId', 'goodsName', 'goodsCoverImg', 'sellingPrice', 'goodsCount']}
                                orderItem.update({
                                    'orderId': order.orderId,
                                    'createTime': timezone.now()
                                })
                                orderItems.append(orderItem)
                            # 保存至数据库
                            if daos.OrderItemDao.insertBatch(orderItems) != None and daos.OrderAddressDao.insert(orderAddress) != None:
                                # 所有操作成功后，将订单号返回，以供Controller方法跳转到订单详情
                                return orderNo
                    raise AppServiceException(ServiceResultEnum.DB_ERROR.value)
            except Exception as ex:
                raise ex
        raise AppServiceException(ServiceResultEnum.SHOPPING_ITEM_ERROR.value)

    @staticmethod
    def getOrdersPage(*, page=1, pageSize=None, orderNo=None, orderStatus=None, startTime=None, endTime=None):
        if page is None:
            page = 1
        if pageSize is None:
            pageSize = Constants.DEFAULT_PAGESIZE.value
        start = (page - 1) * pageSize
        limit = page * pageSize
        orders, total = daos.OrderDao.findOrderList(orderNo=orderNo, orderStatus=orderStatus, startTime=startTime, endTime=endTime, start=start, limit=limit)
        return PageResult([item for item in orders.values()], total, pageSize, page)

    @staticmethod
    def updateOrderInfo(order):
        if isinstance(order, models.Order):
            order = order.__dict__
        temp = daos.OrderDao.selectByPrimaryKey(order['orderId'])
        # 不为空且orderStatus>=0且状态为出库之前可以修改部分信息
        if temp != None and 0 <= temp.orderStatus < 3:
            temp.totalPrice = order['totalPrice']
            if daos.OrderDao.updateByPrimaryKey(temp) != None:
                return ServiceResultEnum.SUCCESS.value
            return ServiceResultEnum.DB_ERROR.value
        return ServiceResultEnum.DATA_NOT_EXIST.value

    @staticmethod
    @transaction.atomic()
    def checkDone(ids):
        # 查询所有的订单 判断状态 修改状态和更新时间
        orders = daos.OrderDao.selectByPrimaryKeys(ids)
        errorOrderNos = ""
        if orders.exists():
            for order in orders:
                if order.isDeleted == 1:
                    errorOrderNos = errorOrderNos + order.orderNo + ' '
                    continue
                if order.orderStatus != 1:
                    errorOrderNos = errorOrderNos + order.orderNo + ' '
            if errorOrderNos == '':
                # 订单状态正常 可以执行配货完成操作 修改订单状态和更新时间
                if daos.OrderDao.changeStatus(ids, 2) > 0:
                    return ServiceResultEnum.SUCCESS.value
                return ServiceResultEnum.DB_ERROR.value
            else:
                # 订单此时不可执行出库操作
                if 0 < len(errorOrderNos) < 100:
                    return errorOrderNos + '订单的状态不是支付成功无法执行出库操作'
                return '你选择了太多状态不是支付成功的订单，无法执行配货完成操作'
        # 未查询到数据 返回错误提示
        return ServiceResultEnum.DATA_NOT_EXIST.value

    @staticmethod
    @transaction.atomic()
    def checkOut(ids):
        # 查询所有的订单 判断状态 修改状态和更新时间
        orders = daos.OrderDao.selectByPrimaryKeys(ids)
        errorOrderNos = ""
        if orders.exists():
            for order in orders:
                if order.isDeleted == 1:
                    errorOrderNos = errorOrderNos + order.orderNo + ' '
                    continue
                if order.orderStatus != 1 and order.orderStatus != 2:
                    errorOrderNos = errorOrderNos + order.orderNo + ' '
            if errorOrderNos == '':
                # 订单状态正常 可以执行出库操作 修改订单状态和更新时间
                if daos.OrderDao.changeStatus(ids, 3) > 0:
                    return ServiceResultEnum.SUCCESS.value
                return ServiceResultEnum.DB_ERROR.value
            else:
                # 订单此时不可执行出库操作
                if 0 < len(errorOrderNos) < 100:
                    return errorOrderNos + '订单的状态不是支付成功或配货完成无法执行出库操作'
                return '你选择了太多状态不是支付成功或配货完成的订单，无法执行出库操作'
        # 未查询到数据 返回错误提示
        return ServiceResultEnum.DATA_NOT_EXIST.value

    @staticmethod
    @transaction.atomic()
    def closeOrder(ids):
        # 查询所有的订单 判断状态 修改状态和更新时间
        orders = daos.OrderDao.selectByPrimaryKeys(ids)
        errorOrderNos = ""
        if orders.exists():
            for order in orders:
                # isDeleted=1 一定为已关闭订单
                if order.isDeleted == 1:
                    errorOrderNos = errorOrderNos + order.orderNo + ' '
                    continue
                # 已关闭或者已完成无法关闭订单
                if order.orderStatus == 4 and order.orderStatus < 0:
                    errorOrderNos = errorOrderNos + order.orderNo + ' '
            if errorOrderNos == '':
                # 订单状态正常 可以执行关闭操作 修改订单状态和更新时间
                if daos.OrderDao.changeStatus(ids, OrderStatusEnum.ORDER_CLOSED_BY_JUDGE.value[0]) > 0:
                    return ServiceResultEnum.SUCCESS.value
                return ServiceResultEnum.DB_ERROR.value
            else:
                # 订单此时不可执行出库操作
                if 0 < len(errorOrderNos) < 100:
                    return errorOrderNos + '订单不能执行关闭操作'
                return '你选择的订单不能执行关闭操作'
        # 未查询到数据 返回错误提示
        return ServiceResultEnum.DATA_NOT_EXIST.value

    @staticmethod
    def getOrderItems(orderId):
        order = daos.OrderDao.selectByPrimaryKey(orderId)
        if order != None:
            orderItems = daos.OrderItemDao.selectByOrderId(orderId)
            # 获取订单项数据
            if orderItems.exists():
                return orderItems.values('goodsId', 'goodsCount', 'goodsName', 'goodsCoverImg', 'sellingPrice')
        return []

class ShoppingCartService:
    @staticmethod
    def saveCartItem(goodsId, goodsCount, userId):
        '''
        保存用户的购物车信息
        :param goodsId:
        :param goodsCount:
        :param userId:
        :return:
        '''
        temp = daos.ShoppingCartItemDao.selectByUserIdAndGoodsId(userId, goodsId)
        if temp != None:
            raise AppServiceException(ServiceResultEnum.SHOPPING_CART_ITEM_EXIST_ERROR.value)
        goods = daos.GoodsDao.selectByPrimaryKey(goodsId)
        # 商品为空
        if goods == None:
            raise AppServiceException(ServiceResultEnum.GOODS_NOT_EXIST.value)
        data, total = daos.ShoppingCartItemDao.findCartItems(userId=userId)
        # 超出单个商品的最大数量
        if goodsCount < 1:
            raise AppServiceException(ServiceResultEnum.SHOPPING_CART_ITEM_NUMBER_ERROR.value)
        elif goodsCount > Constants.SHOPPING_CART_ITEM_LIMIT_NUMBER.value:
            raise AppServiceException(ServiceResultEnum.SHOPPING_CART_ITEM_LIMIT_NUMBER_ERROR.value)
        # 超出最大数量
        if total > Constants.SHOPPING_CART_ITEM_TOTAL_NUMBER.value:
            raise AppServiceException(ServiceResultEnum.SHOPPING_CART_ITEM_TOTAL_NUMBER_ERROR.value)
        shoppingCartItem = models.ShoppingCartItem(goodsId=goodsId, goodsCount=goodsCount)
        shoppingCartItem.userId = userId
        # 保存记录
        if daos.ShoppingCartItemDao.insert(shoppingCartItem) != None:
            return ServiceResultEnum.SUCCESS.value
        raise AppServiceException(ServiceResultEnum.DB_ERROR.value)

    @staticmethod
    def updateNewBeeMallCartItem(userId, cartItemId, goodsCount):
        '''
        更新用户购物车
        :param userId:
        :param cartItemId:
        :param goodsCount:
        :return:
        '''
        shoppingCartItemUpdate = daos.ShoppingCartItemDao.selectByPrimaryKey(cartItemId)
        if shoppingCartItemUpdate == None:
            # raise AppServiceException(ServiceResultEnum.DATA_NOT_EXIST.value)
            return ServiceResultEnum.DATA_NOT_EXIST.value
        if shoppingCartItemUpdate.userId != userId:
            # raise AppServiceException(ServiceResultEnum.REQUEST_FORBIDEN_ERROR.value)
            return ServiceResultEnum.REQUEST_FORBIDEN_ERROR.value
        # 超出单个商品的最大数量
        if goodsCount > Constants.SHOPPING_CART_ITEM_LIMIT_NUMBER.value:
            # raise AppServiceException(ServiceResultEnum.SHOPPING_CART_ITEM_LIMIT_NUMBER_ERROR.value)
            return ServiceResultEnum.SHOPPING_CART_ITEM_LIMIT_NUMBER_ERROR.value
        shoppingCartItemUpdate.goodsCount = goodsCount
        if daos.ShoppingCartItemDao.updateByPrimaryKey(shoppingCartItemUpdate) != None:
            return ServiceResultEnum.SUCCESS.value
        # raise AppServiceException(ServiceResultEnum.DB_ERROR.value)
        return ServiceResultEnum.DB_ERROR.value

    @staticmethod
    def getCartItemById(cartItemId):
        cartItem = daos.ShoppingCartItemDao.selectByPrimaryKey(cartItemId)
        if cartItem == None:
            raise AppServiceException(ServiceResultEnum.DATA_NOT_EXIST.value)
            # return ServiceResultEnum.DATA_NOT_EXIST.value
        return cartItem

    @staticmethod
    def deleteById(cartItemId):
        return daos.ShoppingCartItemDao.deleteByPrimaryKey(cartItemId) != None

    # @staticmethod
    # def getShoppingCartItems(userId):
    #     cartItems,total=daos.ShoppingCartItemDao.findCartItems(userId=userId,limit=Constants.SHOPPING_CART_ITEM_TOTAL_NUMBER.value)
    #     return ShoppingCartService.__getCartItemVOS(cartItems.values('cartItemId','orderId','goodsCount','goodsName','goodsCoverImg','sellingPrice'))

    @staticmethod
    def getCartItemsForSettle(cartItemIds, userId):
        if cartItemIds == None or len(cartItemIds) < 1:
            raise AppServiceException(ServiceResultEnum.SHOPPING_CART_ITEM_NOT_EXIST_ERROR.value)
        shoppingCartItems, total = daos.ShoppingCartItemDao.findCartItems(userId=userId, cartItemIds=cartItemIds)
        if total == 0:
            raise AppServiceException(ServiceResultEnum.SHOPPING_CART_ITEM_NOT_EXIST_ERROR.value)
        if total != len(cartItemIds):
            raise AppServiceException(ServiceResultEnum.PARAM_ERROR.value)
        return ShoppingCartService.__getCartItemVOS(shoppingCartItems.values())

    @staticmethod
    def __getCartItemVOS(shoppingCartItems):
        shoppingCartItemVOS = []
        if len(shoppingCartItems) > 0:
            # 查询商品信息并做数据转换
            goodsIds = [item['goodsId'] for item in shoppingCartItems]
            # goods = models.GoodsInfo.objects.filter(goodsId__in=goodsIds)
            goods = daos.GoodsDao.selectByPrimaryKeys(goodsIds)
            goodsMap = {}
            if goods.exists():
                goodsMap = {item['goodsId']: item for item in goods.values()}
            for shoppingCartItem in shoppingCartItems:
                shoppingCartItemVO = {
                    'cartItemId': shoppingCartItem['cartItemId'],
                    'orderId': shoppingCartItem['orderId'],
                    'goodsCount': shoppingCartItem['goodsCount'],
                    'goodsName': goodsMap.get(shoppingCartItem['goodsId']).get('goodsName'),
                    'goodsCoverImg': goodsMap.get(shoppingCartItem['goodsId']).get('goodsCoverImg'),
                    'sellingPrice': goodsMap.get(shoppingCartItem['goodsId']).get('sellingPrice'),
                }
                if shoppingCartItem['goodsId'] in goodsMap:
                    goodsTemp = goodsMap[shoppingCartItem['goodsId']]
                    shoppingCartItemVO['goodsCoverImg'] = goodsTemp['goodsCoverImg']
                    goodsName = goodsTemp['goodsName']
                    if len(goodsName) > 28:
                        goodsName = goodsName[:28] + '...'
                    shoppingCartItemVO['goodsName'] = goodsName
                    shoppingCartItemVO['sellingPrice'] = goodsTemp['sellingPrice']
                    shoppingCartItemVOS.append(shoppingCartItemVO)
        return shoppingCartItemVOS

    # @staticmethod
    # def pageShoppingCartItems(page=1,pageSize=None,userId=None):
    #     if page is None: page = 1
    #     if pageSize is None: pageSize = Constants.DEFAULT_PAGESIZE.value
    #     start = (page - 1) * pageSize
    #     limit = page * pageSize
    #     shoppingCartItems,total=daos.ShoppingCartItemDao.findCartItems(userId=userId,start=start,limit=limit)
    #     shoppingCartItemsVOS=ShoppingCartService.__getCartItemVOS(shoppingCartItems)
    #     return PageResult(shoppingCartItemsVOS, total, pageSize, page)

    @staticmethod
    def getShoppingCartItems(page=None, pageSize=None, userId=None):
        if page is None and pageSize is None:
            start = 0
            limit = None
        elif page is not None and pageSize is None:
            start = page
            limit = None
        elif page is None and pageSize is not None:
            start = 0
            limit = pageSize
        else:
            start = (page - 1) * pageSize
            limit = page * pageSize
        shoppingCartItems, total = daos.ShoppingCartItemDao.findCartItems(userId=userId, start=start, limit=limit)
        shoppingCartItemsVOS = ShoppingCartService.__getCartItemVOS(shoppingCartItems.values())
        return PageResult(shoppingCartItemsVOS, total, pageSize, page)

class UserAddressService:
    @staticmethod
    def getAddressesByUserId(userId):
        addresses = daos.UserAddressDao.findAddressList(userId)
        return addresses.values()

    @staticmethod
    def saveUserAddress(userAddress):
        if isinstance(userAddress, dict):
            userAddress = models.UserAddress(**userAddress)
        with transaction.atomic():
            if userAddress.defaultFlag == 1:
                # 添加默认地址，需要将原有的默认地址修改掉
                defaultAddress = daos.UserAddressDao.getDefaultAddress(userAddress.userId)
                if defaultAddress != None:
                    defaultAddress.defaultFlag = 0
                    if daos.UserAddressDao.updateByPrimaryKey(defaultAddress) == None:
                        # 未更新成功
                        raise AppServiceException(ServiceResultEnum.DB_ERROR.value)
            return daos.UserAddressDao.insert(userAddress) != None

    @staticmethod
    def getUserAddressById(addressId):
        return daos.UserAddressDao.selectByPrimaryKey(addressId)

    @staticmethod
    def updateUserAddress(userAddress):
        if isinstance(userAddress, models.UserAddress):
            userAddress = {k: v for k, v in userAddress.__dict__.items() if k != '_state'}
        tempAddress = daos.UserAddressDao.selectByPrimaryKey(userAddress.get('addressId'))
        if tempAddress != None:
            with transaction.atomic():
                # 修改为默认地址，需要将原有的默认地址修改掉
                if tempAddress.get('defaultFlag') == 1:
                    defaultAddress = daos.UserAddressDao.getDefaultAddress(userAddress.get('userId'))
                    if defaultAddress != None and defaultAddress.addressId != userAddress.get('addressId'):
                        # 存在默认地址且默认地址并不是当前修改的地址
                        defaultAddress.defaultFlag = 0
                        defaultAddress.updateTime = timezone.now()
                        if daos.UserAddressDao.updateByPrimaryKey(defaultAddress) == None:
                            raise AppServiceException(ServiceResultEnum.DB_ERROR.value)
                return daos.UserAddressDao.updateByPrimaryKey(userAddress) != None
        else:
            raise AppServiceException(ServiceResultEnum.DATA_NOT_EXIST.value)

    @staticmethod
    def getDefaultAddressByUserId(userId):
        return daos.UserAddressDao.getDefaultAddress(userId)

    @staticmethod
    def deleteById(addressId):
        return daos.UserAddressDao.deleteByPrimaryKey(addressId) != None


class UserService:
    @staticmethod
    def register(loginName, password):
        if daos.UserDao.selectByLoginNameAndPassword(loginName) != None:
            raise AppServiceException(ServiceResultEnum.SAME_LOGIN_NAME_EXIST.value)
        passwordMd5 = md5(password.encode('utf8')).hexdigest()
        user = models.User(loginName=loginName, nickName=loginName, introduceSign=Constants.USER_INTRO.value, passwordMd5=passwordMd5)
        if daos.UserDao.insert(user) != None:
            return ServiceResultEnum.SUCCESS.value
        return ServiceResultEnum.DB_ERROR.value

    @staticmethod
    def __getNewToken(timeStr, userId):
        src = timeStr + str(userId) + str(NumberUtil.genRandomNum(4))
        return SystemUtil.genToken(src)

    @staticmethod
    def login(loginName, passwordMd5):
        user = daos.UserDao.selectByLoginNameAndPassword(loginName)
        if user != None:
            if user.lockedFlag == 1:
                return ServiceResultEnum.LOGIN_USER_LOCKED_ERROR.value
            if passwordMd5 == user.passwordMd5:
                # 登录后即执行修改token的操作
                now = time.time()
                expireTime = now + 2 * 24 * 60 * 60
                token = UserService.__getNewToken(str(int(now * 1000)), user.userId)
                userToken = daos.UserTokenDao.selectByPrimaryKey(user.userId)
                if userToken == None:
                    userToken = models.UserToken()
                    userToken.userId = user.userId
                    userToken.token = token
                    userToken.updateTime = datetime.fromtimestamp(now)
                    userToken.expireTime = datetime.fromtimestamp(expireTime)
                    # 新增一条token数据
                    if daos.UserTokenDao.insert(userToken) != None:
                        return token
                else:
                    userToken.token = token
                    userToken.updateTime = datetime.fromtimestamp(now)
                    userToken.expireTime = datetime.fromtimestamp(expireTime)
                    # 更新
                    if daos.UserTokenDao.updateByPrimaryKey(userToken) != None:
                        return token
            else:
                return ServiceResultEnum.LOGIN_PASSWORD_INVALID.value
        else:
            return ServiceResultEnum.LOGIN_NAME_NOT_EXISTS.value

        return ServiceResultEnum.DB_ERROR.value

    @staticmethod
    def updateUserInfo(userId, nickName, introduceSign, passwordMd5=None):
        user = daos.UserDao.selectByPrimaryKey(userId)
        if user == None:
            raise AppServiceException(ServiceResultEnum.DATA_NOT_EXIST.value)
        user.nickName = nickName
        if not (passwordMd5 == None or passwordMd5 == '' or passwordMd5 == md5(''.encode('utf-8')).hexdigest()):
            user.passwordMd5 = passwordMd5
        user.introduceSign = introduceSign
        if daos.UserDao.updateByPrimaryKey(user) != None:
            return True
        return False

    @staticmethod
    def logout(userId):
        return daos.UserTokenDao.deleteByPrimaryKey(userId) != None

    @staticmethod
    def getUsersPage(*, page=1, pageSize=None, loginName=None):
        if page is None:
            page = 1
        if pageSize is None:
            pageSize = Constants.DEFAULT_PAGESIZE.value
        start = (page - 1) * pageSize
        limit = page * pageSize
        users, total = daos.UserDao.findUserList(loginName=loginName, start=start, limit=limit)
        return PageResult([item for item in users.values()], total, pageSize, page)

    @staticmethod
    def lockUsers(ids, lockStatus):
        if ids == None or len(ids) < 1:
            return False
        return daos.UserDao.lockUserBatch(ids, lockStatus) > 0

    @staticmethod
    def getUserInfo(userId):
        user = daos.UserDao.selectByPrimaryKey(userId)
        if user == None:
            return None
        return {k: v for k, v in user.__dict__.items() if k not in ['_state', 'passwordMd5']}


