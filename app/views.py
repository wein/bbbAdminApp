####### VIEWS CONTROLLER ##########

from functions import *
# from app import app
from forms import createMeetingForm, joinMeetingForm
from time import sleep
# from flask.ext.ldap import LDAP, login_required
# from datetime import datetime


######## ROUTES ######

# Root handler
@app.route('/')
@app.route('/index')
@bbbConnectionCheck
# @login_required
def index():
	meetings = getMeetings().find_all('meeting')
	participants = getParticipants(meetings)
	updateJoinUsers(meetings)
	try: 
		if getMeetingInfo(defaultMeeting['meetingID'],defaultMeeting['moderatorPW']).meetingid.string == defaultMeeting['meetingID']:
			defaultMeetingRunning = True
	except:
		defaultMeetingRunning = False
		# defaultMeeting.update({'participants': participants[defaultMeeting['meetingID']]})
		# defaultMeeting.update({'createTime': 'hi'})
	return render_template("index.html", 
		meetings = meetings,
		participants = participants,
		defaultMeeting = defaultMeeting,
		defaultMeetingRunning = defaultMeetingRunning)
		
	

@app.route('/login', methods=['GET', 'POST'])
@bbbConnectionCheck
def login():
    return redirect(url_for('index'))


# handler to generate new meetings functionality
@app.route('/new', methods = ['GET', 'POST'])
@bbbConnectionCheck
def new():
	form = createMeetingForm()
	if form.validate_on_submit():
		meetingID = form.meetingName.data.replace(' ','')
		meetingName = form.meetingName.data.replace(' ','%20')
		if form.attendeePW.data == '':
			attendeePW= app.config['ATTENDEEPW']
		else:
			attendeePW = form.attendeePW.data
		createMeetingStatus = createMeetingCall(meetingName, meetingID, form.moderatorPW.data, attendeePW, record)
		flash(createMeetingStatus.returncode.string)
		return redirect(url_for('index'))
	return render_template("new.html", 
		title = 'New Meeting',
		form = form)


# handler to redirect to join the client
# To_do: remove route without username
@app.route('/join/<meetingid>/<pw>/<createtime>', methods = ['GET', 'POST'])
@app.route('/join/<meetingid>/<pw>/<createtime>/<fullName>', methods = ['GET', 'POST'])
@bbbConnectionCheck
def joinRedirect(meetingid, pw,createtime,fullName):
	return redirect(joinMeetingCall(meetingid,pw,fullName,createtime))

@app.route('/directJoin')
@bbbConnectionCheck
def joinDefaultMeeting():
	return redirect(url_for('joinMeeting',meetingid = 'defaultMeeting'))


@app.route('/join/<meetingid>/', methods=['GET', 'POST'])
@bbbConnectionCheck
def joinMeeting(meetingid):
	form = joinMeetingForm()
	if meetingid == defaultMeeting['meetingID']:
		meetingInfo = getMeetingInfo(defaultMeeting['meetingID'],defaultMeeting['moderatorPW'])
		del form.attendeePW
		if form.validate_on_submit():
			username = form.username.data
			try:
				return redirect(joinMeetingCall(meetingid,defaultMeeting['attendeePW'],username,meetingInfo.createtime.string))
			except:
				return redirect(url_for('createAndJoinDefaultMeeting', username=username))
	else:
		try:
			meetings = getMeetings().find_all('meeting')
			for m in meetings:
				if m.meetingid.string == meetingid:
					meetingInfo = m
			if meetingInfo.attendeepw.string == app.config['ATTENDEEPW']:
				del form.attendeePW
				attendeePW = app.config['ATTENDEEPW']
			if form.validate_on_submit():
				username = form.username.data
				if form.attendeePW:
					attendeePW = form.attendeePW.data
				try:
					return redirect(joinMeetingCall(meetingid,attendeePW,username,meetingInfo.createtime.string))
				except:
					return redirect(url_for('joinMeeting',meetingid=meetingid))
		except:
			flash('The specified meeting is not currently running!')
			return redirect(url_for('index'))
	return render_template("directJoin.html",
		form = form,
		meetingid = meetingid)



# Redirect for O2 team to directly join our sessions
@app.route('/directJoinO2')
@bbbConnectionCheck
def directJoinO2():
	defaultMeetingInfo = getMeetingInfo(defaultMeeting['meetingID'],defaultMeeting['moderatorPW'])
	try:
		return redirect(joinMeetingCall(defaultMeeting['meetingID'],defaultMeeting['attendeePW'],'O2',defaultMeetingInfo.createtime.string))
	except:
		return redirect(url_for('createAndJoinDefaultMeeting', username='O2'))
		# createMeetingStatus = createMeetingCall(defaultMeeting['meetingName'],defaultMeeting['meetingID'],defaultMeeting['moderatorPW'],defaultMeeting['attendeePW'],False)
		# return redirect(joinMeetingCall(defaultMeeting['meetingID'],defaultMeeting['attendeePW'],'O2',createMeetingStatus.createtime.string))

@app.route('/createDefaultMeeting')
def createDefaultMeeting():
	createMeetingStatus = createMeetingCall(defaultMeeting['meetingName'],defaultMeeting['meetingID'],defaultMeeting['moderatorPW'],defaultMeeting['attendeePW'],False)
	return redirect(url_for('index'))

@app.route('/createAndJoinDefaultMeeting/<username>')
def createAndJoinDefaultMeeting(username):
	createMeetingStatus = createMeetingCall(defaultMeeting['meetingName'],defaultMeeting['meetingID'],defaultMeeting['moderatorPW'],defaultMeeting['attendeePW'],False)
	sleep(2)
	return redirect(joinMeetingCall(defaultMeeting['meetingID'],defaultMeeting['attendeePW'],username,createMeetingStatus.createtime.string))

# Detail view of a meeting
@app.route('/meeting/<meetingid>', methods=['GET', 'POST'])
# @app.route('/meeting/<meetingid>/<moderatorpw>', methods=['GET', 'POST'])
@bbbConnectionCheck
def meeting(meetingid):
	form = joinMeetingForm()
	del form.attendeePW
	try:
		for m in getMeetings().find_all('meeting'):
			if m.meetingid.string == meetingid:
				moderatorpw = m.moderatorpw.string
		mInfo = getMeetingInfo(meetingid,moderatorpw)
		joinLink = url_for('joinMeeting',meetingid=meetingid, _external=True)
		if form.validate_on_submit():
			joinURL = url_for('joinUser', meetingid = meetingid, username = form.username.data, _external=True)
			# joinURL = joinMeetingCall(mInfo.meetingid.string,mInfo.attendeepw.string,form.username.data,mInfo.createtime.string)
			joinUsers[mInfo.meetingid.string][form.username.data]=joinURL
			return redirect(url_for('meeting', meetingid=mInfo.meetingid.string,moderatorpw=mInfo.moderatorpw.string))
		return render_template('meeting.html',
			mInfo = mInfo,
			form = form,
			joinUsers = joinUsers,
			joinLink = joinLink)
	except:
		if meetingid == defaultMeeting['meetingID']:
			flash(defaultMeeting['meetingName']+' is not currently running.')
		else:
			flash('Meeting has expired.')
		return redirect(url_for('index'))

@app.route('/join/<meetingid>/<username>')
def joinUser(meetingid,username):
	if username in joinUsers[meetingid].keys():
		for m in getMeetings().find_all('meeting'):
			if m.meetingid.string == meetingid:
				moderatorpw = m.moderatorpw.string
		mInfo = getMeetingInfo(meetingid,moderatorpw)
		return redirect(joinMeetingCall(meetingid,mInfo.attendeepw.string,username,mInfo.createtime.string))
	else:
		return redirect(url_for('index'))


@app.route('/closeMeeting/<meetingid>/<moderatorpw>')
@bbbConnectionCheck
def closeMeeting(meetingid,moderatorpw):
	closeMeeting = Soup(requests.get(endCall(meetingid,moderatorpw)).content)
	flash(closeMeeting.returncode.string)
	flash(closeMeeting.message.string)
	return redirect(url_for('index'))

















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







	# if meetingid == defaultMeeting['meetingID']:
	# 	MeetingInfo = getMeetingInfo(defaultMeeting['meetingID'],defaultMeeting['moderatorPW'])
	# else:
	# 	meetings = getMeetings().find_all('meeting')
	# 	for m in meetings:
	# 		if m.meetingid.string == meetingid:
	# 			meetingInfo = m
	# if meetingInfo.attendeepw.string == app.config['ATTENDEEPW']:
	# 	del form.attendeePW
	# if form.validate_on_submit():
	# 	username = form.username.data
	# 	# if hasattr(form, 'attendeePW'):
	# 	if form.attendeePW.data == '':
	# 		attendeePW = app.config['ATTENDEEPW']
	# 	else:
	# 		attendeePW = form.attendeePW.data
	# 	print attendeePW
	# 	try:
	# 		return redirect(joinMeetingCall(meetingid,attendeePW,username,meetingInfo.createtime.string))
	# 	except:
	# 		if meetingid == defaultMeeting['meetingID']: 
	# 			createMeetingStatus = createMeetingCall(defaultMeeting['meetingName'],defaultMeeting['meetingID'],defaultMeeting['moderatorPW'],defaultMeeting['attendeePW'],False)
	# 			sleep(2)
	# 			return redirect(joinMeetingCall(defaultMeeting['meetingID'],defaultMeeting['attendeePW'],username,createMeetingStatus.createTime.string))
	# 		else:
	# 			flash('The specified meeting is not currently running!')
	# 			return redirect(url_for('index'))
	# return render_template("directJoin.html",
	# 	form = form,
	# 	meetingid = meetingid)


