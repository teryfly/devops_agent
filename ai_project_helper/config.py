import os
def load_config(config_path="config_ai_project_helper.yaml"):
    import yaml
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    # 补充: 环境变量覆盖
    cfg['working_dir'] = os.environ.get('AI_PROJECT_HELPER_WORKING_DIR', cfg.get('working_dir'))
    return cfg

# server.py
config = load_config()
print("实际working_dir:", config.get("working_dir"))