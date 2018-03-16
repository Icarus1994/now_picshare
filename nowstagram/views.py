#coding:utf-8
#views.py主要和网页的跳转有关
# 对于views而言，装饰器下的函数的返回值可以是网页，某个写好的html文件，
# 甚至是一个字符串或者json字符串，此时会在网页上看到返回的字符串
#可以从目录中导入变量

from nowstagram import app,db,alisdk
from nowstagram.models import User,Image,Comment
from flask import render_template,redirect,request,flash,get_flashed_messages,send_from_directory
import random,hashlib
from flask_login import login_user, logout_user, current_user, login_required
import json,hashlib,os,uuid
import flask_login,requests



@app.route('/',methods = {'post','get'})
def index(images = None):
    images = Image.query.order_by(db.desc(Image.id)).limit(10).all()
    return render_template('index.html',images = images)


@app.route('/image/<int:image_id>/')
@login_required
def image(image_id):
    image = Image.query.get(image_id)
    print (image_id)
    if image == None:
        return redirect('/')
    return render_template('pageDetail.html',image = image)


@app.route('/profile/<int:user_id>/',methods = {'post','get'})
#用户访问该页面的时候必须先登录,因此未登录时就会跳转到一个Unauthenticated页面，也可以设置未登录时跳转到的页面的形式
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    if user == None:
        return redirect('/')
    paginate = Image.query.filter_by(user_id = user_id).paginate(page = 1,per_page = 3,error_out = False)
    # 下面render_template中的images会传递到profile.html中去
    return render_template('profile.html',user = user,images = paginate.items,has_next = paginate.has_next)

#网址要按照如下格式写才能得到图片对应的map,此时后端的接口已经写好了
@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id,page,per_page):
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)
    # 当没有更多图片时要告诉前端
    # map
    map = {'has_next':paginate.has_next}
    images =[]
    for image in paginate.items:
        # imgvo可视化
        imgvo ={'id':image.id, 'url':image.url,'comment_count':len(image.comments)}
        images.append(imgvo)
    map['images']=images
    return json.dumps(map)

# 登录/注册页
@app.route('/regloginpage/',methods = {'post','get'})
def regloginpage():
    msg = ''
    for m in get_flashed_messages(with_categories = False, category_filter=['reglogin']):
        msg = msg + m
        #next实现的功能是：当用户进入某个需要登录的页面而当时未登录时，保证他登录后能自动跳转到之前他想访问的页面
    return render_template('login.html', msg = msg, next = request.values.get('next') )


def redirect_with_msg(target, msg, category):
    if msg != None:
        flash(msg,category = category)
    return redirect(target)


@app.route('/login/',methods = {'get','post'})
def login():
    #与注册时的方法一样
    username = request.values.get('username').strip()  # .strip()移除字符串头尾指定的字符
    password = request.values.get('password').strip()

    if username == '' or password == '':
        return redirect_with_msg('/regloginpage/',u'用户名或密码不能为空',category= 'reglogin')


    #在本地数据库中根据username查询
    user = User.query.filter_by(username = username).first()
    if user == None:
        return redirect_with_msg('/regloginpage/', u'用户名不存在', category='reglogin')
    m = hashlib.md5()   #新建实例
    m.update((password+user.salt).encode('utf-8'))    #初始化
    if (m.hexdigest() != user.password):
        return redirect_with_msg('/regloginpage/', u'用户名或密码错误', category='reglogin')
    #使用户登录
    login_user(user)

#next的传递过程：应该是先由某个页面跳转到regloginpage时将其next传递给next参数，当此时用户进行登录时将此时网页中的next网址赋值给next
    next = request.values.get("next")
    if next != None and next.startswith('/'):
        return redirect(next)

    return redirect('/')


@app.route('/reg/',methods = {'post','get'})
def reg():
    #request.args  是url中的参数
    #request.values 是网页中http post方法提交过来的数据
    username = request.values.get('username').strip()   #.strip()移除字符串头尾指定的字符
    password = request.values.get('password').strip()

    if username == '' or password == '':
        return redirect_with_msg('/regloginpage/',u'用户名或密码不能为空',category= 'reglogin')

    #用户如果已经存在的话就不需要再注册
    user = User.query.filter_by(username = username).first()
    if user != None:
        #这里relogin也许不需要修改

        return redirect_with_msg('/regloginpage/',u'用户名已经存在',category= 'reglogin')


    salt = '.'.join(random.sample('01234565689abcdefghi',10))
    m = hashlib.md5()
    m.update((password+salt).encode("utf-8"))
    password = m.hexdigest()
    user = User(username,password,salt)
    db.session.add(user)
    db.session.commit()

#用户注册完后自动登录
    login_user(user)

    next = request.values.get("next")
    if next != None and next.startswith('/'):
        return redirect(next)

    return redirect('/')

@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')


# 下载图片（显示），即取出二进制流图片并返回它
# @app.route('/image/<image_name>')
# def view_image(image_name):
#     return send_from_directory(app.config['UPLOAD_DIR'],image_name)


def save_to_local(file,file_name):
    save_dir = app.config['UPLOAD_DIR']
    file.save(os.path.join(save_dir,file_name))
    return '/image/' + file_name

# 解决：通过上传图片保存到数据库，并且可以通过url访问图片
#上传保存
# 只有post请求在报文头后可以带数据
@app.route('/upload/',methods = {'post'})
def upload():
    # 以下表示请求中的数据文件，'file'表示file关键字
    # debugge栏中显示request.files是一个多key字的字典
    print (request.files)
    file = request.files['file']
    # file拥有的方法
    # 后缀名
    file_ext = ''
    # 有后缀名的话
    if file.filename.find('.')>0 :
        file_ext = file.filename.rsplit('.',1,)[1].strip().lower()
    if file_ext in app.config['ALLOWED_EXT']:
        file_name = str(uuid.uuid1()).replace('-','')+'.'+file_ext
        # 在postman相应route中发送图片文件，在body--pretty中会返回'ok'
        url = alisdk.ali_upload_file(file,file_name)
        # url如果出问题会返回None
        if url != None:
            db.session.add(Image(url, current_user.id))
            db.session.commit()
            return redirect('/profile/%d/' % current_user.id)
    return redirect('/')

@app.route('/addcomment/',methods ={'post'})
def add_comment():
    image_id = int(request.values['image_id'])
    content = request.values['content'].strip()
    comment = Comment(content, image_id, current_user.id )
    db.session.add(comment)
    db.session.commit()

    return json.dumps({"code":0,"content":content,"id":comment.id,
                       "username":comment.user.username,
                       "user_id":comment.user.id})

@app.route('/index/images/<int:page>/<int:per_page>/')
def index_images(page, per_page):
    paginate = Image.query.order_by(db.desc(Image.id)).paginate(page = page,per_page=per_page,error_out=False)
    map = {'has_next':paginate.has_next}
    images = []
    for image in paginate.items:
        comments = []
        for i in range(0,min(2,len(image.comments))):
            comment = image.comments[i]
            comments.append({'username':comment.user.username,
                             'user_id':comment.user_id,
                             'content':comment.content})
        # 可视化，以下使得网页上我们能看到一张图片上附带有这些内容
        imgvo = {'id':image.id,
                 'url':image.url,
                 'user_id':image.user_id,
                 # 用户头像
                 'head_url':image.user.head_url,
                 'created_date':str(image.create_date),
                 'comments':comments}
        images.append(imgvo)
    # 向字典Map中添加新的键值对
    map['images'] = images
    return json.dumps(map)

