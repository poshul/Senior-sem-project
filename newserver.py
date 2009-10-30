import socket
import time
import sys

#arguments block
print len(sys.argv)
print sys.argv[1]
if len(sys.argv) == 4:# and sys.argv[1]==1: #if we are the 1st server we get our priority ie 1, the client IP and the total number of servers
    priority=sys.argv[1]
    cliip=sys.argv[2]
    numservers=sys.argv[3]
elif len(sys.argv) ==3: # if not the 1st server we only get our priority and the address of the 1st server
    priority=sys.argv[1]
    primserv=sys.argv[2]
else:
    print "usage"
    quit()


#if priority==1: #Conditionality to be implemented later
clientSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM )#will need to be conditional to being primary server
clientSocket.connect(( cliip,2487)) #will need to take an arg from stdin
while True:
    time.sleep(1)
    now=time.strftime('%X')
    print now
# Send segment starts here
    try:
        clientSocket.send ( now )
    except:
        print "send fail"
        quit()
    print "sent"
    try:
        clientSocket.recv(100)
    except:
        print "recv fail"
        quit()
# Send segment ends here
