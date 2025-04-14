# 🔐 Secure Vault Pro - Encrypted Data Storage System

![Project Banner](https://via.placeholder.com/800x200?text=Secure+Vault+Pro+AES-256+Encryption)

A secure web application for storing sensitive data with military-grade encryption, built with Streamlit and Python.

## 🚀 Features

- **Military-Grade Encryption**: AES-256 encryption for all stored data
- **Double Authentication**: Login password + separate decryption passkey
- **Secure Session Management**: Automatic lockout after 3 failed attempts
- **Data Portability**: Download decrypted data as text files
- **Activity Tracking**: Last access timestamps and session duration monitoring
- **Responsive Design**: Works on desktop and mobile devices

## ⚙️ Technical Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.9+
- **Encryption**: Fernet (AES-128-CBC with PKCS7 padding)
- **Hashing**: SHA-256 for password storage
- **Data Storage**: JSON files with encrypted content

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/GlitchPhantomX/Secure-Data-Ecryption.git
   cd app.py
