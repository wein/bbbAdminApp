from flask_wtf import Form
from wtforms import TextField, BooleanField, TextAreaField
from wtforms.validators import Required, Length

# class LoginForm(Form):
# 	openid = TextField('openid', validators = [Required()])
# 	remember_me = BooleanField('remember_me', default = False)

class createMeetingForm(Form):
    meetingName = TextField('meetingName', validators = [Required()])
    moderatorPW = TextField('moderatorPW')
    attendeePW = TextField('attendeePW')

class joinMeetingForm(Form):
	username = TextField('username', validators = [Required()])

