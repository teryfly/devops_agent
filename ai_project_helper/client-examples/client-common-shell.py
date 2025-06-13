import grpc

from ai_project_helper.proto import helper_pb2 as helper_pb2, helper_pb2_grpc
def main():
    plan_path = "examples/2.txt"
    with open(plan_path, "r", encoding="utf-8") as f:
        plan_text = f.read()

    with grpc.insecure_channel("localhost:50051") as channel:
        stub = helper_pb2_grpc.AIProjectHelperStub(channel)
        request = helper_pb2.PlanRequest(plan_text=plan_text)
        print("=== 任务："+plan_path+" 已提交,开始执行===\n")
   
        for feedback in stub.RunPlan(request):
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