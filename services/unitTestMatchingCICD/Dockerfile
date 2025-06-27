# Dockerfile.tests
ARG BASE_IMAGE=python:3.10
FROM ${BASE_IMAGE}

COPY src_requirements.txt src_requirements.txt
COPY container_requirements.txt container_requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r ./src_requirements.txt && \
    pip install --no-cache-dir -r ./container_requirements.txt

# Set default env var, override if needed at runtime
ENV SKIPSQLALCHEMYTESTS=Y

# Default command (can be overridden)
CMD ["python3", "-m", "pytest", "./test", "--maxfail=1"]
