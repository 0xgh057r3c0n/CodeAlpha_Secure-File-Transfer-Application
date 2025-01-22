import os
import csv
import socket
import datetime
from hashlib import sha256
from cryptography.fernet import Fernet

KEY = b'7Jj8z6d9d5HmvO4YgnWVTRKhjvSfv_jOkFHZVdkHYN8='
IP = socket.gethostbyname(socket.gethostname())
PORT = 4455
ADDR = (IP, PORT)
SIZE = 102400
credentials = {
    "UserOne": "password1",
    "UserTwo": "password2"
}

def Encrypt_Data(data):
    fernet = Fernet(KEY)
    cipherText = fernet.encrypt(data.encode())
    return cipherText

def Decrypt_Data(data):
    fernet = Fernet(KEY)
    try:
        plainText = fernet.decrypt(data.encode())
        return plainText.decode()
    except Exception as e:
        print(f"Decryption failed: {str(e)}")
        return None

def Log_To_CSV(log_data):
    with open("logs.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(log_data)

def Chunk_File(file_path, chunk_size):
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            yield chunk

def Merkle_Tree(chunks):
    hashes = [sha256(chunk).hexdigest() for chunk in chunks]
    while len(hashes) > 1:
        hashes = [sha256((hashes[i] + hashes[i+1]).encode()).hexdigest() for i in range(0, len(hashes), 2)]
    return hashes[0] if hashes else ''

def Upload_File(conn, addr):
    file_name = conn.recv(SIZE).decode()
    print(f"Filename: {file_name} received")
    conn.send("filename received".encode())
    data = conn.recv(SIZE)
    decrypted_data = Decrypt_Data(data)
    if decrypted_data:
        with open("Received Data/" + file_name, 'wb') as file:
            file.write(decrypted_data.encode())
    client_hash_val = conn.recv(SIZE).decode()
    print(f"Hash value {client_hash_val}")
    file_chunk = Chunk_File("Received Data/" + file_name, 1024)
    server_hash_val = Merkle_Tree(file_chunk)
    print(f"Hash value: {server_hash_val}")
    if server_hash_val == client_hash_val:
        conn.send("True".encode())
        log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "Upload", file_name, "Successful"]
        Log_To_CSV(log_data)
        print('Your data is in good hands')
    else:
        conn.send("False".encode())
        log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "Upload", file_name, "Unsuccessful"]
        Log_To_CSV(log_data)
        print('Your data is not in good hands')

def Download_File(conn, addr):
    file_name = conn.recv(SIZE).decode()
    print(f"Filename: {file_name} received")
    conn.send("filename received".encode())
    if os.path.exists("Received Data/" + file_name):
        conn.send("Exist".encode())
        print("File exists")
        msg = conn.recv(SIZE).decode()
        print(msg)
        with open("Received Data/" + file_name, 'r') as file:
            data = file.read()
            conn.send(Encrypt_Data(data))
        file_chunk = Chunk_File("Received Data/" + file_name, 1024)
        hash_val = Merkle_Tree(file_chunk)
        print(f"Hash value: {hash_val}")
        conn.send(hash_val.encode())
        log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "Download", file_name, "Successful"]
        Log_To_CSV(log_data)
    else:
        conn.send("NotExist".encode())
        log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "Download", file_name, "File not found"]
        Log_To_CSV(log_data)
        print("File does not exist")

def Authenticate_User(conn, addr):
    encrypted_data = conn.recv(SIZE).decode()
    print(f"Encrypted data received: {encrypted_data}")
    decrypted_data = Decrypt_Data(encrypted_data)
    if decrypted_data is None:
        conn.send("Decryption failed".encode())
        print("Decryption failed")
        return False
    print(f"Decrypted data: {decrypted_data}")
    try:
        username, password = decrypted_data.split('\n')
        print(f"Username: {username}, Password: {password}")
    except ValueError:
        conn.send("Invalid data format".encode())
        print("Invalid data format received")
        return False
    if username in credentials and credentials[username] == password:
        conn.send("Authentication successful".encode())
        log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "Auth", f"{username},:{password}", "Successful"]
        Log_To_CSV(log_data)
        print('Your Authentication is Successful')
        return True
    else:
        conn.send("Authentication failed".encode())
        log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "Auth", f"{username},:{password}", "Unsuccessful"]
        Log_To_CSV(log_data)
        print('Your Authentication is failed')
        return False

def Show_Files(conn, addr):
    files = []
    for file in os.listdir('./Received Data'):
        if file.endswith(".txt"):
            files.append(file)
    if files:
        files = '\n'.join(files)
        print("Files: \n", files)
    else:
        files = "None"
    msg = conn.recv(SIZE).decode()
    conn.send(files.encode())
    log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "Get File Names"]
    Log_To_CSV(log_data)
    print("File names sent!")

def main():
    print("Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print("Server is listening")
    while True:
        conn, addr = server.accept()
        print(f"New connection: {addr} connected.")
        log_data = [str(datetime.datetime.now().date()), str(datetime.datetime.now().time()), str(addr), "New connection"]
        Log_To_CSV(log_data)
        transfer_type = conn.recv(SIZE).decode()
        print(f"Received Transfer type: {transfer_type}")
        conn.send("Received Transfer type".encode())
        if transfer_type == "Upload":
            Upload_File(conn, addr)
        elif transfer_type == "Download":
            Download_File(conn, addr)
        elif transfer_type == "Show":
            Show_Files(conn, addr)
        elif transfer_type == "Auth":
            Authenticate_User(conn, addr)
        else:
            print("Invalid Transfer Type Received")
            break
    conn.close()
    print(f"Disconnected with {addr}")
    return

if __name__ == '__main__':
    if not os.path.exists("Received Data"):
        os.makedirs("Received Data")
        print("Directory 'Received Data' created.")
    if not os.path.exists("logs.csv"):
        with open("logs.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Timestamp", "Client Address", "Event", "Filename", "Status"])
    main()
