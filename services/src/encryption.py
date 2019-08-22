from Crypto.Cipher import AES
from Crypto.Random import OSRNG
from base64 import b64decode, b64encode


def __INT__get32BytesFromSalt(salt):
  retBytes = b''
  for x in range(0,32):
    idx = x % len(salt)
    retBytes = retBytes + salt[idx:(idx+1)]

  return retBytes


BLOCK_SIZE = 16
def pad(data):
    length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + chr(length)*length

def unpad(data):
    return data[:-ord(data[-1])]

# Based on https://stackoverflow.com/questions/11567290/cryptojs-and-pycrypto-working-together
def encryptPassword(plainText, salt):
  if (type(salt)) is not bytes:
    salt = bytes(salt, 'utf-8')

  passphrase = __INT__get32BytesFromSalt(salt)

  IV = OSRNG.posix.new().read(BLOCK_SIZE)
  aes = AES.new(passphrase, AES.MODE_CBC, IV)

  cipherText = aes.encrypt(pad(plainText))

  return b64encode(IV).decode("utf-8"), b64encode(cipherText).decode("utf-8")
#  return (b64encode(iv).decode("utf-8"), b64encode(ciphertext).decode("utf-8"))

def decryptPassword(iv, cypherText, salt):
  if (type(salt)) is not bytes:
    salt = bytes(salt, 'utf-8')
  #iv and cypherText are base64 encoded strings
  ivi=b64decode(iv)
  cypherTexti=b64decode(cypherText)
  passphrase=__INT__get32BytesFromSalt(salt)

  print("ivi", ivi)
  print("cypherTexti", cypherTexti)
  print("passphrase", passphrase)

  aes = AES.new(passphrase, AES.MODE_CBC, ivi)
  paddedPlainText = aes.decrypt(cypherTexti).decode()
  return unpad(paddedPlainText)

def encryptPasswordX(plainText, salt):
  if (type(salt)) is not bytes:
    salt = bytes(salt, 'utf-8')

  #salt is bytes or string
  #plain text is STRING
  #return value is bytes
  iv = OSRNG.posix.new().read(AES.block_size) #'This is an IV456'
  obj = AES.new(__INT__get32BytesFromSalt(salt), AES.MODE_CFB, iv)
  ciphertext = obj.encrypt(plainText)

  #output base64 encoded strings
  return (b64encode(iv).decode("utf-8"), b64encode(ciphertext).decode("utf-8"))

def decryptPasswordX(iv, cypherText, salt):
  if (type(salt)) is not bytes:
    salt = bytes(salt, 'utf-8')
  #iv and cypherText are base64 encoded strings
  ivi=b64decode(iv)
  cypherTexti=b64decode(cypherText)
  salti=__INT__get32BytesFromSalt(salt)

  print("decryptPassword salt:", salti)
  print("decryptPassword IV:", ivi)
  print("decryptPassword cypherTexti:", cypherTexti)

  #recieved val is BYTES
  #returned val needs to be STRING
  obj2 = AES.new(salti, AES.MODE_CFB, ivi)
  decrypted = obj2.decrypt(cypherTexti)
  print("decrypted:", decrypted)
  return decrypted.decode("utf-8")
