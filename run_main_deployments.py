from prefect.deployments import run_deployment


def main():
    print('LOGGING: Running esports bronze flow')
    run_deployment(name="main-flow-bronze/esports-bronze")
    print('LOGGING: Running esports silver flow')
    run_deployment(name="main-flow-silver/esports-silver")
    print('LOGGING: Running esports gold flow')
    run_deployment(name="main-flow-gold/esports-gold")
    print('LOGGING: ENDING FLOWS')
    

if __name__ == "__main__":
    main()
    