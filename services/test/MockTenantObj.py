
class MockTenantObj():
    appObj = None
    def __init__(self, appObj):
        self.appObj = appObj

    def getJwtTokenTimeout(self):
        return self.appObj.APIAPP_JWT_TOKEN_TIMEOUT

    def getRefreshTokenTimeout(self):
        return self.appObj.APIAPP_REFRESH_TOKEN_TIMEOUT

    def getRefreshSessionTimeout(self):
        return self.appObj.APIAPP_REFRESH_SESSION_TIMEOUT

