# Secure File Transfer Application

## Overview
This project is a secure file transfer application that ensures the safe and efficient transfer of data between clients and a server. It incorporates encryption, file chunking, and Merkle trees for data integrity verification.

## Features
- 🔒 **Secure Data Transfer**: Uses AES encryption via the `cryptography.fernet` library to encrypt and decrypt files.
- 🗂️ **File Chunking**: Splits large files into manageable chunks for transfer.
- 🌲 **Merkle Tree Implementation**: Verifies data integrity during transmission.
- 💻 **Streamlit Integration**: User-friendly interface for the client-side application.
- 📜 **Logging**: Server logs all incoming file transfers.

## Project Structure
```
CodeAlpha_Secure-File-Transfer-Application/
├── client-side/
│   ├── client.py             # Main client-side script
│   ├── requirements.txt      # Client dependencies
│   └── Downloaded/           # Directory for downloaded files
├── server-side/
│   ├── server.py             # Main server-side script
│   ├── logs.csv              # File transfer logs
│   └── Received Data/        # Directory for received files
└── requirements.txt          # Project-wide dependencies
```

## 🚀 Setup

### Prerequisites
- Python 3.8 or above
- Install dependencies using pip:
  ```bash
  pip3 install -r requirements.txt
  ```

### Running the Server
1. Navigate to the `server-side` directory:
   ```bash
   cd server-side
   ```
2. Run the server script:
   ```bash
   python3 server.py
   ```
3. The server will start listening for incoming file transfers.

### Running the Client
1. Navigate to the `client-side` directory:
   ```bash
   cd client-side
   ```
2. Run the client script with Streamlit:
   ```bash
   streamlit run client.py
   ```
3. Use the Streamlit interface to select and send files to the server.

## 🔧 Technical Details

### Encryption
- The application uses AES encryption with the `cryptography.fernet` library.
- Files are encrypted before transmission to ensure confidentiality.

### Data Integrity
- Implements a Merkle tree structure to verify the integrity of the transmitted data.
- Hashes of file chunks are combined to form a tree, with the root hash ensuring end-to-end verification.

### File Chunking
- Large files are divided into chunks (default size: 102,400 bytes) to facilitate efficient transmission.

## 📋 Usage
1. Start the server and client applications.
2. Select a file in the client interface.
3. The file will be:
   - Chunked
   - Encrypted
   - Transmitted to the server
4. The server will decrypt and store the file, verifying its integrity using the Merkle tree.

## 📝 Logging
- The server logs all file transfer activities in `logs.csv`.
- Logs include details like transfer timestamps and file names.

## 📦 Dependencies
- `cryptography`
- `pandas`
- `streamlit`
- `socket`

## 🌟 Future Improvements
- Add support for multiple clients.
- Implement secure key exchange using public-key cryptography.
- Enhance the user interface for better usability.

## 📜 License
This project is licensed under the MIT License. See the LICENSE file for details.

## 🤝 Contributions
Contributions are welcome! Please fork the repository and submit a pull request for review.

## 📧 Contact
For questions or support, please contact [gauravbhattacharjee54@gmail.com].

