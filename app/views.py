from  flask import render_template, flash, redirect, session, url_for, request, g
from app import app
from forms import EditForm
from datetime import datetime
import hashlib, requests
from bs4 import BeautifulSoup as Soup

server = 'http://bigbluebutton.int.tngtech.com/bigbluebutton/api/'
secret = 'b453bf804155f4b33d973c9ba25079a7'

# --------  Parameters  --------
name = 'Test'
attendeePW = 'ap'
moderatorPW = 'mp'
fullName = 'User'
welcome = ''
maxParticipants = ''
# record = False


# Creates the checksum of an input string
def createHash(hashString):
	m = hashlib.sha1()
	m.update(hashString)
	return m.hexdigest()


def getMeetingInfoCall(meetingid,moderatorpw):
	checksum = createHash('getMeetingInfomeetingID={0}&password={1}{2}'.format(meetingid,moderatorpw,secret))
	apiCall = '{0}getMeetingInfo?meetingID={1}&password={2}&checksum={3}'.format(server,meetingid,moderatorpw,checksum)
	return Soup(requests.get(apiCall).content)

# Get Meeting Info Call generator
def getMeetingsCall():
	checksum = createHash('getMeetings{0}'.format(secret))
	apiCall = '{0}getMeetings?checksum={1}'.format(server,checksum)
	return Soup(requests.get(apiCall).content)

def createMeetingCall(meetingName,meetingID,moderatorPW,attendeePW,record):
	checksum = createHash('createname={0}&meetingID={1}&moderatorPW={2}&attendeePW={3}&record={4}{5}'.format(meetingName,meetingID,moderatorPW,attendeePW,record,secret))
	apiCall = '{0}create?name={1}&meetingID={2}&moderatorPW={3}&attendeePW={4}&record={5}&checksum={6}'.format(server,meetingName,meetingID,moderatorPW,attendeePW,record,checksum)
	return Soup(requests.get(apiCall).content)



# Root handler
@app.route('/')
@app.route('/index')
def index():
	createMessage = session['createMessage']
	meetings = getMeetingsCall().find_all('meeting')
	return render_template("index.html", 
		title = 'Admin',
		createMessage = createMessage,
		meetings = meetings)



# handler to generate new meetings functionality
@app.route('/new', methods = ['GET', 'POST'])
def new():
	form = EditForm()
	if form.validate_on_submit():
		record = False
		createMeetingStatus = createMeetingCall(form.meetingName.data, form.meetingID.data, form.moderatorPW.data, form.attendeePW.data, record)
		flash(createMeetingStatus.returncode.string)
		return redirect(url_for('index'))
	return render_template("new.html", 
		title = 'New Meeting',
		secret = secret,
		form = form)



def joinMeetingCall(meetingID,pw,fullName,createTime):
	checksum = createHash('joinmeetingID={0}&password={1}&fullName={2}&createTime={3}{4}'.format(meetingID,pw,fullName,createTime, secret))
	return '{0}join?meetingID={1}&password={2}&fullName={3}&createTime={4}&checksum={5}'.format(server,meetingID,pw,fullName,createTime,checksum)

@app.route('/join/<meetingid>/<pw>/<createtime>', methods = ['GET', 'POST'])
@app.route('/join/<meetingid>/<pw>/<createtime>/<fullName>', methods = ['GET', 'POST'])
def join(meetingid, pw,createtime,fullName):
	return redirect(joinMeetingCall(meetingid,pw,fullName,createtime))



# end Call: end a session call
def endCall(meetingID,moderatorPW):
	checksum = createHash('endmeetingID={0}&password={1}{2}'.format(meetingID,moderatorPW,secret))
	return '{0}end?meetingID={1}&password={2}&checksum={3}'.format(server,meetingID,moderatorPW,checksum)

@app.route('/closeMeeting/<meetingid>/<moderatorpw>')
def closeMeeting(meetingid,moderatorpw):
	closeMeetingCall = Soup(requests.get(endCall(meetingid,moderatorpw)).content)
	flash(closeMeetingCall.returncode.string)
	flash(closeMeetingCall.message.string)
	return redirect(url_for('index'))



# Detail view of a meeting
@app.route('/meeting/<meetingid>')
@app.route('/meeting/<meetingid>/<moderatorpw>')
def meeting(meetingid,moderatorpw):
	mInfo = getMeetingInfoCall(meetingid,moderatorpw)
	return render_template('meeting.html',
		mInfo = mInfo)























