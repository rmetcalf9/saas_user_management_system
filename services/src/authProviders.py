#Provides auth provider functions
from authProviders_Internal import authProviderInternal
    
def authProviderFactory(type, configJSON):
  if type=='internal':
    return authProviderInternal('internal', configJSON)
  return None
  
  
