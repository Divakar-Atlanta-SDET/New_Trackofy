import os

import yaml


def load_config(environment: str):
    with open(
        f"config/environments/{environment}.yaml",
        "r"
    ) as file:
        config = yaml.safe_load(file)

    # Lets large/parallel runs (e.g. full regression via pytest-xdist) force
    # headless without permanently flipping the shared yaml default, which
    # other devs rely on for interactive debugging.
    headless_override = os.getenv("TRACKOFY_HEADLESS")
    if headless_override is not None:
        config["headless"] = headless_override.strip().lower() in ("1", "true", "yes")

    return config
