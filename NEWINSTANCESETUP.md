# New Instance Setup notes

When I get time I plan to write a setup guide. In the mean time I am putting problems I encountered when setting up second and third instances for future inclusion into the guide.


## originHeader wrong

I spent ages with failed login before I realised the error was the origin was wrong. I was not able to get it working on non-443 port.


## Gateway configuration with Kong

When setup and running it was logging in successfully but on the first service call to the frontend it was instantly going back to the login with session expired.
I determined that the JWT token had no "kong_iss": "kong_iss" token. This was because I configured with gateway configured to {"Type": "none"}.
I changed the config to {"Type": "kong", "kongISS": "kong_iss"}

A consumer needs to be created in Kong.

Create a consumer using algorithm HS256 but don't fill anything in. Once created copy the secret that consumer was assigned.
Setup a secret on the server titled saas_jwtsecret consisting of this string:

```
docker secret create saas_jwtsecret - <<EOF
COPYED_SECRET_FROM_KONGA
EOF
```

You must also create a base64 encoded version of this secret. Do this in python3 as follows:
```
import base64
sec = b'COPYED_SECRET_FROM_KONGA'
base64.b64encode(sec)
```

The output may end with ='s depending on padding.
Take the result (excluding b'')

Create consumer
 - username: saas_user
 - groups: saas_user_management
 - credential -> JWT
   set key to kong_iss, algorithm=HS256, secret=value_from_python_step leave everything else blank
when it is created a secret will be generated. This needs to be converted to base64.
