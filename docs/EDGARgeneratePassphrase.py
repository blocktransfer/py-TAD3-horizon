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

print(generateRandomPassword())

