from appObj import appObj

import sys
import os
import datetime
import pytz

if sys.version_info[0] < 3:
  raise Exception("Must be using Python 3.6")
if sys.version_info[0] == 3:
  if sys.version_info[1] < 6:
    raise Exception("Must be using at least Python 3.6")

curDatetime = datetime.datetime.now(pytz.utc)
appObj.init(os.environ, curDatetime)

def call_exit_gracefully():
  appObj.exit_gracefully(None, None)

try:
  import uwsgi
  uwsgi.atexit = call_exit_gracefully
except:
  print('uwsgi not availiable')

globalFlaskAppObj = appObj.flaskAppObject

if __name__ == "__main__":
  #Custom handler to allow me to use my own logger
  from werkzeug.serving import WSGIRequestHandler, _log

  class CustomRequestHandler(WSGIRequestHandler):
    # Stop logging sucessful health checks
    #Stops flask logging health checks
    # dosen't work in container with nginx
    def log_request(self, code='-', size='-'):
      ignore = False
      if code > 199:
        if code < 300:
          if "healthcheck=true" in self.requestline:
            ignore = True
      if ignore:
        return
      return super(CustomRequestHandler, self).log_request(code,size)

  expectedNumberOfParams = 0
  if ((len(sys.argv)-1) != expectedNumberOfParams):
    raise Exception('Wrong number of paramaters passed (Got ' + str((len(sys.argv)-1)) + " expected " + str(expectedNumberOfParams) + ")")

  appObj.run(CustomRequestHandler)