from app import app, db, login_manager
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

##################################################
#### Login Manager user_loader function Model ####
##################################################
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#############################
#### User Database Model ####
#############################
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    admin = db.Column(db.Boolean, default=False, nullable=False)
    username = db.Column(db.String(64), index=True, unique=True,  nullable=False)
    email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_image = db.Column(db.String(60), nullable=False, default='default.png')
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_seconds=1800):
        s = Serializer(app.config.secret_key, expires_seconds)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config.secret_key)
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f'<User {self.username}>'

#############################
#### Post Database Model ####
#############################
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Post {self.title}, {self.date_posted}'