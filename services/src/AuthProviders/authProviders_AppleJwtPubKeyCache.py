import constants
import requests
from datetime import datetime, timedelta, timezone
import threading

class AuthProviders_AppleJwtPubKeyCache():
    def __init__(self, isAppRunningInTestingMode=False):
        self.isAppRunningInTestingMode = isAppRunningInTestingMode
        self.cachedKeys = None
        self.lastSuccessfulLoad = None
        self.lastRefreshAttempt = None
        self.refreshLock = threading.Lock()

    def getKey(self, kid):
        if self.isAppRunningInTestingMode:
            if kid==constants.testmodersakeyforjwtsigning["kid"]:
                return constants.testmodersakeyforjwtsigning

        if self.cachedKeys is None:
            self.loadCachedKeys()

        if kid in self.cachedKeys:
            return self.cachedKeys[kid]

        #
        # Unknown kid.
        # This can happen when Apple rotates signing keys.
        #
        # Try refreshing, but rate limit refresh attempts.
        #
        if self.canRefreshKeys():
            self.loadCachedKeys()

            if kid in self.cachedKeys:
                return self.cachedKeys[kid]

        return None

    def canRefreshKeys(self):
        now = datetime.now(timezone.utc)
        if self.lastRefreshAttempt is None:
            return True
        # Prevent repeated refresh attempts
        # caused by attacker-controlled random kid values
        if self.lastRefreshAttempt > now - timedelta(minutes=10):
            return False
        return True

    def loadCachedKeys(self):
        # Only one thread should refresh
        with self.refreshLock:
            # Another thread may have refreshed while we waited
            # on the lock.
            if self.cachedKeys is not None:
                if (
                    self.lastRefreshAttempt is not None and
                    self.lastRefreshAttempt > datetime.now(timezone.utc) - timedelta(minutes=1)
                ):
                    return
            self.lastRefreshAttempt = datetime.now(timezone.utc)
            response = requests.get(
                constants.apple_signon_public_key_url,
                timeout=20
            )
            response.raise_for_status()
            keys = response.json()["keys"]
            self.cachedKeys = {
                key["kid"]: key
                for key in keys
            }
            self.lastSuccessfulLoad = datetime.now(timezone.utc)
