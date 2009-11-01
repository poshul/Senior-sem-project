import socket
import time
import sys

#arguments block
print len(sys.argv)
print sys.argv[1]
if len(sys.argv) == 4:# and sys.argv[1]==1: #if we are the 1st server we get our priority ie 1, the client IP and the total number of servers
    priority=int(sys.argv[1])
    cliip=sys.argv[2]
    numservers=int(sys.argv[3])
elif len(sys.argv) ==3: # if not the 1st server we only get our priority and the address of the 1st server
    priority=int(sys.argv[1])
    primserv=sys.argv[2]
else:
    print "usage"
    quit()
#end arguments block

#initialization block
print priority
priordict=dict()
instancedict=dict()
if priority==1: #do if we are the primary server
    print "entered pr1"
    numconnected=1 #We start with one server connected: us 
    nummapped=1
    tempdict=dict() #not sure if we need this but I will keep it in for now
    instancedict[1]=socket.gethostbyname(socket.getfqdn())#instancedict is primed with our IP ONLY WORKS IF THE MACHINE KNOWS ITS FQDN NEED TO FIX
    minit1socket= socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
    minit1socket.bind( ( '', 2400))
    minit1socket.listen(numservers)
    while numconnected<numservers: #while we have more to connect 
        channel, details =minit1socket.accept() #accept a connection
        numconnected=numconnected + 1 # increase the number of connected
        print "connection from:", details
        tempdict[numconnected]=channel #map the connection to its connection order
        priordict[details]=channel #map the connection to the priority
        print priordict #temporary fix
        print tempdict #temporary fix
    
    for x in priordict:
        thispriority=int(priordict[x].recv(100)) #receive the priority from the server at x converted to an int
        print thispriority
        instancedict[thispriority]=x[0] #extract the first item from the tuple x, ie the address
        priordict[x].send ("ack")
    print instancedict
        

# for non primary server do this:
else:
    print "entered prinot 1"
    pr1socket= socket.socket (socket.AF_INET, socket.SOCK_STREAM ) #open socket to connect to primary server
    pr1socket.connect((primserv,2400)) #connect to primary server
    pr1socket.send (str(priority))#need to add try here
    ack= pr1socket.recv(100) # wait for acknowledgement
    if ack!="ack":
        print "primary server failed to acknowledge"
        quit()
    else:
        print "success"
        quit() #temporary




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
