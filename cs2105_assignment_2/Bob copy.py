from socket import *
import sys
import zlib



global seq_num
seq_num = 0
       
def check_duplicates(segment, seq_num):
    recv_ack = segment.split("_")[0]
    if 0 <= int(recv_ack) <= 99:
        return int(seq_num) > int(recv_ack)
    else:
        print("missing ack num")
        return False

def wrong_ack(segment, seq_num):
    recv_ack = segment.split("_")[0]
    return int(seq_num) != int(recv_ack)

corrupt_pkt = 0   
recved_pkts = 1

portnum = int(sys.argv[1])

printed = [False] * 99


try:

    while True:
        bobSocket = socket(AF_INET, SOCK_DGRAM)
        bobSocket.bind(('localhost', portnum))
        #print("bound")
        
        
        message, aliceAddress = bobSocket.recvfrom(64)
        #print("***")
        #print(message.decode(), aliceAddress )
        #print("***")
        if len(message.decode()) > 64:
            print("too long!")
        recved_pkts +=1

        #deconstruct alice msg and check if checksum is correct, its not a duplicate
         
        if len(message.decode().split("_")) != 3:
            print("corrupted packet.")
            corrupt_pkt += 1
            bobSocket.sendto("corrupt".encode(), aliceAddress)
        elif printed[seq_num]:
            bobSocket.sendto("duplicate".encode(), aliceAddress)
            print("duplicate! seq no:"+ str(seq_num) + str(printed[seq_num]) )
        elif wrong_ack(message.decode(), seq_num):
            corrupt_pkt += 1
            print('wrong ack bob_seq:' + seq_num +" but alice is sending "+ message.split("_")[0])
            bobSocket.sendto("wrongack".encode(), aliceAddress)
        else:
            #print("full message:"+message.decode())
            bobSocket.sendto(message, aliceAddress)
            #print("seq num: " + str(seq_num) + str(printed[seq_num]))
            if not printed[seq_num]: 
                print(message.decode().split("_")[2])
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


