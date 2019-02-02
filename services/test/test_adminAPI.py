from TestHelperSuperClass import testHelperAPIClient, env
from constants import masterTenantName, jwtHeaderName, jwtCookieName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole
import json
import copy
from tenants import AddAuth, CreatePerson, GetTenant
from appObj import appObj
from authProviders import authProviderFactory
from authProviders_base import getAuthRecord

tenantWithNoAuthProviders = {
  "Name": "NewlyCreatedTenantNoAuth",
  "Description": "Tenant with no auth providers",
  "AllowUserCreation": False,
  "AuthProviders": []
}
sampleInternalAuthProv001_CREATE = {
  "guid": None,
  "Type": "internal",
  "AllowUserCreation": False,
  "MenuText": "Default Menu Text",
  "IconLink": "string",
  "ConfigJSON": "{\"userSufix\": \"@internalDataStore\"}",
  "saltForPasswordHashing": None
} 


class test_api(testHelperAPIClient):
  def getNormalJWTToken(self):
    return self.makeJWTTokenWithMasterTenantRoles([DefaultHasAccountRole, masterTenantDefaultSystemAdminRole])
  
  
  def makeJWTTokenWithMasterTenantRoles(self, roles):
    UserID = 'abc123'
    userDict = {
      "UserID": UserID,
      "TenantRoles": { masterTenantName: roles}
    }
    return self.generateJWTToken(userDict)


class test_securityTests(test_api):
  def test_noTokenSupplied(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants')
    self.assertEqual(result.status_code, 401)
  
  def test_jwtWithNoRoles(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([])
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants', headers={ jwtHeaderName: jwtToken})
    self.assertEqual(result.status_code, 401)

  def test_jwtWithOnlyAccountRole(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([DefaultHasAccountRole])
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants', headers={ jwtHeaderName: jwtToken})
    self.assertEqual(result.status_code, 401)

  def test_jwtWithOnlyAdminRole(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([masterTenantDefaultSystemAdminRole])
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants', headers={ jwtHeaderName: jwtToken})
    self.assertEqual(result.status_code, 401)

  def test_jwtWorksAsCookie(self): 
    self.testClient.set_cookie('localhost', jwtCookieName, self.getNormalJWTToken())
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants')
    self.assertEqual(result.status_code, 200)

  def test_wrongTenantFails(self): 
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + 'xx/tenants', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 401)

  def test_jwtWorksAsHeader(self): 
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

class test_funcitonal(test_api):
  def getTenantDICT(self, tenantName):
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    
    for curTenant in resultJSON['result']:
      if curTenant['Name'] == tenantName:
        return curTenant
    return None
  
  def createTenantForTesting(self, tenantDICT):
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201)
    resultJSON = json.loads(result.get_data(as_text=True))
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithNoAuthProviders, [], msg='JSON of created Tenant is not the same')
    
  def createTenantForTestingWithMutipleAuthProviders(self, tenantDICT, authProvDictList):
    self.createTenantForTesting(tenantDICT)
    tenantWithSingleAuthProvider = copy.deepcopy(tenantDICT)
    a = []
    for b in authProvDictList:
      a.append(copy.deepcopy(b))
    tenantWithSingleAuthProvider['AuthProviders'] = a

    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithSingleAuthProvider['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithSingleAuthProvider), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)
    return json.loads(result.get_data(as_text=True))
    
  def test_getDefaultSingleTenant(self): 
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqual(resultJSON['pagination'], {"offset": 0, "pagesize": 100, "total": 1})
    self.assertEqual(len(resultJSON["result"]),1,msg="Only 1 result should be returned")
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["result"][0], {"AllowUserCreation": False, "AuthProviders": "ignored", "Description": "Master Tenant for User Management System", "Name": "usersystem"}, ['AuthProviders'])
    self.assertEqual(len(resultJSON["result"][0]['AuthProviders']),1,msg="Wrong number of auth providers")
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["result"][0]['AuthProviders'][0], {"AllowUserCreation": False, "ConfigJSON": "{\"userSufix\": \"@internalDataStore\"}", "IconLink": None, "MenuText": "Website account login", "Type": "internal"}, ['guid', "saltForPasswordHashing"])

  def test_createTenant(self):
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithNoAuthProviders), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201)
    resultJSON = json.loads(result.get_data(as_text=True))
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithNoAuthProviders, [], msg='JSON of created Tenant is not the same')

  def test_createTenantInvalidJSON(self):
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps({}), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400)

  def test_createTenantWithDuplicateNameFails(self):
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithNoAuthProviders), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201)
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithNoAuthProviders), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400, msg='Shouldn\'t be able to create a two tenants with the same name')

  def test_updateTenantDescription(self):
    self.createTenantForTesting(tenantWithNoAuthProviders)
    
    tenantWithChangedDescription = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithChangedDescription['Description'] = "Changed Description"

    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithChangedDescription['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithChangedDescription), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithChangedDescription, [], msg='JSON of updated Tenant is not the same as what it was set to')
    self.assertJSONStringsEqualWithIgnoredKeys(self.getTenantDICT(tenantWithChangedDescription['Name']), tenantWithChangedDescription, [], msg='Tenant wasnt changed in get result')
    
  def test_CanNotUpdateTenantName(self):
    self.createTenantForTesting(tenantWithNoAuthProviders)
    
    tenantWithChangedDescription = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithChangedDescription['Name'] = "SomeOtherName"

    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithNoAuthProviders['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithChangedDescription), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400)
  
  def test_UpdateAllowUserCreation(self):
    self.createTenantForTesting(tenantWithNoAuthProviders)
    
    tenantWithChangedDescription = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithChangedDescription['AllowUserCreation'] = True

    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithChangedDescription['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithChangedDescription), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithChangedDescription, [], msg='JSON of updated Tenant is not the same as what it was set to')
    self.assertJSONStringsEqualWithIgnoredKeys(self.getTenantDICT(tenantWithChangedDescription['Name']), tenantWithChangedDescription, [], msg='Tenant wasnt changed in get result')


  def test_addAuthProvider(self):
    self.createTenantForTesting(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider['AuthProviders'] = [copy.deepcopy(sampleInternalAuthProv001_CREATE)]

    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithSingleAuthProvider['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithSingleAuthProvider), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithSingleAuthProvider, ['AuthProviders'], msg='JSON of updated Tenant is not the same as what it was set to')
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['AuthProviders'][0], tenantWithSingleAuthProvider['AuthProviders'][0], ['saltForPasswordHashing','guid'], msg='JSON of updated authprov is not the same as what it was set to')
    
    #Copy assigned guid and salt for get test
    tenantWithSingleAuthProvider['AuthProviders'][0]['guid'] = resultJSON['AuthProviders'][0]['guid']
    tenantWithSingleAuthProvider['AuthProviders'][0]['saltForPasswordHashing'] = resultJSON['AuthProviders'][0]['saltForPasswordHashing']
    
    self.assertJSONStringsEqualWithIgnoredKeys(self.getTenantDICT(tenantWithSingleAuthProvider['Name']), tenantWithSingleAuthProvider, [], msg='Tenant wasnt changed in get result')

  def test_addAuthProviderSupplyingSaltFails(self):
    self.createTenantForTesting(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider['AuthProviders'] = [copy.deepcopy(sampleInternalAuthProv001_CREATE)]
    tenantWithSingleAuthProvider['AuthProviders'][0]['saltForPasswordHashing'] = '12345'

    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithSingleAuthProvider['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithSingleAuthProvider), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400)
  
  #If the guid is supplied then an update is assumed but should error if not present
  def test_addAuthProviderNotThereFails(self):
    self.createTenantForTesting(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider['AuthProviders'] = [copy.deepcopy(sampleInternalAuthProv001_CREATE)]
    tenantWithSingleAuthProvider['AuthProviders'][0]['guid'] = '12345'

    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithSingleAuthProvider['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithSingleAuthProvider), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400)

  def test_addTwoAuthProvidersTogether(self):
    self.createTenantForTesting(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider['AuthProviders'] = [copy.deepcopy(sampleInternalAuthProv001_CREATE), copy.deepcopy(sampleInternalAuthProv001_CREATE)]

    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithSingleAuthProvider['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithSingleAuthProvider), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithSingleAuthProvider, ['AuthProviders'], msg='JSON of updated Tenant is not the same as what it was set to')
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['AuthProviders'][0], tenantWithSingleAuthProvider['AuthProviders'][0], ['saltForPasswordHashing','guid'], msg='JSON of updated authprov is not the same as what it was set to')
    
    #Copy assigned guid and salt for get test
    for c in [0, 1]:
      tenantWithSingleAuthProvider['AuthProviders'][c]['guid'] = resultJSON['AuthProviders'][c]['guid']
      tenantWithSingleAuthProvider['AuthProviders'][c]['saltForPasswordHashing'] = resultJSON['AuthProviders'][c]['saltForPasswordHashing']
    
    self.assertJSONStringsEqualWithIgnoredKeys(self.getTenantDICT(tenantWithSingleAuthProvider['Name']), tenantWithSingleAuthProvider, [], msg='Tenant wasnt changed in get result')
  
  def test_addSecondAuthProvider(self):
    resultJSON = self.createTenantForTestingWithMutipleAuthProviders(tenantWithNoAuthProviders, [sampleInternalAuthProv001_CREATE])

    #Now add secondAuth provider as an update
    existingAuthProv = resultJSON['AuthProviders'][0]

    tenantWithSingleAuthProvider = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider['AuthProviders'] = [existingAuthProv, copy.deepcopy(sampleInternalAuthProv001_CREATE)]
    
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithSingleAuthProvider['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithSingleAuthProvider), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithSingleAuthProvider, ['AuthProviders'], msg='JSON of updated Tenant is not the same as what it was set to')
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['AuthProviders'][0], tenantWithSingleAuthProvider['AuthProviders'][0], ['saltForPasswordHashing','guid'], msg='JSON of updated authprov is not the same as what it was set to')
    
    #Copy assigned guid and salt for get test
    for c in [0, 1]:
      tenantWithSingleAuthProvider['AuthProviders'][c]['guid'] = resultJSON['AuthProviders'][c]['guid']
      tenantWithSingleAuthProvider['AuthProviders'][c]['saltForPasswordHashing'] = resultJSON['AuthProviders'][c]['saltForPasswordHashing']
    
    self.assertJSONStringsEqualWithIgnoredKeys(self.getTenantDICT(tenantWithSingleAuthProvider['Name']), tenantWithSingleAuthProvider, [], msg='Tenant wasnt changed in get result')

  def test_updateAuthProviderSaltIsNoneFails(self):
    resultJSON = self.createTenantForTestingWithMutipleAuthProviders(tenantWithNoAuthProviders, [sampleInternalAuthProv001_CREATE])
    existingAuthProv = resultJSON['AuthProviders'][0]

    existingAuthProvWithSaltAsNone = copy.deepcopy(existingAuthProv)
    existingAuthProvWithSaltAsNone['saltForPasswordHashing'] = None
    
    tenantDICT = copy.deepcopy(tenantWithNoAuthProviders)
    tenantDICT['AuthProviders'] = [existingAuthProvWithSaltAsNone]
    
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantDICT['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400)

  def test_updateAuthProviderDifferentSaltFails(self):
    resultJSON = self.createTenantForTestingWithMutipleAuthProviders(tenantWithNoAuthProviders, [sampleInternalAuthProv001_CREATE])
    existingAuthProv = resultJSON['AuthProviders'][0]

    existingAuthProvWithSaltAsNone = copy.deepcopy(existingAuthProv)
    existingAuthProvWithSaltAsNone['saltForPasswordHashing'] = 'ABC123'
    
    tenantDICT = copy.deepcopy(tenantWithNoAuthProviders)
    tenantDICT['AuthProviders'] = [existingAuthProvWithSaltAsNone]
    
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantDICT['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400)

  def test_updateAuthProviderWhenTenantHasTwoAuthProviders(self):
    resultJSON = self.createTenantForTestingWithMutipleAuthProviders(tenantWithNoAuthProviders, [sampleInternalAuthProv001_CREATE,sampleInternalAuthProv001_CREATE])
  
    newMenuTextToUse = 'Changed Menu Text'
    guidOfAuthProvToChange = resultJSON['AuthProviders'][0]['guid']
    tenantDictBeforeChange = self.getTenantDICT(tenantWithNoAuthProviders['Name'])
    expectedDictAfterChange = copy.deepcopy(tenantDictBeforeChange)
    for a in expectedDictAfterChange['AuthProviders']:
      if a['guid']==guidOfAuthProvToChange:
        a['MenuText'] = newMenuTextToUse

    changedAuthProvs = [resultJSON['AuthProviders'][0],resultJSON['AuthProviders'][1]]
    changedAuthProvs[0]['MenuText'] = newMenuTextToUse
    changedTenantDICT = copy.deepcopy(tenantWithNoAuthProviders)
    changedTenantDICT['AuthProviders'] = changedAuthProvs
    
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithNoAuthProviders['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(changedTenantDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)    
    
    changedResultJSON = self.getTenantDICT(tenantWithNoAuthProviders['Name'])
    self.assertJSONStringsEqualWithIgnoredKeys(changedResultJSON, expectedDictAfterChange, [], msg='New Tenant JSON isn\'t the expected value')
  
  def test_updateTenantDescription_TenantHasMutipleAuthProvsWhichShouldBeUnchanged(self):
    #Must make sure salts are not changed
    origTenantDict = self.createTenantForTestingWithMutipleAuthProviders(tenantWithNoAuthProviders, [sampleInternalAuthProv001_CREATE,sampleInternalAuthProv001_CREATE])
    changedTenantDict = copy.deepcopy(origTenantDict)
    changedTenantDict['Description'] = 'Changed description'
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + changedTenantDict['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(changedTenantDict), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)    

    changedResultJSON = self.getTenantDICT(tenantWithNoAuthProviders['Name'])
    self.assertJSONStringsEqualWithIgnoredKeys(changedResultJSON, changedTenantDict, [], msg='New Tenant JSON isn\'t the expected value')
  
  def test_deleteOnlyAuthProvider(self):
    origTenantDict = self.createTenantForTestingWithMutipleAuthProviders(tenantWithNoAuthProviders, [sampleInternalAuthProv001_CREATE])
    authProvGUID = origTenantDict['AuthProviders'][0]['guid']

    #Also create some auth data for the single auth
    person = CreatePerson(appObj)
    authData = AddAuth(appObj, tenantWithNoAuthProviders['Name'], authProvGUID, {
      "username": 'AA', 
      "password": b'BB'
      },
      person['guid']
    )

    #Before we delete the auth provider we must get the key it used to create the userAuth
    AuthProvider = authProviderFactory(
      sampleInternalAuthProv001_CREATE["Type"],
      json.loads(sampleInternalAuthProv001_CREATE["ConfigJSON"]),
      authProvGUID
    )
    authTypeConfigDict = {'username': 'AA'}
    authRecordKey = AuthProvider._makeKey(authTypeConfigDict)
    #Use the key the first time to make sure auth record exists
    authRecord = getAuthRecord(appObj, authRecordKey)
    #print("print Auth Record is:",authRecord)

    
    changedTenantDict = copy.deepcopy(origTenantDict)
    changedTenantDict['AuthProviders'] = []
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + changedTenantDict['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(changedTenantDict), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200) 
    
    changedResultJSON = self.getTenantDICT(tenantWithNoAuthProviders['Name'])
    self.assertJSONStringsEqualWithIgnoredKeys(changedResultJSON, changedTenantDict, [], msg='New Tenant JSON isn\'t the expected value')
    self.assertEqual(len(changedResultJSON['AuthProviders']),0,msg='Wrong number of remaining auth providers')
    
    #Check auth record has been NOT been removed
    # auth records will not be removed with the tenant as auth records
    # are independant of tenant. Any clean up will be done when the person is deleted
    authRecord2 = getAuthRecord(appObj, authRecordKey)
    self.assertJSONStringsEqualWithIgnoredKeys(authRecord, authRecord2, [], msg='Error userAuths should not have changed')
    
  def test_deleteTwoAuthProvidersTogether(self):
    origTenantDict = self.createTenantForTestingWithMutipleAuthProviders(tenantWithNoAuthProviders, [sampleInternalAuthProv001_CREATE,sampleInternalAuthProv001_CREATE])
    
    changedTenantDict = copy.deepcopy(origTenantDict)
    changedTenantDict['AuthProviders'] = []
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + changedTenantDict['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(changedTenantDict), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200) 

    changedResultJSON = self.getTenantDICT(tenantWithNoAuthProviders['Name'])
    self.assertJSONStringsEqualWithIgnoredKeys(changedResultJSON, changedTenantDict, [], msg='New Tenant JSON isn\'t the expected value')
    self.assertEqual(len(changedResultJSON['AuthProviders']),0,msg='Wrong number of remaining auth providers')

  def test_deleteOneOfThreeAuthProviders(self):
    origTenantDict = self.createTenantForTestingWithMutipleAuthProviders(tenantWithNoAuthProviders, [sampleInternalAuthProv001_CREATE,sampleInternalAuthProv001_CREATE,sampleInternalAuthProv001_CREATE])
  
    changedTenantDict = copy.deepcopy(origTenantDict)
    changedTenantDict['AuthProviders'] = [origTenantDict['AuthProviders'][0],origTenantDict['AuthProviders'][1]]
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + changedTenantDict['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(changedTenantDict), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200) 

    changedResultJSON = self.getTenantDICT(tenantWithNoAuthProviders['Name'])
    self.assertJSONStringsEqualWithIgnoredKeys(changedResultJSON, changedTenantDict, [], msg='New Tenant JSON isn\'t the expected value')
    self.assertEqual(len(changedResultJSON['AuthProviders']),2,msg='Wrong number of remaining auth providers')
  
  def test_deleteTenant(self):
    origTenantDict = self.createTenantForTestingWithMutipleAuthProviders(tenantWithNoAuthProviders, [sampleInternalAuthProv001_CREATE,sampleInternalAuthProv001_CREATE,sampleInternalAuthProv001_CREATE])
    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + origTenantDict['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}
    )
    self.assertEqual(result.status_code, 200) 
    
    changedResultJSON = self.getTenantDICT(tenantWithNoAuthProviders['Name'])
    self.assertTrue(changedResultJSON is None, msg="Deleted tenant still exists")

  def test_cantDeleteMasterTenant(self):
    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + masterTenantName, 
      headers={ jwtHeaderName: self.getNormalJWTToken()}
    )
    self.assertEqual(result.status_code, 400) 
    
    changedResultJSON = self.getTenantDICT(masterTenantName)
    self.assertTrue(changedResultJSON is not None, msg="Managed to delete Master Tenant")

  def test_deleteTenantBadName(self):
    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + "someNonExistingTenantName", 
      headers={ jwtHeaderName: self.getNormalJWTToken()}
    )
    self.assertEqual(result.status_code, 400) 

