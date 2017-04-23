import os, json
import pyaudio
import wave
import time
import cutAudio
from flask import Flask, render_template, request, json, redirect, session, send_from_directory, url_for
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash, secure_filename
from pyAudioAnalysis import audioTrainTest as aT
from twilio.rest import Client

# Your Account SID from twilio.com/console
account_sid = "AC7407fc4200b8481833bce71b66bc6d4a"
# Your Auth Token from twilio.com/console
auth_token  = "c53f3e49f9c08602d1cc008bc588d777"

client = Client(account_sid, auth_token)

mysql = MySQL()
app = Flask(__name__)
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'BucketList'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','wav'])
mysql.init_app(app)
app.secret_key = 'why would I tell you my secret key?'




@app.route("/")
def main():
    return render_template('index.html')

@app.route("/main")
def goHome():
	return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('newSignUp.html')

@app.route('/signUp', methods = ['POST'])
def signUp():
	_name = request.form['inputName']
	print _name+"name"
	_email = request.form['inputEmail']
	_password = request.form['inputPassword']

	_hashed_password = generate_password_hash(_password)
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.callproc('sp_createUser',(_name,_email,_password))
	data = cursor.fetchall()
#	return None
	if len(data) is 0:
 		conn.commit()
 		return json.dumps({'message':'User created successfully !'})

@app.route('/showSignIn')
def showSignIn():
    return render_template('signin.html')

@app.route('/validateLogin', methods= ['POST'])
def validateLogin():
	try:
		_username = request.form['inputEmail']
		_password = request.form['inputPassword']
		con = mysql.connect()
		cursor = con.cursor()
		cursor.callproc('sp_validateLogin',(_username,))
		data = cursor.fetchall()
		if len(data) >0:
			if str(data[0][3]) == _password:
				print (data[0])
				session['user'] = data[0]
				return redirect('/userHome')
			else:
				return render_template('error.html', error = "Wrong email")

		else:
			return render_template('error.html', error = "wrong email")
	except Exception as e:
		return render_template('error.html', error = str(e))

@app.route('/userHome', methods = ['GET'])
def userHome():
	if session.get('user'):
		user_data = session['user']
		print (str(user_data)+"THE USER DATA")

		letters = user_data[4:]

		alphabet = ['a','b','c','d']
		dictionary = {}
		for i,char in enumerate(alphabet):
			dictionary[char] = letters[i]


		lettersNeeded = []
		for letter in dictionary.keys():
			if dictionary[letter] == None:
				lettersNeeded.append(letter)
		print (lettersNeeded)
		lettersNeeded = [x.upper() for x in lettersNeeded]


		_username = user_data[1]



		return render_template('userHomeNew.html', lettersNeeded = sorted(lettersNeeded), _username = _username)
	else:
		return render_template('error.html', error = "Unauthoraized access")
@app.route('/logout')
def logut():
	session.pop('user',None)
	return redirect("/")

@app.route('/showInput')
def showInput():
	if session.get('user'):
		return render_template('showInput.html')
@app.route('/showUpload')
def showUpload():
	if session.get('user'):
		return render_template('upload.html')

@app.route('/upload', methods= ['POST'])
def upload():
	if session.get('user'):
		myfile = request.files['file']
		print request.form['Letter']
		filename = secure_filename(myfile.filename)
		dirName, fileExtension = os.path.splitext(filename)
		_username = session['user'][1]
		if not os.path.exists('uploads/'+_username+"/"+dirName):
			os.mkdir('uploads/'+_username+"/"+dirName)
		print session['user']
		#print _email

		path = os.path.join(app.config["UPLOAD_FOLDER"], _username,dirName)
		path = os.path.join(path,filename)

		myfile.save(path)
		cutAudio.cutAudio(_username,dirName)
		cutAudio.removeOldFile(_username, dirName)

		# myList = ["uploads/mike",'uploads/test']
		# aT.featureAndTrain(myList,1.0,1.0,aT.shortTermWindow,aT.shortTermStep,'svm',_username,False)
		# print aT.fileClassification('uploads/Audio_Track-6.wav',_username,'svm')
		return render_template('index.html')

@app.route('/showSendText', methods=["GET"])
def showSendText():
	print "inloadcontacs"
	if session.get('user'):
		name = session['user'][1]
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.callproc('sp_loadContacts',(name,))
		tupleOfContacts = cursor.fetchall()[1:]
		listOfContacts = []
		for contact in tupleOfContacts:
			listOfContacts.append(contact[0])
		return render_template('sendText.html',listOfContacts=listOfContacts)

@app.route('/showAddContact')
def showAddContact():
	return render_template('addContact.html')
@app.route('/addContact', methods=['POST'])
def addContact():
	c_name = request.form['inputName']
	c_number = request.form['inputPhone']
	name = session['user'][1]
	username = session['user'][2]
	password = session['user'][3]
	#_hashed_password = generate_password_hash(_password)
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.callproc('sp_addContactNew',(name,username,password,c_name,c_number))
	data = cursor.fetchall()
#	return None
	if len(data) is 0:
 		conn.commit()
 		return json.dumps({'message':'User created successfully !'})

@app.route('/sendText', methods =['POST'])
def sendText():
	print "in send text"
	#print type(request.files)
	username = session['user'][1]
	path = os.path.join(app.config["UPLOAD_FOLDER"],username)
	filename = str(time.time())+"something.wav"
	path = os.path.join(path,filename)
	request.files['lkjkj'].save(path)
	print path
	classification = aT.fileClassification(path,'uploads/'+username+'/'+username,"extratrees")
	index = int(classification[0])
	print index
	print classification
	letter = classification[2][index]
	#os.remove(path)
	return letter

@app.route('/train')
def train():
	if session.get('user'):
		username = session['user'][1]
		if os.path.exists('uploads/'+username+'/'+username):
			os.remove('uploads/'+username+'/'+username)
		if os.path.exists('uploads/'+username+'/'+username+'.arff'):
			os.remove('uploads/'+username+'/'+username+'.arff')		
		if os.path.exists('uploads/'+username+'/'+username+"MEANS"):
			os.remove('uploads/'+username+'/'+username+"MEANS")
		if os.path.exists('uploads/'+username+'/'+username+"SMtemp"):
			os.remove('uploads/'+username+'/'+username+"SMtemp")
		if os.path.exists('uploads/'+username+'/'+username+"SMtemp.arff"):
			os.remove('uploads/'+username+'/'+username+"SMtemp.arff")
		if os.path.exists('uploads/'+username+'/'+username+"SMtempMEANS"):
			os.remove('uploads/'+username+'/'+username+"SMtempMEANS")

		listOfDirs = os.listdir('uploads/'+username)
		myList = []
		for directory in listOfDirs:
			myList.append('uploads/'+username+'/'+directory)
		aT.featureAndTrain(myList,1.0,1.0,aT.shortTermWindow,aT.shortTermStep,'extratrees','uploads/'+username+'/'+username,False)
		if os.path.exists('uploads/'+username+'/'+directory+'/'+directory+'.wav'):
			os.remove('uploads/'+username+'/'+directory+'/'+directory+'.wav')
		return render_template('userHomeNew.html')


@app.route('/loadContacts', methods=['GET'])
def loadContacts():
	print "inloadcontacs"
	if session.get('user'):
		name = session['user'][1]
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.callproc('sp_loadContacts',(name,))
		tupleOfContacts = cursor.fetchall()[1:]
		listOfContacts = []
		for contact in tupleOfContacts:
			listOfContacts.append(contact)
		return listOfContacts

@app.route('/selectedContact', methods = ['GET', 'POST'])
def selectedContact():
	print "IN SELECTED CONTACT"
	name= request.form['clicked_id']
	text = request.form['text']
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.callproc('sp_getNumber',(name,))
	number = cursor.fetchall()[0][0]
	print number
	message = client.messages.create(
    to=number, 
    from_="+16103475834",
    body=text)
	return "success!"









if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)

