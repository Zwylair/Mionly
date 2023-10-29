import eel


@eel.expose
def rot1_encrypt(text: str) -> str:
    encrypted = ''
    for char in text:
        if char.isalpha():
            a = 'a' if char.islower() else 'A'
            encrypted += chr(((ord(char) - ord(a) + 1) % 26) + ord(a))
        else:
            encrypted += char
    return encrypted


@eel.expose
def rot1_decrypt(text: str) -> str:
    encrypted = ''
    for char in text:
        if char.isalpha():
            a = 'a' if char.islower() else 'A'
            encrypted += chr(((ord(char) - ord(a) - 1) % 26) + ord(a))
        else:
            encrypted += char
    return encrypted
