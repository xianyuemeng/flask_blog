from . import home
from flask import render_template, url_for, request, session, jsonify
from app.models import *
from app.dysms import demo_sms_send
import os, json, time, random, re, random


# 请求处理之前的 装饰器
@home.before_request
def checklogin():
    # 获取当前的请求路径
    path = request.path
    # 要求登录才能请求的路径
    urllist = [url_for('home.createblog')]
    if path in urllist:
        # 判断是否登录
        if not session.get('VipUser',None):
            return '<script>alert("请先登录");location.href="'+url_for('home.login')+'?next='+path+'"</script>'


# 退出登录
@home.route('/logout/')
def logout():
    session.pop('VipUser')
    return "<script>alert('退出成功');location.href='/'</script>"


# 发送验证码
@home.route('/send_vcode', methods=['GET','POST'])
def sendSMS():
    # 接受手机号
    phone = request.values['phone']
    print(phone)
    # 生成验证码
    code = random.randint(10000, 99999)
    # 存储到session中
    # session['code'] = code
    print(code)

    res = demo_sms_send.send(code, phone)
    res = jsonify(eval(res))
    print(res)
    print(type(res))

    # 将验证码存入 session
    session['vcode'] = code

    print('session:',session['vcode'])
    # vcode = Vcode.query.first()
    # if vcode:
    #     vcode.vcode = code
    #     db.session.add(vcode)
    #     db.session.commit()
    # else:
    #     vcode = Vcode(vcode=code)
    #     db.session.add(vcode)
    #     db.session.commit()

    return res


# 注册
@home.route('/register',  methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        data = {
            'login':url_for('home.login'),
            'register':url_for('home.register'),
            'sendSMS':url_for('home.sendSMS')
        }

        return render_template('home/lw-re.html', url=data)
    elif request.method == 'POST':
        try:
            if str(request.values['vcode']) == str(session['vcode']):
            
                data = {}
                data['email'] = request.values['email']
                data['pwd'] = User.MD5password(request.values['pwd'])
                data['phone'] = request.values['phone']

                ob = User(**data)
                db.session.add(ob)
                db.session.commit()

                res = '<script>alert("注册成功,请登录!");location.href="{login}"</script>'.format(login=url_for('home.login'))
                return res
            else:
                res = '<script>alert("注册失败,验证码错误,请重新注册!!");history.back(-1)</script>'
                return res

        except:
            res = '<script>alert("注册失败,请重新注册!!");history.back(-1)</script>'
            return res


# 发布博文
@home.route('/createblog',methods=['GET','POST'])
def createblog():
    if request.method == 'GET':
        # 获取所有的标签
        tags = Tags.query.all()
        # 返回一个博文发布页面
        return render_template('/home/blogs/add.html', tags=tags)
    elif request.method == "POST":
        data = {}
        # 接受消息
        data['title'] = request.values['title']
        data['context'] = request.values['context']
        data['uid'] = session['VipUser']['id']
        print(data)

        # 入库 加标签
        ob = Posts(**data)
        ob.tags = list(map(lambda x:Tags.query.get(x),request.form.getlist('tags')))
        db.session.add(ob)
        db.session.commit()
        
        return '<script>alert("发布成功");location.href="{}"</script> '.format(url_for('home.bloginfo',pid=ob.id))


# 博文详情
# @home.route('/bloginfo/<int:pid>')
# def bloginfo(pid):
#     # 读取文章内容
#     info = Posts.query.get(pid)
#     tags = info.tags
#     # 查找评论信息
#     comments = Comments.query.filter_by(posts_id=pid).all()

#     data = {'info':info, 'tags': tags, 'comments':comments}

#     return render_template('home/blogs/article.html', info=data)

@home.route('/bloginfo/<int:pid>')
def bloginfo(pid):
    # 读取文章内容
    blog = Posts.query.get(pid)
    tags = blog.tags
    # 查找评论信息
    comments = Comments.query.filter_by(posts_id=pid).all()

    data = {'blog':blog, 'tags': tags, 'comments':comments}

    return render_template('home/blogs/article.html', **data)


# 博文列表,按标签
@home.route('/blogs/tags/<int:tid>/')
def tagsblogs(tid):
    # 根据标签id获取标签
    tag = Tags.query.get(tid)
    data = {'tag':tag}

    return render_template('home/blogs/tagslist.html',**data)


# 博文,用户,标签,搜索
@home.route('/blogs/search')
def blogssearch():
    # 接受关键字
    keywords = request.args.get('keywords')
    # 按用户搜索
    users = User.query.filter(User.name.contains(keywords)).all()
    # 博文标题搜索
    blogs = Posts.query.filter(Posts.title.contains(keywords)).all()
    # 组合数据
    data = {'users':users,'blogs':blogs}
    return render_template('/home/blogs/search.html', **data)


# 博文列表 按用户
@home.route('/blogs/user/<int:uid>/')
def userblogs(uid):
    # 获取页码数
    p = int(request.args.get('p',1))
    # 获取博文数据  参数1 当前页码数  参数2 每页显示的数量
    posts = Posts.query.filter_by(uid=uid).paginate(p,5)
    a = list(posts.iter_pages())
    b = len(a)
    # data = {'posts':posts,'a':a, 'b':b}

    # 根据用户id获取当前用户的所有博文列表
    # posts = Posts.query.filter_by(uid=uid).all()
    user = User.query.get(uid)
    data = {'posts': posts, 'user': user,'a':a, 'b':b}
   
    return render_template('home/blogs/userlist.html',**data)


# 评论
@home.route('/comment',methods=["post"])
def comment():
    data={}
    data['context'] = request.values['context']
    data['posts_id'] = request.values['pid']
    data['user_id'] = session['VipUser']['id']

    ob = Comments(**data)
    db.session.add(ob)
    db.session.commit()
    
    res = '<script>alert("评论成功!");location.href="{ok}"</script>'.format(ok=url_for('home.bloginfo',pid=request.values['pid']))
    return res


# 回复
@home.route('/hf',methods=["POST"])
def hf():
    # 获取回复的信息
    data = {}
    data['cid'] = request.values['cid']
    data['context'] = request.values['context']
    data['user_id'] = session['VipUser']['id']
    try:
        data['rid'] = request.values['rid']
    except:
        pass

    # 评论
    r = Comments.query.get(request.values['cid'])
    pid = r.posts_id

    ob = Reply(**data)
    db.session.add(ob)
    db.session.commit()
    res = "<script>alert('回复成功');location.href='{}'</script> ".format(url_for('home.bloginfo',pid=pid))
    return res


# 富文本编辑器配置
@home.route('/ueditconfig/', methods=['GET', 'POST'])
def ueditconfig():
    from app import BASE_DIR
    # 获取请求动作
    action = request.args.get('action')
    result = {}
    # 读取配置文件
    if action == 'config':
    # 初始化时，返回配置文件给客户端
        with open(os.path.join(BASE_DIR,'static', 'ueditor', 'php',
                               'config.json')) as fp:
            try:
                # 删除 `/**/` 之间的注释
                CONFIG = json.loads(re.sub(r'\/\*.*\*\/', '', fp.read()))
            except:
                CONFIG = {}
        result = CONFIG
    # 文件上传
    if action  == 'uploadimage':
        upfile = request.files['upfile']  # 这个表单名称以配置文件为准
        # upfile 为 FileStorage 对象
        # 这里保存文件并返回相应的URL

        Suffix = upfile.filename.split('.').pop()
        filename = str(time.time())+str(random.randint(10000,99999))+'.'+Suffix
        imgurl = '/static/uploads/'+filename
        upfile.save(BASE_DIR+imgurl)

        result = {
            "state": "SUCCESS",
            "url": imgurl,
            "title": filename,
            "original":filename
        }
        print(BASE_DIR)
    return json.dumps(result)


# 登陆
@home.route('/login', methods=['GET', 'POST'])
def login():
    nextpath = request.args.get('next','/')
    # print(nextpath)
    if request.method == 'GET':
        data = {
            'login':url_for('home.login'),
            'register':url_for('home.register')
        }

        return render_template('home/lw-log.html', url=data)
    elif request.method == 'POST':
        email = request.form['email']
        password = User.MD5password(request.values['pwd']) 
        try:
            # 查数据
            ob = User.query.filter_by(email=email).first()
            if password == ob.pwd:
                session['VipUser'] = {
                    'email': email,
                    'id': ob.id, 
                    'phone': ob.phone,
                    'face': ob.face
                    }
                res = '<script>alert("登录成功");location.href="{next}"</script>'.format(next=nextpath)
                return res
            else:
                res = '<script>alert("账号或者密码错误,请重新登录!!");history.back(-1)</script>'
                return res
            
        except:
            res = '<script>alert("账号或者密码错误,请重新登录!!");history.back(-1)</script>'
            return res


# 个人中心
@home.route('/myinfo')
def myinfo():
    uid = session['VipUser']['id']
    ob = User.query.get(uid)
    # 获取页码数
    p = int(request.args.get('p',1))
    # 获取博文数据  参数1 当前页码数  参数2 每页显示的数量
    posts = Posts.query.filter_by(uid=uid).paginate(p,2)
    a = list(posts.iter_pages())
    b = len(a)
    data = {'posts':posts,'a':a, 'b':b, 'ob': ob}
    return render_template('home/myinfo.html', **data)


# 编辑个人信息
@home.route('/editinfo')
def editinfo():
    uid = session['VipUser']['id']
    ob = User.query.get(uid)
    data = {'ob': ob}
    return render_template('home/editinfo.html', **data)


# 执行修改个人信息
@home.route('/update', methods=['POST','GET'])
def update():
    from app import BASE_DIR
    if request.method == 'POST':
        # 获取对象
        uid = session['VipUser']['id']
        ob = User.query.get(uid)
        print(ob.name)
        # 执行修改
        ob.name = request.values['name']
        ob.phone = request.values['phone']
        ob.age = request.values['age']
        ob.sex = request.values['sex']
        ob.info = request.values['info']
        if request.values['pwd']:
            ob.pwd = User.MD5password(request.values['pwd']) 
        try:
            # 检测是否有文件上传
            myfile = request.files['face']
            try:
                os.remove(BASE_DIR + ob.face)
            except:
                pass

            Suffix = myfile.filename.split('.').pop()
            filename = str(time.time())+str(random.randint(10000,99999))+'.'+Suffix
            imgurl = '/static/uploads/'+filename
            myfile.save(BASE_DIR + imgurl)
            ob.face = imgurl

        except:
            pass

        db.session.add(ob)
        db.session.commit()

        res = '<script>alert("修改成功");location.href="{}"</script>'.format(url_for('home.myinfo'))

        return res
    else:
        return '请求错误'
    

# 首页
@home.route('/')
def home():
    # 获取页码数
    p = int(request.args.get('p',1))
    # 获取博文数据  参数1 当前页码数  参数2 每页显示的数量
    posts = Posts.query.filter().paginate(p,3)
    a = list(posts.iter_pages())
    b = len(a)
    data = {'posts':posts,'a':a, 'b':b}
    # print(b)
    return render_template('home/lw-index.html', **data)
