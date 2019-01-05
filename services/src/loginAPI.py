#This is the publiclly availiable loginAPI

from flask import request
from flask_restplus import Resource, fields
import datetime
import pytz
from baseapp_for_restapi_backend_with_swagger import readFromEnviroment

def getAPIModel(appObj):
  serverInfoServerModel = appObj.flastRestPlusAPIObject.model('mainAPI', {
    'Version': fields.String(default='DEFAULT', description='Version of container running on server')
  })
  return appObj.flastRestPlusAPIObject.model('ServerInfo', {
    'Server': fields.Nested(serverInfoServerModel)
  })  

  
def registerAPI(appObj):

  nsServerinfo = appObj.flastRestPlusAPIObject.namespace('serverinfo', description='General Server Operations')
  @nsServerinfo.route('/')
  class servceInfo(Resource):
  
    '''General Server Operations'''
    @nsServerinfo.doc('getserverinfo')
    @nsServerinfo.marshal_with(getAPIModel(appObj))
    @nsServerinfo.response(200, 'Success')
    def get(self):
     '''Get general information about the server'''
     curDatetime = datetime.datetime.now(pytz.utc)
     return {}
    
