# Client of a DNS query

import sys
from socket import *

def main():
	while 1:
		host = "localhost" # Remote hostname. It can be changed to anything you desire.
		port = 9889 # Port number.

		try:
			cSock = socket(AF_INET, SOCK_STREAM)
			# allows us to immediately reuse socket's port upon termination:
			# cSock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) 
		except error as msg:
			cSock = None # Handle exception

		try:
			cSock.connect((host, port))
		except error as msg:
			cSock = None # Handle exception

		if cSock is None:
			print("Error: cannot open socket")
			sys.exit(1) # If the socket cannot be opened, quit the program.

		print("Type in a domain name to query, or 'q' to quit:")
		while 1:
			st =input() # Get input from users.
			if st == "":
				continue
			else:
				break
		if st == "q" or  st == "Q":
			cSock.close()
			sys.exit(1) # If input is "q" or "Q", quit the program.
		cSock.send(st.encode()) # Otherwise, send the input to server.
		data = cSock.recv(1024).decode() # Receive from server.#py3 specific
		print("Received:", data) # Print out the result.

main()
