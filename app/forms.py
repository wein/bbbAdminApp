from flask_wtf import Form
from wtforms import TextField, BooleanField, TextAreaField
from wtforms.validators import Required, Length

class LoginForm(Form):
	openid = TextField('openid', validators = [Required()])
	remember_me = BooleanField('remember_me', default = False)

class EditForm(Form):
    meetingName = TextField('meetingName', validators = [Required()])
    meetingID = TextField('meetingID', validators = [Required()])
    moderatorPW = TextField('moderatorPW', validators = [Required()])
    attendeePW = TextField('attendeePW', validators = [Required()])
    #about_me = TextAreaField('about_me', validators = [Length(min = 0, max = 140)])