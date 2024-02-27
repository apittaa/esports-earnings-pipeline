from prefect.deployments import run_deployment


def main():
    run_deployment(name="main-flow-bronze/esports-bronze")
    run_deployment(name="main-flow-silver/esports-silver")
    run_deployment(name="main-flow-gold/esports-gold")
    

if __name__ == "__main__":
    main()
    