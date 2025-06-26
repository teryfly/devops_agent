import grpc
import sys
from datetime import datetime
from collections import defaultdict
from ai_project_helper.proto import helper_pb2 as helper_pb2, helper_pb2_grpc

def truncate_long_text(text, max_length=200):
    """截断长文本用于显示"""
    if len(text) > max_length:
        return text[:max_length] + f"... [内容过长，已截断，完整长度: {len(text)}]"
    return text

def print_feedback(feedback):
    """格式化打印反馈信息"""
    # 状态图标
    status_icons = {
        "running": "🔄",
        "success": "✅",
        "warning": "⚠️",
        "failed": "❌"
    }
    icon = status_icons.get(feedback.status.lower(), "❓")
    
    # 状态标签
    status_label = {
        "running": "运行中",
        "success": "成功",
        "warning": "警告",
        "failed": "失败"
    }.get(feedback.status.lower(), feedback.status.upper())
    
    # 区分计划步骤和执行步骤
    step_type = "📝 计划" if feedback.action_index < 0 else f"🔧 步骤 {feedback.step_index}/{feedback.total_steps}"
    
    print(f"{icon} [{status_label}] {step_type} - {feedback.step_description}")
    
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
    print(f"  计划部分: {statistics['plan_parts']}")
    print(f"  执行步骤: {statistics['total_steps']}")
    print(f"  执行动作: {statistics['total_actions']}")
    print(f"  ✅ 成功动作: {statistics['success_actions']}")
    print(f"  ⚠️ 警告动作: {statistics['warning_actions']}")
    print(f"  ❌ 失败动作: {statistics['failed_actions']}")
    
    # 动作类型统计
    print("\n🔧 动作类型统计:")
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
    if len(sys.argv) < 2:
        print("请传入带路径的txt文件名作为参数")
        return

    plan_path = sys.argv[1]
    with open(plan_path, "r", encoding="utf-8") as f:
        plan_text = f.read()

    # 执行统计变量
    statistics = {
        "plan_parts": 0,
        "total_steps": 0,
        "total_actions": 0,
        "success_actions": 0,
        "warning_actions": 0,
        "failed_actions": 0,
        "action_types": defaultdict(int),
        "errors": [],
        "warnings": []
    }
    
    start_time = datetime.now()

    with grpc.insecure_channel("localhost:50051") as channel:
        stub = helper_pb2_grpc.AIProjectHelperStub(channel)
        request = helper_pb2.PlanGenerateRequest(
            requirement=plan_text,
            model="GPT-4.1",
            llm_url="http://43.132.224.225:8000/v1/chat/completions"
        )
        print(f"\n📝 请求生成计划: {plan_path}")

        try:
            for feedback in stub.GetPlanThenRun(request):
                print_feedback(feedback)
                
                # 统计计划部分
                if feedback.action_index < 0:
                    statistics["plan_parts"] += 1
                
                # 只统计执行动作的最终状态
                if feedback.action_index >= 0 and feedback.status.lower() in ["success", "warning", "failed"]:
                    statistics["total_actions"] += 1
                    statistics["action_types"][feedback.action_type] += 1
                    
                    # 更新步骤计数
                    if feedback.step_index > statistics["total_steps"]:
                        statistics["total_steps"] = feedback.step_index
                    
                    # 记录问题信息
                    if feedback.status.lower() == "warning":
                        statistics["warning_actions"] += 1
                        statistics["warnings"].append({
                            "step": feedback.step_index,
                            "action": feedback.action_index + 1,
                            "description": feedback.step_description,
                            "message": feedback.error or feedback.output
                        })
                    elif feedback.status.lower() == "failed":
                        statistics["failed_actions"] += 1
                        statistics["errors"].append({
                            "step": feedback.step_index,
                            "action": feedback.action_index + 1,
                            "description": feedback.step_description,
                            "message": feedback.error
                        })
                    else:  # success
                        statistics["success_actions"] += 1

        except grpc.RpcError as e:
            print(f"gRPC错误: {e.code()}: {e.details()}")
            statistics["errors"].append({
                "step": "通信错误",
                "action": "N/A",
                "description": "gRPC通信失败",
                "message": f"{e.code()}: {e.details()}"
            })
            statistics["failed_actions"] += 1

    # 计算执行时间并打印汇总
    duration = (datetime.now() - start_time).total_seconds()
    print_summary(statistics, duration)

if __name__ == "__main__":
    main()