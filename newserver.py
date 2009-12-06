
import socket
import time
import sys





def acknow(thissock): #function for testing that the other server/client acknowldged correctly
    try:
        ack= thissock.recv(3) #just read what would be the acknowldged
    except socket.error:
        print "socket error in acknow"
        quit()
    print "ack", ack #temporary
    if ack!="ack":
        print "failed acknowledgement, got:", ack, sys.exc_info()# temporary
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
    print "instancedict",instancedict
    #merge the dicts
    for k in priordict:
        for j in instancedict:
            if instancedict[j]==k:
                instancedict[j]=priordict[k]
    priordict=instancedict
    print "instancedict2",instancedict
    for i in priordict: #start propagating the list of other servers to each other server
#        print "entered asinine for loop" #temporary
        try:
            bytes=priordict[i].send("moveon")
            print "sent",bytes
        except socket.error:
            print "failure in sending moveon",sys.exc_info() #temporary
            quit() #temporary
        acknow(priordict[i])
    print "done initializing primary"
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
#                        print instancedict
                        innerloop=False
                    elif innercom=="moveon": # if we get a moveon directly after a getdict
                        print "got inner moveon"
                        innerloop=False
                        listenloop=False
            elif mastercom=="moveon": #if we get a moveon and we werent just in a get dict
                print "got moveon"
                pr1socket.send("ack") #ack the moveon
                listenloop=False
        print "startup done"
    return priordict

def sendclienttime(cliip, now):
# Send segment starts here
    try:
        clientSocket.send (str( now )) #converts to a string
    except:
        print "send fail", sys.exc_info()
        quit()
    print "sent"
    try:
        clientSocket.recv(10) 
    except:
        print "recv fail", sys.exc_info()
        quit()
# Send segment ends here

def readlocaltime(oldtime): # reads the system time and then compares it to 
    #now=time.strftime('%X') #changed to ease comparisons
    now=time.time()
    if now-oldtime>10: #if time has changed too much
        now=time.time() #try to read again
        if now-oldtime>10: #we have tried and failed
            print "time is wrong, quitting"
            quit() # temporary, will be sending a failure message
        # if it works on the second pass we continue
    print now
    return now

def openclientsocket(cliip):
    clientSocket = socket.socket (socket.AF_INET, socket.SOCK_STREAM )#will need to be conditional to being primary server 
    clientSocket.connect(( cliip,2487)) #will need to take an arg from stdin 
    return clientSocket

def sendtimeall(now, priordict):
    print "entered sendtimeall" #temporary
    for x in priordict:
        try:
            priordict[x].send(str(now))
            print "sent to ",x
        except:
            print sys.exc_info() #temporary
            print "error in send time all" #temporary
            quit() #temporary

def receivetimeall(priordict):
    print "entered receivetimeall" #temporary
    returndict=dict()
    print "priordict",priordict #temporary
    for x in priordict: # PROBLEM EXISTS HERE
        print x 
        try:
#            print priordict[x].recv(100)
            returndict[x]=priordict[x].recv(10)
        except:
            print sys.exc_info() #temporary
            print "error in receivetimeall" #temporary
            quit() #temporary
    return returndict

def endofsegment(priordict): #sends acks to all other servers, reads acks from all other servers
    print "entered end of segment" #temporary
    for x in priordict:
        try:
            priordict[x].send("ack")
            print "sent ack to:",x #temporary
        except:
            print "endofsegment problem",sys.exc_info() #temporary
            quit()
    for y in priordict:
        try:
            print "y",y #temporary
            acknow(priordict[y])
        except:
            print "endofsegment2 problem",sys.exc_info() #temporary
            quit()


def checktime(ourtime, theirtime):#checks times from other servers against this server, returning OK if the times are within 10 seconds and FAIL otherwise
    if abs(ourtime-float(theirtime))>10: #cast theirtime as a float
        return "FAIL"
    else:
        return "OK"

def timeok(now, timedict, priordict): #takes a dictionary of times, and sockets,m and the current time and sends whether the times gotten from each server are within 10 seconds of the current time
    for x in priordict:
        try:
            priordict[x].send(checktime(now,timedict[x]))
        except:
            print "time ok problem",sys.exc_info() #temporary
            quit()

def amiok(priordict): #takes the results of timeok, if more than half are fails return that you are going to die.
    failnumber=0
    print "entered amiok" # temporary
    for x in priordict:
        thisresult='' #temporary !!
        try:
            thisresult=priordict[x].recv(10)
            print "thisresult",thisresult
        except:
            print "amiokrecv problem",sys.exc_info() #temporary
            quit()
        if thisresult=="FAIL":
            failnumber=failnumber+1
    print "failnumber", failnumber #temporary
    print "lendict",len(priordict)
    if failnumber>(len(priordict)/2):
        print "Amiok true" #temporary
        return True
    else:
        return False

def sendmessage(priordict,message): #sends a message to all connected servers
    for x in priordict:
        try:
            priordict[x].send(message)
        except:
            print "failure to send message",sys.exc_info() #temporary
            quit()

def dealwithdeath(priordict,priority, active):
    dellist=[] #create an empty list to put the servers to delete in
    for x in priordict:
        status='' # temporary !!
        try:
            status=priordict[x].recv(10)
            print "status",status
        except:
            print "failure to receive death or life",sys.exc_info #temporary
            quit()
        if status=="dying":
            intermediate=False #by default we assume there is no intermediate
            itwasactive=True #we assume the dying server was active
            for z in range(1,x):#we check to see if any higher priority servers than the current one exist
                if x in priordict:
                    intermediate=False
                #can be made more efficent by short circuit will do if I get time temporary
            for y in range(x+1,priority): #for all of the possible dicts in between the dying one and us
                if y in priordict:#test to see if they are still alive
                    intermediate=True # if so we have an intermediate
            if intermediate==False and itwasactive==True:
                active=True #if the failing server is the one before us and it was active we are active
            dellist.append(x)
    print "dellist",dellist #temporary
    for y in dellist: #go through all the servers marked for deletion
        del priordict[y]#we remove the failing server from our dictionary 
    print "priordict",priordict #temporary
    return (priordict, active) #we return the modified (or not) priordict, and whether we are now active or not 



#arguments block
print len(sys.argv)
print sys.argv[1]
if len(sys.argv) == 4:# and sys.argv[1]==1: #if we are the 1st server we get our priority ie 1, the client IP and the total number of servers
    priority=int(sys.argv[1])
    cliip=sys.argv[2]
    if priority==1:
        numservers=int(sys.argv[3])
    else:
        primserv=sys.argv[3]
else:
    print "usage: priority, clientIP, number of servers, IFF priority is 1"
    print "priority, ClientIP, Primary server IP otherwise"
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

now=time.time() #changed to ease comparisons
#now=time.strftime('%X') #here we prime now to use as oldtime for getting the time
#at this point we enter into the loop
try: # takes exceptions in both broken sockets and ctrl-C
    while True:
# client connect changed to be after possible active server change in dealwithdeath
#end initialization block
#get time is here
        now=readlocaltime(now)
        now=int(now) #Get rid of decimal
        sendtimeall(now, priordict)
        timedict=receivetimeall(priordict)
        print "timedict",timedict # temporary
        time.sleep(1) # temporary !!
        endofsegment(priordict)
# end gettime

#checktime is here
        print "started checktime" #temporary
        timeok(now,timedict,priordict)
#        endofsegment(priordict) #shouldnt be here we have unresolved items in the socket
#end checktime

#consistency check is here
        dying=amiok(priordict)
        endofsegment(priordict)
        time.sleep(1) #temporary !!
        print "priordict", priordict #temporary
        endofsegment(priordict) #temporary
        print "did consistancy check.  I am:", dying #temporary
        if dying:
            sendmessage(priordict,"dying")
        else:
            sendmessage(priordict,"alive")
#        (priordict,active)=dealwithdeath(priordict, priority, active)
        if len(priordict)!=0: #deals with the issues returning an empty dict temporary
            (priordict,active)=dealwithdeath(priordict,priority,active)
        if dying: #We actually die here if things fuck up
            print "dying"
            quit()
        time.sleep(1) #temporary !!
        endofsegment(priordict) #added cause we are at the end of a segment here
# Send segment starts here
        if active: # if we are the primary server
            try: #try to see if connection exists
                print clientSocket #simple way to test existence, Temporary
            except: # if it doesnt we open it
                clientSocket = openclientsocket(cliip)
        if active:    #NEED TO CHANGE ORDER HERE
            sendclienttime(cliip, now)
# End Send segment
        time.sleep(1)
except KeyboardInterrupt:
    print "we were excepted by keyboard" # in future we do something here
    quit()
