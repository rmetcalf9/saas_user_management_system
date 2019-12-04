import TestHelperSuperClass
from appObj import appObj
from encryption import decryptPassword, encryptPassword

#@TestHelperSuperClass.wipd
class test_encryption(TestHelperSuperClass.testHelperSuperClass):
  def test_passwordEncrypt(self):
    plainText="AAAAA"
    salt=appObj.bcrypt.gensalt()

    (iv, cypherText) = encryptPassword(plainText, salt)
    plainText2 = decryptPassword(iv, cypherText, salt)

    self.assertEqual(plainText, plainText2)

  def test_passwordEncrypt2(self):
    plainText="AAAAA\n\n\n"
    salt=appObj.bcrypt.gensalt()

    (iv, cypherText) = encryptPassword(plainText, salt)
    plainText2 = decryptPassword(iv, cypherText, salt)

  def test_passwordEncrypt3(self):
    plainText="AAAAA\0\0\0"
    salt=appObj.bcrypt.gensalt()

    (iv, cypherText) = encryptPassword(plainText, salt)
    plainText2 = decryptPassword(iv, cypherText, salt)

    self.assertEqual(plainText, plainText2)

  def test_passwordEncrypt4(self):
    plainText="AAAAA\0\0\0sadrgfrg"
    salt=appObj.bcrypt.gensalt()

    (iv, cypherText) = encryptPassword(plainText, salt)
    plainText2 = decryptPassword(iv, cypherText, salt)

    self.assertEqual(plainText, plainText2)
