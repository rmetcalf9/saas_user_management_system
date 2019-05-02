
function passwordERRORMessage (passwordd, passwordd2) {
  if (/[A-Z]/.test(passwordd) !== true) {
    return 'Password must contain at least one uppercase letter'
  }
  if (/[a-z]/.test(passwordd) !== true) {
    return 'Password must contain at least one lowercase letter'
  }
  if (/\d/.test(passwordd) !== true) {
    return 'Password must contain at least one number'
  }
  if (passwordd.length < 5) {
    return 'Password must be at least 5 characters'
  }
  if (passwordd !== passwordd2) {
    return 'Passwords must match'
  }
  return 'Password'
}

function isSet (value) {
  if (value === null) {
    return false
  }
  if (typeof (value) === 'undefined') {
    return false
  }
  if (value === 'undefined') {
    return false
  }
  return true
}

export default {
  passwordERRORMessage: passwordERRORMessage,
  isSet: isSet
}
