#!/usr/bin/python
import time
import os
import multiprocessing as mp
import logging
import socket
import xml.etree.ElementTree as ET

tree = ET.parse('config/connections.xml')
root = tree.getroot()

for neighbor in root.iter('client'):
	command = "osascript -e 'tell application \"Terminal\" to do script \"cd ~/Documents/CMPSC_271/Lamport-Distributed-Solution/python/ && python ./client.py " + neighbor.find('port').text + " " + neighbor.find('process_id').text + " " + neighbor.find('name').text + " " + neighbor.find('ip').text + " " + " \"' "
	os.system(command)
	time.sleep(2)

time.sleep(3)
command = "osascript -e 'tell application \"Terminal\" to do script \"cd ~/Documents/CMPSC_271/Lamport-Distributed-Solution/python/ && python ./blockchain.py " + " \"' "
os.system(command)