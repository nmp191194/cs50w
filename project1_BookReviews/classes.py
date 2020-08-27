from wtforms import Form, BooleanField, StringField, PasswordField, validators

# signup form
class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.Length(min=8, max=15),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

# search form
class SearchQuery(Form):
    query = StringField('', [validators.DataRequired()])

class User():
    def __init__(self, username, hashed_pwd):
        self.username = username
        self.hashed_pwd = hashed_pwd

    def __repr__(self):
        return self.username
