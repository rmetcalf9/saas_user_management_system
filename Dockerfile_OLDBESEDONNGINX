FROM nginx:1.23.1-alpine

#docker file for saas_user_management_system microservice
# I have built this as a single container microservice to ease versioning

MAINTAINER Robert Metcalf

##https://vladikk.com/2013/09/12/serving-flask-with-nginx-on-ubuntu/

ENV APP_DIR /app
##web dirs arealso configured in nginx conf
ENV APIAPP_FRONTEND /frontend
ENV APIAPP_FRONTEND_FRONTEND /frontend
ENV APIAPP_FRONTEND_ADMINFRONTEND /adminfrontend


ENV APIAPP_APIURL http://localhost:80/api
ENV APIAPP_APIDOCSURL http://localhost:80/apidocs
ENV APIAPP_FRONTENDURL http://localhost:80/frontend
ENV APIAPP_APIACCESSSECURITY '[]'

ENV APIAPP_DEFAULTMASTERTENANTJWTCOLLECTIONALLOWEDORIGINFIELD "http://localhost"

#Port for python app should always be 80 as this is is hardcoded in nginx config
ENV APIAPP_PORT 80

# APIAPP_MODE is now defined here instead of run_app_docker.sh
#  this is to enable dev mode containers (and avoid dev cors errors)
ENV APIAPP_MODE DOCKER

# APIAPP_VERSION is not definable here as it is read from the VERSION file inside the image

EXPOSE 80


RUN apk add --no-cache bash python3 curl python3-dev build-base linux-headers pcre-dev libffi-dev openldap-dev && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    rm -r /root/.cache && \
    pip3 install --upgrade pip && \
    mkdir ${APP_DIR} && \
    mkdir ${APIAPP_FRONTEND_FRONTEND} && \
    mkdir ${APIAPP_FRONTEND_ADMINFRONTEND} && \
    mkdir /var/log/uwsgi && \
    pip3 install uwsgi && \
    wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem -O /rds-combined-ca-bundle.pem

COPY ./services/src ${APP_DIR}
RUN pip3 install -r ${APP_DIR}/requirements.txt

COPY ./frontend/dist/spa ${APIAPP_FRONTEND_FRONTEND}
COPY ./adminfrontend/dist/spa ${APIAPP_FRONTEND_ADMINFRONTEND}
COPY ./VERSION /VERSION
COPY ./services/run_app_docker.sh /run_app_docker.sh
COPY ./nginx_default.conf /etc/nginx/conf.d/default.conf
COPY ./uwsgi.ini /uwsgi.ini

STOPSIGNAL SIGTERM


CMD ["/run_app_docker.sh"]

# Regular checks. Docker won't send traffic to container until it is healthy
#  and when it first starts it won't check the health until the interval so I can't have
#  a higher value without increasing the startup time
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://127.0.0.1:80/public/web/frontend/index.html?healthcheck=true || exit 1

##docker run --network pythontestingnetwork --rm --name saas_user_management_system -e APIAPP_APIURL=${EXTURL}:${EXTPORT80}/api -e APIAPP_APIDOCSURL=${EXTURL}:${EXTPORT80}/apidocs -e APIAPP_FRONTENDURL=${EXTURL}:${EXTPORT80}/frontend -e APIAPP_MASTERPASSWORDFORPASSHASH=ABC -e APIAPP_DEFAULTHOMEADMINUSERNAME=admin -e APIAPP_DEFAULTHOMEADMINPASSWORD=admin -p 80:80 -d metcarob/saas_user_managmenet_system:latest
