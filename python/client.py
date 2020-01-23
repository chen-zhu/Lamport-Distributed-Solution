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
import random
import string
import signal
import copy

import threading

from helper import list_clients, to_client_exist, randomId, randomSleep
from socket import error as socket_error

#usage: ini_client.php (port_num) (process_id) (client_names) (ip)
if len(sys.argv) != 5: 
	print('exit')
	sys.exit(1)

print("*****************************************************\n Client Name: " + sys.argv[3] + "\n*****************************************************\n\n")

clients_list = list_clients()
client_sockets = []

lock = threading.Lock()
request_queue = queue.Queue()
#request_list = []

clock = 0

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


def update_clock(received_time):
	global clock 
	clock = max(clock, received_time) + 1

#spevial algorithm that helps us to sort list!
def sort_by_time_process_id(val):
	return  int(val['time']) * 10 + int(val['process_id'])

def print_queue(queue_to_be_sorted):
	cpy = copy.deepcopy(queue_to_be_sorted)
	while not cpy.empty(): 
		item = cpy.get()
		print(item)
	
#unfortunately, regarding the multiprocessing, we can only utilize multiprocessing.queue as shared memory obj. 
#therefore, manually multiprocessing.queue sorting is required.
def sort_queue(request_queue):
	tmp_list = []
	while not request_queue.empty(): 
			item = request_queue.get()
			tmp_list.append(item)
	tmp_list.sort(key = sort_by_time_process_id, reverse = True)
	#then put sorted back to queue!
	while len(tmp_list):
		request_queue.put(tmp_list.pop())


#check if this client is currently on the top of queue. 
#check after: 
# 		1. receiving reply from clients.
#		2. receiving release from clients. 
#		3. dequeue
def check_queue_top(lock): 
	global request_queue
	global clock
	lock.acquire()

	if not request_queue.empty(): 
		sort_queue(request_queue)
		#time.sleep(1)
		top_one = request_queue.get()
		#print(top_one)

		if top_one['reply_count'] >= len(clients_list) - 1 and top_one['from'] == sys.argv[3]: 
			#top_one['time'] = clock

			#push to blockchain 
			json_body = json.dumps(top_one)
			#print(time.strftime("%H:%M:%S", time.localtime()) + " -> Client " + sys.argv[3] + " enters critical section. ")
			#print('sending to blcok chain: ' + json_body)
			#randomSleep()
			blockchain_socket.sendall(json_body)

			#broadcast release to all clients.
			top_one['type'] = 'release'
			for c_socket in client_sockets:
				update_clock(clock)
				print('>>>Sent mgs type: [release] for verify_id: ' + str(top_one["verify"]) + ". Msg clock value: " + str(clock))
				top_one['time'] = clock
				json_body = json.dumps(top_one)
				randomSleep()
				c_socket.sendall(json_body)
		else: 
			request_queue.put(top_one) 
			sort_queue(request_queue)

	lock.release()


def process_input_request(reuqest_body, lock): 
	global request_queue
	global clock
	#1. add it self queue
	lock.acquire()
	#print("Put into queue with clock: " + str(clock))
	request_queue.put(copy.deepcopy(reuqest_body)) #hummm not sure how python pass by reference work.

	#2. order self queue. 
	sort_queue(request_queue)
	lock.release()

	#3. Broadcast~ 
	for c_socket in client_sockets:
		lock.acquire()
		update_clock(clock)
		reuqest_body['time'] = clock
		print('>>>Sent mgs type: [request] for verify_id: ' + str(reuqest_body["verify"]) + '. Msg clock value: ' + str(reuqest_body["time"]))
		lock.release()
		#print("send clock " + str(clock))
		#DO NOT PUT SLEEP HERE! IT WOULD SCREW UP TIME! 
		json_body = json.dumps(reuqest_body)
		c_socket.sendall(json_body)


def process_received_msg(msg, lock, socket):
	global request_queue
	global clock
	#print("\n[Received]: " + msg + "\n")
	try:
		received = json.loads(msg) 
	except ValueError:
		print("Json decode failed. " + msg)
	#update local clock!
	lock.acquire()
	update_clock(int(received["time"]))
	print('<<<Received msg type: [' + received["type"] + "] with verify_id: " +  str(received["verify"]) + ". Received Time: " + str(received["time"]) + ". Adj Local Time To " + str(clock))
	lock.release()

	#print("[Received msg with type " + str(received["type"]) + " " + str(received["from"]) + " " + str(received["to"]) + "]")
	#message type: 1. request type from all others & add to local queue & sort 2. Release request from all others.
	# 1. request 
	# 2. reply 
	# 3. release
	if received['type'] == 'request':
		lock.acquire()
		#print('Received request with from ' +  str(received["from"]))
		#a. insert
		#donno know to json decode to dictionary
		insert = {
			"from": str(received["from"]),
			"to": str(received["to"]),
			"msg": str(received["msg"]),
			"time": int(received["time"]),
			"process_id": int(received["process_id"]),
			"reply_count": int(received["reply_count"]), 
			"type": str(received["type"]), 
			"verify": str(received["verify"])
		}
		request_queue.put(insert)
		#print('received request. set local time to ' + str(clock) + ' according to ' + str(received["time"]))

		#b. sort queue.
		sort_queue(request_queue)
		print("Sorted Queue: ")
		queue_copy = queue.Queue()

		while not request_queue.empty(): 
			item = request_queue.get()
			print(item)
			queue_copy.put(item)

		if queue_copy.empty():
			print("[Debug]: No items on the local queue!")

		#then put everything back!
		while not queue_copy.empty(): 
			request_queue.put(queue_copy.get())

		#c. reply!
		update_clock(clock)
		#print('Before sending, update clock to ' + str(clock))
		print('>>>Sent mgs type: [reply] to ' + received["from"] + ' for verify_id: ' + str(received["verify"]) + ". Msg Clock Value: " + str(clock))
		received['type'] = 'reply'
		received['turnback_agent'] = sys.argv[3]
		received['time'] = clock #update time to local clock~~
		json_body = json.dumps(received)
		randomSleep()
		socket.sendall(json_body)
		lock.release()
		check_queue_top(lock)
	elif received['type'] == 'reply': 
		lock.acquire()
		queue_copy = queue.Queue()
		#print("Enter reply check: " + str(received['verify']) + " turnback agent: " + str(received["turnback_agent"]) )
		while not request_queue.empty(): 
			item = request_queue.get()
			#check of it is the matching event/request
			if item['verify'] == str(received["verify"]): 
				item["reply_count"] = item["reply_count"] + 1
				#print("received reply. increment!" + str(item["reply_count"]) + " - " + item['verify'] + " turnback agent: " + str(received["turnback_agent"]) )
			queue_copy.put(item)

		#then put everything back!
		while not queue_copy.empty(): 
			request_queue.put(queue_copy.get())

		sort_queue(request_queue)
		lock.release()
		time.sleep(1)
		check_queue_top(lock)
	elif received['type'] == 'release':
		#print('Received release with from ' +  str(received["from"]))
		lock.acquire()
		sort_queue(request_queue)
		dequeue = request_queue.get()
		#print("Deleted record: " + json.dumps(dequeue))
		lock.release()
		check_queue_top(lock)


#each client's socket keeps checking message in sub thread.
def socket_keep_receiving(socket, lock, index):
	global request_queue
	while True:
		#time.sleep(5)
		lock.acquire()
		sort_queue(request_queue)
		lock.release()
		#print("waiting for socket receive..." + str(index))
		data = socket.recv(1024)
		if len(data)>0: 
			randomSleep()
			#print("received: " + data)
			#thread & socket issue. 
			new_json = data.replace("}{", "}-----{") 
			split_list = new_json.split("-----")
			for sl in split_list:
				process_received_msg(sl, lock, socket)		

#create threads for each connected socket so that it keeps receiving message.
for c_socket in client_sockets:
	process = threading.Thread(target=socket_keep_receiving, args=(c_socket, lock, client_sockets.index(c_socket)))
	#process.daemon = True
	process.start()

def blockchain_response(socket, lock):
	while True:
		data = socket.recv(1024)
		if len(data)>0: 
			print("*** Blockchain Response *** " + data)

process = threading.Thread(target=blockchain_response, args=(blockchain_socket, lock, ))
process.start()

print("Please type in command to perform Blockchain transaction or check balance.\n")
print("Ex. To transfer $3 to clinet B, please type \'B 3\' \nEx. To check current balance, please type \'balance\'\n")

while True:
	text = raw_input("")
	split = text.split()
	if len(split) == 0: 
		continue
	elif len(split) == 2: 
		if to_client_exist(split[0]) == False:
			print("Client does not exist.\n")
			continue
		elif split[0] == sys.argv[3]:
			print("Cannot transfer money to self!")
			continue
		if not split[1].isdigit() or int(split[1]) < 0 :
			print("Invalid Amount. Transaction amount must be a positive integer.")
			continue
		lock.acquire()
		update_clock(clock)
		reuqest_body = {
			"from": sys.argv[3],
			"to": split[0],
			"msg": split[1],
			"time": clock,
			"process_id": sys.argv[2],
			"reply_count": 0, 
			"type": "request", 
			"verify": randomId()
		}
		lock.release()
		process = threading.Thread(target=process_input_request, args=(reuqest_body, lock, ))
		#process.daemon = True
		process.start()
	elif split[0] == 'balance':
		lock.acquire()
		update_clock(clock)
		reuqest_body = {
			"from": sys.argv[3],
			"to": "__none__",
			"msg": split[0],
			"time": clock,
			"process_id": sys.argv[2],
			"reply_count": 0, 
			"type": "request", 
			"verify": randomId()
		}
		lock.release()
		process = threading.Thread(target=process_input_request, args=(reuqest_body, lock, ))
		#process.daemon = True
		process.start()
	elif split[0] == 'check':
		lock.acquire()
		print('Local Clock: ' + str(clock))

		queue_copy = queue.Queue()

		while not request_queue.empty(): 
			item = request_queue.get()
			print(item)
			queue_copy.put(item)

		if queue_copy.empty():
			print("[Debug]: No items on the local queue!")

		#then put everything back!
		while not queue_copy.empty(): 
			request_queue.put(queue_copy.get())
		lock.release()
	else: 
		print("Invalid Input.\n")


















