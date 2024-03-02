from prefect.deployments import Deployment
from prefect.infrastructure.container import DockerContainer
from ingest_gold import main_flow_gold


docker_container_block = DockerContainer.load("docker-esports-pipeline")

esports_gold_deploy = Deployment.build_from_flow(
    flow=main_flow_gold,
    name="esports-gold",
    infrastructure=docker_container_block
)


if __name__ == "__main__":
    esports_gold_deploy.apply()
    