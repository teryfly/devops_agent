### 客户端使用说明

#### 1. 获取项目计划

```
python main_client.py get-plan \
  --project my-project-123 \
  --requirement "创建一个Flask Web应用，包含用户认证功能" \
  --model GPT-4.1 \
  --llm-url http://llm-server/v1
```

#### 2. 执行现有计划

```
python main_client.py execute-plan \
  --project my-project-123 \
  --plan-file path/to/plan.txt
```

#### 3. 获取并执行计划

```
python main_client.py get-and-execute \
  --project my-project-123 \
  --requirement "创建一个Flask Web应用，包含用户认证功能" \
  --model GPT-4.1 \
  --llm-url http://llm-server/v1
```