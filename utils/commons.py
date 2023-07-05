import json
import math
import random
import re
import time
from enum import Enum
from hashlib import md5

from django.http import JsonResponse


class NumberUtil:
    #  与数字处理相关的工具类
    @staticmethod
    def genRandomNum(length):
        # 生成指定长度的随机数
        n = random.randint(1, 9)
        result = n
        for i in range(1, length):
            n = random.randint(0, 9)
            result = result * 10 + n
        return result

    @staticmethod
    def genOrderNo():
        now = int(time.time() * 1000)
        num = NumberUtil.genRandomNum(4)
        return str(now) + str(num)

    @staticmethod
    def isPhone(phone):
        result = re.match("^((13[0-9])|(14[5,7])|(15[^4,\\D])|(17[0-8])|(18[0-9]))\\d{8}$", str(phone))
        return result != None


class SystemUtil:
    @staticmethod
    def genToken(src):
        '''
        登录或注册成功后,生成保持用户登录状态会话token值
        :param src:为用户最新一次登录时的now()+user.id+random(6)
        :return:
        '''
        if src == None or src == '':
            return None
        result = md5(src.encode('utf-8')).hexdigest()
        if len(result) == 31:
            result = result + '_'
        return result


class ServiceResultEnum(Enum):
    SUCCESS = (0, "success")
    ERROR = (-1, "error")
    DB_ERROR = (-2, "database error")
    DATA_NOT_EXIST = (-10, "未查询到记录！")
    PARAM_ERROR = (-11, "参数错误！")
    SAME_CATEGORY_EXIST = (-12, "有同级同名的分类！")
    SAME_LOGIN_NAME_EXIST = (-13, "用户名已存在！")
    LOGIN_NAME_NULL = (-14, "请输入登录名！")
    LOGIN_NAME_IS_NOT_PHONE = (-15, "请输入正确的手机号！")
    LOGIN_PASSWORD_NULL = (-16, "请输入密码！")
    LOGIN_VERIFY_CODE_NULL = (-17, "请输入验证码！")
    LOGIN_VERIFY_CODE_ERROR = (-18, "验证码错误！")
    LOGIN_NAME_NOT_EXISTS = (-19, "用户名不存在！")
    LOGIN_PASSWORD_INVALID = (-20, "密码错误！")
    GOODS_NOT_EXIST = (-21, "商品不存在！")
    GOODS_PUT_DOWN = (-22, "商品已下架！")
    SHOPPING_CART_ITEM_LIMIT_NUMBER_ERROR = (-23, "超出单个商品的最大购买数量！")
    SHOPPING_CART_ITEM_NUMBER_ERROR = (-24, "商品数量不能小于 1 ！")
    SHOPPING_CART_ITEM_TOTAL_NUMBER_ERROR = (-25, "超出购物车最大容量！")
    SHOPPING_CART_ITEM_EXIST_ERROR = (-26, "已存在！无需重复添加！")
    LOGIN_ERROR = (-27, "登录失败！")
    NOT_LOGIN_ERROR = (-28, "未登录！")
    ADMIN_NOT_LOGIN_ERROR = (-29, "管理员未登录！")
    TOKEN_EXPIRE_ERROR = (-30, "无效认证！请重新登录！")
    ADMIN_TOKEN_EXPIRE_ERROR = (-31, "管理员登录过期！请重新登录！")
    USER_NULL_ERROR = (-32, "无效用户！请重新登录！")
    LOGIN_USER_LOCKED_ERROR = (-33, "用户已被禁止登录！")
    ORDER_NOT_EXIST_ERROR = (-34, "订单不存在！")
    NULL_ADDRESS_ERROR = (-35, "地址不能为空！")
    ORDER_PRICE_ERROR = (-36, "订单价格异常！")
    ORDER_ITEM_NULL_ERROR = (-37, "订单项异常！")
    ORDER_GENERATE_ERROR = (-38, "生成订单异常！")
    SHOPPING_ITEM_ERROR = (-39, "购物车数据异常！")
    SHOPPING_ITEM_COUNT_ERROR = (-40, "库存不足！")
    ORDER_STATUS_ERROR = (-41, "订单状态异常！")
    OPERATE_ERROR = (-42, "操作失败！")
    REQUEST_FORBIDEN_ERROR = (-43, "禁止该操作！")


class PageResult:
    def __init__(self, list, totalCont, pageSize, currPage):
        self.pageSize = pageSize
        self.currPage = currPage
        self.totalCont = totalCont
        if totalCont == None or pageSize == None:
            self.totalCont = 1
        else:
            self.totalPage = int(math.ceil(totalCont / pageSize))
        self.list = list


class Constants(Enum):
    DEFAULT_SELECT_LIMIT = 1000
    DEFAULT_PAGESIZE = 10
    FILE_UPLOAD_DIC = "\\upload\\"  # 上传文件的默认url前缀，根据部署设置自行修改
    INDEX_CAROUSEL_NUMBER = 5  # 首页轮播图数量
    INDEX_CATEGORY_NUMBER = 10  # 首页一级分类的最大数量
    INDEX_GOODS_HOT_NUMBER = 4  # 首页热卖商品数量
    INDEX_GOODS_NEW_NUMBER = 5  # 首页新品数量
    INDEX_GOODS_RECOMMOND_NUMBER = 10  # 首页推荐商品数量
    SHOPPING_CART_ITEM_TOTAL_NUMBER = 20  # 购物车中商品的最大数量
    SHOPPING_CART_ITEM_LIMIT_NUMBER = 5  # 购物车中单个商品的最大购买数量
    GOODS_SEARCH_PAGE_LIMIT = 10  # 搜索分页的默认条数（每页10条）
    SHOPPING_CART_PAGE_LIMIT = 5
    ORDER_SEARCH_PAGE_LIMIT = 5  # 我的订单列表分页的默认条数（每页5条）
    SELL_STATUS_UP = 0  # 商品上架状态
    SELL_STATUS_DOWN = 1  # 商品下架状态
    TOKEN_LENGTH = 32
    USER_INTRO = "随新所欲，蜂富多彩"
    Token_To_User = "userToken"
    Token_To_Admin = "adminUserToken"
    TOKEN_DECORATOR_PARAM_NAME = "user"


class CategoryLevelEnum(Enum):
    DEFAULT = 0, "ERROR"
    LEVEL_ONE = 1, "一级分类"
    LEVEL_TWO = 2, "二级分类"
    LEVEL_THREE = 3, "三级分类"


class OrderStatusEnum(Enum):
    DEFAULT = -9, "ERROR"
    ORDER_PRE_PAY = 0, "待支付"
    OREDER_PAID = 1, "已支付"
    OREDER_PACKAGED = 2, "配货完成"
    OREDER_EXPRESS = 3, "出库成功"
    ORDER_SUCCESS = 4, "交易成功"
    ORDER_CLOSED_BY_MALLUSER = -1, "手动关闭"
    ORDER_CLOSED_BY_EXPIRED = -2, "超时关闭"
    ORDER_CLOSED_BY_JUDGE = -3, "商家关闭"

    @classmethod
    def getOrderStatusEnumByCode(cls, code):
        for item in OrderStatusEnum:
            if item.value[0] == code:
                return item


class PayTypeEnum(Enum):
    DEFAULT = -1, "ERROR"
    NOT_PAY = 0, "无"
    ALI_PAY = 1, "支付宝"
    WEIXIN_PAY = 2, "微信支付"

    @classmethod
    def getPayTypeEnumByCode(cls, code):
        for item in PayTypeEnum:
            if item.value[0] == code:
                return item


class PayStatusEnum(Enum):
    DEFAULT = -1, "支付失败"
    PAY_ING = 0, "支付中"
    PAY_SUCCESS = 1, "支付成功"


class ParseRequestData:
    '''
    解析请求参数
    '''

    class ParamType(Enum):
        '''
        获取参数的位置
        '''
        GET_ONLY = 1  # 解析GET数据
        POST_ONLY = 2  # 解析POST表单数据
        BODY_ONLY = 3  # 解析输入流
        FILE_ONLY = 4  # 解析文件
        COOKIE_ONLY = 5  # 解析COOKIE
        SESSION_ONLY = 6  # 解析SESSION
        GET_POST = 7  # 同时解析GET和POST表单数据
        GET_POST_BODY = 8  # 同时解析GET、POST和输入留

    '''
    解析request中的数据
    '''

    def __init__(self, request):
        self.__request = request
        self.__data = {}  # 数据缓存变量
        self.__parseData()  # 具体获取request中的数据的方法

    def __parseData(self):
        '''
        获取request对象的各种数据
        :return:
        '''
        # GET数据
        GET = {k: v for k, v in self.__request.GET.items()}
        # POST
        POST = {k: v for k, v in self.__request.POST.items()}
        # FILES
        FILES = self.__request.FILES
        # COOKIES
        COOKIES = self.__request.COOKIES
        # BODY
        BODY = self.__request.body
        # SESSION
        SESSION = {}
        if self.__request != None and len(self.__request.session.items()) > 0:
            SESSION = {k: v for k, v in self.__request.session.items()}

        result = {
            'GET': GET,
            'POST': POST,
            'BODY': BODY,
            'FILES': FILES,
            'COOKIES': COOKIES,
            'SESSION': SESSION
        }
        self.__data = result

    def __to_dict(self, data):
        '''
        递归将数据解析为dict
        :param data:
        :return:
        '''
        try:
            result = json.loads(data)
        except:
            return data
        if isinstance(result, list):
            sub_result = []
            for item in result:
                if item != None:
                    if isinstance(item, str):
                        sub_result.append(self.__to_dict(item))
                        continue
                sub_result.append(item)
            result = sub_result
        elif isinstance(result, dict):
            sub_result = {}
            for key in result:
                if result.get(key) != None:
                    if isinstance(result.get(key), str):
                        sub_result[key] = self.__to_dict(result.get(key))
                        continue
                sub_result[key] = result.get(key)
            result = sub_result
        return result

    def get_request_data(self, *, param_type=ParamType.GET_POST_BODY, key=None, default=None, typecls=str):
        '''
        获取数据的方法
        :param param_type: 获取参数类型
        :param key: 键
        :param default: 默认值
        :param typecls: 数据类型
        :return:
        '''
        data = None
        if param_type in [ParseRequestData.ParamType.FILE_ONLY, ParseRequestData.ParamType.BODY_ONLY]:
            # 解析文件和输入流
            if param_type == ParseRequestData.ParamType.BODY_ONLY:
                data = self.__data.get('BODY', default)  # bytes
            elif param_type == ParseRequestData.ParamType.FILE_ONLY:
                data = {k: self.__data.get('FILES').getlist(k) for k in self.__data.get('FILES')}
                if key != None:
                    data = data.get(key, default)
        else:  # 需要按数据类型解析
            if key == None:
                if param_type == ParseRequestData.ParamType.GET_ONLY:
                    data = self.__data.get('GET', default)
                elif param_type == ParseRequestData.ParamType.POST_ONLY:
                    data = self.__data.get('POST', default)
                elif param_type == ParseRequestData.ParamType.COOKIE_ONLY:
                    data = self.__data.get('COOKIES', default)
                elif param_type == ParseRequestData.ParamType.SESSION_ONLY:
                    data = self.__data.get('SESSION', default)
                elif param_type == ParseRequestData.ParamType.GET_POST:
                    data = self.__data.get('GET', {})
                    data.update(self.__data.get('POST', {}))
                    if len(data) == 0:
                        data = default
                elif param_type == ParseRequestData.ParamType.GET_POST_BODY:
                    data = {
                        'GET': self.__data.get('GET', default),
                        'POST': self.__data.get('POST', default),
                        'BODY': self.__data.get('BODY', default),
                    }
            else:
                if param_type == ParseRequestData.ParamType.GET_ONLY:
                    data = self.__data.get('GET', {}).get(key, default)
                elif param_type == ParseRequestData.ParamType.POST_ONLY:
                    data = self.__data.get('POST', {}).get(key, default)
                elif param_type == ParseRequestData.ParamType.COOKIE_ONLY:
                    data = self.__data.get('COOKIES', {}).get(key, default)
                elif param_type == ParseRequestData.ParamType.SESSION_ONLY:
                    data = self.__data.get('SESSION', {}).get(key, default)
                elif param_type == ParseRequestData.ParamType.GET_POST:
                    data = self.__data.get('GET', {})
                    data.update(self.__data.get('POST', {}))
                    data = data.get(key, default)
                elif param_type == ParseRequestData.ParamType.GET_POST_BODY:
                    data = self.__data.get('GET', {})
                    data.update(self.__data.get('POST', {}))
                    data = data.get(key, None)
                    if data == None:
                        data = self.__data.get('BODY', b'')

        if param_type != ParseRequestData.ParamType.FILE_ONLY:
            if data != None:
                if typecls == str:
                    if isinstance(data, bytes):
                        if data == b'':
                            data = default
                        else:
                            data = data.decode('utf-8')
                    data = str(data)
                if isinstance(data, str):
                    if typecls == int:
                        if isinstance(data, bytes):
                            if data == b'':
                                data = default
                            else:
                                data = data.decode('utf-8')
                        data = int(data)
                    elif typecls == float:
                        if isinstance(data, bytes):
                            if data == b'':
                                data = default
                            else:
                                data = data.decode('utf-8')
                        data = float(data)
                    elif typecls == list:
                        if isinstance(data, bytes):
                            if data == b'':
                                data = default
                            else:
                                data = data.decode('utf-8')
                        data = json.loads(data)
                    elif typecls == dict:
                        if isinstance(data, bytes):
                            if data == b'':
                                data = default
                            else:
                                data = data.decode('utf-8')
                        data = json.loads(data)
                elif isinstance(data, list):
                    if typecls == list or typecls == dict:
                        sub_data = []
                        for item in data:
                            if isinstance(item, bytes):
                                if item == b'':
                                    item = default
                                else:
                                    item = item.decode('utf-8')
                            try:
                                if isinstance(item, str):
                                    sub_data.append(json.loads(item))
                                    continue
                            except:
                                pass
                            sub_data.append(item)
                        data = sub_data
                elif isinstance(data, dict):
                    if typecls == list or typecls == dict:
                        sub_data = {}
                        for key in data:
                            if data.get(key) != None:
                                item = data.get(key)
                                if isinstance(item, bytes):
                                    if item == b'':
                                        item = default
                                    else:
                                        item = item.decode('utf-8')
                                try:
                                    if isinstance(item, str):
                                        sub_data[key] = json.loads(item)
                                        continue
                                except:
                                    pass
                            sub_data[key] = data.get(key)
                        data = sub_data
        if param_type == ParseRequestData.ParamType.GET_POST_BODY:
            if typecls == dict:
                temp = {}
                temp.update(data.get('GET', {}))
                temp.update(data.get('POST', {}))
                if isinstance(data.get('BODY'), dict):
                    temp.update(data.get('BODY', {}))
                else:
                    temp['BODY'] = data.get('BODY')
                # data=temp
                data = {k: self.__to_dict(v) for k, v in temp.items()}
            elif typecls == list:
                temp = []
                if isinstance(data.get('GET'), list):
                    temp = temp + data.get('GET')
                else:
                    temp.append(data.get('GET'))
                if isinstance(data.get('POST'), list):
                    temp = temp + data.get('POST')
                else:
                    temp.append(data.get('POST'))
                if isinstance(data.get('BODY'), list):
                    temp = temp + data.get('BODY')
                else:
                    temp.append(data.get('BODY'))
                # data=temp
                data = [self.__to_dict(v) for v in temp]
        return data


def get_request_params(request, *, key, default=None, typecls=str):
    '''
    解析请求参数
    :param request:
    :param key: 参数名
    :param default: 参数的默认值
    :param typecls: 参数的数据类型
    :return:
    '''
    result = None
    if request.method == 'GET':
        result = request.GET.get(key, default)
    elif request.method == 'POST':
        result = request.POST.get(key, default)
    else:
        result = request.body
        if typecls == list or typecls == dict:
            if result != None:
                result = result.decode('utf-8')
    if request.method != 'GET' and (result == None or result == ''):
        result = request.GET.get(key, default)
    if result != None:
        if typecls == str:
            pass
        elif typecls == int:
            result = int(result)
        elif typecls == list:
            result = json.loads(result)
        elif typecls == dict:
            result = json.loads(result)
    return result


class Result:
    '''
    响应信息的格式
    '''

    def __init__(self, *, resultCode=None, message=None, data=None):
        self.resultCode = resultCode  # 业务码，比如成功、失败、权限不足等 code，可自行定义
        self.message = message  # 返回信息，后端在进行业务处理后返回给前端一个提示信息，可自行定义
        self.data = data  # 数据结果，泛型，可以是列表、单个对象、数字、布尔值等


class ResultGenerator:
    '''
    响应结果生成工具
    '''
    DEFAULT_SUCCESS_MESSAGE = "SUCCESS"
    DEFAULT_FAIL_MESSAGE = "FAIL"
    RESULT_CODE_SUCCESS = 200
    RESULT_CODE_SERVER_ERROR = 500

    @staticmethod
    def __parseBytes(data):
        pass

    @staticmethod
    def genSuccessResult(*, message=None, data=None):
        result = Result(resultCode=ResultGenerator.RESULT_CODE_SUCCESS)
        if message == None:
            result.message = ResultGenerator.DEFAULT_SUCCESS_MESSAGE
        else:
            result.message = message
        if data != None:
            result.data = data
        return result

    @staticmethod
    def genJsonResponseSuccessResult(*, message=None, data=None):
        if data != None:
            if not isinstance(data, dict) and \
                    not isinstance(data, list) and \
                    not isinstance(data, str) and \
                    not isinstance(data, float) and \
                    not isinstance(data, int):
                data = data.__dict__
        result = ResultGenerator.genSuccessResult(message=message, data=data)
        return JsonResponse(result.__dict__, safe=False)

    @staticmethod
    def genFailResult(*, message=None, data=None):
        result = Result(resultCode=ResultGenerator.RESULT_CODE_SERVER_ERROR)
        if message == None:
            result.message = ResultGenerator.DEFAULT_FAIL_MESSAGE
        else:
            result.message = message
        if data != None:
            result.data = data
        return result

    @staticmethod
    def genJsonResponseFailResult(*, message=None, data=None):
        if data != None:
            if not isinstance(data, dict) and \
                    not isinstance(data, list) and \
                    not isinstance(data, str) and \
                    not isinstance(data, float) and \
                    not isinstance(data, int):
                data = data.__dict__
        result = ResultGenerator.genFailResult(message=message, data=data)
        return JsonResponse(result.__dict__, safe=False)

    @staticmethod
    def genResult(*, resultCode=None, message=None, data=None):
        result = Result()
        if resultCode != None:
            result.resultCode = resultCode
        else:
            result.resultCode = ResultGenerator.RESULT_CODE_SERVER_ERROR
        if message != None:
            result.message = message
        else:
            result.message = ResultGenerator.DEFAULT_FAIL_MESSAGE
        if data != None:
            result.data = data
        return result

    @staticmethod
    def genJsonResponseResult(*, resultCode=None, message=None, data=None):
        if data != None:
            if not isinstance(data, dict) and \
                    not isinstance(data, list) and \
                    not isinstance(data, str) and \
                    not isinstance(data, float) and \
                    not isinstance(data, int):
                data = data.__dict__
        result = ResultGenerator.genResult(resultCode=resultCode, message=message, data=data)
        return JsonResponse(result.__dict__, safe=False)


class IndexConfigTypeEnum(Enum):
    DEFAULT = 0, "DEFAULT"
    INDEX_SEARCH_HOTS = 1, "INDEX_SEARCH_HOTS"
    INDEX_SEARCH_DOWN_HOTS = 2, "INDEX_SEARCH_DOWN_HOTS"
    INDEX_GOODS_HOT = 3, "INDEX_GOODS_HOTS"
    INDEX_GOODS_NEW = 4, "INDEX_GOODS_NEW"
    INDEX_GOODS_RECOMMOND = 5, "INDEX_GOODS_RECOMMOND"

    @staticmethod
    def getTypeEnumByCode(cls, code):
        result = IndexConfigTypeEnum.DEFAULT
        for item in IndexConfigTypeEnum:
            if item.value[0] == code:
                result = item
                break
        return result
