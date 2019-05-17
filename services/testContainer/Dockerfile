#This dockerfile builds a container image with python and rednose installed so we can test
# another built container.
# it it is designed to be launched and linked to the running container to preform the tests
# source code is not embedded in the image - it is attached

FROM alpine
MAINTAINER Robert Metcalf

COPY ./requirements.txt /requirements.txt

RUN apk add --no-cache bash python3 curl python3-dev build-base linux-headers pcre-dev libffi-dev && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    rm -r /root/.cache && \
    pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

COPY . /ext_volume


##Steps to run tests on local machine
## use run_localbuild_contianer.sh to start the service then run the following commands:
##docker build . -t metcarob/saas_user_management_systemtest:latest
##docker run --rm --network main_net -e BASEURL_TO_TEST=http://saas_user_management_system_$(cat ../../VERSION | tr '.' '_')_localbuild -e EXPECTED_CONTAINER_VERSION=$(cat ../../VERSION) -e APIAPP_DEFAULTHOMEADMINUSERNAME=admin -e APIAPP_DEFAULTHOMEADMINPASSWORD=admin --mount type=bind,source=$(pwd),target=/ext_volume metcarob/saas_user_management_systemtest:latest nosetests --rednose /ext_volume


##Simple curl test
##docker run --rm --network main_net -e BASEURL_TO_TEST=http://saas_user_management_system_$(cat ../../VERSION | tr '.' '_')_localbuild -e--mount type=bind,source=$(pwd),target=/ext_volume metcarob/saas_user_management_systemtest:latest curl ${BASEURL_TO_TEST}/public/web/apidocs/



