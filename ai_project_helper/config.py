import yaml

def load_config(path="config_ai_project_helper.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)
