import grpc
import os
import re
from datetime import datetime
from concurrent import futures

from ai_project_helper.proto import helper_pb2, helper_pb2_grpc
from ai_project_helper.core.agent import Agent
from ai_project_helper.config import load_config
from ai_project_helper.log_config import setup_logging, get_logger
from ai_project_helper.core.prompt import build_prompt

import requests
# 初始化日志
setup_logging()
logger = get_logger("server")

class AIProjectHelperServicer(helper_pb2_grpc.AIProjectHelperServicer):
    def __init__(self, config):
        self.config = config
        self.agent = Agent(config)
        self.logger = get_logger("server.servicer")

    def RunPlan(self, request, context):
        plan_text = request.plan_text
        logger.info(f"==================接收到客户端请求==================：\n{plan_text[:88]}...\n =============================================================================================================")

        # 使用统一的方法分割步骤
        task_steps = split_plan_into_steps(plan_text)
        step_count = len(task_steps)

        for step_index, step_text in enumerate(task_steps):
            try:
                for fb in self.agent.run_step_text(step_text, step_index=step_index+1, step_count=step_count):
                    # 创建 ActionFeedback 消息时添加新字段
                    feedback = helper_pb2.ActionFeedback(
                        action_index=fb.get("action_index", 0),
                        action_type=fb.get("action_type", ""),
                        step_description=fb.get("step_description", ""),
                        status=fb.get("status", ""),
                        output=fb.get("output", ""),
                        error=fb.get("error", ""),
                        command=fb.get("command", ""),
                        step_index=step_index+1,  # 当前步骤索引
                        total_steps=step_count,    # 总步骤数
                        exit_code=fb.get("exit_code", 0)  # 退出码
                    )
                    yield feedback
                    
                    if fb.get("status") == "failed":
                        logger.error(f"第 {step_index+1} 步执行失败，终止后续步骤")
                        return
            except Exception as e:
                logger.exception(f"第 {step_index+1} 步执行异常")
                context.set_details(f"Step {step_index+1} execution error: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                return    
            
    # 远程 LLM 生成 plan → 本地 LLM 执行 plan”的链式代理
    def GetPlanThenRun(self, request, context): 
        requirement = request.requirement
        model = request.model or self.config['llm']['model']
        llm_url = request.llm_url or self.config['llm']['api_url']
        api_key = self.config['llm']['api_key']
        
        # 获取输入文件名（不带路径）
        input_filename = os.path.basename(request.requirement.split('\n')[0].strip())
        if not input_filename.endswith('.txt'):
            input_filename = 'plan.txt'
        base_name = os.path.splitext(input_filename)[0]
        
        # 创建llm_coding_plans目录
        plans_dir = "llm_coding_plans"
        os.makedirs(plans_dir, exist_ok=True)
        
        # 初始化完整计划文本
        complete_plan_text = ""
        original_prompt = requirement
        accumulated_parts = ""
        current_part = 0  # 当前处理的部分序号
        total_parts = 1   # 总部分数
        
        # 处理多部分计划的循环
        while current_part < total_parts:
            try:
                current_part += 1  # 准备处理下一个部分
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # 精确到秒
                
                # 构建当前提示词
                if current_part == 1:
                    current_prompt = original_prompt
                else:
                    # 正确的历史记录头
                    history_header = f"--- 已经输出过的历史记录一共{current_part-1}部分，记录如下 ---"
                    current_prompt = (
                        f"{original_prompt}\n"
                        f"{history_header}\n"
                        f"{accumulated_parts}\n"
                        f"--- 历史记录结束 ---\n"
                        f"现在开始继续输出下一个部分（第{current_part}/{total_parts}部分）"
                    )
                
                # 保存所有请求内容（包括第一次）
                request_filename = f"{base_name}-Request-{current_part}-of-{total_parts}-{timestamp}.txt"
                request_path = os.path.join(plans_dir, request_filename)
                with open(request_path, "w", encoding="utf-8") as f:
                    f.write(current_prompt)
                logger.info(f"LLM请求内容已保存到: {request_path}")
                
                logger.info(f"请求 LLM-B（{model}@{llm_url}）生成计划 (部分 {current_part}/{total_parts})")
                response = requests.post(
                    llm_url,
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": current_prompt}],
                        "max_tokens": 2048000,
                        "temperature": 0,
                    },
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                response.raise_for_status()
                plan_text = response.json()["choices"][0]["message"]["content"]
                
                # 检查是否是第一部分
                if current_part == 1:
                    first_line = plan_text.split('\n', 1)[0].strip()
                    match = re.match(r'\[(\d+)/(\d+)\]', first_line)
                    
                    if match:
                        total_parts = int(match.group(2))  # 只更新总部分数
                        plan_text = plan_text.split('\n', 1)[1].lstrip()
                    else:
                        total_parts = 1
                
                # 保存当前部分
                part_filename = f"{base_name}-Part-{current_part}-of-{total_parts}-{timestamp}.txt"
                part_path = os.path.join(plans_dir, part_filename)
                
                with open(part_path, "w", encoding="utf-8") as f:
                    f.write(plan_text)
                logger.info(f"LLM生成的第{current_part}/{total_parts}部分计划已保存到: {part_path}")
                
                # 通知客户端
                yield helper_pb2.ActionFeedback(
                    action_index=-1,
                    action_type="llm_plan",
                    step_description=f"LLM-B生成的计划第{current_part}/{total_parts}部分",
                    status="success",
                    output=f"部分{current_part}/{total_parts}已生成并保存",
                    command="",
                    error=""
                )
                
                # 累积当前部分内容（不包含[X/Y]标记）
                accumulated_parts += f"{plan_text}\n\n"
                
                # 处理计划拼接
                if complete_plan_text:
                    # 检查分隔符
                    last_part_ends_with_sep = complete_plan_text.strip().endswith('------')
                    current_part_starts_with_sep = plan_text.strip().startswith('------')
                    
                    # 确保部分之间只有一个分隔符
                    if not last_part_ends_with_sep and not current_part_starts_with_sep:
                        complete_plan_text += "\n------\n"
                    elif last_part_ends_with_sep and current_part_starts_with_sep:
                        # 如果两端都有分隔符，移除一个
                        plan_text = plan_text.lstrip('------').lstrip()
                
                # 添加当前部分内容
                complete_plan_text += plan_text
                
            except Exception as e:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"LLM-B 调用失败: {e}")
                logger.exception(f"LLM-B 调用失败: {e}")
                return

        # 保存完整计划
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"{base_name}-complete-{timestamp}.txt"
        output_path = os.path.join(plans_dir, output_filename)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(complete_plan_text)
        logger.info(f"完整的LLM生成计划已保存到: {output_path}")

        # 通知客户端完整计划已生成
        yield helper_pb2.ActionFeedback(
            action_index=-1,
            action_type="llm_plan",
            step_description="LLM-B生成的完整计划内容",
            status="success",
            output=complete_plan_text,
            command="",
            error=""
        )

        # 分割步骤
        task_steps = split_plan_into_steps(complete_plan_text)
        step_count = len(task_steps)
        logger.info(f"成功分割为 {step_count} 个步骤")

        # 逐步执行每个 step
        for step_index, step_text in enumerate(task_steps):
            try:
                for fb in self.agent.run_step_text(step_text, step_index=step_index + 1, step_count=step_count):
                    yield helper_pb2.ActionFeedback(**fb)
                    if fb.get("status") == "failed":
                        return
            except Exception as e:
                logger.exception(f"Step {step_index+1} 执行失败")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(f"执行第 {step_index+1} 步失败: {e}")
                return
       
    def CreateProject(self, request, context):
        steps = request.project_steps
        logger.info(f"Received project creation steps:\n{steps}")

        try:
            for fb in self.agent.create_project(steps):
                yield helper_pb2.ActionFeedback(**fb)
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            context.set_details(f"Failed to create project: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return

# 统一的分割方法
def split_plan_into_steps(plan_text):
    """
    将计划文本分割为多个步骤
    使用正则表达式识别任何以------开始的行作为分隔符
    """
    import re
    step_delimiter = re.compile(r'^\s*------', re.MULTILINE)
    task_steps = []
    
    # 找到所有匹配位置
    matches = list(step_delimiter.finditer(plan_text))
    
    if not matches:
        # 如果没有分隔符，整个文本作为一个步骤
        if plan_text.strip():
            task_steps.append(plan_text.strip())
    else:
        # 添加第一个步骤（从开始到第一个分隔符）
        start_idx = 0
        for match in matches:
            end_idx = match.start()
            step_text = plan_text[start_idx:end_idx].strip()
            if step_text:
                task_steps.append(step_text)
            start_idx = match.end()
        
        # 添加最后一个步骤（最后一个分隔符之后的内容）
        last_step = plan_text[start_idx:].strip()
        if last_step:
            task_steps.append(last_step)
    
    return task_steps            
def serve():
    config = load_config()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    helper_pb2_grpc.add_AIProjectHelperServicer_to_server(
        AIProjectHelperServicer(config), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    logger.info("服务启动，端口 [::]:50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()