#!/usr/bin/env python3

import urllib.request
import paramiko
import time
import os

listname="blocked_site"
router_ip="192.168.137.1"

def get_blocked_ip():
	request='http://reestr.rublacklist.net/api/ips'
	resp=urllib.request.urlopen(request)
	iplist=resp.read().decode('utf-8')[2:-2].split(';')
	return iplist

def clearing_router():
	numberlist=[]
	getlist,oldlist,stderr=ssh.exec_command("/ip firewall address-list print")
	address_list=oldlist.readlines()
	for line in address_list:
		line=line.split()
		if len(line) >= 3 and line[1] == listname:
			try:
				numberlist.append(line[0])
			except:
				numberlist=[line[0]]
	if len(numberlist)>0:
		clearing_list(numberlist)
		vaiting_clearing()

def clearing_list(numbers):
	while len(numbers)>=50:
		comm=str("/ip firewall address-list remove numbers=" + str(','.join(numbers[-50:])))
		numbers=numbers[:-50]
		stdin=ssh.exec_command(comm)
		#print(comm)
	comm=str("/ip firewall address-list remove numbers=" + str(','.join(numbers)))
	stdin=ssh.exec_command(comm)
	#print(comm)

def vaiting_clearing():
	count=1; cicles=0
	while count != 0:
		count=0; cicles+=1
		getlist,oldlist,stderr=ssh.exec_command("/ip firewall address-list print where list=blocked_site")
		address_list=oldlist.readlines()
		#print("".join(address_list))
		for line in address_list:
			line=line.split()
			if len(line) >= 3 and line[1] == listname:
				count+=1
		if count > 0:
			time.sleep(2)
		if cicles > 100:
			print("Something went wrong... I`ll start one more copy of cleaner.")
			clearing_router()

def writing_new_list(iplist):
	for ip in iplist:
		comm=str("/ip firewall address-list add address=") + str(ip) + str(" list=") + str(listname)
		stdin=ssh.exec_command(comm)
		#print(comm)

# Connecting to router
#paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)
ssh = paramiko.SSHClient()
ssh.load_system_host_keys()
ssh.load_host_keys(os.path.expanduser('/home/sokogen/.ssh/known_hosts'))
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(router_ip, username='antizapret', password='Telegraph!')

clearing_router()

writing_new_list(get_blocked_ip())

ssh.close()