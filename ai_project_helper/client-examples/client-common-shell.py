import grpc
import sys
from datetime import datetime
from collections import defaultdict
from ai_project_helper.proto import helper_pb2 as helper_pb2, helper_pb2_grpc
import re
import ast

def count_lines_in_file_text(file_text):
    """计算文件内容的行数"""
    if not file_text:
        return 0
    return len(file_text.splitlines())

def parse_file_edit_description(step_desc):
    """
    解析file_edit操作的描述，提取文件内容并计算行数
    返回格式为 "file_edit: 约x行"
    """
    match = re.search(r'file_edit\(\s*({.*?})\s*\)', step_desc, re.DOTALL)
    if match:
        dict_str = match.group(1)
        try:
            params = ast.literal_eval(dict_str)
            if 'file_text' in params:
                line_count = count_lines_in_file_text(params['file_text'])
                command_type = params.get('command', '')
                return f"file_edit({command_type}): 约{line_count}行"
        except (SyntaxError, ValueError):
            pass
    return "file_edit: ..."

def truncate_long_text(text, max_length=100):
    """截断长文本用于显示"""
    if len(text) > max_length:
        return text[:max_length] + f"... [总长度: {len(text)}]"
    return text

def print_feedback(feedback):
    # 状态图标
    status_icons = {
        "running": "🔄",
        "success": "✅",
        "warning": "⚠️",
        "failed": "❌"
    }
    icon = status_icons.get(feedback.status.lower(), "❓")
    
    # 步骤类型：计划还是执行
    step_type = "📝 计划" if feedback.action_index < 0 else "🔧 执行"
    
    # 直接使用 step_description 作为描述
    description = feedback.step_description
    
    # 组合输出
    print(f"{icon} {step_type} - {description}")
    
    # 如果有命令，打印命令
    if feedback.command:
        print(f"  🖥️ 命令: {feedback.command}")
    
    # 输出处理 - 仅在客户端显示时截断
    if feedback.output:
        truncated_output = truncate_long_text(feedback.output)
        print(f"  📤 输出: {truncated_output}")
    
    # 错误/警告处理 - 仅在客户端显示时截断
    if feedback.error:
        truncated_error = truncate_long_text(feedback.error)
        print(f"  ⚠️ 错误: {truncated_error}")
    
    print("-" * 60)


def print_summary(statistics, duration):
    """打印执行结果汇总"""
    print("\n" + "=" * 60)
    print(f"🏁 执行完成! 总耗时: {duration:.2f}秒")
    print("📊 执行统计:")
    
    # 步骤类型统计
    print(f"  步骤总数: {statistics['total_steps']}")
    print(f"  动作总数: {statistics['total_actions']}")
    print(f"  ✅ 成功步骤: {statistics['success_steps']}")
    print(f"  ⚠️ 警告步骤: {statistics['warning_steps']}")
    print(f"  ❌ 失败步骤: {statistics['failed_steps']}")
    
    # 动作类型统计
    print("\n🔧 动作统计:")
    for action_type, count in statistics['action_types'].items():
        print(f"  {action_type}: {count}")
    
    # 错误/警告汇总
    if statistics['errors'] or statistics['warnings']:
        print("\n📝 问题汇总:")
        
        # 错误汇总
        if statistics['errors']:
            print("❌ 错误列表:")
            for i, error in enumerate(statistics['errors'], 1):
                print(f"  {i}. [步骤 {error['step']}/动作 {error['action']}] {error['description']}")
                print(f"     → {truncate_long_text(error['message'])}")
        
        # 警告汇总
        if statistics['warnings']:
            print("\n⚠️ 警告列表:")
            for i, warning in enumerate(statistics['warnings'], 1):
                print(f"  {i}. [步骤 {warning['step']}/动作 {warning['action']}] {warning['description']}")
                print(f"     → {truncate_long_text(warning['message'])}")
    
    print("=" * 60)

def main():
    if len(sys.argv) < 3:  # 改为需要两个参数
        print("请传入带路径的txt文件名和项目ID作为参数")
        return

    plan_path = sys.argv[1]
    project_id = sys.argv[2]  # 新增项目ID参数
    
    with open(plan_path, "r", encoding="utf-8") as f:
        plan_text = f.read()

    # 执行统计变量
    statistics = {
        "total_steps": 0,
        "total_actions": 0,
        "success_steps": 0,
        "warning_steps": 0,
        "failed_steps": 0,
        "action_types": defaultdict(int),
        "errors": [],
        "warnings": []
    }
    
    current_step = 0
    start_time = datetime.now()

    with grpc.insecure_channel("localhost:50051") as channel:
        stub = helper_pb2_grpc.AIProjectHelperStub(channel)
        request = helper_pb2.PlanRequest(plan_text=plan_text,project_id=project_id)
        print(f"\n=== 任务: {plan_path} 已提交, 开始执行 ===\n")

        try:
            for feedback in stub.RunPlan(request):
                print_feedback(feedback)
                
                # 更新当前步骤
                if feedback.step_index > current_step:
                    current_step = feedback.step_index
                    statistics["total_steps"] += 1
                
                # 只统计最终状态（非running状态）
                if feedback.status.lower() in ["success", "warning", "failed"]:
                    statistics["total_actions"] += 1
                    statistics["action_types"][feedback.action_type] += 1
                    
                    # 记录问题信息
                    if feedback.status.lower() == "warning":
                        statistics["warning_steps"] += 1
                        statistics["warnings"].append({
                            "step": feedback.step_index,
                            "action": feedback.action_index + 1,
                            "description": feedback.step_description,
                            "message": feedback.error or feedback.output
                        })
                    elif feedback.status.lower() == "failed":
                        statistics["failed_steps"] += 1
                        statistics["errors"].append({
                            "step": feedback.step_index,
                            "action": feedback.action_index + 1,
                            "description": feedback.step_description,
                            "message": feedback.error
                        })
                    else:  # success
                        statistics["success_steps"] += 1

        except grpc.RpcError as e:
            print(f"gRPC错误: {e.code()}: {e.details()}")
            statistics["errors"].append({
                "step": "通信错误",
                "action": "N/A",
                "description": "gRPC通信失败",
                "message": f"{e.code()}: {e.details()}"
            })
            statistics["failed_steps"] += 1

    # 计算执行时间并打印汇总
    duration = (datetime.now() - start_time).total_seconds()
    print_summary(statistics, duration)

if __name__ == "__main__":
    main()