# Run development locally

This runs all the parts locally on the machine.


Make sure setting in saasApilClient.js in adminfrontend is correct
  - const loginFrontendIsDev = true
it should be true

The main file
./run_all_parts_on_dev_machine.sh should work.

Login to admin frontend to test http://localhost:8082/


The three components will be running on these ports:
frontend -> runs on port 8081
adminfrontend -> runs on port 8082
APIServer -> runs on port 8098

## How does frontend (or any app) know which login service to connect to

This is done in the saasApiClinet.js function. It calls registerLoginEndpoint
but it is different depending on if the site is in proddomain or not.
