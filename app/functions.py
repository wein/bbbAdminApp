##############
#### Functions ot the API and calculations

from app import app
import hashlib, requests
from bs4 import BeautifulSoup as Soup
from functools import wraps
from  flask import render_template, flash, redirect, session, url_for, request, g, make_response

#### Parameters & Variable Initialization ####
host = app.config.get('BBBHOST')
secret = app.config.get('SECRET')

defaultMeeting = {'meetingName':app.config.get('MEETINGNAME'), 'meetingID':app.config.get('MEETINGID'), 'moderatorPW':app.config.get('MODERATORPW'), 'attendeePW':app.config.get('ATTENDEEPW'), 'createTime': '-', 'participants': 0, 'record' : False}

joinUsers = {}
record = False


##################
# Auxiliary functions

# Creates the checksum of an input string
def createHash(hashString):
	m = hashlib.sha1()
	m.update(hashString)
	return m.hexdigest()

# Updates joinUsers, a dict that has the current meetings as keys and a 
# dictionary of usernames and join-links as values. This is to keep track of 
# join links that are created for running meetings.
def updateJoinUsers(meetings):
	mIDlist = []
	for m in meetings:
		meetingID = m.meetingid.string
		mIDlist.append(meetingID)
		if meetingID not in joinUsers.keys():
			joinUsers[meetingID]={}
	for mID in joinUsers.keys():
		if mID not in mIDlist:				
			del joinUsers[mID]

# Decorator function that checks the BBB-server is available
def bbbConnectionCheck(f):
	@wraps(f)
	def decorated_function(*args,**kwargs):
		try:
			getMeetings()
		except:
			return render_template("connectionProblem.html")
		return f(*args, **kwargs)
	return decorated_function


##################
# Administration functions

# Creates an API call to generate a new meeting session
def createMeetingCall(meetingName,meetingID,moderatorPW,attendeePW,record):
	checksum = createHash('createname={0}&meetingID={1}&moderatorPW={2}&attendeePW={3}&record={4}{5}'.format(meetingName,meetingID,moderatorPW,attendeePW,record,secret))
	apiCall = '{0}create?name={1}&meetingID={2}&moderatorPW={3}&attendeePW={4}&record={5}&checksum={6}'.format(host,meetingName,meetingID,moderatorPW,attendeePW,record,checksum)
	return Soup(requests.get(apiCall).content)

# Create an join meeting API call that expires with the current session
def joinMeetingCall(meetingID,pw,fullName,createTime):
	checksum = createHash('joinmeetingID={0}&password={1}&fullName={2}&createTime={3}{4}'.format(meetingID,pw,fullName,createTime, secret))
	return '{0}join?meetingID={1}&password={2}&fullName={3}&createTime={4}&checksum={5}'.format(host,meetingID,pw,fullName,createTime,checksum)

# # Create a Non-expiring join meeting API call
# def joinMeetingCallPersistent(meetingID,pw,fullName):
# 	checksum = createHash('joinmeetingID={0}&password={1}&fullName={2}{3}'.format(meetingID,pw,fullName, secret))
# 	return '{0}join?meetingID={1}&password={2}&fullName={3}&checksum={4}'.format(host, meetingID, pw, fullName, checksum)

# end Call: end a session call
def endCall(meetingID,moderatorPW):
	checksum = createHash('endmeetingID={0}&password={1}{2}'.format(meetingID,moderatorPW,secret))
	return '{0}end?meetingID={1}&password={2}&checksum={3}'.format(host,meetingID,moderatorPW,checksum)


##################
# Monitoring Calls

# Get Meeting Info Call generator
def getMeetings():
	checksum = createHash('getMeetings{0}'.format(secret))
	apiCall = '{0}getMeetings?checksum={1}'.format(host,checksum)
	return Soup(requests.get(apiCall).content)

def getMeetingInfo(meetingid,moderatorpw):
	checksum = createHash('getMeetingInfomeetingID={0}&password={1}{2}'.format(meetingid,moderatorpw,secret))
	apiCall = '{0}getMeetingInfo?meetingID={1}&password={2}&checksum={3}'.format(host,meetingid,moderatorpw,checksum)
	return Soup(requests.get(apiCall).content)

def getParticipants(meetings):
	participantsDict = {}
	for m in meetings:
		mID = m.meetingid.string
		participantsDict[mID]=getMeetingInfo(mID.replace(' ','%20'),m.moderatorpw.string).participantcount.string
	return participantsDict

def getIsRunning(meetingID):
	checksum = createHash('isMeetingRunningmeetingID={0}{1}'.format(meetingID,secret))
	apiCall = '{0}isMeetingRunning?meetingID={1}&checksum={2}'.format(host,meetingID,checksum)
	if Soup(requests.get(apiCall).content).running.string == 'true':
		return True
	else:
		return False








