from TestHelperSuperClass import testHelperAPIClient
from appObj import appObj
from constants import masterTenantName

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
        "tenantName": masterTenantName
      }

      
      SaveAuthRecord(appObj, key, mainObjToStore, storeConnection)
      
      authRecord, objVer, creationDateTime, lastUpdateDateTime = getAuthRecord(appObj, key, storeConnection)
      if 'known_as' not in authRecord:
        self.assertTrue(False, msg="known_as field not added")
      self.assertEqual(authRecord['known_as'],authRecord['AuthUserKey'],msg='known_as value didn\'t default to AuthUserKey')

    appObj.objectStore.executeInsideTransaction(dbfn)

    pass

