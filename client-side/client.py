import os
from hashlib import sha256
import socket
import pandas as pd
import streamlit as st
from cryptography.fernet import Fernet

SIZE = 102400
PORT = 4455
KEY = '7Jj8z6d9d5HmvO4YgnWVTRKhjvSfv_jOkFHZVdkHYN8='

def Encrypt_Data(data):
    fernet = Fernet(KEY)
    cipherText = fernet.encrypt(data.encode())
    return cipherText

def Decrypt_Data(data):
    fernet = Fernet(KEY)
    plainText = fernet.decrypt(data.encode())
    return plainText

def Chunk_File(file_path, chunk_size):
    chunks = []
    with open(file_path, "r") as file:
        while True:
            chunk = file.read(chunk_size)
            if chunk:
                chunks.append(chunk)
            else:
                break
    return chunks

def Merkle_Tree(chunks):
    if len(chunks) == 1:
        return sha256(chunks[0].encode()).hexdigest()
    mid = len(chunks) // 2
    left_hash = Merkle_Tree(chunks[:mid])
    right_hash = Merkle_Tree(chunks[mid:])
    return sha256(left_hash.encode() + right_hash.encode()).hexdigest()

def Show_Files(ip):
    IP = socket.gethostbyname(socket.gethostname())
    server_address = (IP, PORT)
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(server_address)
        client.send("Show".encode())
        msg = client.recv(SIZE).decode()
        print(msg)
    except:
        st.error("Connection Failure! Check if the server is active.")
        return
    client.send("Sending Filenames".encode())
    file_names = client.recv(SIZE).decode()
    client.close()
    print("File names Received")
    return file_names

def Upload_File(filename, ip):
    IP = socket.gethostbyname(socket.gethostname())
    server_address = (IP, PORT)
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(server_address)
        client.send("Upload".encode())
        ack_msg1 = client.recv(SIZE).decode()
        print(ack_msg1)
    except:
        st.error("Connection Failure! Check if the server is active.")
        return
    client.send(filename.encode())
    ack_msg2 = client.recv(SIZE).decode()
    print(f"Server: {ack_msg2}")
    with open(filename, "r") as file:
        data = file.read()
        client.sendall(Encrypt_Data(data))
    file_chunk = Chunk_File(filename, 1024)
    hash_value = Merkle_Tree(file_chunk)
    print(f"Hash value: {hash_value}")
    client.send(hash_value.encode())
    verfi_msg = client.recv(SIZE).decode()
    if verfi_msg == "True":
        st.success("Data Integrity assured!", icon="✅")
    else:
        st.error("Data might be lost.")
    ack_msg3 = client.recv(SIZE).decode()
    print(f"Server: {ack_msg3}")
    client.close()
    if ack_msg3 == "File data received":
        return True
    return False

def Authenticate(username, password, ip):
    IP = socket.gethostbyname(socket.gethostname())
    server_address = (IP, PORT)
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(server_address)
        client.send("Auth".encode())
        ack_msg1 = client.recv(SIZE).decode()
        print(ack_msg1)
    except:
        st.error("Connection Failure! Check if the server is active.")
        return
    encrypted_data = Encrypt_Data(f"{username}\n{password}")
    client.sendall(encrypted_data)
    ack_msg2 = client.recv(SIZE).decode()
    print(f"Server: {ack_msg2}")
    client.close()
    if ack_msg2 == "Authentication successful":
        return True
    return False

def Download_File(filename, ip):
    IP = socket.gethostbyname(socket.gethostname())
    server_address = (IP, PORT)
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(server_address)
        client.send("Download".encode())
        ack_msg1 = client.recv(SIZE).decode()
        print(ack_msg1)
    except:
        st.error("Connection Failure! Check if the server is active.")
        return
    client.send(filename.encode())
    ack_msg2 = client.recv(SIZE).decode()
    print(ack_msg2)
    exist = client.recv(SIZE).decode()
    print(f"Exists? {exist}")
    client.send("Downloading".encode())
    if exist == "Exist":
        data = client.recv(SIZE).decode()
        os.makedirs("Downloaded", exist_ok=True)
        with open("Downloaded/" + filename, 'w') as f:
            f.write(Decrypt_Data(data).decode())
        received_hash_val = client.recv(SIZE).decode()
        print(f"Hash value {received_hash_val}")
        client.close()
        file_chunk = Chunk_File("Downloaded/" + filename, 1024)
        file_hash_value = Merkle_Tree(file_chunk)
        print(f"Hash value: {file_hash_value}")
        if file_hash_value == received_hash_val:
            print("Downloaded data has the same hash values")
            st.success("Data Integrity assured!", icon="✅")
            return True
        else:
            st.error("Data might be lost", icon="🚨")
            return False
    elif exist == "NotExist":
        st.error("No such file exists in the server", icon="🚨")
        return False
    else:
        print("Some other error")
        return False

if __name__ == "__main__":
    st.title("Secure File Transfer System")
    st.subheader("Encrypt and Verify in a Flash ⚡")
    ip = st.text_input("Enter IP address of the server: ")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login = st.button("Login")
    if login:
        try:
            if Authenticate(username, password, ip):
                st.success("Authentication successful! You can now use the application.", icon="✅")
            else:
                st.error('Authentication Failed! You can\'t now use the application.', icon="🚨")
        except:
            pass
    st.divider()
    showfiles = st.button("Show Files")
    if showfiles:
        try:
            files = Show_Files(ip)
            if files != "None":
                files = files.split("\n")
                df = pd.DataFrame({"Files in the server: ": files})
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No Files in the server.")
        except:
            pass
    st.divider()
    uploaded_files = st.file_uploader("Choose text files!", accept_multiple_files=True)
    upload = st.button("Upload Files!")
    if upload:
        if uploaded_files:
            filenames = []
            for uploaded_file in uploaded_files:
                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                if Upload_File(uploaded_file.name, ip):
                    st.success(f'File {uploaded_file.name} was transferred successfully!', icon="✅")
                    filenames.append(uploaded_file.name)
                else:
                    st.error(f'There was some problem with transferring {uploaded_file.name}! Try again', icon="🚨")
            print(filenames)
        else:
            st.error(f'Browse files to upload first!', icon="🚨")
    st.divider()
    filename = st.text_input("Enter file you want to download from the server: ")
    download = st.button("Download File")
    if download:
        if filename:
            if Download_File(filename, ip):
                st.success(f'File {filename} was downloaded successfully! Check your "Downloaded" folder.', icon="✅")
            else:
                st.error(f'Downloading of {filename} failed! Try again', icon="🚨")
        else:
            st.error(f'Enter a filename to be downloaded first!', icon="🚨")
