#coding:utf-8
#manager是运行脚本的文件
from nowstagram import app,db
from flask_script import Manager
from sqlalchemy import or_,and_
import random,unittest
#导入user
from nowstagram.models import User,Image,Comment

manager = Manager(app)


def get_image_url():
    return 'https://images.nowcoder.com/head/' + str(random.randint(0,1000)) + 'm.png'


#manager.command下面的函数可以让Py文件有这样的功能：
# 在终端中输入pyThon3 manager.py funcTIon执行该函数
@manager.command
def run_test():
    db.drop_all()
    #创建数据库（怎么知道创建的数据库是叫nowstagram）
    db.create_all()
    # 将以TesT开头的py文件导入测试用例
    tests = unittest.TestLoader().discover('./')
    unittest.TextTestRunner().run(tests)



# 初始化数据，和数据库交互，这时models中的用户被真正插入（插入到数据库中就算真正插入）
@manager.command    # 使该py文件拥有init_database方法
def init_database():
    db.drop_all()  # 删除所有的表
    db.create_all()  # 根据user中的代码创建表（根据列）
    for i in range(0,100):
        # 创建用户（用户名，密码）
        db.session.add(User('User'+str(i),'a'+str(i)))
        # 给每个人加几张图片,db.session.add(class)——创建类
        for j in range(0,10):
            db.session.add(Image(get_image_url(),i+1))
            for k in range(0,3):
                db.session.add(Comment('This is comment '+str(k),1+10*i+j,i+1))

    db.session.commit()  #数据库事物的提交，没提交没用！

    #更新数据
    #直接取.username更新；update+字典形式更新
    for i in range(50,100,2):
        user = User.query.get(i)
        user.username = '[New1]'+user.username
    for i in range(51,100,2):
        User.query.filter(User.id==i).update({'username':'[New2]'+str(i)})
    db.session.commit()


    #删除评论
    for i in range(50,100,2):
        comment = Comment.query.get(i)
        db.session.delete(comment)
    db.session.commit()
'''
    #数据查询
    # 打印的是User类中__repr__方法返回的内容，该方法从flask-sqlalchemy网站可查到
    print ('1',User.query.get(2))
    print ('2',User.query.all())    #打印所有对象的__repr__返回值
    print ('3',User.query.filter_by(id = 5).first())
    #offset(1)偏移了一位，限制打印2个
    print ('4',User.query.order_by(User.id.desc()).offset(1).limit(2).all())
    #查询用户名以0结尾的记录
    print ('5',User.query.filter(User.username.endswith('0')).limit(3).all())
    #不加.all()则显示出这条语句对应的sqlite语句
    print ('6',User.query.filter(or_(User.id == 88,User.id == 99)).all())
    #返回第一个或404
    print ('7',User.query.filter(and_(User.id >88 ,User.id <93)).first_or_404())
    #分页
    print ('8',User.query.order_by(User.id.desc()).paginate(page = 1,per_page = 10 ).items)
    user = User.query.get(1)
    #models.py中User和images关联，打印关联对象
    print ('9',user.images)
    image = Image.query.get(6)
    print ('10',image,image.user)
'''



if __name__ == '__main__':
    manager.run()