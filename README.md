## 使用django框架实现蜂窝商城系统后台

### 1、技术栈：
    Python 3.11
    PyMySql 1.0.2
    Django 4.1.7

### 2、数据库初始化
找到`statics`目录下的`sql`下的`phone_db.sql`文件，直接运行此文件

### 3、项目结构介绍
api：应用，也可叫实例\
==》api_v1：版本迭代（主要分为用户功能和商城功能）\
==》daos.py：DAO层，操作数据库ORM\
==》modes.py：Model层，实体类，每张表对应一个类\
==》services.py：业务层，具体需求要实现的业务逻辑处理\
==》urls.py：二级动态路由，统一管理\
==》views.py：View层，通过前端返回给后端的数据\
logs：日志记录\
phone：项目的主目录*\
==》settings.py：主要配置文件，设置应用、中间件、数据库、时区、资源代理等等...\
==》urls.py：一级动态路由，主要区分多个应用的场景\
statics：存放静态资源\
==》goods-img：一些商品图片\
==》icon:头像图标\
==》数据库sql文件\
templates：存放模板代码\
utils：一些工具类\
==》app_decorators.py：项目的装饰器，也可叫全局过滤器，解析token，验证token，权限管理\
==》commons.py：一些细小的功能点，给封装起来了\
venv：生成环境\
http_test：一些测试的api接口\

### 4、项目启动

添加`Django Server`服务，如果你环境没问题的话，`PyCharm`会自动识别并帮你配置好项目启动所需的设置，点击绿色小箭头，不出意外的话应该如图所示：

<img src="https://www.llhnp.com/usr/images/phone3_server/phone3_serever_activate.png" alt="activate"  />

