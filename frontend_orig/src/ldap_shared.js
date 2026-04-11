import CryptoJS from 'crypto-js'

function get32BytesFromSalt (salt) {
  var retBytes = ''
  for (let i = 0; i < 32; i++) {
    retBytes += salt[i % salt.length]
  }
  // idx = x % len(salt)
  // retBytes = retBytes + salt[idx:(idx+1)]
  return retBytes
}
function getCredentialDict (authProvSaltBase46, username, password) {
  // console.log('saltForPasswordHashing:', this.authProvData.saltForPasswordHashing)
  // console.log('atob:', atob(this.authProvData.saltForPasswordHashing))

  // var authProvSaltBase46 = btoa('tyttt')
  var passphrase = get32BytesFromSalt(atob(authProvSaltBase46))
  var plainText = password
  var IV = CryptoJS.lib.WordArray.random(16)
  // var IV = CryptoJS.enc.Base64.parse('/0iT3mjRzasxO1pTQggZCg==')
  var passphraseWordArray = CryptoJS.enc.Base64.parse(btoa(passphrase))

  var encOptions = {
    iv: IV,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  }
  var encrypted = CryptoJS.AES.encrypt(plainText, passphraseWordArray, encOptions)

  // console.log("Result IV = ", IV.toString(CryptoJS.enc.Base64))
  // console.log("Result cipherText = ", encrypted.ciphertext.toString(CryptoJS.enc.Base64))

  return {
    username: username,
    password: encrypted.ciphertext.toString(CryptoJS.enc.Base64),
    iv: IV.toString(CryptoJS.enc.Base64)
  }
}

export default {
  getCredentialDict: getCredentialDict
}
