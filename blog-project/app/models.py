from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime
import pymysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:123456@localhost/blog"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)

#会员数据模型
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True)
    pwd = db.Column(db.String(100))
    email = db.Column(db.String(100))
    age = db.Column(db.String(10),default='18')
    phone = db.Column(db.String(11),unique=True)
    info = db.Column(db.Text)
    face = db.Column(db.String(255))
    sex = db.Column(db.Integer,default=0)
    status = db.Column(db.Integer, default=0)
    addtime = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    posts = db.relationship('Posts',backref="user",cascade="all, delete,delete-orphan")
    comments = db.relationship('Comments',backref="user",cascade="all, delete,delete-orphan")
    reply = db.relationship('Reply',backref="user",cascade="all, delete,delete-orphan")


    # 加密
    @classmethod
    def MD5password(cls,password):
        import hashlib
        # 创建md5对象
        hl = hashlib.md5()
        hl.update(password.encode(encoding='utf-8'))
        return hl.hexdigest()
        

tags = db.Table('post_tag',
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
)


#文章
class Posts(db.Model):
    __tablename__= 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    context = db.Column(db.Text)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    tags = db.relationship('Tags',secondary=tags,backref='posts')
    addtime = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    comments = db.relationship('Comments',backref="posts",cascade="all, delete,delete-orphan")


#标签
class Tags(db.Model):
    __tablename__='tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    # def __repr__(self):
    #     return self.name


# 评论
class Comments(db.Model):
    __tablename__='comments'
    id = db.Column(db.Integer, primary_key=True)
    addtime = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    posts_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    context = db.Column(db.String(255))
    status = db.Column(db.Integer)
    reply =  db.relationship('Reply',backref="comments",cascade="all, delete,delete-orphan")


# 回复模型
class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cid =  db.Column(db.Integer, db.ForeignKey('comments.id'))
    context = db.Column(db.String(255))
    addtime = db.Column(db.DateTime,index=True,default=datetime.utcnow)
    rid = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# 后台管理员
class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100),unique=True)
    pwd= db.Column(db.String(100))
    status = db.Column(db.Integer, default=0)


manager.add_command('db', MigrateCommand)
    
if __name__=='__main__':
    # db.create_all()
    manager.run()