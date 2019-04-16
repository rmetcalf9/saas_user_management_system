#Script to test a running container
import unittest
import requests
import json
import containerTestCommon

import copy_of_main_constants_do_not_edit as constants

#This file tests access to authed api using different methods of sending the jwt token.


#There are 4 ways that should work:
# 1 send via authroizaion header (Authorization: Bearer XXXX)
# 2 send via header constants.jwtHeaderName (jwt-auth-token)
# 3 send via cookie constants.jwtCookieName (jwt-auth-token)
# 4 send via more complicated cookie constants.loginCookieName (usersystemUserCredentials) - under jwtData -> JWTToken


class test_authedAccessMethods(unittest.TestCase):
  def test_testNormalJWTHeader(self):
    loginDICT = containerTestCommon.getLoginDICTForDefaultUser(self)
    jwtToken = loginDICT['jwtData']['JWTToken']
    
    headers = {'jwt-auth-token': jwtToken}
    cookies = {}
    tenantDICT, call_result = containerTestCommon.callGetService(containerTestCommon.ADMIN,"/" + constants.masterTenantName + "/tenants", [200], None, headers, cookies)

  def test_testNormalJWTCookie(self):
    loginDICT = containerTestCommon.getLoginDICTForDefaultUser(self)
    jwtToken = loginDICT['jwtData']['JWTToken']
    
    headers = {}
    cookies = {'jwt-auth-token': jwtToken}
    tenantDICT, call_result = containerTestCommon.callGetService(containerTestCommon.ADMIN,"/" + constants.masterTenantName + "/tenants", [200], None, headers, cookies)
   
  #Have not been able to implement this test   
  #def test_testComplicatedJWTCookie(self):
  #  loginDICT = containerTestCommon.getLoginDICTForDefaultUser(self)
  #  jwtToken = loginDICT['jwtData']['JWTToken']
  #  
  #  print("loginDICT:",loginDICT)
  #  headers = {}
  #  cookies = {'usersystemUserCredentials': json.dumps(loginDICT)}
  #  tenantDICT, call_result = containerTestCommon.callGetService(containerTestCommon.ADMIN,"/" + constants.masterTenantName + "/tenants", [200], None, headers, cookies)
    