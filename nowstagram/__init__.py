#coding:utf-8
#init.py文件主要是初始化一些实例
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
#加载该文件的配置
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config.from_pyfile('app.conf')
#通过db操作数据库
app.secret_key = 'nowcoder'
db = SQLAlchemy(app)
#创建一个LoginManager类
login_manager = LoginManager(app)
#尚未登录却要查看某人profile页时让其跳转到如下网页，与@login_required连用
login_manager.login_view = '/regloginpage/'

#将代码中的类和数据库中的类（表）结合起来


from nowstagram import models,views

