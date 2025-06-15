import grpc
from ai_project_helper.proto import helper_pb2 as helper_pb2, helper_pb2_grpc

def main():

    plan_path = "examples/f.txt"
    with open(plan_path, "r", encoding="utf-8") as f:
        plan_text = f.read()

    with grpc.insecure_channel("localhost:50051") as channel:
        stub = helper_pb2_grpc.AIProjectHelperStub(channel)
        request = helper_pb2.PlanGenerateRequest(
            requirement=plan_text,
            model="seek70b",          # 可以替换
            llm_url=""              # 留空使用默认
        )
        print(f"Requesting plan generation for:\n{plan_text}\n")
        for feedback in stub.GetPlanThenRun(request):
            print(f"[{feedback.status}] {feedback.step_description}")
            if feedback.output:
                print(f">>> {feedback.output}")
if __name__ == "__main__":
    main()