
## 前置条件

# 首次或每次你修改了 devops_agent/ai_project_helper/proto/agent.proto 后，只需在项目根目录(devops_agent)运行：
```sh
make proto
```
# 会重新生成或覆盖 agent_pb2.py 和 agent_pb2_grpc.py 到 devops_agent/proto/ 目录。
# 然后替换 agent_pb2_grpc.py 中的import为 :
```python
from ai_project_helper.proto import helper_pb2 as helper__pb2
```

## Quickstart
1. Install (after  generates *_pb2.py files):
   ```sh
   pip install .
   pip install -e .
   ```

2. Start the agent server:
   ```sh
   python -m devops_agent.server
   ```

3. Connect and submit a plan (see `examples/plan.txt`).

## Features

- Input: Free-form dev plans (natural language)
- Output: Structured actions + real-time execution feedback
- Extensible: Easily add new actions
- Powered by local LLM via [litellm proxy](https://github.com/BerriAI/litellm)
- Communication: gRPC streaming

## Example Usage

See `examples/` and `client.py` for a complete example.

### Streaming Feedback

For each action, the feedback includes:
- Status (`pending`, `running`, `success`, `failed`)
- Step description
- Terminal output and error (streamed)
- **Exact command being executed (if applicable)**
