from flask_restplus import fields


def getErrorModel(appObj):
  return appObj.flastRestPlusAPIObject.model('Error', {
    'ErrorNumber':  fields.Integer(default='DEFAULT', description='Error Number (Same as HTTP response code)'),
    'Message':  fields.String(default='DEFAULT', description='Error Message')
  })  
  
def getErrorReturn(number, message):
  return {'Error': number, 'Message': message}, number
