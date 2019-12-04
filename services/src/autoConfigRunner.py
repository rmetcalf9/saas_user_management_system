

class AutoConfigRunner():
  configDict = None
  def __init__(self, configDict):
    self.configDict = configDict


  def run(self, appObj):
    print("\n----------------------------")
    print("Running autoconfig...")
    print("----------------------------")
    for step in self.configDict["steps"]:
      AutoConfigRunStepFactory(step).run(appObj)
    print("----------------------------")
    print("Autoconfig run complete")
    print("----------------------------\n\n")


def AutoConfigRunStepFactory(stepDict):
  if stepDict["type"] == "echo":
    return AutoConfigRunStepEcho(stepDict["data"])

  raise Exception("Unknown step type")


class AutoConfigRunStep():
  stepDict = None
  def __init__(self, stepDict):
    self.stepDict = stepDict

  def run(self, appObj):
    raise Exception("Should be overridden")

class AutoConfigRunStepEcho(AutoConfigRunStep):
  def run(self, appObj):
    print("Echo: " + self.stepDict["text"])
