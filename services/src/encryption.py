from Crypto.Cipher import AES
####from Crypto.Random import OSRNG Deprecated in pycryptodome https://pycryptodome.readthedocs.io/en/latest/src/vs_pycrypto.html
from base64 import b64decode, b64encode
import Crypto.Random


'''
Test code put in console to make sure Javascript and Python matches
Python Encryption

2020-04-14 - Replaced pycrypto with PyCryptodome
In future I want to look at the new python crypto library which may be simplier to use
https://pypi.org/project/cryptography/
See https://theartofmachinery.com/2017/02/02/dont_use_pycrypto.html

from Crypto.Cipher import AES
from Crypto.Random import OSRNG
from base64 import b64decode, b64encode
from encryption import pad, unpad, __INT__get32BytesFromSalt

passphraseBase64 = b64encode('tyttt'.encode())
passphrase = __INT__get32BytesFromSalt(b64decode(passphraseBase64))
plainText='aa'
IV=b'\xffH\x93\xdeh\xd1\xcd\xab1;ZSB\x08\x19\n'

##print(bytes(IV).hex())

aes = AES.new(passphrase, AES.MODE_CBC, IV)
cipherText = aes.encrypt(pad(plainText))

print("Base64 IV:", b64encode(IV).decode("utf-8"))
print("HEX IV:", bytes(IV).hex())
print("Result cipherText = ", b64encode(cipherText).decode("utf-8"))


##  Fbv+GmrmrO+YeLfm/g2kVw==


Javascript Encryption

console.log('CryptoJS:', CryptoJS)
function get32BytesFromSalt (salt) {
  var retBytes = ''
  for (let i = 0; i < 32; i++) {
    retBytes += salt[i % salt.length]
  }
  // idx = x % len(salt)
  // retBytes = retBytes + salt[idx:(idx+1)]
  return retBytes
}

var passphraseBase64=btoa('tyttt')
var passphrase = get32BytesFromSalt(atob(passphraseBase64))
var plainText = 'aa'
// var IV = CryptoJS.lib.WordArray.random(16)
var IV = CryptoJS.enc.Base64.parse("/0iT3mjRzasxO1pTQggZCg==")
var passphraseWordArray = CryptoJS.enc.Base64.parse(btoa(passphrase))

var enc_options = {
  iv: IV,
  mode: CryptoJS.mode.CBC,
  padding: CryptoJS.pad.Pkcs7,
}
var encrypted = CryptoJS.AES.encrypt(plainText, passphraseWordArray, enc_options)

console.log("Result IV = ", IV.toString(CryptoJS.enc.Base64))
console.log("Result cipherText = ", encrypted.ciphertext.toString(CryptoJS.enc.Base64))


// Fbv+GmrmrO+YeLfm/g2kVw==


'''

def __INT__get32BytesFromSalt(salt):
  retBytes = b''
  for x in range(0,32):
    idx = x % len(salt)
    retBytes = retBytes + salt[idx:(idx+1)]

  return retBytes


BLOCK_SIZE = 16

#Pad with a number that is the length of the padding that is added
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

  ##IV = OSRNG.posix.new().read(BLOCK_SIZE)
  IV = Crypto.Random.get_random_bytes(BLOCK_SIZE)

  aes = AES.new(passphrase, AES.MODE_CBC, IV)

  cipherText = aes.encrypt(pad(plainText).encode("utf-8"))

  return b64encode(IV).decode("utf-8"), b64encode(cipherText).decode("utf-8")
#  return (b64encode(iv).decode("utf-8"), b64encode(ciphertext).decode("utf-8"))

def decryptPassword(iv, cypherText, salt):
  if (type(salt)) is not bytes:
    salt = bytes(salt, 'utf-8')
  #iv and cypherText are base64 encoded strings
  ivi=b64decode(iv)
  cypherTexti=b64decode(cypherText)
  passphrase=__INT__get32BytesFromSalt(salt)

  ##passphrase="12345678901234567890123456789012"

  #print("Decrypting Password:")
  #print("ivi", ivi)
  #print("cypherTexti", cypherTexti)
  #print("passphrase", passphrase)

  aes = AES.new(passphrase, AES.MODE_CBC, ivi)
  unpaddedPlainText = unpad(aes.decrypt(cypherTexti).decode())

  #print("Res:", unpaddedPlainText)

  return unpaddedPlainText

def encryptPasswordX(plainText, salt):
  if (type(salt)) is not bytes:
    salt = bytes(salt, 'utf-8')

  #salt is bytes or string
  #plain text is STRING
  #return value is bytes
  ###iv = OSRNG.posix.new().read(AES.block_size) #'This is an IV456'
  iv = Crypto.Random.get_random_bytes(AES.block_size)

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

  #recieved val is BYTES
  #returned val needs to be STRING
  obj2 = AES.new(salti, AES.MODE_CFB, ivi)
  decrypted = obj2.decrypt(cypherTexti)
  print("decrypted:", decrypted)
  return decrypted.decode("utf-8")
