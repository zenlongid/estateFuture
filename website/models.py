from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, email, password, profile, birthday, suspended):
        self.id = user_id
        self.email = email
        self.password = password
        self.profile = profile
        self.birthday = birthday
        self.suspended = suspended