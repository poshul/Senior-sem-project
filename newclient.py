import socket
mySocket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
mySocket.bind ( ( '', 2487 ) )
mySocket.listen ( 1 )
while True:
    channel, details = mySocket.accept()
    print 'We have opened a connection with', details
    while True:
        try:
            print channel.recv(100)
        except:
            print "recv error"
            channel.close()
            mySocket.close()
            quit()
        print "received"
        try:
            channel.send("next")
        except:
            print "send error"
            channel.close()
            mySocket.close()
            quit()
