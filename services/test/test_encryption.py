from TestHelperSuperClass import testHelperSuperClass, wipd
from appObj import appObj
from encryption import decryptPassword, encryptPassword

@wipd
class test_encryption(testHelperSuperClass):
  def test_passwordEncrypt(self):
    plainText="AAAAA"
    salt=appObj.bcrypt.gensalt()

    (iv, cypherText) = encryptPassword(plainText, salt)
    plainText2 = decryptPassword(iv, cypherText, salt)

    self.assertEqual(plainText, plainText2)


  def test_passwordEncrypt(self):
    plainText="AAAAA\n\n\n"
    salt=appObj.bcrypt.gensalt()

    (iv, cypherText) = encryptPassword(plainText, salt)
    plainText2 = decryptPassword(iv, cypherText, salt)


  def test_passwordEncrypt(self):
    plainText="AAAAA\0\0\0"
    salt=appObj.bcrypt.gensalt()

    (iv, cypherText) = encryptPassword(plainText, salt)
    plainText2 = decryptPassword(iv, cypherText, salt)

    self.assertEqual(plainText, plainText2)

  def test_passwordEncrypt(self):
    plainText="AAAAA\0\0\0sadrgfrg"
    salt=appObj.bcrypt.gensalt()

    (iv, cypherText) = encryptPassword(plainText, salt)
    plainText2 = decryptPassword(iv, cypherText, salt)

    self.assertEqual(plainText, plainText2)
