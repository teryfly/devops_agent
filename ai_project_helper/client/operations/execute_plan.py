# ai_project_helper/client/operations/execute_plan.py

import grpc
import os
from datetime import datetime
from ai_project_helper.proto import helper_pb2, helper_pb2_grpc
from ai_project_helper.client.utils import (
    save_execution_log,
    print_feedback,
    init_statistics,
    truncate_long_text,
    print_summary
)

def run_execute_plan(request, context):
    """执行计划操作"""
    logger = context["logger"]
    statistics = init_statistics()
    start_time = datetime.now()
    execution_log = ""
    
    # 读取计划文件
    if not os.path.exists(request.plan_text):
        logger.error(f"错误: 计划文件不存在: {request.plan_text}")
        return statistics
    
    with open(request.plan_text, "r", encoding="utf-8") as f:
        plan_text = f.read()
    
    # 创建执行请求
    execute_request = helper_pb2.PlanExecuteRequest(
        plan_text=plan_text,
        project_id=request.project_id
    )
    
    with grpc.insecure_channel(context["grpc_channel"]) as channel:
        stub = helper_pb2_grpc.AIProjectHelperStub(channel)
        
        logger.info(f"🚀 开始执行计划: {request.plan_text}")
        
        try:
            for feedback in stub.RunPlan(execute_request):
                # 收集完整日志
                log_entry = f"Step [{feedback.step_index}/{feedback.total_steps}] - {feedback.step_description}\n"
                if feedback.output:
                    log_entry += f"输出: {feedback.output}\n"
                if feedback.error:
                    log_entry += f"错误: {feedback.error}\n"
                execution_log += log_entry + "-" * 60 + "\n"
                
                print_feedback(feedback)
                
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
            logger.error(f"gRPC错误: {e.code()}: {e.details()}")
            statistics["errors"].append({
                "step": "通信错误",
                "action": "N/A",
                "description": "gRPC通信失败",
                "message": f"{e.code()}: {e.details()}"
            })
            statistics["failed_actions"] += 1
    
    # 保存执行日志
    save_execution_log(request.project_id, execution_log)
    
    duration = (datetime.now() - start_time).total_seconds()
    print_summary(statistics, duration)
    return statistics