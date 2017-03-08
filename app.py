import os, json, boto3
import pyaudio
import wave
import time
from flask import Flask, render_template, request, json, redirect, session, send_from_directory, url_for
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash, secure_filename
from pyAudioAnalysis import audioTrainTest as aT


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
    return render_template('signup.html')

@app.route('/signUp', methods = ['POST'])
def signUp():
	_name = request.form['inputName']
	_email = request.form['inputEmail']
	_password = request.form['inputPassword']
	print (request.form['inputNew'])

	_hashed_password = generate_password_hash(_password)
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.callproc('sp_createUser',(_name,_email,_password))
	data = cursor.fetchall()

	if len(data) is 0:
 		conn.commit()
 		return json.dumps({'message':'User created successfully !'})

 	# else:
 	# 	return json.dumps({'html':'<span>Enter the required fields</span>'})


	# if _name and _email and _password:
	# 	return json.dumps({'html':'<span>All fields good !!</span>'})
	# else:
	# 	return json.dumps({'html':'<span>Enter the required fields</span>'})

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
		return render_template('uploadS3.html')

@app.route('/upload', methods= ['POST'])
def upload():
	if session.get('user'):
		myfile = request.files['file']

		filename = secure_filename(myfile.filename)
		

		_username = session['user'][1]
	#	os.mkdir('uploads/'+_username)
		print session['user']
		#print _email

		path = os.path.join(app.config["UPLOAD_FOLDER"], _username)
		path = os.path.join(path,filename)

		myfile.save(path)

		myList = ["uploads/mike",'uploads/test']
		aT.featureAndTrain(myList,1.0,1.0,aT.shortTermWindow,aT.shortTermStep,'svm',_username,False)
		print aT.fileClassification('uploads/Audio_Track-6.wav',_username,'svm')
		return render_template('index.html')

@app.route('/showSendText', methods=["GET"])
def showSendText():
	# CHUNK = 1024
	# FORMAT = pyaudio.paInt16
	# CHANNELS = 2
	# RATE = 44100
	# RECORD_SECONDS = 1
	# WAVE_OUTPUT_FILENAME = "output1.wav"

	# p = pyaudio.PyAudio()

	# stream = p.open(format=FORMAT,
	#                 channels=CHANNELS,
	#                 rate=RATE,
	#                 input=True,
	#                 frames_per_buffer=CHUNK)

	# print("* recording")

	# frames = []

	# for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	#     data = stream.read(CHUNK)
	#     frames.append(data)

	# print("* done recording")

	# stream.stop_stream()
	# stream.close()
	# p.terminate()

	# wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	# wf.setnchannels(CHANNELS)
	# wf.setsampwidth(p.get_sample_size(FORMAT))
	# wf.setframerate(RATE)
	# wf.writeframes(b''.join(frames))
	# wf.close()
	return render_template('sendText.html')

@app.route('/addContact')
def addContact():
	return render_template('addContact.html')

@app.route('/sendText', methods =['POST'])
def sendText():
	print type(request.files)
	path = os.path.join(app.config["UPLOAD_FOLDER"])
	filename = str(time.time())+"something.wav"
	path = os.path.join(path,filename)

	request.files['lkjkj'].save(path)

	return render_template('index.html')


if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

