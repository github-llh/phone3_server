from utils.commons import ServiceResultEnum

if __name__ == '__main__':
    # print(random.randint(0,10))
    # print(NumberUtil.genRandomNum(6))

    # print(SystemUtil.genToken('abc'))
    # import time
    # print(time.time()*1000)

    # print(datetime.utcfromtimestamp(time.time()))
    # print(datetime.fromtimestamp(time.time()))

    # from datetime import datetime
    # print(datetime.now())

    class A:
        def __init__(self):
            self.a='a'
            self.b='b'
    print(dir(A))
    print(A.__dict__)
    print(A.__dict__.items())
    print(ServiceResultEnum.LOGIN_NAME_NOT_EXISTS.value[0])



