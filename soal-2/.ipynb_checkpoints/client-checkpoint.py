import random
import sys
import socket
import json
import logging
import ssl
import threading
import os
import datetime
import time

server_address = ('172.16.16.101', 12000)


def make_socket(destination_address='localhost', port=12000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        # logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.warning(f"error {str(ee)}")


def make_secure_socket(destination_address='localhost', port=10000):
    try:
        # get it from https://curl.se/docs/caextract.html

        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.verify_mode = ssl.CERT_OPTIONAL
        context.load_verify_locations(os.getcwd() + '/domain.crt')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        # logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        secure_socket = context.wrap_socket(
            sock, server_hostname=destination_address)
        logging.warning(secure_socket.getpeercert())
        return secure_socket
    except Exception as ee:
        logging.warning(f"error {str(ee)}")


def deserialisasi(s):
    logging.warning(f"deserialisasi {s.strip()}")
    return json.loads(s)


def send_command(command_str, is_secure=False):
    alamat_server = server_address[0]
    port_server = server_address[1]
#    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# gunakan fungsi diatas
    if is_secure == True:
        sock = make_secure_socket(alamat_server, port_server)
    else:
        sock = make_socket(alamat_server, port_server)

    # logging.warning(f"connecting to {server_address}")
    try:
        # logging.warning(f"sending message ")
        sock.sendall(command_str.encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received = ""  # empty string
        while True:
            # socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(16)
            if data:
                time.sleep(1)
                # data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = deserialisasi(data_received)
        # logging.warning("data received from server:")
        return hasil
    except Exception as ee:
        logging.warning(f"error during data receiving {str(ee)}")
        return False


#Membantu tracing received or not
myglob = []
def getdatapemain(nomor=0,is_secure=False):
    cmd=f"getdatapemain {nomor}\r\n\r\n"
    hasil = send_command(cmd,is_secure=is_secure)
    if(hasil) :
        myglob.append("sukses")
        return print(hasil['nama'],hasil['nomor'])
        
    else:
        myglob.append("gagal")
        return print(f"kegagalan pada data transfer")

def lihatversi(is_secure=False):
    cmd=f"versi \r\n\r\n"
    hasil = send_command(cmd,is_secure=is_secure)
    return print

def getdatapemain(nomor=0,is_secure=False):
    cmd=f"getdatapemain {nomor}\r\n\r\n"
    hasil = send_command(cmd,is_secure=is_secure)
    return hasil 

def getresultpemain(index,result):
    time_request_start = time.perf_counter()

    result = getdatapemain(random.randint(1, 25))
    if (result):
        latency = time.perf_counter() - time_request_start
        print(result['nama'], result['nomor'], result['posisi'])
        print(f'latency: {latency * 1000:.2f} ms')
        results[index] = latency
    else:
        print('kegagalan pada data transfer')
        results[index] = -1
        
def lihatversi(is_secure=False):
    cmd=f"versi \r\n\r\n"
    hasil = send_command(cmd,is_secure=is_secure)
    return print

if __name__ == '__main__':
    thread_count = int(sys.argv[1]) if len(sys.argv) >= 2 else 5
    request_count = int(sys.argv[2]) if len(sys.argv) >= 3 else 100
    response_count = 0
    latency_sum = 0

    tasks = {}
    results = {}

    time_start = time.perf_counter()
    loops = request_count
    while loops > 0:
        loops_inner =  thread_count if loops >= thread_count else loops

        for i in range(loops_inner):
            tasks[loops - i] = threading.Thread(target=getresultpemain, args=(loops - i, results))
            tasks[loops - i].start()

        for i in range(loops_inner):
            tasks[loops - i].join()
            if (results[loops - i] != -1):
                response_count += 1
                latency_sum += results[loops - i]

        loops -= loops_inner

    time_end = time.perf_counter()
    
    print(f'With {thread_count} threads')
    print(f'Request count: {request_count}')
    print(f'Response count: {response_count}')
    print(f'Average Latency: {(latency_sum / response_count) * 1000:.3f} ms')
    print(f'Execution time: {(time_end - time_start) * 1000:.3f} ms')