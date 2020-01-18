import time
import os
import multiprocessing as mp
import logging
import socket
import xml.etree.ElementTree as ET
import random
import string
from random import randint
from time import sleep

def list_clients(): 
	tree = ET.parse('config/connections.xml')
	root = tree.getroot()
	clients = []
	for neighbor in root.iter('client'):
		clients.append({'name':neighbor.find('name').text, 'process_id':neighbor.find('process_id').text, 'ip':neighbor.find('ip').text, 'port':neighbor.find('port').text})
	#print clients 
	return clients

def to_client_exist(to_name): 
	clients = list_clients()
	for c in clients:
		if c['name'] == to_name: 
			return True
	return False

def randomId(stringLength=5):
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(stringLength))

def randomSleep():
	#print('Network Delay Mocking: sleep. ')
	sleep(randint(0,3))
	#print('Network Delay Mocking: sleep ends. ')