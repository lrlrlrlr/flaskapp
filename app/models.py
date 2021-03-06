import hashlib

import bleach
from datetime import datetime, timedelta
from flask import current_app
from flask import request
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, login_manager


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    # todo 下面db.Interger如果改成db.INTERGER还是一样的吗?
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        '''9.2: 定义默认的用户角色'''
        super(User, self).__init__(**kwargs)  # todo 这句super什么意思???
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.avatar_hash is None and self.email is not None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        '''拒绝访问明文密码'''
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        '''生成哈希密码'''
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        '''验证哈希密码'''
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        '''生成确认token'''
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({
            'confirm': self.id})

    def confirm(self, token):
        '''校验确认token'''
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        '''生成重置密码token'''
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({
            'reset': self.id})

    def reset_password(self, token, new_password):
        '''校验重置密码token'''
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        '''生成重置邮箱token'''
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({
            'change_email': self.id,
            'new_email': new_email})

    def change_email(self, token):
        '''校验重置邮箱token'''
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        '''9.3: 角色验证'''
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        '''9.3: 角色验证'''
        return self.can(Permission.ADMINISTER)

    def ping(self):
        '''10.1: 刷新用户最后访问时间'''
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        '''10.4 用户头像'''
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default,
                                                                     rating=rating)

    @staticmethod
    def generate_fake(count=100):
        from random import seed
        import forgery_py
        from sqlalchemy.exc import IntegrityError

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True)
                     )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    '''9.3: 角色验证'''

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Mylog(db.Model):
    __tablename__ = 'mylog'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    ipaddr = db.Column(db.String(64))
    ipinfo = db.Column(db.String(64))

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    '''博文,记录时间/用户/内容'''
    __tablename__ = 'Posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(
            bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Longurl(db.Model):
    '''长链接'''
    __tablename__ = 'longurl'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(254))
    short_url = db.Column(db.String(254), unique=True)


class UrlCounter(db.Model):
    '''短链访问统计'''
    __tablename__ = 'urlcounter'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(254), db.ForeignKey('longurl.url'))

    time = db.Column(db.DateTime)
    ipaddr = db.Column(db.String(64))
    ua = db.Column(db.Text)

    @staticmethod
    def querier(target_longurl_model):
        '''传入一个Longurl.model,就可以查询它的uv和pv了, 返回的格式:[{day1},{day2},{day3}]'''

        results = list()

        # 查询该url最早有访问记录的时间
        url_first_request_time = \
            db.session.query(db.func.min(UrlCounter.time)).filter(UrlCounter.url == target_longurl_model.url).first()[0]
        # 如果该url有访问记录,则开始查询具体uv与pv
        if url_first_request_time:
            # 确定查询开始与结束日期
            start_date = url_first_request_time.date()
            end_date = datetime.today().date()

            # 生成器:生成指定日期区间列表
            def datelist(start_date, end_date):
                current_date = start_date
                while end_date > current_date:
                    yield current_date
                    current_date = current_date + timedelta(1)

            # 遍历每天的pv和uv,并加入列表
            for current_query_date in datelist(start_date, end_date):
                result = dict()
                result['date'] = current_query_date
                result['url'] = target_longurl_model.url
                result['short_url'] = target_longurl_model.short_url
                result['pv'] = UrlCounter.pv_querier(target_longurl_model.url, start_date=current_query_date,
                                                     end_date=current_query_date + timedelta(1))
                result['uv'] = UrlCounter.uv_querier(target_longurl_model.url, start_date=current_query_date,
                                                     end_date=current_query_date + timedelta(1))
                results.append(result)

            return results

    @staticmethod
    def pv_querier(target_url, start_date=None, end_date=None):
        '''查询指定链接在指定日期的pv量, 日期格式:(str or datetime.date) 2017-01-01 '''

        # 没开始时间,没结束时间:直接查全部uv
        if not start_date and not end_date:
            pv = UrlCounter.query.filter_by(url=target_url).count()
            return pv

        # 有开始时间,没结束时间:结束时间等于现在(到今天24:00)
        if start_date and not end_date:
            end_date = (datetime.today() + timedelta(1)).strftime('%Y-%m-%d')

        # 没开始时间,有结束时间:开始时间等于最早
        if not start_date and end_date:
            start_date = db.session.query(db.func.min(UrlCounter.time)).filter(UrlCounter.url == target_url).first()[
                0].strftime('%Y-%m-%d')

        pv = UrlCounter.query.filter_by(url=target_url).filter(UrlCounter.time.between(start_date, end_date)).count()
        return pv

    @staticmethod
    def uv_querier(target_url, start_date=None, end_date=None):
        '''查询指定链接在指定日期的pv量, 日期格式:(str or datetime.date) 2017-01-01 '''

        # 没开始时间,没结束时间:直接查全部uv
        if not start_date and not end_date:
            uv = db.session.query(UrlCounter.ipaddr).filter(UrlCounter.url == target_url).distinct().count()
            return uv

        # 有开始时间,没结束时间:结束时间等于现在(到今天24:00)
        if start_date and not end_date:
            end_date = (datetime.today() + timedelta(1)).strftime('%Y-%m-%d')

        # 没开始时间,有结束时间:开始时间等于最早
        if not start_date and end_date:
            start_date = db.session.query(db.func.min(UrlCounter.time)).filter(UrlCounter.url == target_url).first()[
                0].strftime('%Y-%m-%d')

        uv = db.session.query(UrlCounter.ipaddr).filter(UrlCounter.url == target_url,
                                                        UrlCounter.time.between(start_date,
                                                                                end_date)).distinct().count()
        return uv
