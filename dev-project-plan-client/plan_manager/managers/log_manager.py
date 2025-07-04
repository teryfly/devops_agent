# Log Management Module

from database.connection import get_connection
import pymysql
from datetime import datetime

class LogManager:
    def create_log(self, document_id, request_content_size):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = """
            INSERT INTO execution_logs (document_id, request_time, request_content_size, created_time)
            VALUES (%s, %s, %s, %s)
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (document_id, now, request_content_size, now))
                return cur.lastrowid

    def update_log(self, log_id, duration_ms=None, server_response=None, has_error=False, error_message=None, status=None, completed_time=None):
        fields = []
        values = []
        if duration_ms is not None:
            fields.append("duration_ms=%s")
            values.append(duration_ms)
        if server_response is not None:
            fields.append("server_response=%s")
            values.append(server_response)
        if has_error is not None:
            fields.append("has_error=%s")
            values.append(has_error)
        if error_message is not None:
            fields.append("error_message=%s")
            values.append(error_message)
        if status is not None:
            fields.append("status=%s")
            values.append(status)
        if completed_time is not None:
            fields.append("completed_time=%s")
            values.append(completed_time)
        if not fields:
            return False
        sql = f"UPDATE execution_logs SET {', '.join(fields)} WHERE id=%s"
        values.append(log_id)
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                return cur.rowcount > 0

    def get_log(self, log_id):
        sql = "SELECT * FROM execution_logs WHERE id=%s"
        with get_connection() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute(sql, (log_id,))
                return cur.fetchone()

    def list_logs(self, document_id):
        sql = "SELECT * FROM execution_logs WHERE document_id=%s ORDER BY request_time DESC"
        with get_connection() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute(sql, (document_id,))
                return cur.fetchall()

    def format_log_display(self, feedback_data):
        # Format log for UI display, expects ActionFeedback-like dicts
        status_icons = {
            "running": "🔄",
            "success": "✅",
            "warning": "⚠️",
            "failed": "❌"
        }
        status_labels = {
            "running": "Running",
            "success": "Success",
            "warning": "Warning",
            "failed": "Failed"
        }
        lines = []
        for feedback in feedback_data:
            icon = status_icons.get(feedback.get("status", "").lower(), "❓")
            label = status_labels.get(feedback.get("status", "").lower(), feedback.get("status", "").upper())
            if feedback.get("action_index", 0) < 0:
                step_type = "📝 Plan"
            else:
                step_type = f"🔧 Step {feedback.get('step_index', 1)}/{feedback.get('total_steps', 1)}"
            line = f"{icon} [{label}] {step_type} - {feedback.get('step_description', '')}"
            lines.append(line)
            if feedback.get("output"):
                out = feedback["output"]
                if len(out) > 200:
                    out = out[:200] + "...[truncated]"
                lines.append(f"  📤 Output: {out}")
            if feedback.get("error"):
                err = feedback["error"]
                if len(err) > 200:
                    err = err[:200] + "...[truncated]"
                lines.append(f"  ⚠️ Error: {err}")
            lines.append("-" * 60)
        return "\n".join(lines)