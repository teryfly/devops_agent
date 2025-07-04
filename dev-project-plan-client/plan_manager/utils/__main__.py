# For command-line launch: python -m plan_manager.utils
# Demo: print_feedback usage

from .print_feedback import print_feedback

if __name__ == "__main__":
    # Example feedback dicts
    feedbacks = [
        {
            "action_index": -1,
            "step_description": "Complete plan generated",
            "status": "success",
            "output": "",
            "error": "",
        },
        {
            "action_index": 0,
            "action_type": "file_edit",
            "step_description": "file_edit(command='create', path='backend/app/main.py')",
            "status": "running",
            "output": "File created successfully: /aiWorkDir/my-project-123/backend/app/main.py",
            "error": "",
            "step_index": 1,
            "total_steps": 33
        },
        {
            "action_index": 1,
            "action_type": "directory",
            "step_description": "directory(command='create', path='backend/app/models')",
            "status": "success",
            "output": "",
            "error": "",
            "step_index": 1,
            "total_steps": 33
        },
        {
            "action_index": 2,
            "action_type": "shell_command",
            "step_description": "shell_command(command='npm install')",
            "status": "failed",
            "output": "",
            "error": "npm: command not found",
            "step_index": 2,
            "total_steps": 33
        }
    ]
    for fb in feedbacks:
        print_feedback(fb)