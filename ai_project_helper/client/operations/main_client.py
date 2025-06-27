import argparse
import grpc
from ai_project_helper.proto import helper_pb2
from .client_utils import setup_logging
from .operations import get_plan, execute_plan, get_plan_then_execute

def main():
    # 设置日志
    logger = setup_logging()
    
    # 创建参数解析器
    parser = argparse.ArgumentParser(description="AI项目助手客户端")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 通用参数
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--grpc", default="localhost:50051", help="gRPC服务器地址 (默认: localhost:50051)")
    parent_parser.add_argument("--project", required=True, help="项目ID")
    
    # get-plan 命令
    get_plan_parser = subparsers.add_parser("get-plan", parents=[parent_parser], help="获取项目计划")
    get_plan_parser.add_argument("--requirement", required=True, help="项目需求描述")
    get_plan_parser.add_argument("--model", default="GPT-4.1", help="使用的模型 (默认: GPT-4.1)")
    get_plan_parser.add_argument("--llm-url", default="http://43.132.224.225:8000/v1/chat/completions", 
                                help="LLM API URL (默认: http://43.132.224.225:8000/v1/chat/completions)")
    
    # execute-plan 命令
    execute_plan_parser = subparsers.add_parser("execute-plan", parents=[parent_parser], help="执行现有计划")
    execute_plan_parser.add_argument("--plan-file", required=True, help="计划文件路径")
    
    # get-and-execute 命令
    get_execute_parser = subparsers.add_parser("get-and-execute", parents=[parent_parser], help="获取并执行计划")
    get_execute_parser.add_argument("--requirement", required=True, help="项目需求描述")
    get_execute_parser.add_argument("--model", default="GPT-4.1", help="使用的模型 (默认: GPT-4.1)")
    get_execute_parser.add_argument("--llm-url", default="http://43.132.224.225:8000/v1/chat/completions", 
                                   help="LLM API URL (默认: http://43.132.224.225:8000/v1/chat/completions)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建请求对象
    if args.command == "get-plan":
        request = helper_pb2.PlanGetRequest(
            requirement=args.requirement,
            model=args.model,
            llm_url=args.llm_url,
            project_id=args.project
        )
        operation = get_plan.run_get_plan
    elif args.command == "execute-plan":
        request = helper_pb2.PlanExecuteRequest(
            plan_text=args.plan_file,
            project_id=args.project
        )
        operation = execute_plan.run_execute_plan
    elif args.command == "get-and-execute":
        request = helper_pb2.PlanThenExecuteRequest(
            requirement=args.requirement,
            model=args.model,
            llm_url=args.llm_url,
            project_id=args.project
        )
        operation = get_plan_then_execute.run_get_plan_then_execute
    
    # 创建上下文
    context = {
        "grpc_channel": args.grpc,
        "logger": logger
    }
    
    # 执行操作
    operation(request, context)

if __name__ == "__main__":
    main()