from flask import request
from flask_restplus import Resource, fields
import datetime
import pytz
from baseapp_for_restapi_backend_with_swagger import readFromEnviroment

def getServerInfoModel(appObj):
  serverInfoServerModel = appObj.flastRestPlusAPIObject.model('mainAPI', {
    'Version': fields.String(default='DEFAULT', description='Version of container running on server')
  })
  return appObj.flastRestPlusAPIObject.model('ServerInfo', {
    'Server': fields.Nested(serverInfoServerModel)
  })  

def registerServerInfoAPIFn(appObj, namespacePassed):

  @namespacePassed.route('/serverinfo')
  class servceInfo(Resource):
  
    '''General Server Operations'''
    @namespacePassed.doc('getserverinfo')
    @namespacePassed.marshal_with(getServerInfoModel(appObj))
    @namespacePassed.response(200, 'Success')
    def get(self):
     '''Get general information about the server'''
     curDatetime = datetime.datetime.now(pytz.utc)
     return { 
      'Server': { 'Version': appObj.version },
     }
    
