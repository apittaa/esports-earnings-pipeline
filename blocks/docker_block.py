from prefect.infrastructure.docker import DockerContainer


docker_block = DockerContainer(
    image="devpitta/prefect:esports_pipeline",
    image_pull_policy="ALWAYS",
    auto_remove=True,
)

docker_block.save("esports-pipeline", overwrite=True)
