RJM_PYTHON_TEST_IMAGE="python:3.8.13-slim"
CURRENT_DIR=$(shell pwd)
CMD_TO_RUN_IN_DOCKER_CODEFRESH_UNIT_TEST="pip3 install --no-cache-dir -r ./src/requirements.txt && pip3 install --no-cache-dir -r ./testContainer/requirements.txt && export SKIPSQLALCHEMYTESTS=Y && python3 -m pytest ./test"

codefresh_unit_test:
	@echo "Make target to simulate codefresh unit_test stage"
	@docker run --rm \
		-v ${CURRENT_DIR}:/main_clone \
		-w /main_clone/services \
		--entrypoint /bin/bash \
		${RJM_PYTHON_TEST_IMAGE} \
		-c ${CMD_TO_RUN_IN_DOCKER_CODEFRESH_UNIT_TEST}
