import TestHelperSuperClass
from appObj import appObj
import constants
from tenants import GetTenant
import copy
import json

from AuthProviders.authsCommon import SaveAuthRecord, getAuthRecord

randomTenantName = "someRandomTenantForTesting"
authProvGUID =  'd366fdd2-b40d-4c12-9d91-2e11ddf9bbe7'
Issue49_PreviousTenantExample = {
  'Name': randomTenantName,
  'Description': 'Msaddsastem',
  'AllowUserCreation': False,
  'AuthProviders': {
    authProvGUID: {
      'guid':authProvGUID,
      'MenuText': 'Website account login',
      'IconLink': None,
      'Type': 'internal',
      'AllowUserCreation': False,
      'AllowLink': False, 'AllowUnlink': False, 'LinkText': 'Link Website Account',
      'ConfigJSON': {'userSufix': '@internalDataStore'}, 'saltForPasswordHashing': 'JDJiJDEyJGxYdGkzMlhENkxrd1lVbkx3LjF2aC4='
    }
  }
}
AddTenantLoginCustomDisplay_PreviousTenantExample = {
  'Name': randomTenantName,
  'Description': 'Master Tenadfsfsdfsdnt for User Management System',
  'AllowUserCreation': False,
  'AuthProviders': { authProvGUID: {
    'guid': authProvGUID, 'Type': 'internal', 'AllowUserCreation': False, 'AllowLink': False,
    'AllowUnlink': False, 'LinkText': 'Link Website Account', 'MenuText': 'Website account login',
    'IconLink': None,
    'ConfigJSON': '{"userSufix": "@internalDataStore"}', 'StaticlyLoadedData': {}, 'saltForPasswordHashing': 'JDJiJDEyJGxYdGkzMlhENkxrd1lVbkx3LjF2aC4='}},
  'JWTCollectionAllowedOriginList': ['http://a.com', 'https://b.com', 'http://c.co.uk'],
  'TicketOverrideURL': ''
}

#@TestHelperSuperClass.wipd
class testDataStructureEvolutionClass(TestHelperSuperClass.testHelperAPIClient):
  def test_userAuths_addKnownAs(self):
    #We added a column "known_as" to this object

    def dbfn(storeConnection):
      #Add an item that looks like previous type
      key = "abc123@34365ffsd"
      mainObjToStore = {
        "AuthUserKey": key + '@123',
        "AuthProviderType": 'Internal',
        "AuthProviderGUID": 'xx',
        "AuthProviderJSON": 'x',
        "personGUID": 'personGUID',
        "tenantName": constants.masterTenantName
      }
      SaveAuthRecord(appObj, key, mainObjToStore, storeConnection)

      authRecord, objVer, creationDateTime, lastUpdateDateTime = getAuthRecord(appObj, key, storeConnection)
      if 'known_as' not in authRecord:
        self.assertTrue(False, msg="known_as field not added")
      self.assertEqual(authRecord['known_as'],authRecord['AuthUserKey'],msg='known_as value didn\'t default to AuthUserKey')

    appObj.objectStore.executeInsideTransaction(dbfn)

  def test_Issue42_AddingFieldsToAuthProviders(self):
    def dbfn(storeConnection):
      PreviousTenantExample = {
        'Name': 'PreviousTenantExample',
        'Description': 'Master Tenant for User Management System',
        'AllowUserCreation': False,
        'AuthProviders': {
          '6b061b3e-eaf1-4653-b60f-2880a76255f2': {
            'guid': '6b061b3e-eaf1-4653-b60f-2880a76255f2',
            'MenuText': 'Website account login',
            'IconLink': None,
            'Type': 'internal',
            'AllowUserCreation': False,
            'ConfigJSON': {
              'userSufix': '@internalDataStore'
            },
            'saltForPasswordHashing': 'JDJiJDEyJGxYdGkzMlhENkxrd1lVbkx3LjF2aC4='
          }
        }
      }
      storeConnection.saveJSONObject("tenants", PreviousTenantExample['Name'], PreviousTenantExample)
      tenantObj = GetTenant(PreviousTenantExample["Name"], storeConnection, appObj=appObj)
      self.assertNotEqual(tenantObj, None, msg="Tenant Object not found")
      for x in tenantObj.getAuthProviderGUIDList():
        authProvDict = tenantObj.getAuthProvider(x)
        self.assertEqual(authProvDict['AllowLink'], False, msg="AllowLink not defaulted properly")
        self.assertEqual(authProvDict['AllowUnlink'], False, msg="AllowUnlink not defaulted properly")
        self.assertEqual(authProvDict['LinkText'], 'Link ' + authProvDict['Type'], msg="LinkText not defaulted properly")
    appObj.objectStore.executeInsideTransaction(dbfn)

  def test_Issue42_ServiceCallWorksWithoutExtraFields(self):
    tenantDict = self.getTenantDICT(constants.masterTenantName)

    #Before we start change all the fields to non-default values
    tenantDictNonDefaultValues = copy.deepcopy(tenantDict)
    tenantDictNonDefaultValues["AuthProviders"][0]['AllowLink'] = True
    tenantDictNonDefaultValues["AuthProviders"][0]['AllowUnlink'] = True
    tenantDictNonDefaultValues["AuthProviders"][0]['LinkText'] = 'nonDefaultLinkText'
    tenantDictNonDefaultValuesRes = self.updateTenant(tenantDictNonDefaultValues, [200])


    #Remove the added fields from structure (testing that we can edit without changing values)
    tenantDictForEditTest = copy.deepcopy(tenantDictNonDefaultValuesRes)
    del tenantDictForEditTest["AuthProviders"][0]['AllowLink']
    del tenantDictForEditTest["AuthProviders"][0]['AllowUnlink']
    del tenantDictForEditTest["AuthProviders"][0]['LinkText']

    #This tests editing an authProv - as this is editing existing this should default
    # data from existing values
    tenantDict2 = self.updateTenant(tenantDictForEditTest, [200])

    print(tenantDict2)

    self.assertEqual(tenantDict2["AuthProviders"][0]['AllowLink'],True, msg="AllowLink was changed when it was not provided in update payload")
    self.assertEqual(tenantDict2["AuthProviders"][0]['AllowUnlink'],True, msg="AllowUnlink was changed when it was not provided in update payload")
    self.assertEqual(tenantDict2["AuthProviders"][0]['LinkText'],'nonDefaultLinkText', msg="LinkText was changed when it was not provided in update payload")

    oldAuthProv = copy.deepcopy(TestHelperSuperClass.sampleInternalAuthProv001_CREATE)
    del oldAuthProv['AllowLink']
    del oldAuthProv['AllowUnlink']
    del oldAuthProv['LinkText']
    tenantDict["AuthProviders"].append(oldAuthProv)

    #This tests editing an authProv
    tenantDict3 = self.updateTenant(tenantDict2, [200])

  def test_Issue49_AddingJWTCollecitonAllowedOriginFieldToTenantMASTER(self):
    #This is defaulted to None for all tenants apart from master where it defaults to the comma seperated list in
    # env['APIAPP_DEFAULTMASTERTENANTJWTCOLLECTIONALLOWEDORIGINFIELD']
    def dbfn(storeConnection):

      PreviousTenantExample = {
        'Name': constants.masterTenantName,
        'Description': 'Master Tenant for User Management System',
        'AllowUserCreation': False,
        'AuthProviders': {
          'd366fdd2-b40d-4c12-9d91-2e11ddf9bbe7': {
            'guid': 'd366fdd2-b40d-4c12-9d91-2e11ddf9bbe7',
            'MenuText': 'Website account login',
            'IconLink': None,
            'Type': 'internal',
            'AllowUserCreation': False,
            'AllowLink': False, 'AllowUnlink': False, 'LinkText': 'Link Website Account',
            'ConfigJSON': {'userSufix': '@internalDataStore'}, 'saltForPasswordHashing': 'JDJiJDEyJGxYdGkzMlhENkxrd1lVbkx3LjF2aC4='
          }
        }
      }
      #Save old version of tenant into datastore

      def updTenant(tenant, storeConnection):
        if tenant is None:
          raise constants.tenantDosentExistException
        return PreviousTenantExample
      storeConnection.updateJSONObject("tenants", PreviousTenantExample['Name'], updTenant, 2)

      jsonData, objVersion, creationDateTime, lastUpdateDateTime, _ = storeConnection.getObjectJSON("tenants",constants.masterTenantName)
      tenantObj = GetTenant(PreviousTenantExample["Name"], storeConnection, appObj=appObj)
      #print(tenantObj.getJSONRepresenation())

      originList = list(map(lambda x: x.strip(), TestHelperSuperClass.env['APIAPP_DEFAULTMASTERTENANTJWTCOLLECTIONALLOWEDORIGINFIELD'].split(',')))

      self.assertEqual(tenantObj.getJWTCollectionAllowedOriginList(), originList, msg="Did not default master tenant origin list to default env param")


    appObj.objectStore.executeInsideTransaction(dbfn)

  def Issue49_putOldStyleTenantIntoStore(self, storeConnection):
      #Save old version of tenant into datastore
      storeConnection.saveJSONObject("tenants", Issue49_PreviousTenantExample['Name'], copy.deepcopy(Issue49_PreviousTenantExample))

  def test_Issue49_AddingJWTCollecitonAllowedOriginFieldToTenant(self):
    #This is defaulted to None for all tenants apart from master where it defaults to the comma seperated list in
    # env['APIAPP_DEFAULTMASTERTENANTJWTCOLLECTIONALLOWEDORIGINFIELD']
    def dbfn(storeConnection):
      self.Issue49_putOldStyleTenantIntoStore(storeConnection)

      jsonData, objVersion, creationDateTime, lastUpdateDateTime, _ = storeConnection.getObjectJSON("tenants",constants.masterTenantName)
      tenantObj = GetTenant(randomTenantName, storeConnection, appObj=appObj)
      #print(tenantObj.getJSONRepresenation())

      self.assertEqual(tenantObj.getJWTCollectionAllowedOriginList(), [], msg="Origin list of non-master tenant incorrect")

      jsonRep = tenantObj.getJSONRepresenation()
      expectedResult = copy.deepcopy(Issue49_PreviousTenantExample)
      expectedResult["AuthProviders"] = [{
            'guid':authProvGUID,
            'MenuText': 'Website account login',
            "StaticlyLoadedData": {},
            'IconLink': None,
            'Type': 'internal',
            'AllowUserCreation': False,
            'AllowLink': False,
            'AllowUnlink': False,
            'LinkText': 'Link Website Account',
            'ConfigJSON': "{\"userSufix\": \"@internalDataStore\"}",
            'saltForPasswordHashing': 'JDJiJDEyJGxYdGkzMlhENkxrd1lVbkx3LjF2aC4='
      }]
      expectedResult["ObjectVersion"] = 1
      expectedResult["JWTCollectionAllowedOriginList"] = []
      expectedResult["TicketOverrideURL"] = ""

      keysAddedInFutureTenantStructureUpdates = ["TenantBannerHTML", "SelectAuthMessage"]
      self.assertJSONStringsEqualWithIgnoredKeys(jsonRep,expectedResult, keysAddedInFutureTenantStructureUpdates, msg="Invalid JSON representation of Object")

    appObj.objectStore.executeInsideTransaction(dbfn)

  def test_Issue49_ServiceCallWorksWithoutExtraFields(self):
    tenantDict = self.getTenantDICT(constants.masterTenantName)

    #Before we start change all the fields to non-default values
    tenantDictNonDefaultValues = copy.deepcopy(tenantDict)
    tenantDictNonDefaultValues["JWTCollectionAllowedOriginList"] = ['http://nonstandard']
    tenantDictNonDefaultValuesRes = self.updateTenant(tenantDictNonDefaultValues, [200])

    #Remove the added fields from structure (testing that we can edit without changing values)
    tenantDictForEditTest = copy.deepcopy(tenantDictNonDefaultValuesRes)
    del tenantDictForEditTest["JWTCollectionAllowedOriginList"]

    #This tests editing an authProv - as this is editing existing this should default
    # data from existing values
    tenantDict2 = self.updateTenant(tenantDictForEditTest, [200])

    #print(tenantDict2)
    #print(tenantDictNonDefaultValues)

    self.assertEqual(tenantDict2["JWTCollectionAllowedOriginList"],tenantDictNonDefaultValues["JWTCollectionAllowedOriginList"], msg="JWTCollectionAllowedOriginList was changed when it was not provided in update payload")

  def test_Issue49_GetPaginatedServiceCallWorks(self):
    def dbfn(storeConnection):
      self.Issue49_putOldStyleTenantIntoStore(storeConnection)

      #Get tenant getList
      result = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
      self.assertEqual(result.status_code, 200)

      resultJSON = json.loads(result.get_data(as_text=True))

    appObj.objectStore.executeInsideTransaction(dbfn)

  def test_AddTenantLoginCustomDisplay(self):
    def dbfn(storeConnection):
      storeConnection.saveJSONObject("tenants", AddTenantLoginCustomDisplay_PreviousTenantExample['Name'], copy.deepcopy(AddTenantLoginCustomDisplay_PreviousTenantExample))

      result = self.testClient.get(self.adminAPIPrefix + '/' + constants.masterTenantName + '/tenants', headers={ constants.jwtHeaderName: self.getNormalJWTToken()})
      self.assertEqual(result.status_code, 200)

      resultJSON = json.loads(result.get_data(as_text=True))

      foundTenant = None
      for curTenant in resultJSON["result"]:
        if curTenant["Name"] == AddTenantLoginCustomDisplay_PreviousTenantExample['Name']:
          foundTenant = curTenant

      if foundTenant is None:
        raise Exception("Could not find sample tenant")

      self.assertEqual(foundTenant["TenantBannerHTML"], "")
      self.assertEqual(foundTenant["SelectAuthMessage"], "How do you want to verify who you are?")

    appObj.objectStore.executeInsideTransaction(dbfn)
