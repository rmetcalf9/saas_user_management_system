from objectStores_base import ObjectStore, StoringNoneObjectAfterUpdateOperationException, WrongObjectVersionException, ObjectStoreConfigError, MissingTransactionContextException
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, BigInteger, DateTime, JSON


def testFunctionToBeGotRidOf():
  print("Test start")

  connectionString="mysql+pymysql://saas_user_man_user:saas_user_man_testing_password@127.0.0.1:10103/saas_user_man"

  engine = create_engine(connectionString, pool_recycle=3600, pool_size=20, max_overflow=0)

  metadata = MetaData()
  users = Table('rjm_test_table', metadata,
      Column('id', Integer, primary_key=True),
      Column('name', String(2048)),
      Column('fullname', String(2048)),
  )

  metadata.create_all(engine)

  print("Test end")

###testFunctionToBeGotRidOf()


# Class that will store objects in memory only
class ObjectStore_SQLAlchemy(ObjectStore):
  engine = None
  objDataTable = None
  objectPrefix = None
  def __init__(self, ConfigDict):
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
        Column('key', String(255), primary_key=True),
        Column('objectDICT', JSON()),
        Column('objectVersion', BigInteger),
        Column('creationDate', DateTime(timezone=True)), 
        Column('lastUpdateDate', DateTime(timezone=True))
    )
    metadata.create_all(self.engine)

  def _startTransaction(self):
    connection = self.engine.connect()
    trans = connection.begin()
    def execute(statement):
      return connection.execute(statement.execution_options(autocommit=False))
    return {
      'execute': execute,
      'trans': trans
    }
  def _commitTransaction(self, transactionContext):
    return transactionContext["trans"].commit()
  def _rollbackTransaction(self, transactionContext):
    return transactionContext["trans"].rollback()

  def resetDataForTest(self):
    transactionContext = self.startTransaction()
    query = self.objDataTable.delete()
    result = transactionContext["execute"](query)
    self.commitTransaction(transactionContext)
    
  def _saveJSONObject(self, appObj, objectType, objectKey, JSONString, objectVersion, transactionContext):
    if transactionContext is None:
      raise MissingTransactionContextException
    query = self.objDataTable.select(whereclause=(self.objDataTable.c.key==objectKey))
    result = transactionContext["execute"](query)
    firstRow = result.first()
    if firstRow is None:
      if objectVersion is not None:
        raise WrongObjectVersionException
      newObjectVersion = 1
      query = self.objDataTable.insert().values(key=objectKey, objectVersion=newObjectVersion)
      result = transactionContext["execute"](query)
      if len(result.inserted_primary_key) != 1:
        raise Exception('_saveJSONObject wrong number of rows inserted')
      if result.inserted_primary_key[0] != objectKey:
        raise Exception('_saveJSONObject issue with primary key')
      return newObjectVersion
    if firstRow.objectVersion != objectVersion:
      raise WrongObjectVersionException
    newObjectVersion = firstRow.objectVersion + 1
    query = self.objDataTable.update(whereclause=(self.objDataTable.c.key==objectKey)).values(objectVersion=newObjectVersion, objectDICT=JSONString)
    result = transactionContext["execute"](query)
    if result.rowcount != 1:
      raise Exceptoin('_saveJSONObject wrong number of rows updated')
    return newObjectVersion

  def _removeJSONObject(self, appObj, objectType, objectKey, objectVersion, ignoreMissingObject, transactionContext):
    if transactionContext is None:
      raise MissingTransactionContextException
    raise Exception('_removeJSONObject Not Implemented')
  def _updateJSONObject(self, appObj, objectType, objectKey, updateFn, objectVersion, transactionContext):
    if transactionContext is None:
      raise MissingTransactionContextException
    raise Exception('_updateJSONObject Not Implemented')
    
  #Return value is objectDICT, ObjectVersion, creationDate, lastUpdateDate
  #Return None, None, None, None if object isn't in store
  def _getObjectJSON(self, appObj, objectType, objectKey):
    query = self.objDataTable.select(whereclause=(self.objDataTable.c.key==objectKey))
    result = self.engine.connect().execute(query)
    firstRow = result.first()
    if firstRow is None:
      return None, None, None, None
    if result.rowcount != 1:
      raise Exception('_getObjectJSON Wrong numnber of rows returned for key')
    creationDate = None
    lastUpdateDate = None
    return firstRow.objectDICT, firstRow.objectVersion, creationDate, lastUpdateDate


  def _getPaginatedResult(self, appObj, objectType, paginatedParamValues, request, outputFN):
    raise Exception('_getPaginatedResult Not Implemented')
