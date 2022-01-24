from socket import *
import sys
import zlib

global checksum
checksum = b''

global seq_num
seq_num = 0

def is_corrupted(segment):
    recv_checksum = segment.split("_")[1]
    return checksum == recv_checksum
       

def wrong_ack(segment):
    recv_ack = segment.split("_")[0]
    return seq_num == recv_ack

portnum = int(sys.argv[1])
bobSocket = socket(AF_INET, SOCK_DGRAM)
bobSocket.bind(('', portnum))
sys.stderr.write("bob is ready to listen")

while True:
    message, aliceAdd = bobSocket.recvfrom(64)
    sys.stderr.write(message.decode())

    if len(message.decode()) == 0:
        break


    #deconstruct alice msg and check if checksum is correct, its not a duplicate
    if is_corrupted(message.decode()) or wrong_ack(message.decode()):
        sys.stderr.write("corrupted packet.")
    else:
        print(message.decode().split("_")[2])
        bobSocket.sendto(message, aliceAdd)

    

