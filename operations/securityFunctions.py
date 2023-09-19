import random, string

PASSWORD_LENGTH = 8
EDGAR_SPEC_CHARS = "@#*$"

def generateRandomPassword():
  characterPool = string.ascii_letters + string.digits + EDGAR_SPEC_CHARS
  while True:
    password = "".join(random.choice(characterPool) for _ in range(PASSWORD_LENGTH))
    hasDigit = any(char.isdigit() for char in password)
    hasSpecChar = any(char in EDGAR_SPEC_CHARS for char in password)
    if hasDigit and hasSpecChar:
      return password

def generate_token(length = 10):
  characters = string.ascii_letters + string.digits + string.punctuation
  return ''.join(random.choice(characters) for _ in range(length))

print(generate_token())