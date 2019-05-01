
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

export default {
  passwordERRORMessage: passwordERRORMessage
}
