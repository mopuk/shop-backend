from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("dummypassword")

def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(password, hash):
    return password_hash.verify(password, hash)

def check_requirements_for_password(password: str):
    if len(password) < 6:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in "!@#$%^&*_" for char in password):
        return False
    return True