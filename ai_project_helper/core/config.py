# core/config.py

import yaml
import os

def load_config(config_path="config_ai_project_helper.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    # 允许环境变量覆盖
    config['working_dir'] = os.environ.get("AI_HELPER_WORKING_DIR", config.get('working_dir'))
    return config
