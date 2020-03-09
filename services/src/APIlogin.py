import APIlogin_Legacy
import APIlogin_Tickets

def registerAPI(appObj):
  nsLogin = appObj.flastRestPlusAPIObject.namespace('public/login', description='Public API for displaying login pages.')

  APIlogin_Legacy.registerAPI(appObj=appObj, nsLogin=nsLogin)
  APIlogin_Tickets.registerAPI(appObj=appObj, nsLogin=nsLogin)
