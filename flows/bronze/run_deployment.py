from prefect.deployments import run_deployment


def main():
    run_deployment(name="main-flow-bronze/esports-bronze")
    

if __name__ == "__main__":
    main()
    