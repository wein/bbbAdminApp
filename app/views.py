from  flask import render_template, flash, redirect, session, url_for, request, g, make_response
from app import app
from forms import createMeetingForm, joinMeetingForm
# from flask.ext.ldap import LDAP, login_required
from datetime import datetime
import hashlib, requests
from bs4 import BeautifulSoup as Soup

server = 'http://conference.tngtech.com/bigbluebutton/api/'
secret = 'b453bf804155f4b33d973c9ba25079a7'

# --------  Parameters  --------
name = 'Test'
attendeePW = 'ap'
moderatorPW = 'mp'
fullName = 'User'
welcome = ''
maxParticipants = ''
joinUsers = {}
# record = False

# # Login Config
# app.config['LDAP_HOST'] = 'ldap.int.tngtech.com'
# app.config['LDAP_PORT'] = '636'
# app.config['LDAP_DOMAIN'] = 'tngtech.com'
# app.config['LDAP_SEARCH_BASE'] = 'OU=Users,DC=tngtech.com,DC=com'
# app.config['LDAP_LOGIN_VIEW'] = 'login'
# app.config['LDAP_LOGIN_TEMPLATE'] = 'login.html'
# app.config['LDAP_SUCCESS_REDIRECT'] = 'index'

# ldap = LDAP(app)
# app.secret_key = "hellos"
# app.add_url_rule('/login', 'login', ldap.login, methods=['GET', 'POST'])


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

def updateJoinUsers(meetings):
	mIDlist = []
	for m in meetings:
		mIDlist.append(m.meetingid.string)
	for mID in joinUsers.keys():
		if mID not in mIDlist:				
			del joinUsers[mID]
	print joinUsers


def getParticipants(meetings):
	participantsDict = {}
	for m in meetings:
		mID = m.meetingid.string
		print mID
		print m.moderatorpw.string
		participantsDict[mID]=getMeetingInfoCall(mID,m.moderatorpw.string).participantcount.string
	return participantsDict

# Root handler
@app.route('/')
@app.route('/index')
# @login_required
def index():
	meetings = getMeetingsCall().find_all('meeting')
	# try:
	participants = getParticipants(meetings)
	updateJoinUsers(meetings)
	return render_template("index.html", 
		meetings = meetings,
		participants = participants)
	# except:
	# 	return render_template("index.html", 
	# 		meetings = {},
	# 		participants = 0)

@app.route('/login', methods=['GET', 'POST'])
def login():
    render_template("index.html")



# handler to generate new meetings functionality
@app.route('/new', methods = ['GET', 'POST'])
def new():
	form = createMeetingForm()
	if form.validate_on_submit():
		record = False
		createMeetingStatus = createMeetingCall(form.meetingName.data, form.meetingName.data, form.moderatorPW.data, form.attendeePW.data, record)
		flash(createMeetingStatus.returncode.string)
		joinUsers[str(form.meetingName.data)]={}
		return redirect(url_for('index'))
	return render_template("new.html", 
		title = 'New Meeting',
		# secret = secret,
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
@app.route('/meeting/<meetingid>', methods=['GET', 'POST'])
@app.route('/meeting/<meetingid>/<moderatorpw>', methods=['GET', 'POST'])
def meeting(meetingid,moderatorpw):
	form = joinMeetingForm()
	mInfo = getMeetingInfoCall(meetingid,moderatorpw)
	if mInfo.messagekey.string == 'notFound':
		flash('Meeting has expired.')
		return redirect(url_for('index'))
	if form.validate_on_submit():
		joinURL = joinMeetingCall(mInfo.meetingid.string,mInfo.attendeepw.string,form.username.data,mInfo.createtime.string)
		# flash('Success! URL created: '+joinURL)
		joinUsers[mInfo.meetingid.string][form.username.data]=joinURL
		return redirect(url_for('meeting', meetingid=mInfo.meetingid.string,moderatorpw=mInfo.moderatorpw.string))
	return render_template('meeting.html',
		mInfo = mInfo,
		form = form,
		joinUsers = joinUsers)























