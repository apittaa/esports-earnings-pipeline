import subprocess

print('LOGGING: Deploying bronze flow')
subprocess.run("python flows/bronze/deploy_ingest_bronze.py", shell=True, check=False)
print('LOGGING: Deploying silver flow')
subprocess.run("python flows/silver/deploy_ingest_silver.py", shell=True, check=False)
print('LOGGING: Deploying gold flow')
subprocess.run("python flows/gold/deploy_ingest_gold.py", shell=True, check=False)
print('LOGGING: ENDING DEPLOYMENTS')
