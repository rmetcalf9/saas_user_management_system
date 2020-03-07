# File to keep all the shared models that are required
#  for both the login and admin API's
from flask_restplus import fields
from object_store_abstraction import RepositoryObjBaseClass

def getTenantModel(appObj):
  AuthProviderModel = appObj.flastRestPlusAPIObject.model('AuthProviderInfo', {
    'guid': fields.String(default='abc', description='Unique identifier of AuthProvider'),
    'Type': fields.String(default='internal', description='Authorization provider type'),
    'AllowUserCreation': fields.Boolean(default=False,description='Allow unknown logins to create new users. (Must be set to true at this level AND Tenant level to work)'),   
    'AllowLink': fields.Boolean(default=False,description='Allow user to add this as a secondary auth method'),
    'AllowUnlink': fields.Boolean(default=False,description='Allow user to remove this auth method (As long as they have others availiable)'),
    'LinkText': fields.String(default='Link', description='Text to show on link button in Security settings UI'),
    'MenuText': fields.String(default='click here', description='Item text used in login method selection screen'),
    'IconLink': fields.String(default=None, description='Image link used in login method selection screen'),
    'ConfigJSON': fields.String(default=None, description='Extra configuration required per auth type'),
    'StaticlyLoadedData': fields.Raw(description='Other data loaded for this auth type'),
    'saltForPasswordHashing': fields.String(default=None, description='Salt that can be used for password hashing (Depends on auth method)')
  })
  return appObj.flastRestPlusAPIObject.model('TenantInfo', {
    'Name': fields.String(default='DEFAULT', description='Name and unique identifier of tenant'),
    'Description': fields.String(default='DEFAULT', description='Description of tenant'),
    'AllowUserCreation': fields.Boolean(default=False,description='Allow unknown logins to create new users. (Must be set to true at this level AND AuthPRovider level to work)'),
    'AuthProviders': fields.List(fields.Nested(AuthProviderModel)),
    'JWTCollectionAllowedOriginList': fields.List(fields.String(default='DEFAULT', description='Allowed origin to retrieve JWT tokens from')),
    'ObjectVersion': fields.String(default='DEFAULT', description='Obect version required to sucessfully preform updates')
  })

#register user responds with this model
def getUserModel(appObj):
  TenantRoleModel = appObj.flastRestPlusAPIObject.model('TenantRoleModel', {
    'TenantName': fields.String(default='DEFAULT', description='Tenant Name'),
    'ThisTenantRoles': fields.List(fields.String(description='Role the user has been assigned for this tenant')),
  })

  return appObj.flastRestPlusAPIObject.model('UserInfo', {
    'UserID': fields.String(default='DEFAULT', description='Unique identifier of User'),
    'known_as': fields.String(description='User friendly identifier for username'),
    'TenantRoles': fields.List(fields.Nested(TenantRoleModel)),
    'other_data': fields.Raw(description='Any other data supplied by auth provider', required=True),
    'associatedPersonGUIDs': fields.List(fields.String(description='GUIDs of associated user accounts')),
    'ObjectVersion': fields.String(default='DEFAULT', description='Obect version required to sucessfully preform updates'),
    'creationDateTime': fields.DateTime(dt_format=u'iso8601', description='Datetime user was created'),
    'lastUpdateDateTime': fields.DateTime(dt_format=u'iso8601', description='Datetime user was lastupdated')
  })

def getPersonModel(appObj):
  personAuthsModel = appObj.flastRestPlusAPIObject.model('PersonAuthsInfo', {
    'AuthUserKey': fields.String(default='DEFAULT', description='Unique identifier of Auth'),
    'known_as': fields.String(default='DEFAULT', description='User friendly identifier for Auth'),
    'AuthProviderType': fields.String(default='DEFAULT', description='Type of AuthProvider for this Auth'),
    'AuthProviderGUID': fields.String(default='DEFAULT', description='Unique identifier of AuthProvider for this Auth'),
    'tenantName': fields.String(default='DEFAULT', description='Name of the Tenant this auth is associated with')
  })
  return appObj.flastRestPlusAPIObject.model('PersonInfo', {
    'guid': fields.String(default='DEFAULT', description='Unique identifier of Person'),
    'associatedUsers': fields.List(fields.Nested(getUserModel(appObj))),
    'personAuths': fields.List(fields.Nested(personAuthsModel)),
    'ObjectVersion': fields.String(default='DEFAULT', description='Obect version required to sucessfully preform updates'),
    'creationDateTime': fields.DateTime(dt_format=u'iso8601', description='Datetime user was created'),
    'lastUpdateDateTime': fields.DateTime(dt_format=u'iso8601', description='Datetime user was lastupdated')
  })

#Used with both login and link
def getLoginPostDataModel(appObj):
  return appObj.flastRestPlusAPIObject.model('LoginPostData', {
  'authProviderGUID': fields.String(default='DEFAULT', description='Unique identifier of AuthProvider to log in with', required=True),
  'credentialJSON': fields.Raw(description='JSON structure required depends on the Auth Provider type', required=True),
  'UserID': fields.String(default='DEFAULT', description='If a person has access to mutiple Users then they specify the UserID of the one they need to login with')
  })

#Used with both login response and refresh response and link response
def getLoginResponseModel(appObj):
  jwtTokenModel = appObj.flastRestPlusAPIObject.model('JWTTokenInfo', {
    'JWTToken': fields.String(description='JWTToken'),
    'TokenExpiry': fields.DateTime(dt_format=u'iso8601', description='Time the JWTToken can be used until')
  })
  refreshTokenModel = appObj.flastRestPlusAPIObject.model('RefreshTokenInfo', {
    'token': fields.String(description='Refresh Token'),
    'TokenExpiry': fields.DateTime(dt_format=u'iso8601', description='Time the Refresh token can be used until')
  })
  return appObj.flastRestPlusAPIObject.model('LoginResponseData', {
    'possibleUsers': fields.List(fields.Nested(getUserModel(appObj))),
    'jwtData': fields.Nested(jwtTokenModel, skip_none=True),
    'refresh': fields.Nested(refreshTokenModel, skip_none=True),
    'userGuid': fields.String(description='Unique identifier of user to be used by the application'),
    'authedPersonGuid': fields.String(description='Unique identifier of person for use with Auth APIs'),
    'ThisTenantRoles': fields.List(fields.String(description='Role the user has been assigned for this tenant')),
    'known_as': fields.String(description='User friendly identifier for username'),
    'other_data': fields.Raw(description='Any other data supplied by auth provider', required=True),
    'currentlyUsedAuthProviderGuid': fields.String(description='GUID of auth provider used to login with'),
    'currentlyUsedAuthKey': fields.String(description='Key of auth used to login with')
  })

def getCreateTicketTypeModel_welcomeMessage(appObj):
  return appObj.flastRestPlusAPIObject.model('CreateTicketType_welcomeMessage', {
    'agreementRequired': fields.Boolean(default=False, description='Prompt user to agree'),
    'title': fields.String(default='DEFAULT', description='Title'),
    'body': fields.String(default='DEFAULT', description='Body'),
    'okButtonText': fields.String(default='DEFAULT', description='Ok button text')
  })

def getCreateTicketTypeModel(appObj):
  return appObj.flastRestPlusAPIObject.model('CreateTicketType', {
    'tenantName': fields.String(default='DEFAULT', description='Tenant name for this ticket type'),
    'ticketTypeName': fields.String(default='DEFAULT', description='Name displayed on admin screent'),
    'description': fields.String(default='DEFAULT', description='Description of ticket type'),
    'enabled': fields.Boolean(default=False,description='Can the ticket type currently be used'),
    'welcomeMessage': fields.Nested(getCreateTicketTypeModel_welcomeMessage(appObj), skip_none=True),
    'allowUserCreation': fields.Boolean(default=False,description='Allow unknown logins to create new users when using this ticket.'),
    'issueDuration': fields.Integer(default='DEFAULT', description='Hours to issue ticket for on creation'),
    'roles': fields.List(fields.String(default='DEFAULT', description='List of roles this tickert type will assign')),
    'postUseURL': fields.String(default='DEFAULT', description='URL to send user to after ticket is used'),
    'postInvalidURL': fields.String(default='DEFAULT', description='URL to send user to after invalid or request validaiton')
  })

def getTicketTypeModel(appObj):
  return appObj.flastRestPlusAPIObject.model('TicketType', {
    'id': fields.String(default='DEFAULT', description='Unique identifier of User from login system'),
    'tenantName': fields.String(default='DEFAULT', description='Tenant name for this ticket type'),
    'ticketTypeName': fields.String(default='DEFAULT', description='Name displayed on admin screent'),
    'description': fields.String(default='DEFAULT', description='Description of ticket type'),
    'enabled': fields.Boolean(default=False,description='Can the ticket type currently be used'),
    'welcomeMessage': fields.Nested(getCreateTicketTypeModel_welcomeMessage(appObj), skip_none=True),
    'allowUserCreation': fields.Boolean(default=False,description='Allow unknown logins to create new users when using this ticket.'),
    'issueDuration': fields.Integer(default=None, description='Hours to issue ticket for on creation'),
    'roles': fields.List(fields.String(default='DEFAULT', description='List of roles this tickert type will assign')),
    'postUseURL': fields.String(default='DEFAULT', description='URL to send user to after ticket is used'),
    'postInvalidURL': fields.String(default='DEFAULT', description='URL to send user to after invalid or request validaiton'),
    RepositoryObjBaseClass.getMetadataElementKey(): fields.Nested(RepositoryObjBaseClass.getMetadataModel(appObj, flaskrestplusfields=fields))
  })

def responseModel(appObj):
  return appObj.flastRestPlusAPIObject.model('ResponseModel', {
    'response': fields.String(default='FAIL', description='OK if the operation succeeded'),
    'message': fields.String(default='None', description='Error message')
  })

def getTicketTypeCreateBatchProcessModel(appObj):
  return appObj.flastRestPlusAPIObject.model('TicketTypeCreateBatchProcessModel', {
    'foreignKeyDupAction': fields.String(default='FAIL', description='Should be ReissueAll or Skip'),
    'foreignKeyList': fields.List(fields.String(default='FAIL', description='Foreign key'))
  })

def getTicketTypeCreateBatchProcessResponseModel(appObj):
  statsModel = appObj.flastRestPlusAPIObject.model('TicketTypeCreateBatchProcessResponseStatsModel', {
    'issued': fields.Integer(default=None, description='Number of tickets issued'),
    'reissued': fields.Integer(default=None, description='Number of tickets reissued'),
    'skipped': fields.Integer(default=None, description='Number of tickets skipped')
  })
  resultModel = appObj.flastRestPlusAPIObject.model('TicketTypeCreateBatchProcessResponseResultModel', {
    'ticketGUID': fields.String(default='DEFAULT', description='GUID for this ticket'),
    'foreignKey': fields.String(default='DEFAULT', description='foreignKey for this ticket'),
  })

  return appObj.flastRestPlusAPIObject.model('TicketTypeCreateBatchProcessResponseModel', {
    'results': fields.List(fields.Nested(resultModel)),
    'stats': fields.Nested(statsModel)
  })

def getTicketModel(appObj):
  return appObj.flastRestPlusAPIObject.model('TicketType', {
    'id': fields.String(default='DEFAULT', description='Unique identifier of Ticket - used in URL'),
    'typeGUID': fields.String(default='DEFAULT', description='Unique identifier of Ticket - used in URL'),
    'expiry': fields.DateTime(dt_format=u'iso8601', description='Datetime ticket will expire'),
    'foreignKey': fields.String(default='DEFAULT', description='Unique identifier of Ticket - used in URL'),
    'usedDate': fields.DateTime(dt_format=u'iso8601', description='Datetime ticket was used or none if it wasn\'t'),
    'useWithUserID': fields.String(default=None, description='Unique identifier of Ticket - used in URL'),
    'reissueRequestedDate': fields.DateTime(dt_format=u'iso8601', description='Datetime ticket was reissueRequestedDate'),
    'reissuedTicketID': fields.String(default=None, description='Unique identifier of Ticket - used in URL'),
    'disabled': fields.Boolean(default=False,description='Has this ticket been disabled'),
    RepositoryObjBaseClass.getMetadataElementKey(): fields.Nested(RepositoryObjBaseClass.getMetadataModel(appObj, flaskrestplusfields=fields))
  })

def getTicketWithCaculatedFieldsModel(appObj):
  return appObj.flastRestPlusAPIObject.model('TicketTypeWithCaculated', {
    'id': fields.String(default='DEFAULT', description='Unique identifier of Ticket - used in URL'),
    'typeGUID': fields.String(default='DEFAULT', description='Unique identifier of Ticket - used in URL'),
    'expiry': fields.DateTime(dt_format=u'iso8601', description='Datetime ticket will expire'),
    'foreignKey': fields.String(default='DEFAULT', description='Unique identifier of Ticket - used in URL'),
    'usedDate': fields.DateTime(dt_format=u'iso8601', description='Datetime ticket was used or none if it wasn\'t'),
    'useWithUserID': fields.String(default=None, description='Unique identifier of Ticket - used in URL'),
    'reissueRequestedDate': fields.DateTime(dt_format=u'iso8601', description='Datetime ticket was reissueRequestedDate'),
    'reissuedTicketID': fields.String(default=None, description='Unique identifier of Ticket - used in URL'),
    'disabled': fields.Boolean(default=False,description='Has this ticket been disabled'),
    RepositoryObjBaseClass.getMetadataElementKey(): fields.Nested(RepositoryObjBaseClass.getMetadataModel(appObj, flaskrestplusfields=fields)),
    # Extra below
    'usableState': fields.String(default='DEFAULT', description='Usable state of this ticket')
  })


