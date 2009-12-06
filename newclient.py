import socket
import sys
mySocket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
mySocket.bind ( ( '', 2487 ) )
mySocket.listen ( 1 )
while True:
    channel, details = mySocket.accept()
    print 'We have opened a connection with', details
    while True:
        try:
            received=channel.recv(100)
            if received!='': #dont print junk when we are establishing new connection
                print "received", received
        except socket.error:
            channel,details =mySocket.accept()
            print "opened a new socket with",details
        except:
            print "recv error",sys.exc_info()
            channel.close()
            mySocket.close()
            quit()
        try:
            channel.send("next")
        except socket.error:
            channel,details =mySocket.accept()
            print "opened a new socket with",details
        except:
            print "send error",sys.exc_info()
            channel.close()
            mySocket.close()
            quit()
