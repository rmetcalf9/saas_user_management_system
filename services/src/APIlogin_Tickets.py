from flask import request
from flask_restplus import Resource, fields
import apiSharedModels
import constants
from werkzeug.exceptions import BadRequest

def getLoginAPITicketModel(appObj):
  return appObj.flastRestPlusAPIObject.model('LoginAPITicketModel', {
    'ticketType': fields.Nested(apiSharedModels.getTicketTypeModel(appObj)),
    'isUsable': fields.String(default='INVALID', description='Is the ticket usable (INVALID, EXPIRED or USABLE)'),
    'expiry': fields.DateTime(dt_format=u'iso8601', description='Datetime ticket will expire')
  }
)

def registerAPI(appObj, nsLogin):

  @nsLogin.route('/<string:tenant>/tickets/<string:ticketGUID>')
  class servceInfo(Resource):

    '''Get Login Ticket'''
    @nsLogin.doc('get login ticket')
    @nsLogin.marshal_with(getLoginAPITicketModel(appObj))
    @nsLogin.response(200, 'Success', model=getLoginAPITicketModel(appObj))
    @nsLogin.response(400, 'Bad Request')
    def get(self, tenant, ticketGUID):
     '''Get ticket for login api to use'''
     def dbfn(storeConnection):
       return appObj.TicketManager.getTicketAndTypeDict(
         tenantName=tenant,
         ticketGUID=ticketGUID,
         storeConnection=storeConnection
        )
     return appObj.objectStore.executeInsideConnectionContext(dbfn)

  @nsLogin.route('/<string:tenant>/tickets/<string:ticketGUID>/requestreissue')
  class servceInfo(Resource):

    '''Request expired ticket reissue'''
    @nsLogin.doc('get login ticket')
    @nsLogin.marshal_with(getLoginAPITicketModel(appObj))
    @nsLogin.response(200, 'Success', model=getLoginAPITicketModel(appObj))
    @nsLogin.response(400, 'Bad Request')
    def get(self, tenant, ticketGUID):
     '''Get ticket for login api to use'''
     def dbfn(storeConnection):
       try:
         return appObj.TicketManager.userRequestTicketReissue(
           tenantName=tenant,
           ticketGUID=ticketGUID,
           storeConnection=storeConnection,
           appObj=appObj
          )
       except constants.customExceptionClass as err:
         if (err.id == 'notpostorenew'):
           raise BadRequest(err.text)
         raise err

     return appObj.objectStore.executeInsideTransaction(dbfn)
