FROM prefecthq/prefect:2.14.13-python3.10

COPY docker_requirements.txt .

RUN apt-get update && apt-get install -y wget openjdk-17-jdk-headless

ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64

RUN pip install -r docker_requirements.txt --trusted-host pypi.python.org --no-cache-dir

COPY flows /opt/prefect/flows
COPY data /opt/prefect/data
COPY .env /opt/prefect
COPY credentials /opt/prefect/credentials
COPY utils /opt/prefect/utils
COPY dbt /opt/prefect/dbt

# ENTRYPOINT ["prefect", "agent", "start", "-q", "default"]
