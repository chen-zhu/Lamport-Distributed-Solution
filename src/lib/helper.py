import time
import os
import multiprocessing as mp
import logging
import socket
import xml.etree.ElementTree as ET

def list_clients()
	tree = ET.parse('config/connections.xml')
	root = tree.getroot()
	clients = []
	for neighbor in root.iter('client'):
		clients.append({'name':neighbor.find('name').text, 'process_id':neighbor.find('process_id').text, 'ip':neighbor.find('ip').text, 'port':neighbor.find('port').text})
	print clients 
	return clients







