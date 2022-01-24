
from socket import*
import sys
import zlib


global checksum
checksum = b''

global seq_num
seq_num = 0


def prep_package(data, seq_num):
    checksum = zlib.crc32(data.encode())
    segment = '' + str(seq_num) +"_"+ str(checksum) +"_"+ data

    if len(segment) > 64:
        sys.stderr.write("segment length too long")

    return segment.encode()

def is_corrupted(segment):
    recv_checksum = segment.split("_")[1]
    return checksum == recv_checksum
       

def wrong_ack(segment):
    recv_ack = segment.split("_")[0]
    return seq_num == recv_ack

portnum = int(sys.argv[1])
aliceSocket = socket(AF_INET, SOCK_DGRAM)
print("Alice is listening")

while True:
    data = sys.stdin.readline()
    print("data:" + data)
    aliceSocket.sendto(prep_package(data, seq_num), ('', portnum))
    aliceSocket.settimeout(0.05)

try:
    recv_segment, recv_addr = aliceSocket.recvfrom(64)
    print("recieved:"+ recv_segment)
    

except timeout:
    sys.stderr.write("timeout")

aliceSocket.close()

