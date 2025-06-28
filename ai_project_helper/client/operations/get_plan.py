import grpc
from datetime import datetime
from ai_project_helper.proto import helper_pb2, helper_pb2_grpc
from ai_project_helper.client.utils import (
    save_plan, 
    print_feedback, 
    init_statistics
)

def run_get_plan(request, context):
    """执行获取计划操作"""
    logger = context["logger"]
    statistics = init_statistics()
    start_time = datetime.now()
    complete_plan = ""
    
    with grpc.insecure_channel(context["grpc_channel"]) as channel:
        stub = helper_pb2_grpc.AIProjectHelperStub(channel)
        
        logger.info(f"📝 请求生成计划: {request.requirement}")
        
        try:
            for feedback in stub.GetPlan(request):
                print_feedback(feedback)
                
                # 统计计划部分
                if feedback.action_index < 0:
                    statistics["plan_parts"] += 1
                
                # 保存完整计划
                if feedback.complete_plan:
                    complete_plan = feedback.complete_plan
                    save_plan(request.project_id, complete_plan)
            
            if complete_plan:
                logger.info(f"✅ 计划获取完成，已保存到 received-plans 目录")
            else:
                logger.warning("⚠️ 未接收到完整计划内容")
                
        except grpc.RpcError as e:
            logger.error(f"gRPC错误: {e.code()}: {e.details()}")
            statistics["errors"].append({
                "step": "通信错误",
                "action": "N/A",
                "description": "gRPC通信失败",
                "message": f"{e.code()}: {e.details()}"
            })
    
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"🏁 操作完成! 总耗时: {duration:.2f}秒")
    return statistics