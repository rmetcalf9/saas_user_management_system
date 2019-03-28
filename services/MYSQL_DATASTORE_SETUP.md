# Setting up a mysql datastore for use with saas_user_management_system

Commands run as a root user on mysql server (Change schema name, username and password)
```
create database saas_user_management_system CHARACTER SET utf8 COLLATE utf8_general_ci;
## Check it is utf-8
SELECT schema_name, default_character_set_name FROM information_schema.SCHEMATA;
CREATE USER saas_user_management_system_user@'%' IDENTIFIED BY 'dev_machine_pass' REQUIRE SSL;
grant ALL on saas_user_management_system.* TO saas_user_management_system_user@'%';
FLUSH PRIVILEGES;
select host, user, ssl_type from user;
```

Test is is possible to connect to the database using that user by running the following in python3 repl:
```
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

username = 'saas_user_management_system_user'
password = 'dev_machine_pass'
host = '127.0.0.1'
db = 'saas_user_management_system'

url = 'mysql+pymysql://' + username + ':' + password + '@' + host + '/' + db

print('Connecting to ' + url + ' using sqlalchemy')

engine = create_engine(url)

```
