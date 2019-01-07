export default {
  authproviders: {
    Name: 'usersystem',
    AllowUserCreation: false,
    Description: 'Master Tenant for User Management System',
    AuthProviders: [
      {
        guid: '97aa9ed0-0c22-4ecd-9801-3fa1692acd0e',
        Type: 'internal',
        AllowUserCreation: false,
        IconLink: null,
        ConfigJSON: '{\'userSufix\': \'@internalDataStore\'}',
        MenuText: 'Website account login'
      }
    ]
  }
}
