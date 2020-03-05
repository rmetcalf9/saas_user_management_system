# This file is for the ticket type repository

from object_store_abstraction import RepositoryBaseClass, RepositoryValidationException
from repositoryTicketTypeObj import factoryFn as ticketTypeObjFactoryFn
import constants

def requireBooleanElement(obj, elementName, objectName):
  RepositoryBaseClass.RequireStringElement(obj, elementName, objectName)
  if not isinstance(obj[elementName], bool):
    raise RepositoryValidationException(objectName + " must have a " + elementName + " that is a boolean")

def reqireIntegerElement(obj, elementName, objectName, minval=None, maxval=None):
  RepositoryBaseClass.RequireStringElement(obj, elementName, objectName)
  try:
    val = int(obj[elementName])
  except ValueError:
    raise RepositoryValidationException(objectName + " must have a " + elementName + " that is an integer")
  if minval is not None:
    if val < minval:
      raise RepositoryValidationException(objectName + " must have a " + elementName + " that is an integer greater than " + str(minval))
  if maxval is not None:
    if val > maxval:
      raise RepositoryValidationException(objectName + " must have a " + elementName + " that is an integer less than " + str(maxval))


class TicketTypeRepositoryClass(RepositoryBaseClass):
  objName = "TicketType"

  def __init__(self):
    RepositoryBaseClass.__init__(self, "tickettypes", ticketTypeObjFactoryFn)

  def runUpsertValidation(self, obj):
    RepositoryBaseClass.RequireStringElement(obj, "tenantName", self.objName)
    RepositoryBaseClass.RequireStringElement(obj, "ticketTypeName", self.objName)
    RepositoryBaseClass.RequireStringElement(obj, "description", self.objName)
    requireBooleanElement(obj, "enabled", self.objName)
    RepositoryBaseClass.RequireStringElement(obj, "welcomeMessage", self.objName)
    requireBooleanElement(obj["welcomeMessage"], "agreementRequired", self.objName + ".welcomeMessage")
    RepositoryBaseClass.RequireStringElement(obj["welcomeMessage"], "title", self.objName + ".welcomeMessage")
    RepositoryBaseClass.RequireStringElement(obj["welcomeMessage"], "body", self.objName + ".welcomeMessage")
    RepositoryBaseClass.RequireStringElement(obj["welcomeMessage"], "okButtonText", self.objName + ".welcomeMessage")
    requireBooleanElement(obj, "allowUserCreation", self.objName)
    reqireIntegerElement(obj, "issueDuration", self.objName)
    RepositoryBaseClass.RequireListElement(obj, "roles", self.objName)
    for curRole in obj["roles"]:
      if not isinstance(curRole, str):
        raise RepositoryValidationException(self.objName + " must have all roles as strings")
      if curRole=="":
        raise RepositoryValidationException(self.objName + " must have all roles as non-empty strings")
      if curRole==constants.DefaultHasAccountRole:
        raise RepositoryValidationException(self.objName + " not valid to assign " + constants.DefaultHasAccountRole + " role")
    if len(obj["roles"]) == 0:
      raise RepositoryValidationException(self.objName + " must have at least one role")
    RepositoryBaseClass.RequireStringElement(obj, "postUseURL", self.objName)
    RepositoryBaseClass.RequireStringElement(obj, "postInvalidURL", self.objName)


