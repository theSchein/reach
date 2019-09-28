from flask_login import UserMixin

# TODO: Remove this and replace with a general seed
USERS = [
  {
    "username": "carl",
    "password": "carl",
    # "email": "carl.partridge@gmail.com",
  },
  {
    "username": "mike",
    "password": "mike",
  },
  {
    "username": "julie",
    "password": "julie",
  },
  {
    "username": "lillian",
    "password": "lillian",
  },
  {
    "username": "rafiq",
    "password": "rafiq",
  },
  {
    "username": "geoff",
    "password": "geoff",
  },
]

class User(UserMixin):

  def __init__(self, data):
    self.username = data["username"]
    # self.email = data["email"]

  # This property should return True if the user is authenticated, i.e. they have provided valid credentials. (Only authenticated users will fulfill the criteria of login_required.)
  # def is_authenticated(self):
  #   return True

  # # # This property should return True if this is an active user - in addition to being authenticated, they also have activated their account, not been suspended, or any condition your application has for rejecting an account. Inactive accounts may not log in (without being forced of course).
  # def is_active(self):
  #   return True

  # # # This property should return True if this is an anonymous user. (Actual users should return False instead.)
  # def is_anonymous(self):
  #   return False

  # This method must return a unicode that uniquely identifies this user, and can be used to load the user from the user_loader callback. Note that this must be a unicode - if the ID is natively an int or some other type, you will need to convert it to unicode.
  def get_id(self):
    return self.username

  def get(user_id):
    for user in USERS:
      if user["username"] == user_id:
        return User(user)
      else:
        return None

  def validate(username, password):
    for user in USERS:
      if (user["username"] == username and user["password"] == password):
        return User(user)
      else:
        return None
