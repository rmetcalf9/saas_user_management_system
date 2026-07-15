import constants
import requests
from datetime import datetime, timedelta, UTC

class AuthProviders_AppleJwtPubKeyCache():
    isAppRunningInTestingMode = None
    cachedKeys = None
    lastLoaded = None
    def __init__(self, isAppRunningInTestingMode=False):
        self.isAppRunningInTestingMode = isAppRunningInTestingMode
        self.cachedKeys = None
        self.lastLoaded = None

    def getKey(self, kid):
        if self.isAppRunningInTestingMode:
            if kid==constants.testmodersakeyforjwtsigning["kid"]:
                return constants.testmodersakeyforjwtsigning

        if self.cachedKeys is None:
            self.loadCachedKeys()

        if kid in self.cachedKeys:
            return self.cachedKeys[kid]

        if self.lastLoaded < datetime.now(UTC) - timedelta(hours=5):
            self.loadCachedKeys()
            if kid in self.cachedKeys:
                return self.cachedKeys[kid]

        return None

    def loadCachedKeys(self):
        response = requests.get(constants.apple_signon_public_key_url, timeout=10)
        response.raise_for_status()
        self.cachedKeys = {
            key["kid"]: key
            for key in response.json()["keys"]
        }
        self.lastLoaded = datetime.now(UTC)