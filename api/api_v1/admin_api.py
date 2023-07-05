'''
管理后台接口
'''
import os
from datetime import datetime
from fileinput import filename
from pathlib import Path

from django.utils import timezone
from logger import logger

from api import services
from phone import settings
from utils.app_decorators import admin_token_decorator
from utils.commons import get_request_params, Constants, ResultGenerator, ParseRequestData, ServiceResultEnum, \
    CategoryLevelEnum, IndexConfigTypeEnum, NumberUtil


class CarouselAPI:
    '''
    后台管理系统轮播图模块接口
    '''
    @staticmethod
    @admin_token_decorator()
    def list(request, *args, **kwargs):
        # 轮播图列表
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        pageNumber = params_data.get('pageNumber', 1)  # 页码
        pageSize = params_data.get('pageSize')  # 页面大小
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        logger.debug("[Debug] carousel api,adminUser={}".format(adminUser))
        if pageNumber == None or pageNumber < 1:
            pageNumber = 1
        if pageSize == None or pageSize < 1:
            pageSize = Constants.DEFAULT_PAGESIZE.value
        params = {
            "page": pageNumber,
            'pageSize': pageSize
        }
        data = services.CarouselService.getCarouselPage(**params)
        return ResultGenerator.genJsonResponseSuccessResult(data=data)

    @staticmethod
    @admin_token_decorator()
    def save(request, *args, **kwargs):
        # 新增轮播图
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        logger.debug("[Debug] carousel api,adminUser={}".format(adminUser))
        if params_data.get('carouselUrl') == None or params_data.get('carouselRank') == None:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        params = params_data
        params.update({
            'isDeleted': 0,
            'createUser': adminUser.get('adminUserId'),
            'updateUser': adminUser.get('adminUserId')
        })
        result = services.CarouselService.saveCarousel(params)
        if result == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=result)

    @staticmethod
    @admin_token_decorator()
    def modify(request, *args, **kwargs):
        # 修改轮播图信息，修改轮播图信息
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        logger.debug("[Debug] carousel api,adminUser={}".format(adminUser))
        if params_data.get('carouselUrl') == None or params_data.get('carouselId') =='' or params_data.get('carouselUrl')==None or params_data.get('carouselRank')==None:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        params = params_data
        params.update({
            'updateUser':adminUser.get('adminUserId'),
            'updateTime':timezone.now()
        })
        # 剔除不需要的键值对
        params = {k: v for k, v in params.items() if k not in ['BODY', Constants.Token_To_Admin.value]}
        result = services.CarouselService.updateCarousel(params)
        if result == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=result)

    @staticmethod
    @admin_token_decorator()
    def info(request, id, *args, **kwargs):
        '''
        获取单条轮播图信息，根据id查询
        '''
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        data = services.CarouselService.getCarouselById(id)
        if data == None:
            return ResultGenerator.genJsonResponseFailResult(ServiceResultEnum.DATA_NOT_EXIST.value)
        return ResultGenerator.genJsonResponseSuccessResult(
            data={k: v for k, v in data.__dict__.items() if k != '_state'})

    @staticmethod
    @admin_token_decorator()
    def remove(request, *args, **kwargs):
        # 批量删除轮播图信息
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        ids = params_data.get('ids')
        if not (ids == None or isinstance(ids, list) or isinstance(ids, str)):
            ids = [ids]
        if isinstance(ids, str):
            ids = ids.split(',')
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        if ids == None or len(ids) < 1:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        if services.CarouselService.deleteBath(ids):
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message='删除失败')

class CategoryAPI:
    '''
    后踢管理系统分类模块接口
    '''
    @staticmethod
    @admin_token_decorator()
    def list(request, *args, **kwargs):
        # 根据级别和上级分类id查询
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        params = {
            'page': params_data.get('pageNumber') if not (params_data.get('pageNumber') == None or params_data.get('pageNumber') < 1) else 1,
            'pageSize': params_data.get('pageSize') if not (params_data.get('pageSize') == None) else Constants.DEFAULT_PAGESIZE.value,
            'categoryLevel': params_data.get('categoryLevel'),
            'parentId': params_data.get('parentId')
        }
        data = services.CategoryService.getCategorisPage(**params)
        return ResultGenerator.genJsonResponseSuccessResult(data=data)

    @staticmethod
    @admin_token_decorator()
    def listForSelect(request, *args, **kwargs):
        # 用于三级分类联动效果制作
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        categoryId = params_data.get('categoryId', None)
        if categoryId == None or categoryId < 1:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        category = services.CategoryService.getGoodsCategoryById(categoryId)
        # 既不是一级分类也不是二级分类则为不返回数据
        if category == None or category.categoryLevel == CategoryLevelEnum.LEVEL_THREE.value[0]:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        # 如果是一级分类则返回当前一级分类下的所有二级分类，以及二级分类列表中第一条数据下的所有三级分类列表
        categoryResult = {}
        if category.categoryLevel == CategoryLevelEnum.LEVEL_ONE.value[0]:
            # 查询一级分类列表中第一个实体的所有二级分类
            secondLevelCategories = services.CategoryService.selectByLevelAndParentIdsAndNumber([categoryId], CategoryLevelEnum.LEVEL_TWO.value[0])
            if secondLevelCategories.exists():
                # 查询二级分类列表中第一个实体的所有三级分类
                thirdLevelCategories = services.CategoryService.selectByLevelAndParentIdsAndNumber([secondLevelCategories.first().categoryId], CategoryLevelEnum.LEVEL_THREE.value[0])
                categoryResult['secondLevelCategories'] = [item for item in secondLevelCategories.values()]
                categoryResult['thirdLevelCategories'] = [item for item in thirdLevelCategories.values()]
        if category.categoryLevel == CategoryLevelEnum.LEVEL_TWO.value[0]:
            # 如果是二级分类则返回当前分类下的所有三级分类列表
            thirdLevelCategories = services.CategoryService.selectByLevelAndParentIdsAndNumber([categoryId], CategoryLevelEnum.LEVEL_THREE.value[0])
            categoryResult['thirdLevelCategories'] = [item for item in thirdLevelCategories.values()]
        return ResultGenerator.genJsonResponseSuccessResult(data=categoryResult)

    @staticmethod
    @admin_token_decorator()
    def save(request, *args, **kwargs):
        # 新增分类
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        if params_data.get('categoryLevel') == None or params_data.get('categoryName') == None or params_data.get('categoryName') == '' or params_data.get('parentId') == None or params_data.get('categoryRank') == None:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        params = {k: v for k, v in params_data.items() if k not in ['BODY', Constants.Token_To_Admin.value]}
        params.update({
            'isDeleted':0,
            'createUser':adminUser.get('adminUserId'),
            'updateUser': adminUser.get('adminUserId'),
            'createTime':timezone.now(),
            'updateTime':timezone.now()
        })
        result = services.CategoryService.saveCategory(params)
        if result == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=result)

    @staticmethod
    @admin_token_decorator()
    def modify(request, *args, **kwargs):
        # 修改分类信息
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        if params_data.get('categoryId') == None or params_data.get('categoryLevel') == None or params_data.get('categoryName') == None or params_data.get('categoryName') == '' or params_data.get('parentId') == None or params_data.get('categoryRank') == None:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        params = {k: v for k, v in params_data.items() if k not in ['BODY', Constants.Token_To_Admin.value]}
        params.update({
            # 'isDeleted':0,
            # 'createUser':params_data.get(Constants.Token_To_Admin.value).get('adminUserId'),
            'updateUser': adminUser.get('adminUserId'),
            'updateTime': timezone.now()
        })
        result = services.CategoryService.updateGoodsCategory(params)
        if result == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=result)

    @staticmethod
    @admin_token_decorator()
    def info(request, *args, **kwargs):
        # 获取单条分类信息，根据id查询
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        category = services.CategoryService.getGoodsCategoryById(id)
        if category == None:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.DATA_NOT_EXIST.value)
        return ResultGenerator.genJsonResponseSuccessResult(data={k: v for k, v in category.__dict__.items() if k !='_state'})

    @staticmethod
    @admin_token_decorator()
    def remove(request, *args, **kwargs):
        # 批量删除分类信息
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        ids = params_data.get('ids')
        if ids != None and not isinstance(ids, list):
            if isinstance(ids, str):
                ids = ids.split(',')
        if ids != None and not isinstance(ids, list):
            ids = [ids]
        if ids == None or len(ids) < 1:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        if services.CategoryService.deleteBatch(adminUser.get('adminUserId'), ids):
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult('删除失败')

class GoodsAPI:
    '''
    后台管理系统商品模块接口
    '''
    @staticmethod
    @admin_token_decorator()
    def list(request, *args, **kwargs):
        # 商品列表，可根据名称和上架状态筛选
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        pageNumber = params_data.get('pageNumber')
        pageSize = params_data.get('pageSize')
        if pageNumber == None or pageNumber < 1:
            pageNumber = 1
        if pageSize == None or pageSize < 1:
            pageSize = Constants.DEFAULT_PAGESIZE.value
        params = {
            'page': pageNumber,
            'pageSize': pageSize,
            'goodsName': params_data.get('goodsName'),
            'goodsSellStatus': params_data.get('goodsSellStatus'),
        }
        data = services.GoodsService.getGoodsPage(**params)
        return ResultGenerator.genJsonResponseSuccessResult(data=data)

    @staticmethod
    @admin_token_decorator()
    def save(request, *args, **kwargs):
        # 新增商品信息
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        if params_data.get('goodsName') == None or params_data.get('goodsName') == '' or \
                params_data.get('goodsIntro') == None or params_data.get('goodsIntro') == '' or \
                params_data.get('tag') == None or params_data.get('tag') == '' or \
                params_data.get('originalPrice') == None or params_data.get('goodsCategoryId') == None or \
                params_data.get('sellingPrice') == None or params_data.get('stockNum') == None or \
                params_data.get('goodsSellStatus') == None or \
                params_data.get('goodsCoverImg') == None or \
                params_data.get('goodsDetailContent') == None:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        params = {k: v for k, v in params_data.items() if k not in ['BODY', Constants.Token_To_Admin.value]}
        params.update({
            'createUser': adminUser.get('adminUserId'),
            'updateUser': adminUser.get('adminUserId'),
        })
        # params=models.GoodsInfo(**params)
        result = services.GoodsService.saveGoods(params)
        if result == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=result)

    @staticmethod
    @admin_token_decorator()
    def modify(request, *args, **kwargs):
        # 修改商品信息
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        if params_data.get('goodsId') == None or \
                params_data.get('goodsName') == None or params_data.get('goodsName') == '' or \
                params_data.get('goodsIntro') == None or params_data.get('goodsIntro') == '' or \
                params_data.get('tag') == None or params_data.get('tag') == '' or \
                params_data.get('originalPrice') == None or params_data.get('goodsCategoryId') == None or \
                params_data.get('sellingPrice') == None or params_data.get('stockNum') == None or \
                params_data.get('goodsSellStatus') == None or \
                params_data.get('goodsCoverImg') == None or \
                params_data.get('goodsDetailContent') == None:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        params = {k: v for k, v in params_data.items() if k not in ['BODY', Constants.Token_To_Admin.value]}
        params.update({
            'updateUser': adminUser.get('adminUserId'),
            'updateTime': datetime.now()
        })
        # params=models.GoodsInfo(**params)
        result = services.GoodsService.updateGoods(params)
        if result == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=result)

    @staticmethod
    @admin_token_decorator()
    def info(request, id, *args, **kwargs):
        # 获取单挑商品信息，根据id查询
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        params_data=ParseRequestData(request).get_request_data(typecls=dict)
        goods = services.GoodsService.getGoodsById(id)
        if goods == None:
            return ResultGenerator.genJsonResponseFailResult(ServiceResultEnum.DATA_NOT_EXIST.value)
        result = {
            'goods': {k: v for k, v in goods.__dict__.items() if k != '_state'}
        }
        categoryId = goods.goodsCategoryId
        thridCategory = services.CategoryService.getGoodsCategoryById(categoryId)
        if thridCategory != None:
            result['thridCategory'] = {k: v for k, v in thridCategory.__dict__.items() if k != '_state'}
            categoryId = thridCategory.parentId
        secondCategory = services.CategoryService.getGoodsCategoryById(categoryId)
        if secondCategory != None:
            result['secondCategory'] = {k: v for k, v in secondCategory.__dict__.items() if k != '_state'}
            categoryId = secondCategory.parentId
        else:
            result['secondCategory'] = result['thridCategory']
            del result['thridCategory']
        firstCategory = services.CategoryService.getGoodsCategoryById(categoryId)
        if firstCategory != None:
            result['firstCategory'] = {k: v for k, v in firstCategory.__dict__.items() if k != '_state'}
        else:
            temp3 = None
            temp2 = None
            if 'thridCategory' in result:
                temp3 = result['thridCategory']
                del result['thridCategory']
            if 'secondCategory' in result:
                temp2 = result['secondCategory']
                del result['secondCategory']
            if temp2 == None:
                temp2 = temp3
                temp3 = None
            if temp3 != None:
                result['secondCategory'] = temp3
            if temp2 != None:
                result['firstCategory'] = temp2
        return ResultGenerator.genJsonResponseSuccessResult(data=result)

    @staticmethod
    @admin_token_decorator()
    def changeStatus(request, sellStatus, *args, **kwargs):
        # 批量修改销售状态
        params_data = ParseRequestData(request).get_request_data(typecls=dict)  # 当前用户信息
        ids = params_data.get('ids')
        if ids != None and not isinstance(ids, list):
            if isinstance(ids, str):
                ids = ids.split(",")
        if ids != None and not isinstance(ids, list):
            ids = [ids]
        if ids == None or len(ids) < 1:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        if sellStatus != Constants.SELL_STATUS_UP.value and sellStatus != Constants.SELL_STATUS_DOWN.value:
            return ResultGenerator.genJsonResponseFailResult(message="状态异常")
        if services.GoodsService.batchUpdateSellStatus(ids, sellStatus):
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult('删除失败')

class IndexConfigAPI:
    '''
    后台管理系统首页配置模块接口
    '''
    @staticmethod
    @admin_token_decorator()
    def list(request, *args, **kwargs):
        # 首页配置列表
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        pageNumber = params_data.get('pageNumber', 1)
        pageSize = params_data.get('pageSize', Constants.DEFAULT_PAGESIZE.value)
        configType = params_data.get('configType', 1)  # 1-搜索框热搜 2-搜索下拉框热搜 3-(首页)热销商品 4-(首页)新品上线 5-(首页)为你推荐
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        if pageNumber < 1:
            pageNumber = 1
        if pageSize < 1:
            pageSize = Constants.DEFAULT_PAGESIZE.value
        configTypeEnum = IndexConfigTypeEnum.getTypeEnumByCode(configType)
        if configTypeEnum.value == IndexConfigTypeEnum.DEFAULT.value:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        params = {
            'page': pageNumber,
            'pageSize': pageSize,
            'configType': configType
        }
        data = services.IndexConfigService.getConfigsPage(**params)
        return ResultGenerator.genJsonResponseSuccessResult(data=data)

    @staticmethod
    @admin_token_decorator()
    def save(request, *args, **kwargs):
        # 新增首页配置项
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        if params_data.get('configType') == None or \
                params_data.get('configName') == None or \
                params_data.get('configName') == '' or \
                params_data.get('configRank') == None:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        params = {k: v for k, v in params_data.items() if k not in ['BODY', Constants.Token_To_Admin.value]}
        params.update({
            'createUser': adminUser.get('adminUserId'),
            'updateUser': adminUser.get('adminUserId'),
            'isDeleted': 0
        })
        result = services.IndexConfigService.saveIndexConfig(params)
        if result == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=result)

    @staticmethod
    @admin_token_decorator()
    def modify(request, *args, **kwargs):
        # 修改首页配置项
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        if params_data.get('configId') == None or \
                params_data.get('configType') == None or \
                params_data.get('configName') == None or \
                params_data.get('configName') == '' or \
                params_data.get('configRank') == None:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        params = {k: v for k, v in params_data.items() if k not in ['BODY', Constants.Token_To_Admin.value]}
        params.update({
            'updateUser': adminUser.get('adminUserId'),
            'updateTime': datetime.now()
        })
        result = services.IndexConfigService.updateIndexConfig(params)
        if result == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=result)

    @staticmethod
    @admin_token_decorator()
    def info(request, id, *args, **kwargs):
        # 获取单挑首页配置项消息，根据id查询
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        config = services.IndexConfigService.getIndexConfigById(id)
        if config == None:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.DATA_NOT_EXIST.value)
        return ResultGenerator.genJsonResponseSuccessResult(data={k: v for k, v in config.__dict__.items() if k != '_state'})

    @staticmethod
    @admin_token_decorator()
    def remove(request, *args, **kwargs):
        # 批量修改首页配置项
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        ids = params_data.get('ids')
        if ids != None and not isinstance(ids, list):
            if isinstance(ids, str):
                ids = ids.split(",")
        if ids != None and not isinstance(ids, list):
            ids = [ids]
        if ids == None or len(ids) < 1:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)  # 当前用户信息
        if services.IndexConfigService.deleteBatch(adminUser.get('adminUserId'), ids):
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult('删除失败')

class AdminUserAPI:
    '''
    后台管理系统管理员模块接口
    '''

    @staticmethod
    def login(request, *args, **kwargs):
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        userName = params_data.get('userName')
        passwordMd5 = params_data.get('passwordMd5')
        result = services.AdminUserService.login(userName, passwordMd5)
        logger.info("manage login api,adminName={},result={}".format(userName, result))
        # 登录成功
        if len(result) == Constants.TOKEN_LENGTH.value:
            return ResultGenerator.genJsonResponseSuccessResult(data=result)
        return ResultGenerator.genJsonResponseFailResult(message=result)

    @staticmethod
    @admin_token_decorator()
    def profile(request, *args, **kwargs):
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        admin = services.AdminUserService.getUserDetailById(adminUser.get('adminUserId'))
        if adminUser != None:
            admin.loginPassword = '******'
            return ResultGenerator.genJsonResponseSuccessResult(data={k: v for k, v in admin.__dict__.items() if k != '_state'})
        return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.DATA_NOT_EXIST.value)

    @staticmethod
    @admin_token_decorator()
    def password(request, *args, **kwargs):
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        originalPassword = params_data.get('originalPassword')
        newPassword = params_data.get('newPassword')
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        if originalPassword == None or originalPassword == '' or newPassword == None or newPassword == '':
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        if services.AdminUserService.updatePassword(adminUser.get('adminUserId'), originalPassword, newPassword):
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.DB_ERROR.value)

    @staticmethod
    @admin_token_decorator()
    def name(request, *args, **kwargs):
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        loginName = params_data.get('loginUserName')
        nickName = params_data.get('nickName')
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        if nickName == None or nickName == '':
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        if services.AdminUserService.updateName(adminUser.get('adminUserId'), loginName, nickName):
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.DB_ERROR.value)

    @staticmethod
    @admin_token_decorator()
    def logout(request, *args, **kwargs):
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value,None)
        if services.AdminUserService.logout(adminUser.get('adminUserId')):
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult()

class OrderAPI:
    '''
    后台管理系统订单模块接口
    '''
    @staticmethod
    @admin_token_decorator()
    def list(request, *args, **kwargs):
        # 订单列表，可根据订单号和订单状态筛选
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        pageNumber = params_data.get('pageNumber', 1)
        pageSize = params_data.get('pageSize', Constants.DEFAULT_PAGESIZE.value)
        orderStatus = params_data.get('orderStatus')
        orderNo = params_data.get('orderNo')
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        params = {
            'page': pageNumber,
            'pageSize': pageSize,
        }
        if orderNo != None: params['orderNo'] = orderNo
        if orderStatus != None: params['orderStatus'] = orderStatus
        data = services.OrderService.getOrdersPage(**params)
        return ResultGenerator.genJsonResponseSuccessResult(data=data)

    @staticmethod
    @admin_token_decorator()
    def modify(request, *args, **kwargs):
        # 修改订单价格
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        if params_data.get('totalPrice') == None or params_data.get('orderId') == None or \
                params_data.get('orderId') < 1 or params_data.get('totalPrice') < 1:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        params = {k: v for k, v in params_data.items() if k not in ['BODY', Constants.Token_To_Admin.value]}
        params.update({
            'updateTime': timezone.now()
        })
        result = services.OrderService.updateOrderInfo(params)
        if result == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=result)

    @staticmethod
    @admin_token_decorator()
    def info(request, *args, **kwargs):
        # 获取订单项数据，根据id查询
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        orderItems = services.OrderService.getOrderItems(id)
        if orderItems.exists():
            data = [item for item in orderItems.values()]
            return ResultGenerator.genJsonResponseSuccessResult(data=data)
        return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.DATA_NOT_EXIST.value)

    @staticmethod
    @admin_token_decorator()
    def detail(request, id, *args, **kwargs):
        # 订单详情接口，传参为订单号
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        data = services.OrderService.getOrderDetailByOrderId(id)
        return ResultGenerator.genJsonResponseSuccessResult(data=data)

    @staticmethod
    @admin_token_decorator()
    def checkDone(request, *args, **kwargs):
        # 修改订单状态为配货成功，批量修改
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        ids = params_data.get('ids')
        if ids != None and not isinstance(ids, list):
            if isinstance(ids, str):
                ids = ids.split(",")
        if ids != None and not isinstance(ids, list):
            ids = [ids]
        if ids == None or len(ids) < 1:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        result = services.OrderService.checkDone(ids)
        if result == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=result)

    @staticmethod
    @admin_token_decorator()
    def checkOut(request, *args, **kwargs):
        # 修改订单状态为已出库，批量修改
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        ids = params_data.get('ids')
        if ids != None and not isinstance(ids, list):
            if isinstance(ids, str):
                ids = ids.split(",")
        if ids != None and not isinstance(ids, list):
            ids = [ids]
        if ids == None or len(ids) < 1:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        result = services.OrderService.checkOut(ids)
        if result == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=result)

    @staticmethod
    @admin_token_decorator()
    def closeOrder(request, *args, **kwargs):
        # 修改订单状态为商家关闭，批量修改
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        ids = params_data.get('ids')
        if ids != None and not isinstance(ids, list):
            if isinstance(ids, str):
                ids = ids.split(",")
        if ids != None and not isinstance(ids, list):
            ids = [ids]
        if ids == None or len(ids) < 1:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        result = services.OrderService.closeOrder(ids)
        if result == ServiceResultEnum.SUCCESS.value:
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message=result)

class UserAPI:
    '''
    后台管理系统注册用户模块接口
    '''
    @staticmethod
    @admin_token_decorator()
    def list(request, *args, **kwargs):
        # 商城注册用户列表
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        pageNumber = params_data.get('pageNumber', 1)
        pageSize = params_data.get('pageSize', Constants.DEFAULT_PAGESIZE.value)
        lockStatus = params_data.get('lockStatus')
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        params = {
            'page': pageNumber,
            'pageSize': pageSize,
        }
        if lockStatus != None:
            params.update({'lockedFlag': lockStatus})
        data = services.UserService.getUsersPage(**params)
        return ResultGenerator.genJsonResponseSuccessResult(data=data)

    @staticmethod
    @admin_token_decorator()
    def lock(request, lockStatus, *args, **kwargs):
        # 修改用户状态，批量修改，用户禁用与解除禁用（0-未锁定 1-已锁定）
        params_data = ParseRequestData(request).get_request_data(typecls=dict)
        ids = params_data.get('ids')
        if ids != None and not isinstance(ids, list):
            if isinstance(ids, str):
                ids = ids.split(",")
        if ids != None and not isinstance(ids, list):
            ids = [ids]
        if ids == None or len(ids) < 1:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        if lockStatus != 0 and lockStatus != 1:
            return ResultGenerator.genJsonResponseFailResult(message=ServiceResultEnum.PARAM_ERROR.value)
        if services.UserService.lockUsers(ids, lockStatus):
            return ResultGenerator.genJsonResponseSuccessResult()
        return ResultGenerator.genJsonResponseFailResult(message="禁用失败")

class UploadAPI:
    '''
    后台管理系统文件上传接口
    '''
    @staticmethod
    @admin_token_decorator()
    def upload(request, *args, **kwargs):
        # 单图上传
        file = request.FILES.get('file')
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_NAME.value, None)
        if file == None:
            return ResultGenerator.genJsonResponseFailResult(message='文件上传失败')
        # 上传文件的目录
        dest_dir = Path(settings.BASE_DIR / Constants.FILE_UPLOAD_DIC.value)
        if not dest_dir.exists():  # 上传目录如果不存在，则创建
            os.makedirs(dest_dir)
        # 获取上传文件的扩展名
        suffix_index = file.name.rfind('.')
        suffix_name = ''
        if suffix_index != 1:
            suffix_name = file.name[suffix_index:]  # 字符串切片
        # 构建新文件名 YYYYMMDD_HHMMSS + 四位随机数字
        filename = timezone.now().strftime('%Y%m%d_%H%M%S') + str(NumberUtil.genRandomNum(4) + suffix_name)
        fname = os.path.join(settings.BASE_DIR / Constants.FILE_UPLOAD_DIC.value, filename)  # 完整文件名
        # 写文件
        with open(fname, 'wb') as f:
            f.write(file.file.read())
        # 返回文件名
        return ResultGenerator.genJsonResponseSuccessResult(data=Constants.FILE_UPLOAD_DIC.value + filename)

    @staticmethod
    @admin_token_decorator()
    def uploadV2(request, *args, **kwargs):
        # 多图上传， wangEditor图片上传
        adminUser = kwargs.get(Constants.TOKEN_DECORATOR_PARAM_NAME.value, None)
        # 判断是否有文件上传
        if request.FILES == None or len(request.FILES) == 0:
            return ResultGenerator.genJsonResponseFailResult(message='无文件上传')
        # 上传文件的目录
        dest_dir = Path(settings.BASE_DIR / Constants.FILE_UPLOAD_DIC.value)
        if not dest_dir.exists():  # 上传目录如果不存在，则创建
            os.makedirs(dest_dir)
        success_files = []  # 成功上传的文件名
        for files in request.FILES:  # 多个上传的键
            for file in request.FILES.getlist(files):  # 遍历指定键下的所有文件
                # 获取上传文件的扩展名
                suffix_index = file.name.rfind('.')
                suffix_name = ''
                if suffix_index != -1:
                    suffix_name = file.name[suffix_index:]  # 字符串切片
                # 构建新文件名 YYYYMMDD_HHMMSS +四位随机数字
                filename = timezone.now().strftime('%Y%m%d_%H%M%S') + str(NumberUtil.genRandomNum(4)) + suffix_name
                fname = os.path.join(settings.BASE_DIR / Constants.FILE_UPLOAD_DIC.value, filename)  # 完整文件名
                # 写文件
                with open(fname, 'wb') as f:
                    f.write(file.file.read())
                success_files.append(Constants.FILE_UPLOAD_DIC.value + filename)
            return ResultGenerator.genJsonResponseSuccessResult(data=success_files)




