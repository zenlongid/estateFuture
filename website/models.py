from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, email, name, password, profile, birthday, bookmarks, suspended):
        self.id = user_id
        self.email = email
        self.name = name
        self.password = password
        self.profile = profile
        self.birthday = birthday
        self.bookmarks = bookmarks
        self.suspended = suspended