-- Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    dev_environment VARCHAR(500) NOT NULL COMMENT 'Development language and environment',
    grpc_server_address VARCHAR(255) NOT NULL DEFAULT '192.168.120.238:50051',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
ALTER TABLE `projects` ADD COLUMN `llm_model` VARCHAR(64) DEFAULT NULL;
ALTER TABLE `projects` ADD COLUMN `llm_url` VARCHAR(128) DEFAULT NULL;

-- Plan Categories Table
CREATE TABLE IF NOT EXISTS plan_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    prompt_template TEXT NOT NULL COMMENT 'Prompt template supporting {doc} and {env} placeholders',
    message_method VARCHAR(100) NOT NULL COMMENT 'gRPC method name',
    auto_save_category_id INT NULL COMMENT 'Category ID for auto-saving',
    is_builtin BOOLEAN DEFAULT FALSE COMMENT 'Whether it is a built-in category',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Plan Documents Table (先创建，不包含外键到execution_logs)
CREATE TABLE IF NOT EXISTS plan_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    category_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    content LONGTEXT NOT NULL,
    version INT NOT NULL DEFAULT 1,
    source ENUM('user', 'server','chat') NOT NULL DEFAULT 'user',
    related_log_id INT NULL COMMENT 'Related execution log ID',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES plan_categories(id),
    INDEX idx_project_category (project_id, category_id),
    INDEX idx_created_time (created_time)
);

-- Execution Logs Table
CREATE TABLE IF NOT EXISTS execution_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    request_time DATETIME NOT NULL,
    request_content_size INT NOT NULL,
    duration_ms INT NULL COMMENT 'Execution duration in milliseconds',
    has_error BOOLEAN DEFAULT FALSE,
    server_response LONGTEXT NULL COMMENT 'Complete server response',
    error_message TEXT NULL,
    status ENUM('running', 'completed', 'failed') DEFAULT 'running',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_time DATETIME NULL,
    FOREIGN KEY (document_id) REFERENCES plan_documents(id) ON DELETE CASCADE,
    INDEX idx_document_time (document_id, request_time)
);

-- Document Tags Table
CREATE TABLE IF NOT EXISTS document_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    tag_name VARCHAR(100) NOT NULL,
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES plan_documents(id) ON DELETE CASCADE,
    UNIQUE KEY unique_doc_tag (document_id, tag_name)
);

-- System Configuration Table
CREATE TABLE IF NOT EXISTS system_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    description VARCHAR(255),
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 添加外键约束到plan_categories的auto_save_category_id
ALTER TABLE plan_categories 
ADD CONSTRAINT fk_category_auto_save 
FOREIGN KEY (auto_save_category_id) REFERENCES plan_categories(id);

-- 添加外键约束到plan_documents的related_log_id (可选的外键)
ALTER TABLE plan_documents 
ADD CONSTRAINT fk_document_log 
FOREIGN KEY (related_log_id) REFERENCES execution_logs(id) ON DELETE SET NULL;

-- Built-in Plan Categories
INSERT INTO plan_categories (name, prompt_template, message_method, is_builtin) VALUES
('需求计划', '请根据以下需求文档生成详细的开发计划：\n\n开发环境：{env}\n\n需求内容：\n{doc}', 'PlanGetRequest', true),
('开发计划', '请执行以下开发计划：\n\n开发环境：{env}\n\n计划内容：\n{doc}', 'PlanExecuteRequest', true),
('测试计划', '请根据以下测试计划进行测试：\n\n开发环境：{env}\n\n测试内容：\n{doc}', 'PlanExecuteRequest', true),
('整改计划', '请根据以下整改计划进行代码整改：\n\n开发环境：{env}\n\n整改内容：\n{doc}', 'PlanExecuteRequest', true)
ON DUPLICATE KEY UPDATE name=name;

-- System Configuration Data
INSERT INTO system_config (config_key, config_value, description) VALUES
('db_host', 'localhost', 'Database host address'),
('db_port', '3306', 'Database port'),
('db_user', 'sa', 'Database username'),
('db_password', 'dm257758', 'Database password'),
('db_name', 'plan_manager', 'Database name'),
('retry_max_count', '3', 'Maximum retry attempts'),
('retry_wait_seconds', '60', 'Retry wait time (seconds)'),
('log_level', 'INFO', 'Log level')
ON DUPLICATE KEY UPDATE config_key=config_key;

-- Conversations and Messages Tables

CREATE TABLE IF NOT EXISTS conversations (
    id VARCHAR(64) PRIMARY KEY,
    system_prompt TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    conversation_id VARCHAR(64),
    role VARCHAR(32),
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

ALTER TABLE conversations
ADD COLUMN project_id INT NOT NULL DEFAULT 0
ADD COLUMN name VARCHAR(32) DEFAULT NULL COMMENT '会话名称',
ADD COLUMN assistance_role VARCHAR(16) DEFAULT NULL COMMENT '助手角色',
ADD COLUMN model VARCHAR(64) DEFAULT NULL COMMENT '使用的模型名称';


