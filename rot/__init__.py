def encrypt(text: str, gap: int = 1) -> str:
    encrypted = ''
    for char in text:
        if char.isalpha():
            a = 'a' if char.islower() else 'A'
            encrypted += chr(((ord(char) - ord(a) + gap) % 26) + ord(a))
        else:
            encrypted += char
    return encrypted


def decrypt(text: str, gap: int = 1) -> str:
    encrypted = ''
    for char in text:
        if char.isalpha():
            a = 'a' if char.islower() else 'A'
            encrypted += chr(((ord(char) - ord(a) - gap) % 26) + ord(a))
        else:
            encrypted += char
    return encrypted
