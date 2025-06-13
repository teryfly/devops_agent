import grpc
from ai_project_helper.proto import helper_pb2, helper_pb2_grpc

def main():
    steps_path = "examples/1.txt"
    with open(steps_path, "r", encoding="utf-8") as f:
        steps_text = f.read()

    with grpc.insecure_channel("localhost:50051") as channel:
        stub = helper_pb2_grpc.AIProjectHelperStub(channel)
        request = helper_pb2.ProjectRequest(project_steps=steps_text)
        print("=== 新建项目任务已提交，开始执行 ===\n")
        for feedback in stub.CreateProject(request):
            print(f"Step [{feedback.action_index}] [{feedback.status}] {feedback.action_type}: {feedback.step_description}")
            if feedback.command:
                print(f"  COMMAND: {feedback.command}")
            if feedback.output:
                print(f"  OUT: {feedback.output}", end="")
            if feedback.error:
                print(f"  ERR: {feedback.error}", end="")
            print("-" * 60)

if __name__ == "__main__":
    main()