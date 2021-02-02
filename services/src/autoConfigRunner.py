from tenants import CreateTenant, AddAuthProvider, GetTenant, CreateUser, GetAuthProvider
import constants
from persons import CreatePerson
from authProviders_Internal import getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse
from users import associateUserWithPerson, AddUserRole

class AutoConfigRunner():
  steps = None
  def __init__(self, configDict):
    self.steps = []
    for step in configDict["steps"]:
      self.steps.append(AutoConfigRunStepFactory(step))


  def run(self, appObj, storeConnection):
    print("\n----------------------------")
    print("Running autoconfig...")
    print("----------------------------")
    for step in self.steps:
      step.run(appObj, storeConnection)
      if not step.passed:
        print("Autoconfig errored!!!")
        raise Exception("Auto config errored")
    print("----------------------------")
    print("Autoconfig run complete")
    print("----------------------------\n\n")


def AutoConfigRunStepFactory(stepDict):
  if stepDict["type"] == "echo":
    return AutoConfigRunStepEcho(stepDict["data"])
  elif stepDict["type"] == "createTenant":
    return AutoConfigRunStepCreateTenant(stepDict["data"])
  elif stepDict["type"] == "addAuthProvider":
    return AutoConfigRunStepAddAuthProvider(stepDict["data"])
  elif stepDict["type"] == "addInternalUserAccount":
    return AutoConfigRunStepAddInternalUserAccount(stepDict["data"])

  raise Exception("Unknown step type")


class AutoConfigRunStep():
  stepDict = None
  passed = None
  def __init__(self, stepDict, storeConnection):
    self.stepDict = stepDict
    self.passed = False

  def setPassed(self):
    self.passed = True

  def run(self, appObj, storeConnection):
    raise Exception("Should be overridden")

class AutoConfigRunStepEcho(AutoConfigRunStep):
  text = None
  def __init__(self, stepDict):
    self.text = stepDict["text"]
  def run(self, appObj, storeConnection):
    print("Echo: " + self.text)
    self.setPassed()

class AutoConfigRunStepCreateTenant(AutoConfigRunStep):
  tenantName = None
  description = None
  allowUserCreation = None
  JWTCollectionAllowedOriginList = None
  TicketOverrideURL = None
  TenantBannerHTML = None
  SelectAuthMessage = None
  def __init__(self, stepDict):
    if "TenantBannerHTML" not in stepDict:
      stepDict["TenantBannerHTML"] = ""
    if "SelectAuthMessage" not in stepDict:
      stepDict["SelectAuthMessage"] = "How do you want to verify who you are?"
    self.tenantName = stepDict["tenantName"]
    self.description = stepDict["description"]
    self.allowUserCreation = stepDict["allowUserCreation"]
    self.JWTCollectionAllowedOriginList = stepDict["JWTCollectionAllowedOriginList"]
    self.TicketOverrideURL = ""
    self.TenantBannerHTML = stepDict["TenantBannerHTML"]
    self.SelectAuthMessage = stepDict["SelectAuthMessage"]
    if "TicketOverrideURL" in stepDict:
      self.TicketOverrideURL = stepDict["TicketOverrideURL"]
  def run(self, appObj, storeConnection):
    retVal = CreateTenant(
      appObj=appObj,
      tenantName=self.tenantName,
      description=self.description,
      allowUserCreation=self.allowUserCreation,
      storeConnection=storeConnection,
      JWTCollectionAllowedOriginList=self.JWTCollectionAllowedOriginList,
      TicketOverrideURL=self.TicketOverrideURL,
      TenantBannerHTML = self.TenantBannerHTML,
      SelectAuthMessage = self.SelectAuthMessage
    )
    print("CreateTenant: " + retVal.getName())
    self.setPassed()

class AutoConfigRunStepAddAuthProvider(AutoConfigRunStep):
  tenantName = None
  menuText = None
  iconLink = None
  Type = None
  AllowUserCreation = None
  configJSON = None
  AllowLink = None
  AllowUnlink = None
  LinkText = None

  def __init__(self, stepDict):
    self.tenantName = stepDict["tenantName"]
    self.menuText = stepDict["menuText"]
    self.iconLink = stepDict["iconLink"]
    self.Type = stepDict["Type"]
    self.AllowUserCreation = stepDict["AllowUserCreation"]
    self.configJSON = stepDict["configJSON"]
    self.AllowLink = stepDict["AllowLink"]
    self.AllowUnlink = stepDict["AllowUnlink"]
    self.LinkText = stepDict["LinkText"]
  def run(self, appObj, storeConnection):
    try:
      retVal = AddAuthProvider(
        appObj=appObj,
        tenantName=self.tenantName,
        menuText=self.menuText,
        iconLink=self.iconLink,
        Type=self.Type,
        AllowUserCreation=self.AllowUserCreation,
        configJSON=self.configJSON,
        storeConnection=storeConnection,
        AllowLink=self.AllowLink,
        AllowUnlink=self.AllowUnlink,
        LinkText=self.LinkText
        )
      print("AddAuthProvider: Type " + retVal["Type"] + " added to Tenant " + self.tenantName)
    except constants.customExceptionClass as err:
      if (err.id=='tenantDosentExistException'):
        raise Exception("AddAuthProvider: Tenant " + self.tenantName + " does not exist")
      raise x
    self.setPassed()

class AutoConfigRunStepAddInternalUserAccount(AutoConfigRunStep):
  tenantName = None
  userID = None
  Username = None
  Password = None
  Roles = None

  def __init__(self, stepDict):
    self.tenantName = stepDict["tenantName"]
    self.userID = stepDict["userID"]
    self.Username = stepDict["Username"]
    self.Password = stepDict["Password"]
    self.Roles = stepDict["Roles"]
  def run(self, appObj, storeConnection):
    tenantObj = GetTenant(self.tenantName, storeConnection, appObj=appObj)
    if tenantObj is None:
      raise Exception("AddInternalUserAccount: Tenant " + self.tenantName + " does not exist")
    authProvDict = tenantObj.getSingleAuthProviderOfType("internal")
    if authProvDict is None:
      raise Exception("AddInternalUserAccount: Tenant " + self.tenantName + " does not have (exactly) one internal auth provider")

    CreateUser(
      appObj,
      {"user_unique_identifier": self.userID, "known_as": self.Username},
      self.tenantName,
      'autoConfigRunner/AddInternalUserAccount',
      storeConnection
    )
    person = CreatePerson(appObj, storeConnection, None, 'a','b','c')
    credentialJSON = {
      "username": self.Username,
      "password": getHashedPasswordUsingSameMethodAsJavascriptFrontendShouldUse(
        appObj, self.Username, self.Password, authProvDict['saltForPasswordHashing']
      )
    }
    GetAuthProvider(
      appObj=appObj,
      tenantName=self.tenantName,
      authProviderGUID=authProvDict['guid'],
      storeConnection=storeConnection,
      tenantObj=tenantObj
    ).AddAuth(appObj, credentialJSON, person['guid'], storeConnection)

    associateUserWithPerson(appObj, self.userID, person['guid'], storeConnection)

    for curTenant in self.Roles:
      for curRole in self.Roles[curTenant]:
        AddUserRole(appObj, self.userID, curTenant, curRole, storeConnection)

    print("AddInternalUserAccount: Add " + self.Username + " to tenant " + tenantObj.getName())
    self.setPassed()
