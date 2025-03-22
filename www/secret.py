import secrets

secret_key = secrets.token_hex(32)  # Generates a 64-character (32-byte) hex key
print("Your SECRET_KEY:", secret_key)
