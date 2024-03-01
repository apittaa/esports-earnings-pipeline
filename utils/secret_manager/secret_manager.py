import json

from dotenv import dotenv_values

from google.cloud import secretmanager
from google.api_core.exceptions import PermissionDenied, NotFound


def upload_env_to_secret_manager(project_id, secret_id, env_file_path, service_account_file=None):
    """
    Uploads the contents of a .env file to Google Secret Manager as a single secret with multiple variables.

    Args:
        project_id (str): Google Cloud project ID.
        secret_id (str): ID for the secret in Secret Manager.
        env_file_path (str): Path to the .env file to be uploaded.
        service_account_file (str, optional): Path to the service account key file. Default is None.

    Returns:
        bool: True if the upload is successful, False otherwise.
        str: Error message if the upload fails.
    """
    try:
        # Load .env file
        env_file = dotenv_values(env_file_path)

        # Initialize the Secret Manager client with the service account key file if provided
        if service_account_file:
            client = secretmanager.SecretManagerServiceClient.from_service_account_file(service_account_file)
        else:
            client = secretmanager.SecretManagerServiceClient()

        # Check if the secret exists, create it if not
        parent = f"projects/{project_id}"
        secret_name = f"{parent}/secrets/{secret_id}"
        try:
            client.get_secret(name=secret_name)
        except NotFound:
            try:
                client.create_secret(
                    parent=parent,
                    secret_id=secret_id,
                    secret={"replication":{"automatic":{}}}
                )
            except PermissionDenied:
                return False, "Error: Permission denied. Make sure the service account has the necessary permissions to create secrets."

        # Create the payload with all key-value pairs from the .env file
        # payload = '\n'.join(f"{key}={value}" for key, value in env_file.items())

        # Create the secret version
        parent = f"projects/{project_id}/secrets/{secret_id}"
        response = client.add_secret_version(parent=parent, payload={"data": json.dumps(dict(env_file)).encode('utf-8')})
        print(f'Secret version {response.name} created.')

        print("All secrets uploaded to Secret Manager successfully.")
        return True, None

    except FileNotFoundError:
        error_message = f"Error: The .env file '{env_file_path}' does not exist."
        return False, error_message

    except Exception as e:
        error_message = f"Error: An unexpected error occurred: {str(e)}"
        return False, error_message

# Example usage:
project_id = "esports-earnings-pipeline"
secret_id = "esports-pipeline-env"
env_file_path = ".env"

success, message = upload_env_to_secret_manager(project_id, secret_id, env_file_path)
if success:
    print("Secrets uploaded successfully.")
else:
    print(f"Failed to upload secrets: {message}")


def load_secret(project_id, secret_id, version_id="latest", service_account_file=None):
    """
    Loads a secret from Google Secret Manager.

    Args:
        project_id (str): Google Cloud project ID.
        secret_id (str): ID for the secret in Secret Manager.
        version_id (str, optional): Version ID of the secret to retrieve. Default is "latest".
        service_account_file (str, optional): Path to the service account key file. Default is None.

    Returns:
        str: The value of the secret.
        str: Error message if loading the secret fails.
    """
    try:
        # Initialize the Secret Manager client with the service account key file if provided
        if service_account_file:
            client = secretmanager.SecretManagerServiceClient.from_service_account_file(service_account_file)
        else:
            client = secretmanager.SecretManagerServiceClient()

        # Build the resource name for the secret
        secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

        # Access the secret version
        response = client.access_secret_version(name=secret_name)
        payload = response.payload.data.decode('UTF-8')

        return payload, None

    except Exception as e:
        error_message = f"Error: An unexpected error occurred: {str(e)}"
        return None, error_message

# Example usage:
project_id = "esports-earnings-pipeline"
secret_id = "esports-pipeline-env"

secret_value, error_message = load_secret(project_id, secret_id)
if secret_value is not None:
    print("Secret loaded successfully:", json.loads(secret_value)["API_KEY"])
else:
    print("Failed to load secret:", error_message)
