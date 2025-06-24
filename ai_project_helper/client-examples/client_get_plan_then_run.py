import grpc
import sys
from datetime import datetime
from ai_project_helper.proto import helper_pb2 as helper_pb2, helper_pb2_grpc

def main():
    if len(sys.argv) < 2:
        print("请传入带路径的txt文件名作为参数")
        return

    plan_path = sys.argv[1]  # 改为从参数获取路径
    with open(plan_path, "r", encoding="utf-8") as f:
        plan_text = f.read()

    with grpc.insecure_channel("localhost:50051") as channel:
        stub = helper_pb2_grpc.AIProjectHelperStub(channel)
        request = helper_pb2.PlanGenerateRequest(
            requirement=plan_text,
            model="GPT-4.1",          # 可以替换
            llm_url="http://43.132.224.225:8000/v1/chat/completions"              # 留空使用默认
        )
        print(f"\n请求生成计划: {plan_path}")
        for feedback in stub.GetPlanThenRun(request):
            print(f"[{feedback.status}] {feedback.step_description}")
            if feedback.output:
                print(f">>> {feedback.output}")

if __name__ == "__main__":
    main()