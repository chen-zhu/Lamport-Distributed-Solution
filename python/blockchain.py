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
from helper import list_clients, to_client_exist, randomId, randomSleep


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
		sock.setblocking(0)
		blockchain_connections.append(sock)
		print("[Active Socket]Connected to the client " + c_info['name'] + "\n")
	except socket_error as serr:
		print("[Active Socket]Cannot reach the client " + c_info['name'] + "\n")

print("Successfully connected to all clients\n")
#print(blockchain_connections)
#print("\n")
print(blockchain_transactions)
print("\n")


def balance(client_name): 
	if len(client_name) <= 0:
		return 0
	balance = 0
	for trx in blockchain_transactions:
		if trx['from'] == client_name:
			balance -= int(trx['amount'])
		elif trx['to'] == client_name: 
			balance += int(trx['amount'])
	return balance


#blockchain server only need single thread because only one server can enter cretical section!
#All sockets have non-blocking mode~! 
while True: 
	#keep listen for command.
	for socket in blockchain_connections:
		#print(".")
		#time.sleep(2)
		try:
			data = socket.recv(1024)
			if len(data)>0: 
				print('recieved traffic: ' + data + "\n")
				#1. json decode! 
				request = json.loads(data)
				final_balance = balance(request['from'])

				if request['msg'] == 'balance': 
					#final_balance = balance(request['from'])
					#randomSleep()
					socket.sendall(str(final_balance))
				else: 
					#TODO: check if the client has enough balance to deduct.
					if final_balance < int(request["msg"]): 
						#randomSleep()
						socket.sendall("Transaction Failed. Incorrect Amount.")
					else: 
						before = balance(request['from'])
						insert = {"from":str(request["from"]), "to":str(request["to"]), "amount":str(request["msg"])}
						blockchain_transactions.append(insert)
						print("inserted into blcokchain transaction. Blockchain current TRX records: ")
						print(blockchain_transactions)
						print("\n")
						after = balance(request['from'])
						#randomSleep()
						socket.sendall("Transaction Success. " + "Old Balance: " + str(before) + ". New Balance: " + str(after))
						#insert transaction!
		except socket_error as serr:
			a=1








