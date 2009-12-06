
import socket
import time
import sys





def acknow(thissock): #function for testing that the other server/client acknowldged correctly
    try:
        ack= thissock.recv(3) #just read what would be the acknowldged
    except socket.error:
        print "socket error in acknow", sys.exc_info()
        return "DIED"
#        quit()
    print "ack", ack #temporary
    if ack!="ack":# we now have a special case for if we didnt get anything
        print "failed acknowledgement, got:", ack, sys.exc_info()# temporary
        if ack=="":
            print "we got nothing"
            return "DIED"
        else:
            quit()
#        quit()
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
    mialist=[]
    print "entered sendtimeall" #temporary
    for x in priordict:
        try:
            priordict[x].send(str(now))
            print "sent to ",x
        except socket.error:
            print "we have a server mia adding to list"
            mialist.append(x)
        except:
            print sys.exc_info() #temporary
            print "error in send time all" #temporary
            quit() #temporary
    return mialist

def receivetimeall(priordict):
    mialist=[]
    print "entered receivetimeall" #temporary
    returndict=dict()
    print "priordict",priordict #temporary
    for x in priordict: # PROBLEM EXISTS HERE
        print x 
        try:
#            print priordict[x].recv(100)
            returndict[x]=priordict[x].recv(10)
        except socket.error:
            print "we have a server missing in receivetimeall adding to list"
            mialist.append(x)
        except:
            print sys.exc_info() #temporary
            print "error in receivetimeall" #temporary
            quit() #temporary
    return (returndict, mialist)

def endofsegment(priordict): #sends acks to all other servers, reads acks from all other servers
    mialist=[]
    print "entered end of segment" #temporary
    for x in priordict:
        try:
            priordict[x].send("ack")
            print "sent ack to:",x #temporary
        except socket.error:
            print "error sending in end of segment marking server as bad"
            mialist.append(x)
        except:
            print "endofsegment problem",sys.exc_info() #temporary
            quit()
    for y in priordict:
        try:
            print "y",y #temporary
            amok=acknow(priordict[y])
            if amok=="DIED":
                print "I think it died adding to list of mia"
                mialist.append(y)
        except:
            print "endofsegment2 problem",sys.exc_info() #temporary
            quit()
    return mialist
            

def checktime(ourtime, theirtime):#checks times from other servers against this server, returning OK if the times are within 10 seconds and FAIL otherwise
    if theirtime=='' or abs(ourtime-float(theirtime))>10: #cast theirtime as a float and say fail if theirtime is blank
        return "FAIL"
    else:
        return "OK"

def timeok(now, timedict, priordict): #takes a dictionary of times, and sockets,m and the current time and sends whether the times gotten from each server are within 10 seconds of the current time
    mialist=[]
    for x in priordict:
        try:
            priordict[x].send(checktime(now,timedict[x]))
        except socket.error:
            print "time ok socket error, adding to list"
            mialist.append(x)
        except:
            print "time ok problem",sys.exc_info() #temporary
            quit()
    return mialist

def amiok(priordict): #takes the results of timeok, if more than half are fails return that you are going to die.
    failnumber=0
    mialist=[]
    print "entered amiok" # temporary
    for x in priordict:
        thisresult='' #temporary !!
        try:
            thisresult=priordict[x].recv(10)
            print "thisresult",thisresult
        except socket.error:
            print "amiok socket problem adding to list"
            mialist.append(x)
        except:
            print "amiokrecv problem",sys.exc_info() #temporary
            quit()
        if thisresult=="FAIL":
            failnumber=failnumber+1
    print "failnumber", failnumber #temporary
    print "lendict",len(priordict)
    if failnumber>(len(priordict)/2):
        print "Amiok true" #temporary
        return (True,mialist)
    else:
        return (False,mialist)

def sendmessage(priordict,message): #sends a message to all connected servers
    mialist=[]
    for x in priordict:
        try:
            priordict[x].send(message)
        except socket.error:
            print "sendmessage socket error"
            mialist.append(x)
        except:
            print "failure to send message",message, sys.exc_info() #temporary
            quit()
    return mialist

def dealwithdeath(priordict,priority, active):
    dellist=[] #create an empty list to put the servers to delete in
    mialist=[]
    for x in priordict:
        status='' # temporary !!
        try:
            status=priordict[x].recv(10)
            print "status",status
        except socket.error:
            print "socket error in dealwithdeath"
            mialist.append(x)
        except:
            print "failure to receive death or life",sys.exc_info #temporary
            quit()
        if status=="dying": #need to fix where the try except is in next pass
            if x<priority: #there is no way that we would change active state if we have a higher priority that the failing system
                intermediate=False #by default we assume there is no intermediate
                itwasactive=True #we assume the dying server was active
                for z in range(1,x):#we check to see if any higher priority servers than the current one exist
                    if x in priordict:
                        itwasactive=False
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
    return (priordict, active,mialist) #we return the modified (or not) priordict, and whether we are now active or not 

# currently only definately deals with one failing server in a segment 
def miaresolve(priordict, missinglist,priority,active):
    dellist=[]
    for z in missinglist:
        numinagreement=0 # we reset this at the top of each entry
        numitsdead=0 #reset this too
        # start discover
        for x in priordict:
            try:
                priordict[x].send(str(z))
            except socket.error:
                print "we ignore send errors here" #since we are already aware of failure we ignore errors here
            except:
                print "something wrong in MIA resolve send", sys.exc_info()
                quit()
        for y in priordict:
            try:
                ourrecv=priordict[y].recv(8)
            except socket.error:
                print "not much to see here"
            except:
                "something wrong in miaresolve", sys.exc_info()
                quit()
            print "ourrecv",ourrecv #temporary
            print "z",z
            if ourrecv!='' and int(ourrecv)==z: # if the number to deactivate that we receive agrees with ours, modified to short circuit if we have received nothing
                numinagreement=numinagreement+1
        # end discover
        # start agree
        print "numinagreement", numinagreement
        if numinagreement>=len(priordict)-len(missinglist): # if we received agreement for all servers whose integrity is not in question
            for w in priordict:
                try:
                    priordict[w].send("itsdead")
                except socket.error:
                    print "socket problem in agree segment, big suprise"
                except:
                    print "error in sending itsdead", sys.exc_info()
                    quit()
            for v in priordict:
                print "entering receiving itsdeads"
                try:
                    thisdead=priordict[v].recv(10)
                    print "thisdead", thisdead
                except socket.error:
                    print "socket error recv in agree segment, not a problem"
                except:
                    print "other error in recv of agree segment", sys.exc_info()
                    quit()
                print "thisdead", thisdead
                if thisdead=="itsdead":
                    numitsdead=numitsdead+1
                    print "itsdead+1"
        else:
            for w in priordict:
                try:
                    priordict[w].send("notdead")
                except socket.error:
                    print "socket error sending not dead"
                except:
                    print "other error in sending not dead", sys.exc_info()
                    quit()
            for v in priordict:
                try:
                    priordict[v].recv(10)
                except socket.error:
                    print "socket error receiving while not dead"
                except:
                    print "other error receiving in not dead",sys.exc_info()
                    quit()
        #end agree
        print "numitsdead",numitsdead
        if numitsdead>=len(priordict)-len(missinglist):
            print "we will delete server with priority ",z, " now"
            if z<priority:
                intermediate=False #by default we assume there is no intermediate
                itwasactive=True #we assume the dying server was active
                for t in range(1,z):
                    if t in priordict:
                        itwasactive=False
                for s in range(z+1,priority):
                    if s in priordict:
                        intermediate=True
                if intermediate==False and itwasactive==True:
                    active=True
            dellist.append(z)
            #to be implemented
    for u in dellist:
        del priordict[u]
    return (priordict,active)
    

# from: http://www.testingreflections.com/node/view/5241
# removes duplicate items from a list
def remove_dups(seq):
    x = {}
    for y in seq:
        x[y] = 1
    u = x.keys()
    return u 


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

# we set the timeout of each socket here
for x in priordict:
    priordict[x].settimeout(5)
# end setting the timeouts

#test that all of the timeouts are correct temporary
for y in priordict:
    print "timeout is",priordict[y].gettimeout()

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
        masterMIAlist=[] #initialize the list as empty at the top of every loop
        tempMIAlist=[]
        now=readlocaltime(now)
        now=int(now) #Get rid of decimal
        masterMIAlist.extend(sendtimeall(now, priordict))
        (timedict,tempMIAlist)=receivetimeall(priordict)
        masterMIAlist.extend(tempMIAlist)
        print "timedict",timedict # temporary
        time.sleep(1) # temporary !!
        masterMIAlist.extend(endofsegment(priordict))
# end gettime

#checktime is here
        print "started checktime" #temporary
        masterMIAlist.extend(timeok(now,timedict,priordict))
#        endofsegment(priordict) #shouldnt be here we have unresolved items in the socket
#end checktime

#consistency check is here
        (dying,tempMIAlist)=amiok(priordict)
        masterMIAlist.extend(tempMIAlist)
        masterMIAlist.extend(endofsegment(priordict))
        print "eoslist2",masterMIAlist #temporary
        time.sleep(1) #temporary !!
        print "priordict", priordict #temporary
        masterMIAlist.extend(endofsegment(priordict)) #temporary
        print "eoslist3",masterMIAlist #temporary
        print "did consistancy check.  I am:", dying #temporary
        if dying:
            masterMIAlist.extend(sendmessage(priordict,"dying"))
        else:
            masterMIAlist.extend(sendmessage(priordict,"alive"))
        if len(priordict)!=0: #deals with the issues returning an empty dict temporary
            (priordict,active,tempMIAlist)=dealwithdeath(priordict,priority,active) #tempeos here
        masterMIAlist.extend(tempMIAlist)
        if dying: #We actually die here if things fuck up
            print "dying"
            quit()
        time.sleep(1) #temporary !!
        masterMIAlist.extend(endofsegment(priordict)) #added cause we are at the end of a segment here
        masterMIAlist=remove_dups(masterMIAlist) #remove duplicate items
        print "eoslist4", masterMIAlist #temporary
        if len(masterMIAlist)>0: #temporary
            print "we have things to fix"
            (priordict,active)=miaresolve(priordict,masterMIAlist,priority,active)
            #quit() #temporary
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
