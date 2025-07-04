# Log assembly logic for ActionFeedback

def truncate_long_text(text, max_len=200):
    if text and len(text) > max_len:
        return text[:max_len] + "...[truncated]"
    return text

def print_feedback(feedback):
    # Status icon mapping
    status_icons = {
        "running": "🔄",
        "success": "✅",
        "warning": "⚠️",
        "failed": "❌"
    }

    # Status label mapping
    status_labels = {
        "running": "Running",
        "success": "Success",
        "warning": "Warning",
        "failed": "Failed"
    }

    # Get status icon and label
    icon = status_icons.get(feedback.get("status", "").lower(), "❓")
    status_label = status_labels.get(feedback.get("status", "").lower(), feedback.get("status", "").upper())

    # Distinguish between plan steps and execution steps
    if feedback.get("action_index", 0) < 0:
        step_type = "📝 Plan"  # Plan generation phase
    else:
        step_type = f"🔧 Step {feedback.get('step_index', 1)}/{feedback.get('total_steps', 1)}"

    # Build the main log line
    print(f"{icon} [{status_label}] {step_type} - {feedback.get('step_description', '')}")

    # Add output content (truncate long text)
    if feedback.get("output"):
        truncated_output = truncate_long_text(feedback["output"])
        print(f"  📤 Output: {truncated_output}")

    # Add error message (truncate long text)
    if feedback.get("error"):
        truncated_error = truncate_long_text(feedback["error"])
        print(f"  ⚠️ Error: {truncated_error}")

    print("-" * 60)  # Separator line