import time
import os
import multiprocessing
import logging
import socket
import xml.etree.ElementTree as ET
import sys
import json
import copy
import queue
from helper import list_clients, to_client_exist
from socket import error as socket_error

#usage: ini_client.php (port_num) (process_id) (client_names) (ip)
if len(sys.argv) != 5: 
	print('exit')
	sys.exit(1)

print("*****************************************************\n Client Name: " + sys.argv[3] + "\n*****************************************************\n\n")

clients_list = list_clients()
client_sockets = []
lock = multiprocessing.Lock()

request_queue = multiprocessing.Queue()

#active mode connecting here!
for c_info in clients_list: 
	if c_info['name'] == sys.argv[3]:
		continue
	time.sleep(1)
	print("[Active Socket]Connecting to the client " + c_info['name'] + " > " + c_info['ip'] + ":" + c_info['port'] + ".....")
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		sock.connect((c_info['ip'], int(c_info['port'])))
		sock.sendall(sys.argv[3])
		client_sockets.append(sock)
		print("[Active Socket]Connected to the client " + c_info['name'] + "\n")
	except socket_error as serr:
		print("[Active Socket]Cannot reach the client " + c_info['name'] + "\n")


#passive mode connecting here!
print("Client enters [Passive] connecting mode ... ...\n")
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind((sys.argv[4], int(sys.argv[1])))
socket.listen(24)
blockchain_socket = None

while (len(client_sockets) < len(clients_list) - 1 or blockchain_socket is None): 
	time.sleep(1)
	conn, c_address = socket.accept()
	data = conn.recv(1024)
	#print('received message: ' + data + "\n")
	if data == 'blockchain': 
		blockchain_socket = conn
		break
	else:
		client_sockets.append(conn)

#check if this client is currently on the top of queue. 
#check after: 
# 		1. receiving reply from clients.
#		2. receiving release from clients. 
#		3. dequing
def check_queue_top(lock): 
	lock.acquire()

	if request_queue.empty() == False: 
		top_one = request_queue.get()
		if top_one['reply_count'] == len(clients_list) - 1 and top_one['from'] == sys.argv[3]: 
			#push to blockchain 
			json_body = json.dumps(top_one)
			blockchain_socket.sendall(json_body)

			#broadcast release to all clients.
			top_one['type'] = 'release'
			for c_socket in client_sockets:
				json_body = json.dumps(top_one)
				c_socket.sendall(json_body)
		else: 
			#do something here to resume queue!
			queue_copy = queue.Queue()
			queue_copy.put(top_one)

			while not request_queue.empty(): 
				item = request_queue.get()
				queue_copy.put(item)

			#then put everything back!
			while not queue_copy.empty(): 
				request_queue.put(queue_copy.get())

	lock.release()


def process_input_request(reuqest_body, lock): 
	#1. add it self queue
	lock.acquire()
	request_queue.put(reuqest_body)

	#2. order self queue. 
	#TODO: Sort queue.
	lock.release()

	#3. Broadcast~ 
	for c_socket in client_sockets:
		json_body = json.dumps(reuqest_body)
		c_socket.sendall(json_body)


def process_received_msg(msg, lock, socket):
	print("\n[Received]: " + msg + "\n")
	received = json.loads(msg) 
#message type: 1. request type from all others & add to local queue & sort 2. Release request from all others.
# 1. request 
# 2. reply 
# 3. release
	if received['type'] == 'request':
		lock.acquire()
		#a. insert
		#donno know to json decode to dictionary
		insert = {
			"from": str(received["from"]),
			"to": str(received["to"]),
			"msg": str(received["msg"]),
			"time": int(received["time"]),
			"process_id": int(received["process_id"]),
			"reply_count": int(received["reply_count"]), 
			"type": str(received["type"])
		}
		request_queue.put(insert)
		print('received request.')

		#b. TODO: sort queue.
		lock.release()

		#c. reply!
		received['type'] = 'reply'
		json_body = json.dumps(received)
		socket.sendall(json_body)

	elif received['type'] == 'reply': 
		print("received reply.\n")
		#todo: look up local queue and increase number!
		
		check_queue_top(lock)
	elif received['type'] == 'release':
		print('released release')
		#todo: remove from local queue!
		check_queue_top(lock)



#each client's socket keeps checking message in sub thread.
def socket_keep_receiving(socket, lock):
	while True:
		data = socket.recv(1024)
		if len(data)>0: 
			#if received data, put it in sub thread and process.
			process = multiprocessing.Process(target=process_received_msg, args=(data, lock, socket, ))
			process.daemon = True
			process.start()

#create threads for each connected socket so that it keeps receiving message.
for c_socket in client_sockets:
	process = multiprocessing.Process(target=socket_keep_receiving, args=(c_socket, lock, ))
	#process.daemon = True
	process.start()

print("Please type in command to perform Blockchain transaction or check balance.\n")
print("Ex. To transfer $3 to clinet B, please type \'B 3\' \nEx. To check current balance, please type \'balance\'\n")

while True:
	text = raw_input("Command: ")
	split = text.split()
	if len(split) == 0: 
		continue
	elif len(split) == 2: 
		if to_client_exist(split[0]) == False:
			print("Client does not exist.\n")
			continue;
		reuqest_body = {
			"from": sys.argv[3],
			"to": split[0],
			"msg": split[1],
			"time": time.time(),
			"process_id": sys.argv[2],
			"reply_count": 0, 
			"type": "request" 
		}
		process = multiprocessing.Process(target=process_input_request, args=(reuqest_body, lock, ))
		process.daemon = True
		process.start()
	elif split[0] == 'balance':
		reuqest_body = {
			"from": sys.argv[3],
			"to": "__none__",
			"msg": split[0],
			"time": time.time(),
			"process_id": sys.argv[2],
			"reply_count": 0, 
			"type": "request" 
		}
		process = multiprocessing.Process(target=process_input_request, args=(reuqest_body, lock, ))
		process.daemon = True
		process.start()
	elif split[0] == 'check':
		lock.acquire()
		queue_copy = queue.Queue()

		while not request_queue.empty(): 
			item = request_queue.get()
			print(item)
			queue_copy.put(item)

		#then put everything back!
		while not queue_copy.empty(): 
			request_queue.put(queue_copy.get())
		lock.release()
	else: 
		print("Invalid Input.\n")


















