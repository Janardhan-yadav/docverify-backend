# This file will contain security-related utilities like encryption.

from cryptography.fernet import Fernet
import os

# Generate a key for encryption. In a real application, this key must be securely managed
# and should not be hardcoded or stored in version control. It should be loaded from
# environment variables or a secure vault.
ENCRYPTION_KEY = os.getenv("DOCVERIFY_ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # For development, we can generate one if not set, but this is NOT secure for production.
    # print("Warning: ENCRYPTION_KEY not set, generating a new one. THIS IS NOT FOR PRODUCTION.")
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    # It's better to require it to be set. For this exercise, we'll proceed with a generated one if not found.
    # raise ValueError("ENCRYPTION_KEY environment variable not set.")

if ENCRYPTION_KEY:
    cipher_suite = Fernet(ENCRYPTION_KEY.encode())
else:
    # Fallback if key generation also failed or was skipped (should not happen with current logic)
    print("CRITICAL: Encryption key is not available. Document encryption will not work.")
    cipher_suite = None 

def encrypt_file_content(file_content: bytes) -> bytes:
    if not cipher_suite:
        raise ValueError("Encryption not initialized.")
    return cipher_suite.encrypt(file_content)

def decrypt_file_content(encrypted_content: bytes) -> bytes:
    if not cipher_suite:
        raise ValueError("Encryption not initialized.")
    return cipher_suite.decrypt(encrypted_content)

# Example of how to use with files:
def encrypt_file(file_path: str, encrypted_file_path: str):
    with open(file_path, "rb") as f:
        file_content = f.read()
    encrypted_content = encrypt_file_content(file_content)
    with open(encrypted_file_path, "wb") as f:
        f.write(encrypted_content)

def decrypt_file(encrypted_file_path: str, decrypted_file_path: str):
    with open(encrypted_file_path, "rb") as f:
        encrypted_content = f.read()
    decrypted_content = decrypt_file_content(encrypted_content)
    with open(decrypted_file_path, "wb") as f:
        f.write(decrypted_content)


