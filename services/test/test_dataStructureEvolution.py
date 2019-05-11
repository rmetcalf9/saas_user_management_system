from TestHelperSuperClass import testHelperAPIClient, sampleInternalAuthProv001_CREATE
from appObj import appObj
import constants
from tenants import GetTenant
import copy

from authsCommon import SaveAuthRecord, getAuthRecord

class testDataStructureEvolutionClass(testHelperAPIClient):
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

  def test_Issue42_AddingFieldsToAuthPRoviders(self):
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
      tenantObj = GetTenant(PreviousTenantExample["Name"], storeConnection, 'a','b','c')
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
   
    oldAuthProv = copy.deepcopy(sampleInternalAuthProv001_CREATE)
    del oldAuthProv['AllowLink']
    del oldAuthProv['AllowUnlink']
    del oldAuthProv['LinkText']
    tenantDict["AuthProviders"].append(oldAuthProv)

    #This tests editing an authProv
    tenantDict3 = self.updateTenant(tenantDict2, [200])
