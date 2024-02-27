import subprocess

subprocess.run("python flows/bronze/deploy_ingest_bronze.py", shell=True, check=False)
subprocess.run("python flows/silver/deploy_ingest_silver.py", shell=True, check=False)
subprocess.run("python flows/gold/deploy_ingest_gold.py", shell=True, check=False)
