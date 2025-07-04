# Plan Manager

A software development plan management program supporting project, category, document, and log management, with AI-powered gRPC plan execution.

## Features

- Project management with customizable development environments and gRPC server config
- Plan category management (prompt templates, method mapping, auto-save, etc.)
- Document management with versioning, tagging, and content search
- Real-time execution log display and historical log archive
- gRPC communication with AI Project Helper server
- Tkinter-based modern UI

## Technology Stack

- **Frontend UI**: Python Tkinter
- **Backend Logic**: Python 3.8+
- **Database**: MySQL 8.0
- **gRPC Communication**: grpcio, grpcio-tools
- **Database Operations**: pymysql
- **Configuration Management**: configparser
- **Multithreading**: threading

## Directory Structure

```
plan_manager/
├── main.py
├── config.py
├── database/
│   ├── __init__.py
│   ├── connection.py
│   └── models.py
├── managers/
│   ├── __init__.py
│   ├── project_manager.py
│   ├── category_manager.py
│   ├── document_manager.py
│   └── log_manager.py
├── grpc_client/
│   ├── __init__.py
│   ├── client.py
│   └── helper_pb2.py
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── project_dialog.py
│   ├── category_dialog.py
│   └── widgets/
│       └── __init__.py
└── utils/
    ├── __init__.py
    └── logger.py
```

## Database Schema

Refer to the `Database Design` section in the documentation for table definitions.

## Built-in Data

### Built-in Plan Categories

```sql
INSERT INTO plan_categories (name, prompt_template, message_method, is_builtin) VALUES
('Requirement Plan', 'Generate a detailed development plan based on the following requirements document:\n\nDevelopment Environment: {env}\n\nRequirements:\n{doc}', 'PlanGetRequest', true),
('Development Plan', 'Execute the following development plan:\n\nDevelopment Environment: {env}\n\nPlan Content:\n{doc}', 'PlanExecuteRequest', true),
('Test Plan', 'Perform testing based on the following test plan:\n\nDevelopment Environment: {env}\n\nTest Content:\n{doc}', 'PlanExecuteRequest', true),
('Rectification Plan', 'Perform code rectification based on the following rectification plan:\n\nDevelopment Environment: {env}\n\nRectification Content:\n{doc}', 'PlanExecuteRequest', true);
```

### System Configuration

```sql
INSERT INTO system_config (config_key, config_value, description) VALUES
('db_host', 'localhost', 'Database host address'),
('db_port', '3306', 'Database port'),
('db_user', 'sa', 'Database username'),
('db_password', 'dm257758', 'Database password'),
('db_name', 'plan_manager', 'Database name'),
('retry_max_count', '3', 'Maximum retry attempts'),
('retry_wait_seconds', '60', 'Retry wait time (seconds)'),
('log_level', 'INFO', 'Log level');
```

## gRPC Server Protocol Reference

See `grpc_client/helper_pb2.py` and your `helper.proto` for actual protocol.

## Getting Started

1. Clone this repo and install dependencies (`pip install -r requirements.txt`)
2. Prepare your MySQL database using the schema in this README.
3. Edit your config in `plan_manager.ini` or via the UI.
4. Run:

```bash
python -m plan_manager.main
```

## License

MIT