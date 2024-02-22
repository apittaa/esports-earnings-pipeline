from prefect.deployments import Deployment
from prefect.infrastructure.container import DockerContainer
from ingest_silver import main_flow_silver


docker_container_block = DockerContainer.load("esports-pipeline")

esports_silver_deploy = Deployment.build_from_flow(
    flow=main_flow_silver,
    name="esports-silver",
    infrastructure=docker_container_block
)


if __name__ == "__main__":
    esports_silver_deploy.apply()
    