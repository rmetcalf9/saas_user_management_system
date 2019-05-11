# File to keep all the shared models that are required
#  for both the login and admin API's
from flask_restplus import fields

def getTenantModel(appObj):
  AuthProviderModel = appObj.flastRestPlusAPIObject.model('AuthProviderInfo', {
    'guid': fields.String(default='abc', description='Unique identifier of AuthProvider'),
    'Type': fields.String(default='internal', description='Authorization provider type'),
    'AllowUserCreation': fields.Boolean(default=False,description='Allow unknown logins to create new users. (Must be set to true at this level AND Tenant level to work)'),   
    'AllowLink': fields.Boolean(default=False,description='Allow user to add this as a secondary auth method'),   
    'AllowUnlink': fields.Boolean(default=False,description='Allow user to remove this auth method (As long as they have others availiable)'),   
    'UnlinkText': fields.String(default='Unlink', description='Text to show on unlink button in Security settings UI'),
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
