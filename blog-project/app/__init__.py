from flask import Flask
import os

app = Flask(__name__)
app.debug = True

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint,url_prefix="/admin")

# key = os.urandom(24)
# print(key)
# 创建秘钥
app.config['SECRET_KEY'] = '2\xe18\xa2pmC\xf6\xc5\xf9\x05\xf7o5S!\xaa\x14\x00\xd0\xa6\x87uc'

# 配置服务器地址
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# 注册过滤器,获取所有的标签
@app.template_filter()
def gettagsall(a):
    from app.models import Tags
    tags = Tags.query.all()
    return tags


@app.template_filter()
def get_reply_user(b):
    from app.models import Reply
    rep = Reply.query.get(b)
    return rep.user.name
