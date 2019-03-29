# Ojbect stores readme

Object stores is a database abstraction layer which I plan to spin off into a seperate python library once it makes sense.

This supports using RDB's as well as object key/value based stores.

It is usually better not to have a database abstraction layer as it means that you lose all the spercific benefits of different storage methods. Early on in the development of projects I am never sure which object store I will need to I built this to allow me to experiment with different setups. If projects get to the point where they need a particular type of store that can't be abstracted I will refactor; removing this abstraction layer. 

It is still beneficial in the early phase of projects to be able to change type of object store used as a configuration option.


## Memory 

### Enviroment Paramaters

```
{
  "Type":"Memory"
}
```

When using the memomory store you still need to use executeInsideTransaction to mutate the datastore however transactions have not been implemented so everything is committed even if it is rolled back.

## SQLAlchmey

### Enviroment Paramaters

APIAPP_OBJECTSTORECONFIG:
```
{
  "Type":"SQLAlchemy",
  "connectionString":"mysql+pymysql://saas_user_man_user:saas_user_man_testing_password@127.0.0.1:10103/saas_user_man",
  "objectPrefix":""   (Optional)
}
```

### Database Setup

Example setting up a development testing MYSQL backend:
```
create database saas_user_man CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
## Check it is utf-8
use mysql;
SELECT schema_name, default_character_set_name FROM information_schema.SCHEMATA;
CREATE USER saas_user_man_user IDENTIFIED BY 'saas_user_man_testing_password' REQUIRE SSL;
grant ALL on saas_user_man.* TO saas_user_man_user@'%';
FLUSH PRIVILEGES;
select host, user, ssl_type from user;
```

SQL Connection string:
```
mysql -h${HOSTIP} -usaas_user_man_user -psaas_user_man_testing_password -P10103
```
