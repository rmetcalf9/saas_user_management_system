# New Instance Setup notes

When I get time I plan to write a setup guide. In the mean time I am putting problems I encountered when setting up second and third instances for future inclusion into the guide.


## originHeader wrong

I spent ages with failed login before I realised the error was the origin was wrong. I was not able to get it working on non-443 port.


## Gateway configuration with Kong

When setup and running it was logging in successfully but on the first service call to the frontend it was instantly going back to the login with session expired.
I determined that the JWT token had no "kong_iss": "kong_iss" token. This was because I configured with gateway configured to {"Type": "none"}.
I changed the config to {"Type": "kong", "kongISS": "kong_iss"}


TODO I think I need to configure a consumer and ACL
