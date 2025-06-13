# 统一别名&注册机制
import logging
from .shell import ShellCommandAction
from .file_edit import FileEditAction
from .directory import DirectoryAction

logger = logging.getLogger("ai_project_helper.actions")

# 别名统一到核心功能，避免重复
ACTION_TYPE_ALIAS = {
    "run_command": "shell_command",
    "shell_command": "shell_command",
    "execute_bash": "shell_command",
    "npm_install": "shell_command",
    "npm_init": "shell_command",
    "create_directory": "directory",
    "mkdir": "directory",
    "delete_directory": "directory",
    "write_file": "file_edit",
    "edit_file": "file_edit",
    "str_replace_editor": "file_edit",
    "append_file": "file_edit",
    "file": "file_edit",
    # ...其他action别名
}

ACTION_REGISTRY = {
    "shell_command": ShellCommandAction,
    "file_edit": FileEditAction,
    "directory": DirectoryAction,
    # ...后续直接注册
}

def get_action_class(action_type: str):
    canonical = ACTION_TYPE_ALIAS.get(action_type, action_type)
    if canonical not in ACTION_REGISTRY:
        logger.error(f"Unknown action_type: {action_type} (canonical: {canonical}). Known types: {list(ACTION_REGISTRY.keys())}")
        raise KeyError(f"Unknown action_type: {action_type} (canonical: {canonical})")
    return ACTION_REGISTRY[canonical]
