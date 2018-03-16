#codingz:utf-8

from nowstagram import db,login_manager
from datetime import datetime   #程序媛中有讲过
import random


#通过ORM框架实现Python类和数据库之间的对应
class Comment(db.Model):
    id = db.Column(db.Integer,primary_key = True , autoincrement = True)
    content = db.Column(db.String(1024))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer,default = 0)  #0正常，1异常
    user = db.relationship('User')
    __table_args__ = {'extend_existing':True,'mysql_collate': 'utf8_general_ci'}

    def __init__(self,content, image_id , user_id):
        self.content = content
        self.image_id = image_id
        self.user_id = user_id

    def __repr__(self):
        return '<Comments %d %s>' % (self.id, self.content)


#给网站中的图片设置一个类
class Image(db.Model):
    id = db.Column(db.Integer,primary_key = True , autoincrement = True)
    url = db.Column(db.String(512))
    # 数据库中的外键，表示ID来源于User.id

    # URL为什么不用粘贴网址？db.Datetime是自定义数据类型？

    # id是图片id,user_id是图片所属的人的id，外键链接到user.id这一列上

    # user_id可能有问题
    user_id =db.Column(db.Integer, db.ForeignKey('user.id'))
    create_date = db.Column(db.DateTime)
    comments = db.relationship('Comment')
    __table_args__ = {'extend_existing': True}

# 初始化函数
    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id
        self.create_date = datetime.now() #当前时间

    def __repr__(self):
        return '<Image %d %s>'%(self.id,self.url)


# 指定Python中的类和数据库中的表相关联，ID，username,head_url都表示数据库中的一列，并且有相应的属性
class User(db.Model):
    # 联系mysql语言
    id = db.Column(db.Integer,primary_key = True,autoincrement = True)
    # 限定字符串长度不超过80;每个名字不一样
    username = db.Column(db.String(80),unique = True)
    password = db.Column(db.String(32))
    salt = db.Column(db.String(32))
    # 头像
    head_url = db.Column(db.String(256))
    # 用户和图片是一对多的关系，下文将用户 和图片关联起来
    # 使得图片也能关联用户
    images = db.relationship('Image',backref = 'user',lazy = 'dynamic')
    __table_args__ = {'extend_existing': True}


    #用户的构造函数
    def __init__(self,username,password,salt=''):
        self.username = username
        self.password = password
        self.salt = salt
        #在牛客网已有的图片库中随机选择一张图片作为用户的头像
        self.head_url = 'https://images.nowcoder.com/head/' + str(random.randint(0,1000)) + 'm.png'


    def __repr__(self):
        #要修改，考虑python3语法的变化
        return '<User %d %s>'%(self.id ,self.username)

    #flaks_login中要求用户对象应有的属性
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


#详flask_login官网
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)  #查询数据库加载用户

