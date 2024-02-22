from prefect.deployments import Deployment
from prefect.infrastructure.container import DockerContainer
from ingest_bronze import main_flow_bronze


docker_container_block = DockerContainer.load("esports-pipeline")

esports_bronze_deploy = Deployment.build_from_flow(
    flow=main_flow_bronze,
    name="esports-bronze",
    infrastructure=docker_container_block
)


if __name__ == "__main__":
    esports_bronze_deploy.apply()
    