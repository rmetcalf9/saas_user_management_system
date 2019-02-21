# File to keep all the shared models that are required
#  for both the login and admin API's
from flask_restplus import fields

def getTenantModel(appObj):
  AuthProviderModel = appObj.flastRestPlusAPIObject.model('AuthProviderInfo', {
    'guid': fields.String(default='abc', description='Unique identifier of AuthProvider'),
    'Type': fields.String(default='internal', description='Authorization provider type'),
    'AllowUserCreation': fields.Boolean(default=False,description='Allow unknown logins to create new users. (Must be set to true at this level AND Tenant level to work)'),   
    'MenuText': fields.String(default='click here', description='Item text used in login method selection screen'),
    'IconLink': fields.String(default=None, description='Image link used in login method selection screen'),
    'ConfigJSON': fields.String(default=None, description='Extra configuration required per auth type'),
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
    'ObjectVersion': fields.String(default='DEFAULT', description='Obect version required to sucessfully preform updates')
  })
