# 蜂窝商城系统后台

#### 1、介绍：

根据 GitHub 上的 [newbee-mall](https://github.com/newbee-ltd/newbee-mall) 项目，这是一套商城后台管理系统，由于是基于 Spring Boot 及相关技术栈开发，本人以自学 Python 的家底来改造项目，把 Java 转成 Python 项目。包含数据面板、轮播图管理、商品管理、订单管理、会员管理、分类管理、设置等模块。 

#### 2、系统架构

基于 [Django](http://www.djangoproject.com/) 框架开发...细节太多了

#### 3、项目结构介绍

api：应用，也可叫实例

- api_v1：版本迭代（主要分为用户功能和商城功能）
- daos.py：DAO层，操作数据库ORM
- modes.py：Model层，实体类，每张表对应一个类
- services.py：业务层，具体需求要实现的业务逻辑处理
- urls.py：二级动态路由，统一管理
- views.py：View层，通过前端返回给后端的数据

logs：日志记录

phone：项目的主目录*

- settings.py：主要配置文件，设置应用、中间件、数据库、时区、资源代理等等...
- urls.py：一级动态路由，主要区分多个应用的场景

statics：存放静态资源

- goods-img：一些商品图片
- icon:头像图标
- 数据库sql文件

templates：存放模板代码

utils：一些工具类

- app_decorators.py：项目的装饰器，也可叫全局过滤器，解析token，验证token，权限管理
- commons.py：一些细小的功能点，给封装起来了

venv：生成环境

http_test：一些测试的api接口

#### 4、使用说明

- 找到`statics`目录下的`sql`下的`phone_db.sql`文件，直接运行此文件

- 添加`Django Server`服务，如果你环境没问题的话，`PyCharm`会自动识别并帮你配置好项目启动所需的设置，点击绿色小箭头，不出意外的话应该如图所示：

  <img src="https://www.llhnp.com/usr/images/phone3_server/phone3_serever_activate.png" alt="activate"  />

#### 5、后台管理页面

- 登录页


![login](https://camo.githubusercontent.com/76ec819cb2f490a2f5e4d853f16a1c0f4c4159f8fa8bcbf2d66dcf89c5deac5d/68747470733a2f2f6e65776265652d6d616c6c2e6f73732d636e2d6265696a696e672e616c6979756e63732e636f6d2f706f737465722f70726f647563742f6d616e6167652d6c6f67696e2e706e67)

- 轮播图管理

![lunbo](https://camo.githubusercontent.com/0293cb48b52de4329a75ea83f0959c1644ccd1092a2b4884954b92aa207f4fd2/68747470733a2f2f6e65776265652d6d616c6c2e6f73732d636e2d6265696a696e672e616c6979756e63732e636f6d2f706f737465722f70726f647563742f6d616e6167652d6361726f7573656c2d323032332e706e67)

- 新品上线

![new](https://camo.githubusercontent.com/c124cae1d676821373ecb105cb7d690971ec7ebfa21b5b4d739b4f1ff7e6e8aa/68747470733a2f2f6e65776265652d6d616c6c2e6f73732d636e2d6265696a696e672e616c6979756e63732e636f6d2f706f737465722f70726f647563742f6d616e6167652d696e6465782d636f6e6669672d323032332e706e67)

- 分类管理

![fenlei](https://camo.githubusercontent.com/36c73a3f18c089ba8e6d7a0d5bc8cdb59caa2c732abf617ec612dc6dd2e9b18b/68747470733a2f2f6e65776265652d6d616c6c2e6f73732d636e2d6265696a696e672e616c6979756e63732e636f6d2f706f737465722f70726f647563742f6d616e6167652d63617465676f72792e706e67)

- 商品管理

![goods](https://camo.githubusercontent.com/9ef577a98bc68bc824ae3f466d89e364259a0cfd7bd28272d987a9b93795e2a8/68747470733a2f2f6e65776265652d6d616c6c2e6f73732d636e2d6265696a696e672e616c6979756e63732e636f6d2f706f737465722f70726f647563742f6d616e6167652d676f6f64732d323032332e706e67)

- 商品编辑

![bianji](https://camo.githubusercontent.com/5bdc0f6cface8a77d3c65caca783e9976417b1a63cf57fcb0dd3e564fcb2b096/68747470733a2f2f6e65776265652d6d616c6c2e6f73732d636e2d6265696a696e672e616c6979756e63732e636f6d2f706f737465722f70726f647563742f676f6f64732d656469742d323032332e706e67)

- 订单管理

![dingdan](https://camo.githubusercontent.com/14e8d00ed1bd3402e08f2d12adbddf69e1307d006441030b395301b6aad7d212/68747470733a2f2f6e65776265652d6d616c6c2e6f73732d636e2d6265696a696e672e616c6979756e63732e636f6d2f706f737465722f70726f647563742f6d616e6167652d6f726465722d323032332e706e67)