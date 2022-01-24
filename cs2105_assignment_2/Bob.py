from socket import *
import sys
import zlib


global checksum
checksum = 0

global seq_num
seq_num = 0
       
def check_duplicates(segment, seq_num):
    recv_ack = segment.split("_")[0]
    return str(seq_num) > str(recv_ack)

def wrong_ack(segment, seq_num):
    recv_ack = segment.split("_")[0]
    #print("seq no "+ str(seq_num) + " vs "+ str(recv_ack))
    return str(seq_num) != str(recv_ack)

def is_corrupted(segment):
    recv_checksum = segment.split("_")[1]
    #print(recv_checksum)
    try:
        #print(segment.split("_")[2].encode())

        recv_message = zlib.crc32(segment.split("_")[2].encode())
        #print(recv_message)
        return str(recv_message) != str(recv_checksum)
    except:
        print("out of bounds or something")
    
    

corrupt_pkt = 0   
recved_pkts = 0

portnum = int(sys.argv[1])

global printed
printed = [False] * 99
try:

    while True:
        bobSocket = socket(AF_INET, SOCK_DGRAM)
        bobSocket.bind(('localhost', portnum))
        #print("bound")
        
        
        message, aliceAddress = bobSocket.recvfrom(64)
        #print(message, aliceAddress)
        
        if len(message.decode()) > 64:
            print("too long!")
        recved_pkts +=1

        #deconstruct alice msg and check if checksum is correct, its not a duplicate
         
        if len(message.decode().split("_")) < 3:
            #print("youre supposed to catch.")
            corrupt_pkt += 1
            
            bobSocket.sendto("placeholder".encode(), aliceAddress)

        elif is_corrupted(message.decode()):
            corrupt_pkt += 1
            #print(":(")
            bobSocket.sendto("placeholder".encode(), aliceAddress)
        
        elif check_duplicates(message.decode(), seq_num):
            bobSocket.sendto("duplicate".encode(), aliceAddress)
            #print("duplicate: "+message.decode().split("_")[2], end = "")

        else:
            #print("full message:"+message.decode())

            print(message.decode().split("_")[2], end = "")
            bobSocket.sendto(message, aliceAddress)
            printed[seq_num] = True
            seq_num += 1
            
            
        bobSocket.close()
    # print to standard output
    # send ack back to alice
finally:
    writer = open('Bob.txt', 'w')
    writer.write(format(corrupt_pkt/recved_pkts, '.2f'))
    writer.flush()
    writer.close()
    exit()


