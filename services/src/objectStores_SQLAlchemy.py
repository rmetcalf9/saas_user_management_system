from objectStores_base import ObjectStore, ObjectStoreConnectionContext, StoringNoneObjectAfterUpdateOperationException, WrongObjectVersionException, ObjectStoreConfigError, MissingTransactionContextException, TriedToDeleteMissingObjectException, TryingToCreateExistingObjectException
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, BigInteger, DateTime, JSON, func
import pytz
##import datetime
from dateutil.parser import parse

objectStoreHardCodedVersionInteger = 1

class ConnectionContext(ObjectStoreConnectionContext):
  connection = None
  transaction = None
  objectStore = None

  def __init__(self, objectStore):
    super(ConnectionContext, self).__init__()
    self.objectStore = objectStore
    self.connection = self.objectStore.engine.connect()

  def _startTransaction(self):
    if self.transaction is not None:
      raise Exception("ERROR Starting transaction when there is already one in progress")
    self.transaction = self.connection.begin()

  #Internal function for executing a statement
  ## only called from this file
  def _INT_execute(self, statement):
    if self.transaction is None:
      MissingTransactionContextException
    return self.connection.execute(statement.execution_options(autocommit=False))
    
  def _commitTransaction(self):
    res = self.transaction.commit()
    self.transaction = None
    return res
  def _rollbackTransaction(self):
    res = self.transaction.rollback()
    self.transaction = None
    return res

  def _saveJSONObject(self, objectType, objectKey, JSONString, objectVersion):
    query = self.objectStore.objDataTable.select(whereclause=(self.objectStore.objDataTable.c.key==objectKey))
    result =  self._INT_execute(query)
    firstRow = result.first()
    print("_saveJSONObject:" + objectType + ":" + objectKey + ":", objectVersion)
    if firstRow is not None:
      print(" firstRow:", firstRow)
    curTime = self.objectStore.appObj.getCurDateTime()
    if firstRow is None:
      if objectVersion is not None:
        raise WrongObjectVersionException
      newObjectVersion = 1
      query = self.objectStore.objDataTable.insert().values(
        key=objectKey, 
        objectVersion=newObjectVersion, 
        objectDICT=JSONString,
        creationDate=curTime,
        lastUpdateDate=curTime,
        creationDate_iso8601=curTime.isoformat(),
        lastUpdateDate_iso8601=curTime.isoformat()
      )
      result = self._INT_execute(query)
      if len(result.inserted_primary_key) != 1:
        raise Exception('_saveJSONObject wrong number of rows inserted')
      if result.inserted_primary_key[0] != objectKey:
        raise Exception('_saveJSONObject issue with primary key')
      return newObjectVersion
    if objectVersion is None:
      raise TryingToCreateExistingObjectException
    if firstRow.objectVersion != objectVersion:
      raise WrongObjectVersionException
    newObjectVersion = firstRow.objectVersion + 1
    query = self.objectStore.objDataTable.update(whereclause=(self.objectStore.objDataTable.c.key==objectKey)).values(
      objectVersion=newObjectVersion, 
      objectDICT=JSONString,
      lastUpdateDate=curTime,
      lastUpdateDate_iso8601=curTime.isoformat()
    )
    result = self._INT_execute(query)
    if result.rowcount != 1:
      raise Exceptoin('_saveJSONObject wrong number of rows updated')
    return newObjectVersion

  def _removeJSONObject(self, objectType, objectKey, objectVersion, ignoreMissingObject):
    query = self.objectStore.objDataTable.delete(whereclause=(self.objectStore.objDataTable.c.key==objectKey))
    result = self._INT_execute(query)
    if result.rowcount == 0:
      if not ignoreMissingObject:
        raise TriedToDeleteMissingObjectException
  
  #Return value is objectDICT, ObjectVersion, creationDate, lastUpdateDate
  #Return None, None, None, None if object isn't in store
  ObjTableKeyMap = None
  def _getObjectJSON(self, objectType, objectKey):
    query = self.objectStore.objDataTable.select(whereclause=(self.objectStore.objDataTable.c.key==objectKey))
    result = self._INT_execute(query)
    firstRow = result.fetchone()
    if firstRow is None:
      return None, None, None, None
    if result.rowcount != 1:
      raise Exception('_getObjectJSON Wrong number of rows returned for key')

    dt = parse(firstRow['creationDate_iso8601'])
    creationDate = dt.astimezone(pytz.utc)
    dt = parse(firstRow['lastUpdateDate_iso8601'])
    lastUpdateDate = dt.astimezone(pytz.utc)
    return firstRow['objectDICT'], firstRow['objectVersion'], creationDate, lastUpdateDate


  def _getPaginatedResult(self, objectType, paginatedParamValues, request, outputFN):
    raise Exception('_getPaginatedResult Not Implemented')

class ObjectStore_SQLAlchemy(ObjectStore):
  engine = None
  objDataTable = None
  verTable = None
  objectPrefix = None
  def __init__(self, ConfigDict, appObj):
    super(ObjectStore_SQLAlchemy, self).__init__(appObj)
    if "connectionString" not in ConfigDict:
      raise ObjectStoreConfigError("APIAPP_OBJECTSTORECONFIG SQLAlchemy ERROR - Expected connectionString")
    if "objectPrefix" in ConfigDict:
      self.objectPrefix = ConfigDict["objectPrefix"]
    else:
      self.objectPrefix = ""
    self.engine = create_engine(ConfigDict["connectionString"], pool_recycle=3600, pool_size=20, max_overflow=0)
    
    metadata = MetaData()
    #(objDICT, objectVersion, creationDate, lastUpdateDate)
    #from https://stackoverflow.com/questions/15157227/mysql-varchar-index-length
    #MySQL assumes 3 bytes per utf8 character. 255 characters is the maximum index size you can specify per column, because 256x3=768, which breaks the 767 byte limit.
    self.objDataTable = Table(self.objectPrefix + '_objData', metadata,
        #Tired intorudcing a seperate primary key and using key column as index but
        # I found the same lenght restriction exists on an index
        #Column('id', Integer, primary_key=True),
        #Column('key', String(300), index=True, unique=True),
        Column('key', String(300), primary_key=True),
        Column('objectDICT', JSON),
        Column('objectVersion', BigInteger),
        Column('creationDate', DateTime(timezone=True)), 
        Column('lastUpdateDate', DateTime(timezone=True)),
        Column('creationDate_iso8601', String(length=40)), 
        Column('lastUpdateDate_iso8601', String(length=40))
    )
    self.verTable = Table(self.objectPrefix + '_ver', metadata,
        Column('id', Integer, primary_key=True),
        Column('first_installed_ver', Integer),
        Column('current_installed_ver', Integer),
        Column('creationDate_iso8601', String(length=40)), 
        Column('lastUpdateDate_iso8601', String(length=40))
    )
    metadata.create_all(self.engine)
    
    self._INT_setupOrUpdateVer(appObj)
  
  #AppObj passed in as None
  def _INT_setupOrUpdateVer(self, appObj):
    storeConnection = self.getConnectionContext()
    def someFn(connectionContext):
      curTime = appObj.getCurDateTime()
      query = self.verTable.select()
      result = connectionContext._INT_execute(query)
      if result.rowcount != 1:
        if result.rowcount != 0:
          raise Exception('invalid database structure - can\'t read version')
        #There are 0 rows, create one
        query = self.verTable.insert().values(
          first_installed_ver=objectStoreHardCodedVersionInteger, 
          current_installed_ver=objectStoreHardCodedVersionInteger, 
          creationDate_iso8601=curTime.isoformat(),
          lastUpdateDate_iso8601=curTime.isoformat()
        )
        result = connectionContext._INT_execute(query)
        return
      firstRow = result.first()
      if objectStoreHardCodedVersionInteger == firstRow['current_installed_ver']:
        return
      raise Exception('Not Implemented - update datastore from x to objectStoreHardCodedVersionInteger')
    storeConnection.executeInsideTransaction(someFn)
    

  def _resetDataForTest(self):
    storeConnection = self.getConnectionContext()
    def someFn(connectionContext):
      query = self.objDataTable.delete()
      connectionContext._INT_execute(query)
    storeConnection.executeInsideTransaction(someFn)
    
  def _getConnectionContext(self):
    return ConnectionContext(self)

