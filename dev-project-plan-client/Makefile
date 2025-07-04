# make proto
PROTOC = python -m grpc_tools.protoc
PROTO_DIR = ./plan_manager/grpc_client

proto:
	$(PROTOC) -I$(PROTO_DIR) --python_out=$(PROTO_DIR) --grpc_python_out=$(PROTO_DIR) $(PROTO_DIR)/helper.proto
