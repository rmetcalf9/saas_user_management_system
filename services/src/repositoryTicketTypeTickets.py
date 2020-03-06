from object_store_abstraction import RepositoryBaseClass, RepositoryValidationException
from repositoryTicketTypeTicketsObj import factoryFn as ticketTypeTicketsObjFactoryFn
import constants


class TicketTypeTicketsRepositoryClass(RepositoryBaseClass):
  objName = "TicketTypeTicket"

  def __init__(self):
    RepositoryBaseClass.__init__(self, "tickettypetickets", ticketTypeTicketsObjFactoryFn)
