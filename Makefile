# 每次修改了 ai_project_helper/proto/agent.proto 后，只需在项目根目录运行：
# make proto
PROTOC = python -m grpc_tools.protoc
PROTO_DIR = ./ai_project_helper/proto

proto:
	$(PROTOC) -I$(PROTO_DIR) --python_out=$(PROTO_DIR) --grpc_python_out=$(PROTO_DIR) $(PROTO_DIR)/helper.proto
