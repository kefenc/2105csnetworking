from socket import *
import sys
import zlib

global checksum
checksum = 0


seq_num = 0




def prep_package(data, seq_num):
    checksum = zlib.crc32(data.encode())
    segment = '' + str(seq_num) +"_"+ str(checksum) +"_"+ data

    if len(segment) > 64:
        sys.stderr.write("segment length too long")

    return segment.encode(), checksum, seq_num

def is_corrupted(segment, checksum):
    recv_checksum = segment.split("_")[1]
    print("checksum "+str(checksum)+ "vs recv"+ recv_checksum+", " + str(str(checksum)==str(recv_checksum)))
    return str(checksum) != str(recv_checksum)
       

def wrong_ack(segment, seq_num):
    recv_ack = segment.split("_")[0]
    print("seq no "+ str(seq_num) + " vs "+ str(recv_ack))
    return str(seq_num) != str(recv_ack)
    
    
corrupt_pkt = 0   
recved_pkts = 0

portnum = int(sys.argv[1])





while True:
    aliceSocket = socket(AF_INET, SOCK_DGRAM)
    #print("Alice is listening")
    data = sys.stdin.read(50)
    #while len(data) < 30:
        #data += sys.stdin.readline()
    data_len = len(data)
    # data needs to be 64-5-2 = 57
    if data_len < 1: 
        break

    while data_len > 0:
        tmp_data = data[0: 50]
        data = data[len(tmp_data):]
        data_len -= len(tmp_data)

        segment, checksum, seq_num = prep_package(tmp_data, seq_num)
        

        max_tries = 10
        not_sent = True
    
        while not_sent:
            if max_tries == 0: 
                break
            max_tries -=1
            aliceSocket.sendto(segment, ('localhost', portnum))
            print("send: " + segment.decode(), end= "")
            aliceSocket.settimeout(0.05)

            try:
                recv_segment, recv_addr = aliceSocket.recvfrom(64)
                print("recieved:"+ recv_segment.decode())
                recved_pkts += 1

                ### chec if packet is currupted or wrong ack number, make packet, send and start the timer again
                if recv_segment.decode().strip() == "duplicate":
                    print("get into dup")
                    seq_num += 1
                    seq_num %= 100
                    corrupt_pkt +=1
                    
                    not_sent = False
                elif len(recv_segment.decode().strip().split("_")) < 3:
                    print("pkt len too short")
                    corrupt_pkt +=1
                
                elif is_corrupted(recv_segment.decode(), checksum):
                    print("pkt corrupted")
                    corrupt_pkt +=1

                else:
                    seq_num += 1
                    seq_num %= 100
                    
                    not_sent = False
                    print("sent : true")
            except timeout:
                print("timeout, data loss")
                continue
                ## send packet again n restart timer
                
        
writer = open('Alice.txt', 'w')
writer.write(format(corrupt_pkt/recved_pkts, '.2f'))
writer.flush()
writer.close()
   

"""elif wrong_ack(recv_segment.decode(), seq_num):
    print("wrong ack")
    corrupt_pkt +=1"""