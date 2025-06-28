import os
import re
import ast
import logging
from datetime import datetime
from collections import defaultdict

def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger("client")

def save_content(directory, filename_prefix, content):
    """保存内容到指定目录"""
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{filename_prefix}-{timestamp}.txt"
    path = os.path.join(directory, filename)
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ 内容已保存至: {path}")
    return path

def save_plan(project_id, plan_content):
    """保存计划到 received-plans 目录"""
    return save_content("received-plans", f"{project_id}-plan", plan_content)

def save_execution_log(project_id, log_content):
    """保存执行日志到 plan-exe-logs 目录"""
    return save_content("plan-exe-logs", f"{project_id}-execution", log_content)

def truncate_long_text(text, max_length=200):
    """截断长文本用于显示"""
    if len(text) > max_length:
        return text[:max_length] + f"... [内容过长，已截断，完整长度: {len(text)}]"
    return text

def count_lines_in_file_text(file_text):
    """计算文件内容的行数"""
    if not file_text:
        return 0
    return len(file_text.splitlines())

def parse_file_edit_description(step_desc):
    """解析file_edit操作的描述，提取文件内容并计算行数"""
    match = re.search(r'file_edit\(\s*({.*?})\s*\)', step_desc, re.DOTALL)
    if match:
        dict_str = match.group(1)
        try:
            params = ast.literal_eval(dict_str)
            file_text = params.get('file_text', '')
            command = params.get('command', '')
            line_count = count_lines_in_file_text(file_text)
            return f"file_edit({command}): 约{line_count}行"
        except (SyntaxError, ValueError):
            pass
    return "file_edit: ..."

def print_feedback(feedback):
    """格式化打印反馈信息"""
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

# 添加缺失的 print_summary 函数
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

# 添加 init_statistics 函数
def init_statistics():
    """初始化统计数据结构"""
    return {
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