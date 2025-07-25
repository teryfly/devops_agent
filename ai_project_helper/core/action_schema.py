ACTION_SCHEMAS = {
    "shell_command": {
        "name": "shell_command",
        "description": "Execute a shell command.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute"
                },
                "cwd": {
                    "type": "string",
                    "description": "Working directory for the command (optional)"
                }
            },
            "required": ["command"]
        }
    },
    "file_edit": {
        "name": "file_edit",
        "description": "Edit file: create, update, replace, append, or delete.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Operation type for file editing",
                    "enum": ["create", "update", "str_replace", "append", "delete"]
                },
                "path": {"type": "string", "description": "File path"},
                "file_text": {"type": "string", "description": "File content (for create and update)"},
                "old_str": {"type": "string", "description": "String to replace"},
                "new_str": {"type": "string", "description": "Replacement string"},
                "append_text": {"type": "string", "description": "Text to append"}
            },
            "required": ["command", "path"]
        }
    },
    "directory": {
        "name": "directory",
        "description": "Create or delete directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Operation type for directory",
                    "enum": ["create", "mkdir", "delete", "rmdir"]
                },
                "path": {"type": "string", "description": "Directory path"}
            },
            "required": ["command", "path"]
        }
    }
}