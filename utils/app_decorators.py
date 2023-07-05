'''
项目装饰器
'''
from api import services
from utils.commons import Constants

def user_token_decorator(required=True):
    def __wraper1(func):
        def __wraper2(request, *args, **kwargs):
            # 获取请求的token
            token = request.headers.get('token', None)

            if token == None or token == '':
                if not request == True:
                    return func(request, *args, **kwargs)
                else:  # 如果要求有token，但是又没接收到，应该是抛异常
                    return func(request, *args, **kwargs)

                # 由token查询用户信息
            data = services.UserTokenService.getUserInfoByToken(token)
            if data != None:
                param = {
                    Constants.TOKEN_DECORATOR_PARAM_NAME.value: data.get(Constants.Token_To_User.value)
                }
                return func(request, *args, token=data.get('token'), **param, **kwargs)
            return func(request, *args, **kwargs)
        return __wraper2
    return __wraper1

def admin_token_decorator(required=True):
    def __wraper1(func):
        def __wraper2(request, *args, **kwargs):
            # 获取请求的token
            token = request.headers.get('token', None)

            if token == None or token == '':
                if not request == True:
                    return func(request, *args, **kwargs)
                else:  # 如果要求有token，但是又没接收到，应该是抛异常
                    return func(request, *args, **kwargs)

            # 由token查询用户信息
            data = services.AdminUserTokenService.getUserInfoByToken(token)
            if data != None:
                param = {
                    Constants.TOKEN_DECORATOR_PARAM_NAME.value: data.get(Constants.Token_To_Admin.value)
                }
                return func(request, *args, token=data.get('token'), **param, **kwargs)
            return func(request, *args, **kwargs)
        return __wraper2
    return __wraper1

