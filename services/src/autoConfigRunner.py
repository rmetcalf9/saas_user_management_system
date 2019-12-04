from tenants import CreateTenant

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
    print("----------------------------")
    print("Autoconfig run complete")
    print("----------------------------\n\n")


def AutoConfigRunStepFactory(stepDict):
  if stepDict["type"] == "echo":
    return AutoConfigRunStepEcho(stepDict["data"])
  elif stepDict["type"] == "createTenant":
    return AutoConfigRunStepCreateTenant(stepDict["data"])

  raise Exception("Unknown step type")


class AutoConfigRunStep():
  stepDict = None
  def __init__(self, stepDict, storeConnection):
    self.stepDict = stepDict

  def run(self, appObj, storeConnection):
    raise Exception("Should be overridden")

class AutoConfigRunStepEcho(AutoConfigRunStep):
  text = None
  def __init__(self, stepDict):
    self.text = stepDict["text"]
  def run(self, appObj, storeConnection):
    print("Echo: " + self.text)

class AutoConfigRunStepCreateTenant(AutoConfigRunStep):
  tenantName = None
  description = None
  allowUserCreation = None
  JWTCollectionAllowedOriginList = None
  def __init__(self, stepDict):
    self.tenantName = stepDict["tenantName"]
    self.description = stepDict["description"]
    self.allowUserCreation = stepDict["allowUserCreation"]
    self.JWTCollectionAllowedOriginList = stepDict["JWTCollectionAllowedOriginList"]
  def run(self, appObj, storeConnection):
    retVal = CreateTenant(
      appObj=appObj,
      tenantName=self.tenantName,
      description=self.description,
      allowUserCreation=self.allowUserCreation,
      storeConnection=storeConnection,
      JWTCollectionAllowedOriginList=self.JWTCollectionAllowedOriginList
    )
    print("CreateTenant: " + retVal.getName())
