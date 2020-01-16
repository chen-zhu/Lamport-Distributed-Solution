import time
import os
import multiprocessing as mp
import logging
import socket
import xml.etree.ElementTree as ET
import sys
import json
from helper import list_clients
from socket import error as socket_error

print("*****************************************************\nBlockchain Main Server\n'*****************************************************\n\n")

clients_list = list_clients()
blockchain_connections = []
blockchain_transactions = [
	{"from":"__ini__", "to":"A", "amount":10}, 
	{"from":"__ini__", "to":"B", "amount":10}, 
	{"from":"__ini__", "to":"C", "amount":10}
]

for c_info in clients_list: 
	time.sleep(1)
	print("[Active Socket]Connecting to the client " + c_info['name'] + " > " + c_info['ip'] + ":" + c_info['port'] + ".....")
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		sock.connect((c_info['ip'], int(c_info['port'])))
		sock.sendall('blockchain')
		blockchain_connections.append(sock)
		print("[Active Socket]Connected to the client " + c_info['name'] + "\n")
	except socket_error as serr:
		print("[Active Socket]Cannot reach the client " + c_info['name'] + "\n")

print("Successfully connected to all clients\n")
#print(blockchain_connections)
#print("\n")
print(blockchain_transactions)


def balance(client_name): 
	if len(client_name) <= 0:
		return 0
	balance = 0
	for trx in blockchain_transactions:
		if trx['from'] == client_name:
			balance -= trx['amount']
		elif trx['to'] == client_name: 
			balance += trx['amount']
	return balance


#blockchain server only need single thread because only one server can enter cretical section!
while True: 
	#keep listen for command.
	for socket in blockchain_connections:
		data = socket.recv(1024)
		if len(data)>0: 
			#1. json decode! 
			request = json.loads(data)
			if request['msg'] == 'balance': 
				final_balance = balance(request['from'])
				socket.sendall(final_balance)
			else: 
				insert = {"from":request["from"], "to":request["to"], "amount":request["msg"]}
				blockchain_transactions.append(insert)
				print("inserted into blcokchain transaction.\n")
				print(blockchain_transactions)
				#insert transaction!










