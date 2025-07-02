import os
import sys
import argparse
import grpc

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_project_helper.client.utils import setup_logging
from ai_project_helper.client.operations import (
    get_plan,
    execute_plan,
    get_plan_then_execute
)
from ai_project_helper.proto import helper_pb2

def read_requirement_file(file_path):
    """读取需求文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"需求文件 {file_path} 不存在")
    except Exception as e:
        raise Exception(f"读取需求文件失败: {str(e)}")

def main():
    # 设置日志
    logger = setup_logging()
    
    # 创建参数解析器
    parser = argparse.ArgumentParser(description="AI项目助手客户端")
    subparsers = parser.add_subparsers(dest="command", help="可用命令: A(get-plan), B(execute-plan), AB(get-and-execute)")
    
    # 通用参数
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--grpc", default="localhost:50051", 
                             help="gRPC服务器地址 (默认: localhost:50051)")
    parent_parser.add_argument("--N", dest="project", required=True, help="项目ID")
    parent_parser.add_argument("--F", dest="file_path", required=True, help="文件路径")
    
    # A: get-plan 命令
    get_plan_parser = subparsers.add_parser("A", parents=[parent_parser], 
                                          help="获取项目计划")
    get_plan_parser.add_argument("--model", default="GPT-4.1", 
                               help="使用的模型 (默认: GPT-4.1)")
    get_plan_parser.add_argument("--llm-url", 
                               default="http://43.132.224.225:8000/v1/chat/completions", 
                               help="LLM API URL")
    
    # B: execute-plan 命令
    execute_plan_parser = subparsers.add_parser("B", parents=[parent_parser], 
                                              help="执行现有计划")
    
    # AB: get-and-execute 命令
    get_execute_parser = subparsers.add_parser("AB", parents=[parent_parser], 
                                             help="获取并执行计划")
    get_execute_parser.add_argument("--model", default="GPT-4.1", 
                                  help="使用的模型 (默认: GPT-4.1)")
    get_execute_parser.add_argument("--llm-url", 
                                  default="http://43.132.224.225:8000/v1/chat/completions", 
                                  help="LLM API URL")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建上下文
    context = {
        "grpc_channel": args.grpc,
        "logger": logger
    }
    
    # 根据命令执行相应操作
    try:
        if args.command == "A":
            requirement_text = read_requirement_file(args.file_path)
            request = helper_pb2.PlanGetRequest(
                requirement=requirement_text,
                model=args.model,
                llm_url=args.llm_url,
                project_id=args.project
            )
            get_plan.run_get_plan(request, context)
            
        elif args.command == "B":
            request = helper_pb2.PlanExecuteRequest(
                plan_text=args.file_path,
                project_id=args.project
            )
            execute_plan.run_execute_plan(request, context)
            
        elif args.command == "AB":
            requirement_text = read_requirement_file(args.file_path)
            request = helper_pb2.PlanThenExecuteRequest(
                requirement=requirement_text,
                model=args.model,
                llm_url=args.llm_url,
                project_id=args.project
            )
            get_plan_then_execute.run_get_plan_then_execute(request, context)
    
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        logger.error(f"操作失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()