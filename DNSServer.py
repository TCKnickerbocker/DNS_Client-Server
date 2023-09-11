# Server of DNS query

import sys, threading, os, re, time
from socket import *
import platform


cache = {} # format = hostname : [ipList]
newKeys = [] # domain names added to cache but not dnsFile
cacheLock = threading.Lock()

# Check if DSN_FILE exists (creates it if it does not)
if os.path.isfile("./DNS_mapping.txt"):
	# Read DNS FILE
	dnsFile = open("DNS_mapping.txt", "r+")
	text = dnsFile.read()
	text = text.replace('\n',',') 
	entryList = text.split(',')
	l = len(entryList)
	# Initialize data structure
	for i in range(0, l, 2):
		if entryList[i] != '' and i+1 != l: # if entry pair is not blank & in range
			if entryList[i] not in cache:
				cache[entryList[i]] = [entryList[i+1]]
			else: # add ip to existing list for this domain name
				if entryList[i+1] not in cache[entryList[i]]: # ensures we don't add duplicate IPs
					cache[entryList[i]].append(entryList[i+1])
else:
	dnsFile = open("DNS_mapping.txt", "a")


def main():

	host = "localhost" # Hostname. It can be changed to anything you desire.
	port = 9889 # Port number.

	#create a socket object, SOCK_STREAM for TCP
	#bind socket to the current address on port
	try:
		sSock = socket(AF_INET, SOCK_STREAM)
		# allows us to immediately reuse socket's port upon termination:
		sSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) 

	except error as msg:
		sSock = None
	try:
		sSock.bind((host, port))
	except error as msg:
		sSock = None
	
	#Listen on the given socket maximum number of connections queued is 20
	if sSock is None:
		print("Error: server failed to start socket")
		sys.exit(1) # If the socket cannot be opened, quit the program.

	sSock.listen(20)


	monitor = threading.Thread(target=monitorQuit, args=[])
	monitor.start()

	save = threading.Thread(target=saveFile, args=[])
	save.start()

	print("Server is listening... \nType \"exit\" to close server & write to files")

	while 1:
		#blocked until a remote machine connects to the local port
		connectionSock, addr = sSock.accept()
		server = threading.Thread(target=dnsQuery, args=[connectionSock, addr[0]])
		server.start()


def dnsQuery(connectionSock, srcAddress):

	found = False
	dn = connectionSock.recv(1024).decode()

	# If client tried to exit, close connection socket
	if dn in ["q", "Q", ""]: 
		connectionSock.close()
		return

	# If domain name is in cache, get list of its IPs
	if dn in cache:
		ipList = cache[dn]
		found=True

	if found: # select IP with lowest latency
		res = dnsSelection(ipList)
		method = "CACHE"
	else:
		# If not in data structure, query the local machine DNS lookup to get the IP resolution
		method = "API"
		# Get response, add to cache, newKeys. Lock for safety
		try:
			res = gethostbyname(dn)
		except:
			res = "Host not found"

		cacheLock.acquire()
		newKeys.append(dn) # new key to add to cache
		cache[dn] = [res] # update data structure
		cacheLock.release()


	# Write response to csv
	csv = open("dns-server-log.csv", "a") 
	csv.write(dn + "," + res + "," + method + "\n") # added a newline for nicer formatting
	data = dn+":"+res+":"+method

	# Print out response & domain name, send back to client:
	print(f'Response: {res} for domain name: {dn}')
	connectionSock.send(data.encode())

	# Close the server socket & csv file.
	csv.close()
	connectionSock.close()
  

### Selects ip with lowest response time from list
def dnsSelection(ipList):

	# Base case:
	if len(ipList) == 1:
		return ipList[0]

	ind = 0
	bestPing = float("inf")
	# Time every element in list
	for i in range(0, len(ipList)):

		# Execute ping command, extract time from response
		if platform.system().lower()=='windows':
			spec = '-n'
		else:
			spec = '-c'
		response = os.popen(f"ping {spec} 1 {ipList[i]} ").read()
		timeStr = re.findall("time=[0-9]\d+", response)

		
		if(len(timeStr) > 0):  # Ensure ping returned a time
			curPing = float(timeStr[0][5:])  # get time
			if(curPing < bestPing):  # compare to current best time
				bestPing = curPing
				ind = i

	return ipList[ind] # return lowest latency IP



def saveFile():
	while 1:
        # Lock, write to dnsFile, clear newKeys, release lock & sleep
		cacheLock.acquire()
		for key in newKeys:
			dnsFile.write(key + "," + cache[key][0] + "\n") # write first element in cache with this key
		print("Saved cache")
		newKeys.clear() 
		cacheLock.release()
		time.sleep(15)

def monitorQuit():
	while 1:
		sentence = input()
		if sentence == "exit":
			cacheLock.acquire()
			for key in newKeys:
				dnsFile.write(key + "," + cache[key][0] + "\n") # write first element in cache with this key
			newKeys.clear()
			print("Saved cache")
			cacheLock.release()

			print("Exiting server")
			dnsFile.close()
			os.kill(os.getpid(),9)

main()
