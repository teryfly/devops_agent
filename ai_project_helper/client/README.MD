### 一、客户端使用说明

#### 1. 获取项目计划

```
python main.py get-plan \
  --project myproject --requirement-file requirement.txt \
  --model GPT-4.1 \
  --llm-url http://llm-server/v1
```

#### 2. 执行现有计划

```
python main.py execute-plan \
  --project dev-project \
  --plan-file path/to/plan.txt
```

#### 3. 获取并执行计划

```
python main.py get-and-execute \
  --project dev-project --requirement-file requirement.txt
  --model GPT-4.1 \
  --llm-url http://llm-server/v1
```

### 二、客户端日志拼装逻辑

客户端使用 `client/utils.py` 中的 `print_feedback` 函数将 `ActionFeedback` 转换为可读日志：

```
def print_feedback(feedback):
    # 状态图标映射
    status_icons = {
        "running": "🔄",
        "success": "✅",
        "warning": "⚠️",
        "failed": "❌"
    }
    
    # 状态标签映射
    status_labels = {
        "running": "运行中",
        "success": "成功",
        "warning": "警告",
        "failed": "失败"
    }
    
    # 获取状态图标和标签
    icon = status_icons.get(feedback.status.lower(), "❓")
    status_label = status_labels.get(feedback.status.lower(), 
                                   feedback.status.upper())
    
    # 区分计划步骤和执行步骤
    if feedback.action_index < 0:
        step_type = "📝 计划"  # 计划生成阶段
    else:
        step_type = f"🔧 步骤 {feedback.step_index}/{feedback.total_steps}"
    
    # 构建主日志行
    print(f"{icon} [{status_label}] {step_type} - {feedback.step_description}")
    
    # 添加输出内容（截断长文本）
    if feedback.output:
        truncated_output = truncate_long_text(feedback.output)
        print(f"  📤 输出: {truncated_output}")
    
    # 添加错误信息（截断长文本）
    if feedback.error:
        truncated_error = truncate_long_text(feedback.error)
        print(f"  ⚠️ 错误: {truncated_error}")
    
    print("-" * 60)  # 分隔线
```

### 三. 日志拼装示例

#### 计划生成阶段日志：

```
📝 [成功] 📝 计划 - 完整计划生成完毕
```

#### 执行阶段日志：

```
🔄 [运行中] 🔧 步骤 1/33 - file_edit(command='create', path='backend/app/main.py')
  📤 输出: 文件创建成功: /aiWorkDir/my-project-123/backend/app/main.py
------------------------------------------------------------
✅ [成功] 🔧 步骤 1/33 - directory(command='create', path='backend/app/models')
------------------------------------------------------------
❌ [失败] 🔧 步骤 2/33 - shell_command(command='npm install')
  ⚠️ 错误: npm: command not found
------------------------------------------------------------
```

### 四. 服务端返回字段使用场景总结

| 字段名             | 类型   | 使用场景                   | 日志中的表现                 |
| :----------------- | :----- | :------------------------- | :--------------------------- |
| `action_index`     | int32  | 标识当前动作在步骤中的位置 | 用于区分计划生成和执行动作   |
| `action_type`      | string | 动作类型                   | 显示在描述中（如 file_edit） |
| `step_description` | string | 动作描述                   | 日志的核心描述内容           |
| `status`           | string | 执行状态                   | 决定图标和状态标签           |
| `output`           | string | 标准输出                   | 在日志中显示为"输出"         |
| `error`            | string | 错误信息                   | 在日志中显示为"错误"         |
| `command`          | string | 执行的命令                 | 在描述中显示具体命令         |
| `step_index`       | int32  | 当前步骤序号               | 显示在步骤标识中             |
| `total_steps`      | int32  | 总步骤数                   | 显示在步骤标识中             |
| `exit_code`        | int32  | 退出码                     | 用于内部判断，不直接显示     |
| `complete_plan`    | string | 完整计划                   | 保存到文件，不显示在日志     |

### 五. 完整日志生成流程

1. **服务端执行**：
   - Agent 解析计划并执行动作
   - 生成包含详细信息的 `ActionFeedback` 对象
   - 通过 gRPC 流式发送给客户端
2. **客户端处理**：
   - 接收 `ActionFeedback` 流
   - 调用 `print_feedback()` 格式化每条反馈
   - 使用 `save_execution_log()` 保存完整日志
   - 使用 `print_summary()` 显示最终统计信息
3. **用户看到的日志**：
   - 实时显示每个动作的执行状态
   - 成功/失败有明确的视觉标识
   - 长文本自动截断保证可读性
   - 步骤进度清晰可见
   - 错误信息突出显示