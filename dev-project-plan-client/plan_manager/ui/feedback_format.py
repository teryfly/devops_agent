def format_feedback_log(feedback):
    status_icons = {
        "running": "🔄",
        "success": "✅",
        "warning": "⚠️",
        "failed": "❌"
    }
    status_labels = {
        "running": "运行中",
        "success": "成功",
        "warning": "警告",
        "failed": "失败"
    }
    icon = status_icons.get(feedback.get("status", "").lower(), "❓")
    status_label = status_labels.get(feedback.get("status", "").lower(), feedback.get("status", "").upper())

    # 检查是否是LLM阶段进度（如 "请求LLM第N/M部分"）
    step_desc = feedback.get('step_description', '') or ''
    if step_desc.startswith('请求LLM第') and "部分" in step_desc:
        # 可自定义格式
        lines = [
            f"🟦 [LLM进度] {step_desc}"
        ]
    else:
        if feedback.get("action_index", 0) < 0:
            step_type = "📝 计划"
        else:
            step_type = f"🔧 步骤 {feedback.get('step_index', 1)}/{feedback.get('total_steps', 1)}"

        lines = [f"{icon} [{status_label}] {step_type} - {step_desc}"]

    if feedback.get("output"):
        out = feedback["output"]
        if len(out) > 200:
            out = out[:200] + "...[truncated]"
        lines.append(f"  📤 输出: {out}")
    if feedback.get("error"):
        err = feedback["error"]
        if len(err) > 200:
            err = err[:200] + "...[truncated]"
        lines.append(f"  ⚠️ 错误: {err}")
    lines.append("-" * 60)
    return "\n".join(lines)