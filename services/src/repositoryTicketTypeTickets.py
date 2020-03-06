from object_store_abstraction import RepositoryBaseClass, RepositoryValidationException
from repositoryTicketObj import factoryFn as ticketObjFactoryFn
import constants


class TicketRepositoryClass(RepositoryBaseClass):
  objName = "TicketTypeTicket"

  def __init__(self):
    RepositoryBaseClass.__init__(self, "tickettypetickets", ticketObjFactoryFn)
