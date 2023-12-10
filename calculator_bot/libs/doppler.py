from os import environ, getenv

from dopplersdk import DopplerSDK


def set_env_vars(doppler_required: bool) -> None:
    token = getenv("DOPPLER_TOKEN")
    if not token:
        if doppler_required:
            raise RuntimeError("DOPPLER_TOKEN env variable is not set")
        return

    doppler = DopplerSDK(token)
    projects = doppler.projects.list()
    if not projects.projects:
        raise RuntimeError("No projects found in Doppler")

    project = projects.projects[0]["id"]
    configs = doppler.configs.list(project)
    if not configs.configs:
        raise RuntimeError("No configs found in Doppler")

    config = configs.configs[0]["name"]
    secrets = doppler.secrets.list(config, project)
    for secret, secret_data in secrets.secrets.items():
        environ[secret] = secret_data["computed"]
