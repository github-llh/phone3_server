from django.db import models

# Create your models here.

class AdminUser(models.Model):
    adminUserId = models.BigAutoField(db_column='admin_user_id', primary_key=True)
    loginUserName = models.CharField(db_column='login_user_name', max_length=50)
    loginPassword = models.CharField(db_column='login_password', max_length=50)
    nickName = models.CharField(db_column='nick_name', max_length=50)
    locked = models.IntegerField(db_column='locked')

    class Meta:
        db_table = 'admin_user'

class AdminUserToken(models.Model):
    adminUserId = models.BigIntegerField(db_column='admin_user_id', primary_key=True)
    token = models.CharField(db_column='token', max_length=32)
    updateTime = models.DateTimeField(db_column='update_time')
    expireTime = models.DateTimeField(db_column='expire_time')

    class Meta:
        db_table = 'admin_user_token'

class Carousel(models.Model):
    carouselId = models.BigAutoField(db_column='carousel_id', primary_key=True)
    carouselUrl = models.CharField(db_column='carousel_url', max_length=100)
    redirectUrl = models.CharField(db_column='redirect_url', max_length=100)
    carouselRank = models.IntegerField(db_column='carousel_rank', default=0)
    isDeleted = models.IntegerField(db_column='is_deleted', default=0)
    createUser = models.IntegerField(db_column='create_user')
    createTime = models.DateTimeField(db_column='create_time', auto_now_add=True)
    updateUser = models.IntegerField(db_column='update_user', null=True)
    updateTime = models.DateTimeField(db_column='update_time', null=True, auto_now=True)

    class Meta:
        db_table = 'carousel'

class GoodsCategory(models.Model):
    categoryId = models.IntegerField(db_column='category_id', primary_key=True)
    categoryLevel = models.IntegerField(db_column='category_level', default=0)
    parentId = models.IntegerField(db_column='parent_id', default=0)
    categoryName = models.CharField(db_column='category_name', max_length=50, default='')
    categoryRank = models.IntegerField(db_column='category_rank', default=0)
    isDeleted = models.IntegerField(db_column='is_deleted', default=0)
    createTime = models.DateTimeField(db_column='create_time', auto_now_add=True)
    createUser = models.IntegerField(db_column='create_user', default=0)
    updateTime = models.DateTimeField(db_column='update_time', auto_now=True, null=True)
    updateUser = models.IntegerField(db_column='update_user', null=True, default=0)

    class Meta:
        db_table = 'goods_category'

class GoodsInfo(models.Model):
    goodsId = models.IntegerField(db_column='goods_id', primary_key=True)
    goodsName = models.CharField(db_column='goods_name', max_length=200, default='')
    goodsIntro = models.CharField(db_column='goods_intro', max_length=200, default='')
    goodsCategoryId = models.IntegerField(db_column='goods_category_id', default=0)
    goodsCoverImg = models.CharField(db_column='goods_cover_img', max_length=200, default='/admin/dist/img/no-img.png')
    goodsCaroysel = models.CharField(db_column='goods_carousel', max_length=500, default='/admin/dist/img/no-img.png', null=True)
    goodsDetailContent = models.TextField(db_column='goods_detail_content')
    originalPrice = models.DecimalField(db_column='original_price', max_digits=18, decimal_places=2, default=1)
    sellingPrice = models.DecimalField(db_column='selling_price', max_digits=18, decimal_places=2, default=1)
    stockNum = models.DecimalField(db_column='stock_num', max_digits=18, decimal_places=2, default=0)
    tag = models.CharField(db_column='tag', max_length=20, default='')
    goodsSellStatus = models.IntegerField(db_column='goods_sell_status', default=0)
    createTime = models.DateTimeField(db_column='create_time', auto_now_add=True)
    createUser = models.IntegerField(db_column='create_user', default=0)
    updateTime = models.DateTimeField(db_column='update_time', auto_now=True, null=True)
    updateUser = models.IntegerField(db_column='update_user', null=True, default=0)

    class Meta:
        db_table = 'goods_info'

class IndexConfig(models.Model):
    configId = models.IntegerField(db_column='config_id', primary_key=True)
    configName = models.CharField(db_column='config_name', max_length=20, default='')
    configType = models.IntegerField(db_column='config_type', default=0)
    goodsId = models.IntegerField(db_column='goods_id', default=0)
    redirectUrl = models.CharField(db_column='redirect_url', max_length=100, default='##')
    configRank = models.IntegerField(db_column='config_rank', default=0)
    isDeleted = models.IntegerField(db_column='is_deleted', default=0)
    createTime = models.DateTimeField(db_column='create_time', auto_now_add=True)
    createUser = models.IntegerField(db_column='create_user', default=0)
    updateTime = models.DateTimeField(db_column='update_time', auto_now=True, null=True)
    updateUser = models.IntegerField(db_column='update_user', null=True, default=0)

    class Meta:
        db_table = 'index_config'

class Order(models.Model):
    orderId = models.IntegerField(db_column='order_id', primary_key=True)
    orderNo = models.CharField(db_column='order_no', max_length=20, default='')
    configType = models.IntegerField(db_column='config_type')
    totalPrice = models.DecimalField(db_column='total_price', max_digits=18, decimal_places=2, default=1)
    payStatus = models.IntegerField(db_column='pay_status', default=0)
    payType = models.IntegerField(db_column='pay_type', default=0, null=True)
    payTime = models.DateTimeField(db_column='pay_time', null=True)
    orderStatus = models.IntegerField(db_column='order_status', default=0)
    extraInfo = models.CharField(db_column='extra_info', max_length=100, default='')
    isDeleted = models.IntegerField(db_column='is_deleted', default=0)
    createTime = models.DateTimeField(db_column='create_time', auto_now_add=True)
    updateTime = models.DateTimeField(db_column='update_time', auto_now=True, null=True)

    class Meta:
        db_table = 'order'

class OrderAddress(models.Model):
    orderId = models.IntegerField(db_column='order_id', primary_key=True, default=0)
    userName = models.CharField(db_column='user_name', max_length=30, default='')
    userPhone = models.CharField(db_column='user_phone', max_length=11, default='')
    provinceName = models.CharField(db_column='province_name', max_length=32, default='')
    cityName = models.CharField(db_column='city_name', max_length=32, default='')
    regionName = models.CharField(db_column='region_name', max_length=32, default='')
    detailAddress = models.CharField(db_column='detail_address', max_length=64, default='')

    class Meta:
        db_table = 'order_address'

class OrderItem(models.Model):
    orderItemId = models.IntegerField(db_column='order_item_id', primary_key=True)
    orderId = models.IntegerField(db_column='order_id', default=0)
    goodsId = models.IntegerField(db_column='goods_id', default=0)
    userName = models.CharField(db_column='user_name', max_length=200, default='')
    goodsCoverImg = models.CharField(db_column='goods_cover_img', max_length=200, default='')
    sellingPrice = models.DecimalField(db_column='selling_price', max_digits=18, decimal_places=2, default=1)
    goodsCount = models.IntegerField(db_column='goods_count', default=1)
    createTime = models.DateTimeField(db_column='create_time', auto_now_add=True)

    class Meta:
        db_table = 'order_item'

class ShoppingCartItem(models.Model):
    cartItemId = models.IntegerField(db_column='cart_item_id', primary_key=True)
    userId = models.IntegerField(db_column='user_id')
    goodsId = models.IntegerField(db_column='goods_id', default=1)
    goodsCount = models.DecimalField(db_column='goods_count', max_digits=18, decimal_places=2, default=1)
    isDeleted = models.IntegerField(db_column='is_deleted', default=0)
    createTime = models.DateTimeField(db_column='create_time', auto_now_add=True)
    updateTime = models.DateTimeField(db_column='update_time', auto_now=True, null=True)

    class Meta:
        db_table = 'shopping_cart_item'

class User(models.Model):
    userId = models.IntegerField(db_column='user_id', primary_key=True)
    nickName = models.CharField(db_column='nick_name', max_length=50, default='')
    loginName = models.CharField(db_column='login_name', max_length=11, default='')
    passwordMd5 = models.CharField(db_column='password_md5', max_length=32, default='')
    introduceSign = models.CharField(db_column='introduce_sign', max_length=100, default='')
    isDeleted = models.IntegerField(db_column='is_deleted', default=0)
    lockedFlag = models.IntegerField(db_column='locked_flag', default=0)
    createTime = models.DateTimeField(db_column='create_time', auto_now_add=True)

    class Meta:
        db_table = 'user'

class UserAddress(models.Model):
    addressId = models.IntegerField(db_column='address_id',primary_key=True)
    userId = models.IntegerField(db_column='user_id', default=0)
    userName = models.CharField(db_column='user_name', max_length=30, default='')
    userPhone = models.CharField(db_column='user_phone', max_length=11, default='')
    defaultFlag = models.IntegerField(db_column='default_flag', default=0)
    provinceName = models.CharField(db_column='province_name', max_length=32, default='')
    cityName = models.CharField(db_column='city_name', max_length=32, default='')
    regionName = models.CharField(db_column='region_name', max_length=32, default='')
    detailAddress = models.CharField(db_column='detail_address', max_length=64, default='')
    isDeleted = models.IntegerField(db_column='is_deleted', default=0)
    createTime = models.DateTimeField(db_column='create_time', auto_now_add=True)
    updateTime = models.DateTimeField(db_column='update_time', auto_now=True, null=True)

    class Meta:
        db_table = 'user_address'

class UserToken(models.Model):
    userId = models.IntegerField(db_column='user_id', primary_key=True)
    token = models.CharField(db_column='token', max_length=32)
    updateTime = models.DateTimeField(db_column='update_time', auto_now=True)
    expireTime = models.DateTimeField(db_column='expire_time')

    class Meta:
        db_table = 'user_token'
