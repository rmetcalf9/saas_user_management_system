# This file is for the ticket type repository

from object_store_abstraction import RepositoryBaseClass
from repositoryTicketTypeObj import factoryFn as ticketTypeObjFactoryFn

class TicketTypeRepositoryClass(RepositoryBaseClass):
  def __init__(self):
    RepositoryBaseClass.__init__(self, "tickettypes", ticketTypeObjFactoryFn)

  def runUpsertValidation(self, obj):
    pass
    #RepositoryBaseClass.RequireStringElement(obj, "namespace", "Chart")
    #RepositoryBaseClass.RequireStringElement(obj, "name", "Chart")
    #RepositoryBaseClass.RequireElement(obj, "accessControl", "Chart")
    #RepositoryBaseClass.RequireElement(obj["accessControl"], "AllowAnonExplore", "Chart.accessControl")

