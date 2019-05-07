from TestHelperSuperClass import testHelperAPIClient, env, tenantWithNoAuthProviders, sampleInternalAuthProv001_CREATE
from constants import masterTenantName, jwtHeaderName, jwtCookieName, DefaultHasAccountRole, masterTenantDefaultSystemAdminRole, objectVersionHeaderName
import json
import copy
from tenants import CreatePerson, GetTenant, _getAuthProvider
from appObj import appObj
from authProviders import authProviderFactory
from authProviders_base import getAuthRecord

def AddAuth(appObj, tenantName, authProviderGUID, credentialDICT, personGUID, storeConnection):
  auth = _getAuthProvider(appObj, tenantName, authProviderGUID, storeConnection).AddAuth(appObj, credentialDICT, personGUID, storeConnection)
  return auth


class test_api(testHelperAPIClient):
  def createPersonAndReturnDICT(self):
    newPersonDICT = {
    }
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/persons', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(newPersonDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201, msg="Create person failed - " + result.get_data(as_text=True))
    resultJSON = json.loads(result.get_data(as_text=True))
    
    expectedResult = {
      "ObjectVersion": "1",
      "guid": "IGN",
      "associatedUsers": [],
      "personAuths": []
    }
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, expectedResult, ["guid", "creationDateTime", "lastUpdateDateTime","associatedUsers"], msg='JSON of created Person is not what was expected')
    self.assertTrue("guid" in resultJSON, msg="Missing GUID")
    return resultJSON


class test_securityTests(test_api):
  def test_noTokenSupplied(self):
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants')
    self.assertEqual(result.status_code, 401, result.get_data(as_text=True))
  
  def test_jwtWithNoRoles(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([])
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants', headers={ jwtHeaderName: jwtToken})
    self.assertEqual(result.status_code, 403, result.get_data(as_text=True))

  def test_jwtWithOnlyAccountRole(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([DefaultHasAccountRole])
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants', headers={ jwtHeaderName: jwtToken})
    self.assertEqual(result.status_code, 403, result.get_data(as_text=True)) #Should return Forbidden

  def test_jwtWithOnlyAdminRole(self): 
    jwtToken = self.makeJWTTokenWithMasterTenantRoles([masterTenantDefaultSystemAdminRole])
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants', headers={ jwtHeaderName: jwtToken})
    self.assertEqual(result.status_code, 403, msg="expected Forbidden but got something else - " + result.get_data(as_text=True))

  def test_jwtWorksAsCookie(self): 
    self.testClient.set_cookie('localhost', jwtCookieName, self.getNormalJWTToken())
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants')
    self.assertEqual(result.status_code, 200)

  def test_wrongTenantFails(self): 
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + 'xx/tenants', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 401, result.get_data(as_text=True))

  def test_jwtWorksAsHeader(self): 
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

class test_funcitonal(test_api):
   
  def test_getDefaultSingleTenant(self): 
    result = self.testClient.get(self.adminAPIPrefix + '/' + masterTenantName + '/tenants', headers={ jwtHeaderName: self.getNormalJWTToken()})
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqual(resultJSON['pagination'], {"offset": 0, "pagesize": 100, "total": 1})
    self.assertEqual(len(resultJSON["result"]),1,msg="Only 1 result should be returned")
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["result"][0], {"AllowUserCreation": False, "AuthProviders": "ignored", "Description": "Master Tenant for User Management System", "Name": "usersystem"}, ['AuthProviders',"ObjectVersion"])
    self.assertEqual(resultJSON["result"][0]["ObjectVersion"],"2")

    self.assertEqual(len(resultJSON["result"][0]['AuthProviders']),1,msg="Wrong number of auth providers")
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON["result"][0]['AuthProviders'][0], {"AllowUserCreation": False, "ConfigJSON": "{\"userSufix\": \"@internalDataStore\"}", "StaticlyLoadedData": {}, "IconLink": None, "MenuText": "Website account login", "Type": "internal"}, ['guid', "saltForPasswordHashing"])

  def test_createTenant(self):
    result = self.testClient.post(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithNoAuthProviders), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 201)
    resultJSON = json.loads(result.get_data(as_text=True))
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithNoAuthProviders, ["ObjectVersion"], msg='JSON of created Tenant is not the same')
    self.assertEqual(resultJSON["ObjectVersion"],"1")

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
    tenantJSON = self.createTenantForTesting(tenantWithNoAuthProviders)
    
    tenantWithChangedDescription = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithChangedDescription['Description'] = "Changed Description"
    tenantWithChangedDescription['ObjectVersion'] = tenantJSON['ObjectVersion']

    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithChangedDescription['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithChangedDescription), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithChangedDescription, ["ObjectVersion"], msg='JSON of updated Tenant is not the same as what it was set to')
    self.assertEqual(resultJSON["ObjectVersion"],"2")
    
    self.assertJSONStringsEqualWithIgnoredKeys(self.getTenantDICT(tenantWithChangedDescription['Name']), tenantWithChangedDescription, ["ObjectVersion"], msg='Tenant wasnt changed in get result')
    self.assertEqual(resultJSON["ObjectVersion"],"2")
    
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
    tenantDICT = self.createTenantForTesting(tenantWithNoAuthProviders)
    
    tenantWithChangedDescription = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithChangedDescription['AllowUserCreation'] = True
    tenantWithChangedDescription['ObjectVersion'] = tenantDICT['ObjectVersion']

    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithChangedDescription['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithChangedDescription), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithChangedDescription, ["ObjectVersion"], msg='JSON of updated Tenant is not the same as what it was set to')
    self.assertEqual(resultJSON["ObjectVersion"],"2")    

    self.assertJSONStringsEqualWithIgnoredKeys(self.getTenantDICT(tenantWithChangedDescription['Name']), tenantWithChangedDescription, ["ObjectVersion"], msg='Tenant wasnt changed in get result')


  def test_addAuthProvider(self):
    tenantDICT = self.createTenantForTesting(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider['AuthProviders'] = [copy.deepcopy(sampleInternalAuthProv001_CREATE)]
    tenantWithSingleAuthProvider['ObjectVersion'] = tenantDICT['ObjectVersion']

    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithSingleAuthProvider['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithSingleAuthProvider), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithSingleAuthProvider, ['AuthProviders',"ObjectVersion"], msg='JSON of updated Tenant is not the same as what it was set to')
    self.assertEqual(resultJSON["ObjectVersion"],"2")    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['AuthProviders'][0], tenantWithSingleAuthProvider['AuthProviders'][0], ['saltForPasswordHashing','guid'], msg='JSON of updated authprov is not the same as what it was set to')
    
    #Copy assigned guid and salt for get test
    tenantWithSingleAuthProvider['AuthProviders'][0]['guid'] = resultJSON['AuthProviders'][0]['guid']
    tenantWithSingleAuthProvider['AuthProviders'][0]['saltForPasswordHashing'] = resultJSON['AuthProviders'][0]['saltForPasswordHashing']
    
    self.assertJSONStringsEqualWithIgnoredKeys(self.getTenantDICT(tenantWithSingleAuthProvider['Name']), tenantWithSingleAuthProvider, ["ObjectVersion"], msg='Tenant wasnt changed in get result')

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
    tenantDICT = self.createTenantForTesting(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider['AuthProviders'] = [copy.deepcopy(sampleInternalAuthProv001_CREATE), copy.deepcopy(sampleInternalAuthProv001_CREATE)]
    tenantWithSingleAuthProvider['ObjectVersion'] = tenantDICT['ObjectVersion']

    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithSingleAuthProvider['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithSingleAuthProvider), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithSingleAuthProvider, ['AuthProviders',"ObjectVersion"], msg='JSON of updated Tenant is not the same as what it was set to')
    self.assertEqual(resultJSON["ObjectVersion"],"2")

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['AuthProviders'][0], tenantWithSingleAuthProvider['AuthProviders'][0], ['saltForPasswordHashing','guid'], msg='JSON of updated authprov is not the same as what it was set to')
    
    #Copy assigned guid and salt for get test
    for c in [0, 1]:
      tenantWithSingleAuthProvider['AuthProviders'][c]['guid'] = resultJSON['AuthProviders'][c]['guid']
      tenantWithSingleAuthProvider['AuthProviders'][c]['saltForPasswordHashing'] = resultJSON['AuthProviders'][c]['saltForPasswordHashing']
    
    self.assertJSONStringsEqualWithIgnoredKeys(self.getTenantDICT(tenantWithSingleAuthProvider['Name']), tenantWithSingleAuthProvider, ["ObjectVersion"], msg='Tenant wasnt changed in get result')
    self.assertEqual(resultJSON["ObjectVersion"],"2")
  
  def test_addSecondAuthProvider(self):
    resultJSON = self.createTenantForTestingWithMutipleAuthProviders(tenantWithNoAuthProviders, [sampleInternalAuthProv001_CREATE])

    #Now add secondAuth provider as an update
    existingAuthProv = resultJSON['AuthProviders'][0]

    tenantWithSingleAuthProvider = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider['AuthProviders'] = [existingAuthProv, copy.deepcopy(sampleInternalAuthProv001_CREATE)]
    tenantWithSingleAuthProvider['ObjectVersion'] = resultJSON['ObjectVersion']

    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithSingleAuthProvider['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithSingleAuthProvider), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))
    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithSingleAuthProvider, ['AuthProviders',"ObjectVersion"], msg='JSON of updated Tenant is not the same as what it was set to')
    self.assertEqual(resultJSON["ObjectVersion"],"3")

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['AuthProviders'][0], tenantWithSingleAuthProvider['AuthProviders'][0], ['saltForPasswordHashing','guid'], msg='JSON of updated authprov is not the same as what it was set to')
    
    #Copy assigned guid and salt for get test
    for c in [0, 1]:
      tenantWithSingleAuthProvider['AuthProviders'][c]['guid'] = resultJSON['AuthProviders'][c]['guid']
      tenantWithSingleAuthProvider['AuthProviders'][c]['saltForPasswordHashing'] = resultJSON['AuthProviders'][c]['saltForPasswordHashing']
    
    self.assertJSONStringsEqualWithIgnoredKeys(self.getTenantDICT(tenantWithSingleAuthProvider['Name']), tenantWithSingleAuthProvider, ["ObjectVersion"], msg='Tenant wasnt changed in get result')

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
    changedTenantDICT['ObjectVersion'] = resultJSON['ObjectVersion']
    
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithNoAuthProviders['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(changedTenantDICT), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)    
    
    changedResultJSON = self.getTenantDICT(tenantWithNoAuthProviders['Name'])
    self.assertJSONStringsEqualWithIgnoredKeys(changedResultJSON, expectedDictAfterChange, ["ObjectVersion"], msg='New Tenant JSON isn\'t the expected value')
    self.assertEqual(resultJSON["ObjectVersion"],"2")
  
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
    self.assertJSONStringsEqualWithIgnoredKeys(changedResultJSON, changedTenantDict, ["ObjectVersion"], msg='New Tenant JSON isn\'t the expected value')
    self.assertEqual(changedResultJSON["ObjectVersion"], "3")
  
  def test_deleteOnlyAuthProvider(self):
    origTenantDict = self.createTenantForTestingWithMutipleAuthProviders(tenantWithNoAuthProviders, [sampleInternalAuthProv001_CREATE])
    authProvGUID = origTenantDict['AuthProviders'][0]['guid']
    
    def dbfn(storeConnection):
      #Also create some auth data for the single auth
      def someFn1(connectionContext):
        person = CreatePerson(appObj, storeConnection, None, 'a','b','c')
        authData = AddAuth(appObj, tenantWithNoAuthProviders['Name'], authProvGUID, {
          "username": 'AA', 
          "password": b'BB'
          },
          person['guid'],
          storeConnection
        )
        return person, authData
      (person, authData) = storeConnection.executeInsideTransaction(someFn1)
      

      #Before we delete the auth provider we must get the key it used to create the userAuth
      authProvDict = {
        "Type": "internal",
        "ConfigJSON": json.loads(sampleInternalAuthProv001_CREATE["ConfigJSON"])
      }
      AuthProvider = authProviderFactory(
        authProvDict,
        authProvGUID,
        tenantWithNoAuthProviders['Name']
      )
      authTypeConfigDict = {'username': 'AA'}
      authRecordKey = AuthProvider._makeKey(authTypeConfigDict)
      #Use the key the first time to make sure auth record exists
      authRecord, objVer, creationDateTime, lastUpdateDateTime = getAuthRecord(appObj, authRecordKey, storeConnection)
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
      self.assertJSONStringsEqualWithIgnoredKeys(changedResultJSON, changedTenantDict, ["ObjectVersion"], msg='New Tenant JSON isn\'t the expected value')
      self.assertEqual(changedResultJSON["ObjectVersion"],"3")

      self.assertEqual(len(changedResultJSON['AuthProviders']),0,msg='Wrong number of remaining auth providers')
      
      #Check auth record has been NOT been removed
      # auth records will not be removed with the tenant as auth records
      # are independant of tenant. Any clean up will be done when the person is deleted
      authRecord2, objVer, creationDateTime, lastUpdateDateTime = getAuthRecord(appObj, authRecordKey, storeConnection)
      self.assertJSONStringsEqualWithIgnoredKeys(authRecord, authRecord2, [], msg='Error userAuths should not have changed')
    appObj.objectStore.executeInsideConnectionContext(dbfn)
    
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
    self.assertJSONStringsEqualWithIgnoredKeys(changedResultJSON, changedTenantDict, ["ObjectVersion"], msg='New Tenant JSON isn\'t the expected value')
    self.assertEqual(changedResultJSON["ObjectVersion"],"3")

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
    self.assertJSONStringsEqualWithIgnoredKeys(changedResultJSON, changedTenantDict, ["ObjectVersion"], msg='New Tenant JSON isn\'t the expected value')
    self.assertEqual(changedResultJSON["ObjectVersion"],"3")

    self.assertEqual(len(changedResultJSON['AuthProviders']),2,msg='Wrong number of remaining auth providers')
  
  def test_deleteTenant(self):
    origTenantDict = self.createTenantForTestingWithMutipleAuthProviders(tenantWithNoAuthProviders, [sampleInternalAuthProv001_CREATE,sampleInternalAuthProv001_CREATE,sampleInternalAuthProv001_CREATE])
    result = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + origTenantDict['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken(), objectVersionHeaderName: origTenantDict['ObjectVersion']}
    )
    self.assertEqual(result.status_code, 200, msg="Delete tenant failed - " + result.get_data(as_text=True)) 
    
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

  def test_getTenant(self):
    origTenantDict = self.createTenantForTestingWithMutipleAuthProviders(tenantWithNoAuthProviders, [])
    result = self.testClient.get(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithNoAuthProviders['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}
    )
    self.assertEqual(result.status_code, 200) 
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithNoAuthProviders, ["ObjectVersion"], msg='Incorrect response')
    self.assertEqual(resultJSON["ObjectVersion"],"2")
    
  def test_getTenantBadName(self):
    result = self.testClient.get(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + 'InvalidTenantName', 
      headers={ jwtHeaderName: self.getNormalJWTToken()}
    )
    self.assertEqual(result.status_code, 404) 

  def test_deleteWIthWRongOjectVersionClashCauseError(self):
    origTenantDict = self.createTenantForTestingWithMutipleAuthProviders(tenantWithNoAuthProviders, [])
    result = self.testClient.get(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithNoAuthProviders['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}
    )
    self.assertEqual(result.status_code, 200) 
    resultJSON = json.loads(result.get_data(as_text=True))

    firstRecievedObjectVersion = resultJSON["ObjectVersion"]
    #print("firstRecievedObjectVersion:",firstRecievedObjectVersion)
    
    #Change the object to generate new object version
    changedTenantDict = copy.deepcopy(origTenantDict)
    changedTenantDict['Description'] = 'Changed description'
    result2 = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + changedTenantDict['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(changedTenantDict), 
      content_type='application/json'
    )
    self.assertEqual(result2.status_code, 200)    
    result2JSON = json.loads(result2.get_data(as_text=True))

    secondRecievedObjectVersion = result2JSON["ObjectVersion"]
    #print("secondRecievedObjectVersion:",secondRecievedObjectVersion)

    result3 = self.testClient.delete(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + origTenantDict['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken(), objectVersionHeaderName: firstRecievedObjectVersion}
    )
    self.assertEqual(result3.status_code, 409, msg="Deltion of tenant with old object version didn't fail") 

  def test_twoUpdatesResultInOjectVersionClashCauseError(self):
    origTenantDict = self.createTenantForTestingWithMutipleAuthProviders(tenantWithNoAuthProviders, [])
    result = self.testClient.get(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithNoAuthProviders['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}
    )
    self.assertEqual(result.status_code, 200) 
    resultJSON = json.loads(result.get_data(as_text=True))

    firstRecievedObjectVersion = resultJSON["ObjectVersion"]
    print("firstRecievedObjectVersion:",firstRecievedObjectVersion)
    
    #Change the object to generate new object version
    changedTenantDict = copy.deepcopy(origTenantDict)
    changedTenantDict['Description'] = 'Changed description'
    result2 = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + changedTenantDict['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(changedTenantDict), 
      content_type='application/json'
    )
    self.assertEqual(result2.status_code, 200)    
    result2JSON = json.loads(result2.get_data(as_text=True))

    secondRecievedObjectVersion = result2JSON["ObjectVersion"]
    print("secondRecievedObjectVersion:",secondRecievedObjectVersion)

    print("Now sending with object version:", origTenantDict["ObjectVersion"])

    #Update back to first json without changing the object version - should fail
    changedTenantDict = copy.deepcopy(origTenantDict)
    changedTenantDict['Description'] = 'Changed description'
    result3 = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + changedTenantDict['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(origTenantDict), 
      content_type='application/json'
    )
    self.assertEqual(result3.status_code, 409)    

  def test_addAuthProviderWithGUIDIsEmptyString(self):
    tenantDICT = self.createTenantForTesting(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider['AuthProviders'] = [copy.deepcopy(sampleInternalAuthProv001_CREATE)]
    tenantWithSingleAuthProvider['ObjectVersion'] = tenantDICT['ObjectVersion']
    tenantWithSingleAuthProvider['AuthProviders'][0]['guid'] = ''
    tenantWithSingleAuthProvider['AuthProviders'][0]['saltForPasswordHashing'] = ''
    
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithSingleAuthProvider['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithSingleAuthProvider), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithSingleAuthProvider, ['AuthProviders',"ObjectVersion"], msg='JSON of updated Tenant is not the same as what it was set to')
    self.assertEqual(resultJSON["ObjectVersion"],"2")    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['AuthProviders'][0], tenantWithSingleAuthProvider['AuthProviders'][0], ['saltForPasswordHashing','guid'], msg='JSON of updated authprov is not the same as what it was set to')
    
    #Copy assigned guid and salt for get test
    tenantWithSingleAuthProvider['AuthProviders'][0]['guid'] = resultJSON['AuthProviders'][0]['guid']
    tenantWithSingleAuthProvider['AuthProviders'][0]['saltForPasswordHashing'] = resultJSON['AuthProviders'][0]['saltForPasswordHashing']
    
    self.assertJSONStringsEqualWithIgnoredKeys(self.getTenantDICT(tenantWithSingleAuthProvider['Name']), tenantWithSingleAuthProvider, ["ObjectVersion"], msg='Tenant wasnt changed in get result')

  def test_addAuthProviderWithPasswordSaltNotPresentInJSON(self):
    tenantDICT = self.createTenantForTesting(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider['AuthProviders'] = [copy.deepcopy(sampleInternalAuthProv001_CREATE)]
    tenantWithSingleAuthProvider['ObjectVersion'] = tenantDICT['ObjectVersion']
    del tenantWithSingleAuthProvider['AuthProviders'][0]['guid']
    del tenantWithSingleAuthProvider['AuthProviders'][0]['saltForPasswordHashing']
    
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithSingleAuthProvider['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithSingleAuthProvider), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 200)
    resultJSON = json.loads(result.get_data(as_text=True))

    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON, tenantWithSingleAuthProvider, ['AuthProviders',"ObjectVersion"], msg='JSON of updated Tenant is not the same as what it was set to')
    self.assertEqual(resultJSON["ObjectVersion"],"2")    
    self.assertJSONStringsEqualWithIgnoredKeys(resultJSON['AuthProviders'][0], tenantWithSingleAuthProvider['AuthProviders'][0], ['saltForPasswordHashing','guid'], msg='JSON of updated authprov is not the same as what it was set to')
    
    #Copy assigned guid and salt for get test
    tenantWithSingleAuthProvider['AuthProviders'][0]['guid'] = resultJSON['AuthProviders'][0]['guid']
    tenantWithSingleAuthProvider['AuthProviders'][0]['saltForPasswordHashing'] = resultJSON['AuthProviders'][0]['saltForPasswordHashing']
    
    self.assertJSONStringsEqualWithIgnoredKeys(self.getTenantDICT(tenantWithSingleAuthProvider['Name']), tenantWithSingleAuthProvider, ["ObjectVersion"], msg='Tenant wasnt changed in get result')

  def test_addAuthProviderWithInvalidAuthConfig(self):
    tenantDICT = self.createTenantForTesting(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider = copy.deepcopy(tenantWithNoAuthProviders)
    tenantWithSingleAuthProvider['AuthProviders'] = [copy.deepcopy(sampleInternalAuthProv001_CREATE)]
    tenantWithSingleAuthProvider['ObjectVersion'] = tenantDICT['ObjectVersion']
    tenantWithSingleAuthProvider['AuthProviders'][0]['ConfigJSON'] = '{"AA":"BB"}' #Valid JSON but not valid for an internal auth config
    
    result = self.testClient.put(
      self.adminAPIPrefix + '/' + masterTenantName + '/tenants/' + tenantWithSingleAuthProvider['Name'], 
      headers={ jwtHeaderName: self.getNormalJWTToken()}, 
      data=json.dumps(tenantWithSingleAuthProvider), 
      content_type='application/json'
    )
    self.assertEqual(result.status_code, 400)
    resultJSON = json.loads(result.get_data(as_text=True))
    self.assertEqual(resultJSON['message'],'Invalid Auth Config',msg='Wrong invalid auth message output')

    
