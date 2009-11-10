import socket
import time
import sys





def acknow(thissock): #function for testing that the other server/client acknowldged correctly
    ack= thissock.recv(100)
    if ack!="ack":
        quit()
    return

def initializeprimary(priority, numservers):
    #initialization block
    print priority 
    priordict=dict()
    instancedict=dict()
    minit1socket= socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
    minit1socket.bind( ( '', 2400))
    minit1socket.listen(10) #will always work up to 10 servers, should work after that unless we start hundreds by
    print "entered pr1"
    numconnected=1 #We start with one server connected: us 
    nummapped=1
    tempdict=dict() #not sure if we need this but I will keep it in for now
    while numconnected<numservers: #while we have more to connect 
        channel, details =minit1socket.accept() #accept a connection
        numconnected=numconnected + 1 # increase the number of connected
        print "connection from:", details
        tempdict[numconnected]=channel #map the connection to its connection order
        priordict[details[0]]=channel #map the connection to the priority
        print priordict #temporary fix
        print tempdict #temporary fix    
    for x in priordict: # get the priority from each connected server
        thispriority=int(priordict[x].recv(100)) #receive the priority from the server at x converted to an int
        print thispriority
        instancedict[thispriority]=x #extract the first item from the tuple x, ie the address
        priordict[x].send ("ack")
    print instancedict

    for y in instancedict: #start propagating the list of other servers to each other server
        priordict[instancedict[y]].send("getdict")
        print "sent getdict to",y
        acknow(priordict[instancedict[y]])
        z=y+1 #since we are not including ourself we start here
        while z<=(len(instancedict)+1): # tell the other servers to listen for new connections
            priordict[instancedict[z]].send("listenz")
            print "sent listenz to",z
            acknow(priordict[instancedict[z]])
            z=z+1
        w=y+1
        while w<=(len(instancedict)+1): #send the info to the server
            priordict[instancedict[y]].send(str(w)) #send the priority w to server with priority y
            print "sent priority",w,"to",y
            acknow(priordict[instancedict[y]])
            priordict[instancedict[y]].send(str(instancedict[w])) #send the ip
            print "sent IP",instancedict[w],"to",y
            acknow(priordict[instancedict[y]])
            w=w+1
        priordict[instancedict[y]].send("dictdone") #send that we have finished the dict to the server with priority y
    #tell everyone to move on
    for p in instancedict: #start propagating the list of other servers to each other server
        priordict[instancedict[p]].send("moveon")
    return priordict

def initializenotprimary(priority, primserv):
    #initialization block
    print priority
    priordict=dict()
    instancedict=dict()
    minit1socket= socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
    minit1socket.bind( ( '', 2400))
    minit1socket.listen(10) #will always work up to 10 servers, should work after that unless we start hundreds by
    print "entered prinot 1"
    pr1socket= socket.socket (socket.AF_INET, socket.SOCK_STREAM ) #open socket to connect to primary server
    pr1socket.connect((primserv,2400)) #connect to primary server
    priordict[1]=pr1socket
    pr1socket.send (str(priority))#need to add try here
    ack= pr1socket.recv(100) # wait for acknowledgement
    if ack!="ack":
        print "primary server failed to acknowledge"
        quit()
    else:
        print "success"
        # listen for connections from primary server
        listenloop=True
        while listenloop:
            mastercom=pr1socket.recv(100)
            if mastercom=="listenz": #start listening for a connection
                pr1socket.send("ack") #ack that we have received
                print "listening"
                channel, details= minit1socket.accept()
                priordict[int(len(priordict)+1)]=channel #we connect in priority order therefore the next connection is the next number of priority
                print "got connection from", details
            elif mastercom=="getdict":
                print "got a getdict"
                pr1socket.send("ack") #ack the getdict
                innerloop=True
                while innerloop:
                    innercom=pr1socket.recv(100)
                    print "innercom",innercom
#                    if innercom!='':
                    if innercom!="moveon" and innercom!="dictdone":
                        first=innercom #we get the priority
                        pr1socket.send("ack") #ack that we have received
                        temp=pr1socket.recv(100)
                        print "priority",first
                        print "IP",temp
                        instancedict[int(first)]=temp #receive the IP and pair it with the priority
                        pr1socket.send("ack") #ack that we have received
                        priordict[int(first)]= socket.socket (socket.AF_INET, socket.SOCK_STREAM )#will need to be conditional to being primary server
                        priordict[int(first)].connect((instancedict[int(first)],2400)) #connect to server
                    elif innercom=="dictdone":
                        print "internal dictdone"
                        print priordict
                        print instancedict
                        innerloop=False
                    elif innercom=="moveon": # if we get a moveon directly after a getdict
                        innerloop=False
                        listenloop=False
            elif mastercom=="moveon": #if we get a moveon and we werent just in a get dict
                print "got moveon"
                listenloop=False
        print "startup done"
    return priordict

def sendclienttime(cliip, now):
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

def readlocaltime(oldtime): # reads the system time and then compares it to 
    now=time.strftime('%X')
    print now
    return now



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

if priority==1: #do if we are the primary server
    priordict=initializeprimary(priority, numservers)
else: # if not the primary server
    priordict=initializenotprimary(priority,primserv)
print priordict #temporary

if priority==1:#from now on in the program we only care about our priority on a failover otherwise we care whether we are active or not.
    active=True
else:
    active=False

now=time.strftime('%X') #here we prime now to use as oldtime for getting the time
#at this point we enter into the loop

if active: # if we are the primary server connect
    clientSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM )#will need to be conditional to being primary server 
    clientSocket.connect(( cliip,2487)) #will need to take an arg from stdin 
#end initialization block

#get time is here
    while True:
        now=readlocaltime(now)
# note that in function we have removed the wait
        time.sleep(1)
        print now
# end gettime

# Send segment starts here
        sendclienttime(cliip, now)
# End Send segment
