
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 14:41:56 2018

@author: Group-1
"""
from flask import Flask, render_template, request, session
import sqlite3
import aiml
from seminar2_progress import sntnce as s
import random
import re
from mappings import map_keys
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

botName = "P8-Bot"

@app.route("/")
def home():
	global botName
	session['sid'] = random.randint(1,10000) #uuid.uuid4()
	k.learn("std-startup.xml")
	k.respond("load aiml b", session.get('sid'))
	botName = k.getBotPredicate("name")
	k.setPredicate('email', '', session.get('sid'))

	return render_template("index.html")

@app.route("/get")
def get_bot_response():
	userText = request.args.get('msg')
	return (start(userText))


sent_check = s.Sent_Similarity()

k = aiml.Kernel()
#k.learn("std-startup.xml")
#k.respond("load aiml b")
#botName = k.getBotPredicate("name")
userName = "Anonymous"
# a global id for authentication purpose
user_auth_id=0;
#k.setPredicate('email', '')
GREETING = ['Hello! My name is P8-bot. I will try my best to provide you information related to our College!']

DEFAULT_RESPONSES = ["I did not get you! Pardon please!","I couldn't understand what you just said! Kindly rephrase"
					 " what you said :-)", "What you are saying is out of my understanding! You can ask me"
					 " queries regrading RCOEM, your attendance and grades" ]

EMPTY_RESPONSES = ["Say something! I would love to help you!","Don't hesitate. I'll answer your queries to the best"
				   " of my knowledge!","Say my friend!"]

ONE_WORD_RESPONSES = ["Please elaborate your query for me to understand!", "I could not understand your context, please say more!",
					  "Sorry, I could not get you! Please say something more for me to understand!"]

AUTH_KEYWORDS = ['login', 'cgpa', 'sgpa', 'grades', 'gpa']

AUTH_NOT_REQD = -1
AUTH_NOT_SUCC = 0
AUTH_SUCC = 1
UNAME_REQ = 0
PWD_REQ = 0

#conn = sqlite3.connect('/home/chintan/Projects/College-Information-Chatbot-System-master/seminar2_progress/shrya/sqlite/db/pythonsqlite.db')

#c = conn.cursor()

INVALID_UNAME_RES = ['Invalid username! Would you like to retry or have changed your mood?',
					 'Username does not exist! Would you like to retry or have changed your mood?',
					 'I suppose you forgot your username! Would you like to retry or have changed your mood?']
INVALID_PWD_RES = ['Invalid password! Would you like to retry or have changed your mood?',
					 'I suppose you forgot your password! Would you like to retry or have changed your mood?']

def login(user=False):
	global userName, UNAME_REQ, PWD_REQ
	conn = sqlite3.connect('pythonsqlite.db')
	c=conn.cursor()
	if(k.getPredicate('user_id', session.get('sid'))!=''):
		
		c.close()
		conn.close()
		return int(k.getPredicate('user_id', session.get('sid')))

	if(user==False):

		UNAME_REQ = 1
		c.close()
		conn.close()
		return("Please provide me your username!")
#        user = get_bot_response()
#        k.setPredicate('email', user)
#        k.setPredicate('pwd','')

	if(k.getPredicate('email')!=''):
		user = k.getPredicate('email', session.get('sid'))
		
	c.execute('SELECT id from LOGIN WHERE email=?', [user])   
	pwd = k.getPredicate('pwd', session.get('sid'))
#    print(c.fetchone())
	if(c.fetchone()):
		if(pwd==''):
			PWD_REQ = 1
			c.close()
			conn.close()
			return("Please provide me your password!")
#            pwd = request.args.get('msg')
#            k.setPredicate('pwd', pwd)
			
		c.execute('SELECT id from LOGIN WHERE email=? and pswd=?', [user, pwd])
		idn = c.fetchone()
		if(idn is not None):
			k.setPredicate('user_id', idn[0], session.get('sid'))
			c.execute('SELECT fname from STUD_INFO where id = ?',  idn)
			fname = c.fetchone()[0]
#            print(fname)
			# set predicate name to fname in AIML
			if(k.getPredicate('name', session.get('sid')) in ['Anonymous', '']):
				k.setPredicate('name',fname, session.get('sid'))
#        print(idn)
		if(idn):
			c.close()
			conn.close()
			return('You are Logged In Successfully!', idn[0])
		else:
			c.close()
			conn.close()
			return(random.choice(INVALID_PWD_RES))
			choice = input(userName+": ")
			if('retry' in choice and 'not' not in choice):
				c.close()
				conn.close()
				return login(user)
			else:
				c.close()
				conn.close()
				return None
	else:
		printBot(random.choice(INVALID_UNAME_RES))
		choice = preprocess(input(userName+": "))
		if('RETRY' in choice and 'NOT' not in choice):
			c.close()
			conn.close()
			return login(False)
		else:
			c.close()
			conn.close()
			return None
	# printUser(K.user + inpt1)

def logout():
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
	k.setPredicate('user_id','', session.get('sid'))
	k.setPredicate('email','', session.get('sid'))
	k.setPredicate('pwd','', session.get('sid'))
	c.close()
	conn.close()
	return("I have cleared your login information from my memory! Don't worry, you can trust me anytime!")
	
def displayAllGPA(idn):
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
	c.execute('SELECT fname, sem_id from STUD_INFO where id = ?',  [idn])
	fname, sem_id = c.fetchone()
	# set predicate name to fname in AIML
	if(k.getPredicate('name', session.get('sid')) in ['Anonymous', '']):
		k.setPredicate('name',fname, session.get('sid'))
	# find the GPA accordingly
	query = 'SELECT * from GPA_DETAILS where id = ?'
#    print(query)
	c.execute(query,  [idn])
	result = c.fetchall()[0][1:]
	res_list = {}
	count = 0
	for sgpa in result:
		count = count+1
		if(sgpa==0):
			break;
		res_list["Sem-"+str(count)] = sgpa
#    print(result)
	c.close()
	conn.close()
	return("Your semester wise sgpa is as follows: " +str(res_list))
	
	
def findGPA(idn):
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
	c.execute('SELECT fname, sem_id from STUD_INFO where id = ?',  [idn])
	fname, sem_id = c.fetchone()
	# set predicate name to fname in AIML
	if(k.getPredicate('name', session.get('sid')) in ['Anonymous', '']):
		k.setPredicate('name',fname, session.get('sid'))
	# find the GPA accordingly
#    query = 'SELECT sem'+str(sem_id)+' from GPA_DETAILS where id = ?'
	query = 'SELECT * from GPA_DETAILS where id = ?'
#    print(query)
	c.execute(query,  [idn])
	result = c.fetchall()
#    print(result)
	c.close()
	conn.close()
	return findCGPA(result[0][1:])
	
def findCGPA(sgpa):
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
#    print(sgpa)
	cgpa = 0
	sem = 0
	for gpa in sgpa:
		cgpa+=gpa
		if(gpa!=0.0):
			sem= sem+1
	if(sem==0):
		sem=1
	cgpa/=sem
	cgpa = round(cgpa,2)
	c.close()
	conn.close()
	return('Your CGPA is '+str(cgpa))

def findGPA_sem(idn, sem_id):
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
	c.execute('SELECT fname from STUD_INFO where id = ?',  [idn])
	fname = c.fetchone()
	# set predicate name to fname in AIML
	if(k.getPredicate('name', session.get('sid')) in ['Anonymous', '']):
		k.setPredicate('name',fname, session.get('sid'))
	# find the GPA accordingly
	sem = 'sem'+str(sem_id);
	query = 'SELECT '+sem+' from GPA_DETAILS where id = ?'
#    print(query)
	c.execute(query,  [idn])
	result = c.fetchall()[0][0]
	c.close()
	conn.close()
	return('Your SGPA of '+sem+ " is "+ str(result))
	
def findGPA_current(idn):
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
	c.execute('SELECT fname, sem_id from STUD_INFO where id = ?',  [idn])
	fname, sem_id = c.fetchone()
	# set predicate name to fname in AIML
	if(k.getPredicate('name', session.get('sid')) in ['Anonymous', '']):
		k.setPredicate('name',fname, session.get('sid'))
	# find the GPA accordingly
	query = 'SELECT sem'+str(sem_id)+' from GPA_DETAILS where id = ?'
#    print(query)
	c.execute(query,  [idn])
	result = c.fetchall()[0][0]
	if(result==0.0):
		c.close()
		conn.close()
		return('Results are not out yet!!')
	else:
		c.close()
		conn.close()
		return('Your current SGPA is '+ str(result))


def checkIfAuthRequired(inp):
	# do initial pre-processing
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
	ensw = sent_check.ensw
	inp = inp.lower()
	test_inp = inp.split(' ')
	test_inp = [word for word in test_inp if word not in ensw]
	
	if 'not' not in test_inp:
		k.setPredicate('email', k.getPredicate('email', session.get('sid')).lower(), session.get('sid'))
		k.setPredicate('pwd', k.getPredicate('pwd', session.get('sid')).lower(), session.get('sid'))
		for keyword in AUTH_KEYWORDS:
			if(keyword in test_inp):
				if(('login' not in test_inp) and (k.getPredicate('email')=='')):
					c.close()
					conn.close()
					return('You will have to first authenticate yourself!')
				c.close()
				conn.close()
				return 1
	if('logout' in test_inp):
		logout()
	c.close()
	conn.close()    
	return -1

def conv_mapping(inp):
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
	new_inp = ''
	keys = map_keys.keys()
	arr = inp.split()
	for a in arr:
		if(a in keys):
			new_inp = new_inp + str(map_keys[a])
		else:
			new_inp = new_inp + a
	c.close()
	conn.close() 
	return new_inp

def providePersonalInfo(inp, idn):
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
	p_inp = preprocess(inp).split(' ')
	if(('CGPA') in p_inp):
		c.close()
		conn.close() 
		return findGPA(idn)
	elif((('GPA' in p_inp) or ('SGPA' in p_inp)) and (('ALL' in p_inp) or ('EVERY' in p_inp) or ('EACH' in p_inp))):
		c.close()
		conn.close() 
		return displayAllGPA(idn)
	elif((('GPA' in p_inp) or ('SGPA' in p_inp)) and (('SEMESTER' in p_inp) or ('SEM' in p_inp)) and ('CURRENT' not in p_inp)):
		inp = conv_mapping(inp)
		match = re.search('\\d', inp)
		if(match!=None):
			sem_id = int(match.group())
			c.close()
			conn.close() 
			return findGPA_sem(idn, sem_id)
		else:
			c.close()
			conn.close() 
			return(random.choice(DEFAULT_RESPONSES))
	elif(('GPA' in p_inp) or ('SGPA' in p_inp) or ('CURRENT' in p_inp)):
		c.close()
		conn.close() 
		return findGPA_current(idn)
#    else:
#        print("ok")
#        printBot(random.choice(DEFAULT_RESPONSES))


def auth_module(inp):
	global userName
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
	if(checkIfAuthRequired(inp)==-1):
		c.close()
		conn.close() 
		return -1
	if(k.getPredicate('email', session.get('sid'))!="" and k.getPredicate("pwd", session.get('sid'))!=""):
		user = k.getPredicate('email', session.get('sid'))
		pwd = k.getPredicate('pwd', session.get('sid'))
		c.execute('SELECT id from LOGIN WHERE email=? and pswd=?', [user, pwd])
		idn = c.fetchone()
		if(idn is not None):
			k.setPredicate('user_id', idn[0], session.get('sid'))
			
	if(k.getPredicate('user_id', session.get('sid'))!=""):
		check_inp = inp.lower().split(' ')
		if(('login' in check_inp) and ('not' not in check_inp)):
			return('You are already logged in!')
	idn = login()
	
	if(type(idn)==str):
		return idn
	elif(idn!=None):
		info = providePersonalInfo(inp, idn)
		if(k.getPredicate('name', session.get('sid'))!=''):
			userName = k.getPredicate('name', session.get('sid'))
		c.close()
		conn.close() 
		return info
	else:
		c.close()
		conn.close() 
		return("Operation aborted")
	

def printBot(msg, lst=None):
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
	print(botName+": "+msg)
	if(lst!=None):
		print(botName+": ",lst)
	c.close()
	conn.close() 
	
def match(line, word):
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
	pattern = '\\b'+word+'\\b'
	if re.search(pattern, line, re.I)!=None:
		c.close()
		conn.close() 
		return True
	c.close()
	conn.close() 
	return False

def matchingSentence(inp):
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
	f = open('database/questions.txt')
	match = "";
	max_score=0;
	for line in f.readlines():
		score = sent_check.symmetric_sentence_similarity(inp, line)
		if score > max_score:
			max_score = score
			match = line
	f.close()
	c.close()
	conn.close() 
	return match, max_score

def preprocess(inp):
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
	if(inp!=""):
		if inp[-1]=='.':
			inp = inp[:-1]
	# to remove . symbol between alphabets. Eg. E.G.C becomes EGC
	inp = re.sub('(?<=\\W)(?<=\\w)\\.(?=\\w)(?=\\W)','',inp) 
	# to remove - symbol between alphabet. Eg. E-G-C becomes EGC
	inp = re.sub('(?<=\\w)-(?=\\w)',' ',inp) 
	# to remove . symbol at word boundaries. Eg. .E.G.C. becomes E.G.C
	inp = re.sub('((?<=\\w)\\.(?=\\B))|((?<=\\B)\\.(?=\\w))','',inp)
	# to remove ' ' symbol in acronyms. Eg. E B C becomes EBC
	inp = re.sub('(?<=\\b\\w) (?=\\w\\b)','',inp)
	inp = inp.upper()
#    print(inp)
	c.close()
	conn.close() 
	return inp

def isKeyword(word):
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
	f = open('database/questions.txt','r')
	keywords = f.read().split()
#    print(keywords)
	if(word in keywords):
		c.close()
		conn.close() 
		return True
	else:
		c.close()
		conn.close() 
		return False

def start(inp):

	global userName,UNAME_REQ,PWD_REQ
	conn = sqlite3.connect('pythonsqlite.db')

	c = conn.cursor()
	print(session.get('sid'))
	# tasks: remove punctuation from input or make it get parsed, do something when no match is found; removed last period to end sentence
	p_inp = preprocess(inp)
	# function for transfer to authentication module
	auth = auth_module(inp)
	if(auth!=-1):
		c.close()
		conn.close() 
		return auth
	
	inp = p_inp
	response = k.respond(inp, session.get('sid'))
	if(response=='No match'):
		# to invalidate wrong one-word input
		if(len(inp.split(" "))==1):
			if(isKeyword(inp)==False):
				if(UNAME_REQ==1):
					k.setPredicate('email',inp, session.get('sid'))
					UNAME_REQ = 0
					PWD_REQ = 1
					c.close()
					conn.close() 
					return "Please provide me your password too!"
				if(PWD_REQ==1):
					k.setPredicate('pwd',inp, session.get('sid'))
					PWD_REQ = 0
					c.close()
					conn.close() 
					return "I'll now be able to answer your GEMS related queries if your credentials are valid! Otherwise you will have to provide your credentials again!"
				c.close()
				conn.close() 
				return(random.choice(ONE_WORD_RESPONSES))
				
		inp = matchingSentence(inp)
#        print(inp)
		response = k.respond(inp[0], session.get('sid'))
		confidence = inp[1]
		if(confidence < 0.5):
			log = open('database/invalidated_log.txt','a')
			log.write(p_inp+"\n")
			log.close()
			c.close()
			conn.close() 
			return(random.choice(DEFAULT_RESPONSES))
		else:
			response = re.sub('( )?(http:[%\-_/a-zA-z0-9\\.]*)','<a href="\\2">\\2</a>',response)
#            print(response)
			c.close()
			conn.close() 
			return(response)
	elif(response==""):
		c.close()
		conn.close() 
		return(random.choice(EMPTY_RESPONSES))
	else: 
		response = re.sub('( )?(http:[%\-_/a-zA-z0-9\\.]*)','<a href="\\2">\\2</a>',response)
		c.close()
		conn.close() 
		return (response)
	
	if(k.getPredicate('name', session.get('sid'))!=""):
		userName = k.getPredicate('name', session.get('sid'))
	else:
		k.setPredicate('name','Anonymous', session.get('sid'))
		userName = k.getPredicate('name', session.get('sid'))    

	c.close()
	conn.close() 



if __name__ == "__main__":
	app.run()
	