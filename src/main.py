import os
import sys
import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

DOWNLOAD_TYPES = ["YAML", "HELM"]
YAML_URL = "api/v31.02/defenders/daemonset.yaml"
YAML_FILE_FILENAME = "prisma_cloud_daemonset.yaml"
HELM_CHART_FILENAME = "prisma_cloud_helm_chart"
AUTH_URL = "api/v31.02/authenticate"
HELM_DEPLOYMENT_URL = "api/v31.02/defenders/helm/twistlock-defender-helm.tar.gz"

HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}

PAYLOAD = {
    "consoleAddr": "",
    "namespace": "twistlock",
    "orchestration": "kubernetes",
    "selinux": False,
    "containerRuntime": "containerd",
    "privileged": False,
    "serviceAccounts": True,
    "istio": False,
    "collectPodLabels": False,
    "proxy": None,
    "taskName": None,
    "gkeAutopilot": False,
}


def _get_env_var(env_var_name):
    try:
        env_var_data = os.environ[env_var_name]

    except KeyError:
        sys.exit(f'Error: Please set the "{env_var_name}" environment variable')

    return env_var_data


def _get_token(prisma_console_url, access_key_id, secret_access_key):
    payload = {
        "username": access_key_id,
        "password": secret_access_key,
    }

    auth_url = f"{prisma_console_url}/{AUTH_URL}"
    token = requests.post(auth_url, headers=HEADERS, json=payload, verify=False).json()[
        "token"
    ]

    return token


def _download_file(auth_headers, download_url):
    payload = dict(PAYLOAD)
    console_url = download_url[8:].rsplit("/", 6)[0]
    payload["consoleAddr"] = console_url

    response = requests.post(
        download_url,
        headers=auth_headers,
        json=payload,
        verify=False,
    )

    if response.status_code != 200:
        print(f"Failed to download the file. Status code: {response.status_code}")
        sys.exit()

    return response


def main():
    download_type = _get_env_var("DOWNLOAD_TYPE").upper()
    if download_type not in DOWNLOAD_TYPES:
        sys.exit(f"Error: DOWNLOAD_TYPE {download_type} is not supported.")

    prisma_console_url = _get_env_var("PRISMA_CONSOLE_URL")
    prisma_access_key_id = _get_env_var("PRISMA_ACCESS_KEY_ID")
    prisma_secret_access_key = _get_env_var("PRISMA_SECRET_ACCESS_KEY")

    token = _get_token(
        prisma_console_url, prisma_access_key_id, prisma_secret_access_key
    )

    auth_headers = dict(HEADERS)
    auth_headers["Authorization"] = f"Bearer {token}"

    if download_type == "HELM":
        download_url = f"{prisma_console_url}/{HELM_DEPLOYMENT_URL}"
        response = _download_file(auth_headers, download_url)

        with open(HELM_CHART_FILENAME, "wb") as file:
            file.write(response.content)

        print(f'Helm chart "{HELM_CHART_FILENAME}" downloaded successfully.')
        sys.exit()

    elif download_type == "YAML":
        download_url = f"{prisma_console_url}/{YAML_URL}"
        response = _download_file(auth_headers, download_url)

        with open(YAML_FILE_FILENAME, "w") as output_file:
            output_file.write(response.text)

        print(f'Daemonset "{YAML_FILE_FILENAME}" downloaded successfully.')
        sys.exit()


if __name__ == "__main__":
    main()
