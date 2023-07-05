from django.db.models import F, Q
from django.utils import timezone

from api import models

'''
如果可以，传对象；否则传字典
'''
class AdminUserDao:
    @staticmethod
    def login(userName, password=None):
        try:
            # return models.AdminUser.objects.get(loginUserName=userName, loginPassword=password, locked=0)
            queryset = models.AdminUser.objects.filter(locked=0, loginUserName=userName)
            if password != None:
                queryset = queryset.filter(loginPassword=password)
            return queryset.first()
        except:
            pass

    @staticmethod
    def selectByPrimaryKey(adminUserId):
        try:
            return models.AdminUser.objects.get(adminUserId=adminUserId)
        except:
            pass

    @staticmethod
    def insert(bean):
        '''
        新增
        :param bean: 可以是对象，也可以是字典
        :return: 如果成功是新对象，否则是None
        '''
        # 判断传入的是object还是dict
        try:
            if isinstance(bean, models.AdminUser):
                bean.save()
            elif isinstance(bean, dict):  # 字典
                return models.AdminUser.objects.create(**bean)
        except:
            pass

    @staticmethod
    def updateByPrimaryKey(bean):
        try:
            if isinstance(bean, models.AdminUser):
                bean.save()
            elif isinstance(bean, dict):  # 字典
                # 更新对象，返回是受影响行数
                r = models.AdminUser.objects.filter(adminUserId=bean['adminUserId']).update(**bean)
                if r > 0:  # 更新成功，重新查询对象返回
                    return models.AdminUser.objects.get(adminUserId=bean['adminUserId'])
        except:
            pass

class CarouselDao():
    @staticmethod
    def findCarouselList(start=None, limit=None):
        queryset = models.Carousel.objects.filter(isDeleted=0).order_by('-carouselRank')
        total = queryset.count()
        if start != None and limit != None:
            queryset = queryset[start:limit]
        elif start != None:
            queryset = queryset[start:]
        elif limit != None:
            queryset = queryset[:limit]
        return queryset, total

    @staticmethod
    def selectByPrimaryKey(carouselId):
        try:
            return models.Carousel.objects.get(carouselId=carouselId)
        except:
            pass

    @staticmethod
    def insert(bean):
        try:
            if isinstance(bean, models.Carousel):
                bean.save()
            elif isinstance(bean, dict):
                return models.Carousel.objects.create(**bean)
        except:
            pass

    @staticmethod
    def updateByPrimaeyKey(bean):
        try:
            if isinstance(bean, models.Carousel):
                bean.save()
                return bean
            elif isinstance(bean, dict):
                r = models.Carousel.objects.filter(carouselId=bean['carouselId']).update(**bean)
                if r > 0:
                    return models.Carousel.objects.get(carouselId=bean['carouselId'])
        except Exception as ex:
            print(ex)
            pass

    @staticmethod
    def deleteByPrimaryKey(carouselId):
        try:
            r = models.Carousel.objects.get(carouselId=carouselId, isDeleted=0)
            r.isDeleted = 1
            r.save()
            return r
        except:
            pass

    @staticmethod
    def deletedBatch(ids):
        try:
            return models.Carousel.objects.filter(carouselId_in=ids, isDeleted=0).update(isDeleted=1)
        except:
            return 0

        # 更新之后返回所有被更新对象的QuerySet
        # try:
        #     r=models.Carousel.objects.filter(carouselId__in=ids,isDeleted=0)
        #     ids=[item['carouselId'] for item in r.values('carouselId')] # 真正要修改的id
        #     r=r.update(isDeleted=1)
        #     if r>0:
        #         return models.Carousel.objects.filter(carouselId__in=ids)
        # except: None

class GoodsCategoryDao:
    @staticmethod
    def selectByPrimaryKey(categoryId):
        try:
            return models.GoodsCategory.objects.get(categoryId=categoryId)
        except:
            pass

    @staticmethod
    def insert(bean):
        try:
            if isinstance(bean, models.GoodsCategory):
                bean.save()
            elif isinstance(bean, dict):
                return models.GoodsCategory.objects.create(**bean)
        except:
            pass

    @staticmethod
    def updateByPrimaryKey(bean):
        try:
            if isinstance(bean, models.GoodsCategory):
                temp = models.GoodsCategory.objects.get(categoryId=bean.categoryId)
                bean.createTime = temp.createTime
                bean.save()
                return bean
            elif isinstance(bean, dict):
                r = models.GoodsCategory.objects.filter(categoryId=bean['categoryId']).update(**bean)
                if r > 0:
                    return models.GoodsCategory.objects.get(categoryId=bean['categoryId'])
        except:
            pass

    @staticmethod
    def deleteByPrimaryKey(categoryId):
        try:
            r = models.GoodsCategory.objects.get(categoryId=categoryId, isDeleted=0)
            r.isDeleted = 1
            r.save()
            return r
        except:
            pass

    @staticmethod
    def deletedBatch(ids):
        try:
            return models.GoodsCategory.objects.filter(categoryId__in=ids, isDeleted=0).update(isDeleted=1)
        except:
            return 0

    @staticmethod
    def findGoodsCategoryList(categoryLevel=None, parentId=None, limit=None, start=None):
        queryset = models.GoodsCategory.objects.filter(isDeleted=0)
        if categoryLevel != None:
            queryset = queryset.filter(categoryLevel=categoryLevel)
        if parentId != None:
            queryset = queryset.filter(parentId=parentId)
        queryset = queryset.order_by('-categoryRank')
        total = queryset.count()
        if start != None and limit != None:
            queryset = queryset[start:limit]
        elif start != None:
            queryset = queryset[start:]
        elif limit != None:
            queryset = queryset[:limit]
        return queryset, total

    @staticmethod
    def selectByLevelAndName(categoryName, categoryLeve):
        try:
            return models.GoodsCategory.objects.filter(isDeleted=0, categoryName=categoryName, categoryLeve=categoryLeve).first()
        except:
            pass

    @staticmethod
    def selectByLevelAndParentIdsAndNumber(parentIds, categoryLevel, number=None):
        queryset = models.GoodsCategory.objects.filter(isDeleted=0, parentId__in=parentIds, categoryLevel=categoryLevel).order_by('-categoryRank')
        if number != None and number > 0:
            queryset = queryset[:number]
        return queryset

class IndexConfigDao:
    @staticmethod
    def selectByPrimaryKey(configId):
        try:
            return models.IndexConfig.objects.get(configId=configId)
        except:
            pass

    @staticmethod
    def insert(bean):
        try:
            if isinstance(bean, models.IndexConfig):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                return models.IndexConfig.objects.create(**bean)
        except:
            pass

    @staticmethod
    def updateByPrimaryKey(bean):
        try:
            if isinstance(bean, models.IndexConfig):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                # 更新对象，返回是受影响行数
                r = models.IndexConfig.objects.filter(configId=bean['configId']).update(**bean)
                if r > 0:  # 更新成功，重新查询对象返回
                    return models.IndexConfig.objects.get(configId=bean['configId'])
        except:
            pass

    @staticmethod
    def deleteByPrimaryKey(configId):
        try:
            r = models.IndexConfig.objects.get(configId=configId, isDeleted=0)
            r.isDeleted = 1
            r.save()
            return r
        except:
            pass

    @staticmethod
    def deleteBatch(ids):
        try:
            return models.IndexConfig.objects.filter(configId__in=ids, isDeleted=0).update(isDeleted=1)
        except:
            return 0

    @staticmethod
    def findIndexConfigList(configType=None, start=None, limit=None):
        queryset = models.IndexConfig.objects.filter(isDeleted=0)
        if configType != None:
            queryset = queryset.filter(configType=configType)
        total = queryset.count()
        queryset = queryset.order_by('-configRank')
        if start != None and limit != None:
            queryset = queryset[start:limit]
        elif start != None:
            queryset = queryset[start:]
        elif limit != None:
            queryset = queryset[:limit]
        return queryset, total

class UserAddressDao:
    @staticmethod
    def getDefaultAddress(userId):
        try:
            return models.UserAddress.objects.filter(defaultFlag=1, isDeleted=0, userId=userId).first()
        except:
            pass

    @staticmethod
    def findAddressList(userId):
        return models.UserAddress.objects.filter(isDeleted=0, userId=userId).order_by('-addressId')

    @staticmethod
    def selectByPrimaryKey(addressId):
        try:
            return models.UserAddress.objects.get(addressId=addressId)
        except:
            pass

    @staticmethod
    def insert(bean):
        try:
            if isinstance(bean, models.UserAddress):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                return models.UserAddress.objects.create(**bean)
        except:
            pass

    @staticmethod
    def updateByPrimaryKey(bean):
        try:
            if isinstance(bean, models.UserAddress):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                # 更新对象，返回是受影响行数
                r = models.UserAddress.objects.filter(addressId=bean['addressId']).update(**bean)
                if r > 0:  # 更新成功，重新查询对象返回
                    return models.UserAddress.objects.get(addressId=bean['addressId'])
        except:
            pass

    @staticmethod
    def deleteByPrimaryKey(addressId):
        try:
            r = models.UserAddress.objects.get(addressId=addressId, isDeleted=0)
            r.isDeleted = 1
            r.save()
            return r
        except:
            pass

class UserDao:
    @staticmethod
    def selectByPrimaryKey(userId):
        try:
            return models.User.objects.get(userId=userId)
        except:
            pass

    @staticmethod
    def insert(bean):
        try:
            if isinstance(bean, models.User):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                return models.User.objects.create(**bean)
        except:
            pass

    @staticmethod
    def updateByPrimaryKey(bean):
        try:
            if isinstance(bean, models.User):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                # 更新对象，返回是受影响行数
                r = models.User.objects.filter(userId=bean['userId']).update(**bean)
                if r > 0:  # 更新成功，重新查询对象返回
                    return models.User.objects.get(userId=bean['userId'])
        except:
            pass

    @staticmethod
    def deleteByPrimaryKey(userId):
        try:
            r = models.User.objects.get(userId=userId, isDeleted=0)
            r.isDeleted = 1
            r.save()
            return r
        except:
            pass

    @staticmethod
    def getDefaultAddress(userId):
        try:
            return models.User.objects.filter(defaultFlag=1, isDeleted=0, userId=userId).first()
        except:
            pass

    @staticmethod
    def findAddressList(userId):
        return models.User.objects.filter(isDeleted=0, userId=userId).order_by('-addressId')

    @staticmethod
    def findUserList(loginName=None, start=None, limit=None):
        queryset = models.User.objects.all()
        if loginName != None:
            queryset = queryset.filter(loginName=loginName)
        total = queryset.count()
        queryset = queryset.order_by('-createTime')
        if start != None and limit != None:
            queryset = queryset[start:limit]
        elif start != None:
            queryset = queryset[start:]
        elif limit != None:
            queryset = queryset[:limit]
        return queryset, total

    @staticmethod
    def selectByLoginNameAndPassword(loginName, password=None):
        queryset = models.User.objects.filter(isDeleted=0, loginName=loginName)
        if password != None:
            queryset = queryset.filter(passwordMd5=password)
        try:
            return queryset.first()
        except:
            pass

    @staticmethod
    def lockUserBatch(ids, lockedStatus):
        try:
            return models.User.objects.filter(userId__in=ids).update(lockedFlag=lockedStatus)
        except:
            return 0

class AdminUserTokenDao:
    @staticmethod
    def selectByPrimaryKey(adminUserId):
        try:
            return models.AdminUserToken.objects.get(adminUserId=adminUserId)
        except:
            pass

    @staticmethod
    def insert(bean):
        # 判断传入的是object还是dict
        try:
            if isinstance(bean, models.AdminUserToken):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                return models.AdminUserToken.objects.create(**bean)
        except:
            pass

    @staticmethod
    def updateByPrimaryKey(bean):
        try:
            if isinstance(bean, models.AdminUserToken):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                # 更新对象，返回是受影响行数
                r = models.AdminUserToken.objects.filter(adminUserId=bean['adminUserId']).update(**bean)
                if r > 0:  # 更新成功，重新查询对象返回
                    return models.AdminUserToken.objects.get(adminUserId=bean['adminUserId'])
        except:
            pass

    @staticmethod
    def deleteByPrimaryKey(adminUserId):
        try:
            r = models.AdminUserToken.objects.get(adminUserId=adminUserId)
            result = {k: v for k, v in r.__dict__.items() if k != '_state'}
            r.delete()
            return result
        except:
            pass

    @staticmethod
    def selectByToken(token):
        try:
            return models.AdminUserToken.objects.get(token=token)
        except:
            pass

class GoodsDao:
    @staticmethod
    def selectByPrimaryKey(goodsId):
        try:
            return models.GoodsInfo.objects.get(goodsId=goodsId)
        except:
            pass

    @staticmethod
    def insert(bean):
        # 判断传入的是object还是dict
        try:
            if isinstance(bean, models.GoodsInfo):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                return models.GoodsInfo.objects.create(**bean)
        except:
            pass

    @staticmethod
    def updateByPrimaryKey(bean):
        try:
            if isinstance(bean, models.GoodsInfo):
                bean = {k: v for k, v in bean.__dict__.items() if k != '_state' and v != None}
            elif isinstance(bean, dict):  # 字典
                # 更新对象，返回是受影响行数
                r = models.GoodsInfo.objects.filter(goodsId=bean['goodsId']).update(**bean)
                if r > 0:  # 更新成功，重新查询对象返回
                    return models.GoodsInfo.objects.get(goodsId=bean['goodsId'])
        except:
            pass

    @staticmethod
    def deleteByPrimaryKey(goodsId):
        try:
            r = models.GoodsInfo.objects.get(goodsId=goodsId)
            result = {k: v for k, v in r.__dict__.items() if k != '_state'}
            r.delete()
            if r > 0:
                return result
        except:
            pass

    @staticmethod
    def batchInsert(goodsList):
        '''
        一次插入多行
        :param goodsList: 字典或对象列表
        :return:
        '''
        lst = []
        for item in goodsList:
            if isinstance(item, dict):
                obj = models.GoodsInfo(**item)
                lst.append(obj)
            elif isinstance(item, models.GoodsInfo):
                lst.append(item)
        try:
            return models.GoodsInfo.objects.bulk_create(lst)
        except:
            pass

    @staticmethod
    def updateStockNum(stockDTOS):
        '''
        批量更新库存
        :param stockDTOS:  [{goodsId,goodsCount}]
        :return:
        '''
        result = 0
        for item in stockDTOS:
                try:
                    r = models.GoodsInfo.objects.filter(
                        goodsSellStatus=0,
                        goodsId=item.get('goodsId', ''),
                        stockNum_gte=item.get('goodsCount', 0)
                        ).update(stockNum=F('stockNum') - item.get('goodsCount', 0))
                    if r > 0:
                        result = result + 1
                except:
                    pass
        return result

    @staticmethod
    def batchUpdateSellStatus(goodsIds, sellStatus):
        try:
            return models.GoodsInfo.objects.filter(goodsId__in=goodsIds).update(goodsSellStatus=sellStatus)
        except:
            return 0

    @staticmethod
    def findGoodsList(keyword=None, goodsName=None, goodsCategoryId=None, goodsSellStatus=None, startTime=None,endTime=None, orderBy=None, start=None, limit=None):
        queryset = models.GoodsInfo.objects.all()
        if goodsName != None:
            queryset = queryset.filter(goodsName=goodsName)
        if goodsCategoryId != None:
            queryset = queryset.filter(goodsCategoryId=goodsCategoryId)
        if goodsSellStatus != None:
            queryset = queryset.filter(goodsSellStatus=goodsSellStatus)
        if keyword != None and keyword != '':
            queryset = queryset.filter(Q(goodsName__icontains=keyword) | Q(goodsIntro__icontains=keyword))
        if startTime != None:
            queryset = queryset.filter(createTime__gte=startTime)
        if endTime != None:
            queryset = queryset.filter(createTime__lte=endTime)
        total = queryset.count()
        if orderBy != None:
            if orderBy == 'new':
                queryset = queryset.order_by('-goodsId')
            elif orderBy == 'price':
                queryset = queryset.order_by('-sellingPrice')
            else:
                queryset = queryset.order_by('-stockNum')
        if start != None and limit != None:
            queryset = queryset[start:limit]
        elif start != None:
            queryset = queryset[start:]
        elif limit != None:
            queryset = queryset[:limit]
        return queryset, total

    @staticmethod
    def selectByPrimaryKeys(ids):
        return models.GoodsInfo.objects.filter(goodsId__in=ids)

class OrderAddressDao:
    @staticmethod
    def selectByPrimaryKey(orderId):
        try:
            return models.OrderAddress.objects.get(orderId=orderId)
        except:
            pass

    @staticmethod
    def insert(bean):
        # 判断传入的是object还是dict
        try:
            if isinstance(bean, models.OrderAddress):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                return models.OrderAddress.objects.create(**bean)
        except:
            pass

    @staticmethod
    def updateByPrimaryKey(bean):
        try:
            if isinstance(bean, models.OrderAddress):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                # 更新对象，返回是受影响行数
                r = models.OrderAddress.objects.filter(orderId=bean['orderId']).update(**bean)
                if r > 0:  # 更新成功，重新查询对象返回
                    return models.OrderAddress.objects.get(orderId=bean['orderId'])
        except:
            pass

    @staticmethod
    def deleteByPrimaryKey(orderId):
        try:
            r = models.OrderAddress.objects.get(orderId=orderId)
            result = {k: v for k, v in r.__dict__.items() if k != '_state'}
            r.delete()
            if r > 0:
                return result
        except:
            pass

class OrderItemDao:
    @staticmethod
    def selectByPrimaryKey(orderItemId):
        try:
            return models.OrderItem.objects.get(orderItemId=orderItemId)
        except:
            pass

    @staticmethod
    def insert(bean):
        # 判断传入的是object还是dict
        try:
            if isinstance(bean, models.OrderItem):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                return models.OrderItem.objects.create(**bean)
        except:
            pass

    @staticmethod
    def updateByPrimaryKey(bean):
        try:
            if isinstance(bean, models.OrderItem):
                bean.save()
                return bean
            elif isinstance(bean ,dict):  # 字典
                # 更新对象，返回是受影响行数
                r = models.OrderItem.objects.filter(orderItemId=bean['orderItemId']).update(**bean)
                if r > 0:  # 更新成功，重新查询对象返回
                    return models.OrderItem.objects.get(orderItemId=bean['orderItemId'])
        except:
            pass

    @staticmethod
    def deleteByPrimaryKey(orderItemId):
        try:
            r = models.OrderItem.objects.get(orderItemId=orderItemId)
            result = {k: v for k, v in r.__dict__.items() if k != '_state'}
            r.delete()
            if r > 0:
                return result
        except:
            pass

    @staticmethod
    def selectByOrderId(orderIds):
        if isinstance(orderIds, list):
            return models.OrderItem.objects.filter(orderId__in=orderIds)
        else:
            try:
                return models.OrderItem.objects.get(orderId=orderIds)
            except:
                pass

    @staticmethod
    def insertBatch(orderItems):
        lst = []
        for item in orderItems:
            if isinstance(item, models.OrderItem):
                lst.append(item)
            elif isinstance(item, dict):
                lst.append(models.OrderItem(**item))
        if len(lst) > 0:
            return models.OrderItem.objects.bulk_create(lst)

class OrderDao:
    @staticmethod
    def selectByPrimaryKey(orderId):
        try:
            return models.Order.objects.get(orderId=orderId)
        except:
            pass

    @staticmethod
    def insert(bean):
        # 判断传入的是object还是dict
        try:
            if isinstance(bean, models.Order):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                return models.Order.objects.create(**bean)
        except Exception as ex:
            print(ex)
            pass

    @staticmethod
    def updateByPrimaryKey(bean):
        try:
            if isinstance(bean, models.Order):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                # 更新对象，返回是受影响行数
                r = models.Order.objects.filter(orderId=bean['orderId']).update(**bean)
                if r > 0:  # 更新成功，重新查询对象返回
                    return models.Order.objects.get(orderId=bean['orderId'])
        except:
            pass

    @staticmethod
    def deleteByPrimaryKey(orderId):
        try:
            r = models.Order.objects.get(orderId=orderId, isDeleted=0)
            r.isDeleted = 1
            r.save()
            return r
        except:
            pass

    # @staticmethod
    # def deleteByPrimaryKey(orderId):
    #     try:
    #         r=models.Order.objects.get(orderId=orderId)
    #         result={k:v for k,v in r.__dict__.items() if k !='_state'}
    #         r.delete()
    #         if r>0:
    #             return result
    #     except: pass

    @staticmethod
    def selectByOrderNo(orderNo):
        try:
            return models.Order.objects.get(orderNo=orderNo, isDeleted=0)
        except:
            pass

    @staticmethod
    def selectByPrimaryKeys(orderIds):
        return models.Order.objects.filter(orderId__in=orderIds)

    @staticmethod
    def findOrderList(*, orderNo=None, userId=None, payType=None, orderStatus=None, isDeleted=None, startTime=None, endTime=None, start=None, limit=None):
        queryset = models.Order.objects.all()
        if orderNo!=None:
            queryset = queryset.filter(orderNo=orderNo)
        if userId!=None:
            queryset = queryset.filter(userId=userId)
        if payType!=None:
            queryset = queryset.filter(payType=payType)
        if orderStatus!=None:
            queryset = queryset.filter(orderStatus=orderStatus)
        if isDeleted!=None:
            queryset = queryset.filter(isDeleted=isDeleted)
        if startTime!=None:
            queryset = queryset.filter(createTime__gte=startTime)
        if endTime!=None:
            queryset = queryset.filter(createTime__lte=endTime)
        total = queryset.count()
        queryset = queryset.order_by('-createTime')
        if start!=None and limit!=None:
            queryset = queryset[start:limit]
        elif start!=None:
            queryset = queryset[start:]
        elif limit!=None:
            queryset = queryset[:limit]
        return queryset, total

    @staticmethod
    def changeStatus(orderIds,orderStatus):
        return models.Order.objects.filter(orderId__in=orderIds).update(orderStatus=orderStatus, updateTime=timezone.now())

class ShoppingCartItemDao:
    @staticmethod
    def selectByPrimaryKey(cartItemId):
        try:
            return models.ShoppingCartItem.objects.get(cartItemId=cartItemId)
        except:
            pass

    @staticmethod
    def insert(bean):
        # 判断传入的是object还是dict
        try:
            if isinstance(bean, models.ShoppingCartItem):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                return models.ShoppingCartItem.objects.create(**bean)
        except:
            pass

    @staticmethod
    def updateByPrimaryKey(bean):
        try:
            if isinstance(bean, models.ShoppingCartItem):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                # 更新对象，返回是受影响行数
                r = models.ShoppingCartItem.objects.filter(cartItemId=bean['cartItemId']).update(**bean)
                if r > 0:  # 更新成功，重新查询对象返回
                    return models.ShoppingCartItem.objects.get(cartItemId=bean['cartItemId'])
        except:
            pass

    @staticmethod
    def deleteByPrimaryKey(cartItemId):
        try:
            r = models.ShoppingCartItem.objects.get(cartItemId=cartItemId, isDeleted=0)
            r.isDeleted = 1
            r.save()
            return r
        except: pass

    @staticmethod
    def selectByUserIdAndGoodsId(userId,goodsId):
        try:
            return models.ShoppingCartItem.objects.get(isDeleted=0, userId=userId, goodsId=goodsId)
        except:
            pass

    @staticmethod
    def findCartItems(*, userId=None, cartItemIds=None, start=None, limit=None):
        queryset = models.ShoppingCartItem.objects.filter(isDeleted=0)
        if userId!=None:
            queryset = queryset.filter(userId=userId)
        if cartItemIds!=None:
            if isinstance(cartItemIds, list):
                queryset = queryset.filter(cartItemId__in=cartItemIds)
            else:
                queryset = queryset.filter(cartItemId=cartItemIds)
        total = queryset.count()
        if start!=None and limit !=None:
            queryset = queryset[start:limit]
        elif start!=None:
            queryset = queryset[start:]
        elif limit!=None:
            queryset = queryset[:limit]
        return queryset, total

    @staticmethod
    def deleteBatch(cartItemIds):
        return models.ShoppingCartItem.objects.filter(isDeleted=0, cartItemId__in=cartItemIds).update(isDeleted=1)

class UserTokenDao:
    @staticmethod
    def selectByPrimaryKey(userId):
        try:
            return models.UserToken.objects.get(userId=userId)
        except:
            pass

    @staticmethod
    def insert(bean):
        # 判断传入的是object还是dict
        try:
            if isinstance(bean, models.UserToken):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                return models.UserToken.objects.create(**bean)
        except:
            pass

    @staticmethod
    def updateByPrimaryKey(bean):
        try:
            if isinstance(bean, models.UserToken):
                bean.save()
                return bean
            elif isinstance(bean, dict):  # 字典
                # 更新对象，返回是受影响行数
                r = models.UserToken.objects.filter(userId=bean['userId']).update(**bean)
                if r > 0:  # 更新成功，重新查询对象返回
                    return models.UserToken.objects.get(userId=bean['userId'])
        except:
            pass

    @staticmethod
    def deleteByPrimaryKey(userId):
        try:
            r = models.UserToken.objects.get(userId=userId)
            result = {k: v for k, v in r.__dict__.items() if k != '_state'}
            r = r.delete()
            if r[0] > 0:
                return result
        except:
            pass

    @staticmethod
    def selectByToken(token):
        try:
            return models.UserToken.objects.get(token=token)
        except:
            pass
