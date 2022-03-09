## 建设平台后台

** 构建友好的服务架构，让编程变得简单，猿何必为难猿! **

cd到kscrcdn_api目录下，可以使用manage.py控制脚本进行操作。

BASE_DIR=根目录

```bash
cd $BASE_DIR/kscrcdn_api
```

1. 生成接口文档
```bash
python manage.py apidoc
```

生成的HTML文档在`$BASE_DIR/doc/apidoc`下，可以使用nginx、serve等方式启动web服务进行查看。

2. 启动测试环境

```bash
python manage.py runserver
```



