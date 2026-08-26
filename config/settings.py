import yaml


def load_config(environment: str):
    with open(
        f"config/environments/{environment}.yaml",
        "r"
    ) as file:
        return yaml.safe_load(file)
