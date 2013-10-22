from flask_wtf import Form
from wtforms import TextField, BooleanField, TextAreaField
from wtforms.validators import Required, Length, ValidationError

# class LoginForm(Form):
# 	openid = TextField('openid', validators = [Required()])
# 	remember_me = BooleanField('remember_me', default = False)

class createMeetingForm(Form):
    meetingName = TextField('meetingName', validators = [Required(message='This field is required.'),Length(min = 0, max = 50)])
    moderatorPW = TextField('moderatorPW')
    attendeePW = TextField('attendeePW')

    def validate_meetingName(form, field):
    	if ' ' in field.data:
    		raise ValidationError('Please enter a name without whitespaces.')

class joinMeetingForm(Form):
	username = TextField('username', validators = [Required()])

