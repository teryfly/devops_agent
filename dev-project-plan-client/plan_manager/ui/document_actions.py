from tkinter import messagebox, Toplevel, scrolledtext, END, DISABLED, NORMAL
from threading import Thread

class DocumentActions:
    def __init__(self, document_manager, form, project, document=None):
        self.document_manager = document_manager
        self.form = form  # 允许为 None
        self.project = project
        self.document = document
        self.is_editing = document is not None

    def save_document(self):
        """保存文档，校验并入库"""
        if self.form is None:
            messagebox.showerror("错误", "保存功能只可在编辑弹窗使用。")
            return False
        form_data = self.form.get_form_data()
        if not self._validate_form_data(form_data):
            return False

        try:
            if self.is_editing:
                return self._update_document(form_data)
            else:
                return self._create_document(form_data)
        except Exception as e:
            from ui.error_dialog import show_error
            show_error(self.form.parent, "保存失败", f"保存文档失败: {str(e)}", e)
            return False

    def _validate_form_data(self, form_data):
        if not form_data['filename']:
            messagebox.showerror("校验失败", "文件名不能为空！")
            return False
        if not form_data['content']:
            messagebox.showerror("校验失败", "内容不能为空！")
            return False
        if not form_data['category']:
            messagebox.showerror("校验失败", "请选择分类！")
            return False
        return True

    def _create_document(self, form_data):
        doc_id = self.document_manager.create_document(
            self.project['id'],
            form_data['category']['id'],
            form_data['filename'],
            form_data['content'],
            'user'
        )
        if doc_id:
            self._handle_tags(doc_id, form_data['tags'])
            messagebox.showinfo("成功", "文档创建成功！")
            return True
        return False

    def _update_document(self, form_data):
        conn = self.document_manager.get_connection()
        try:
            with conn.cursor() as cur:
                update_sql = """
                    UPDATE plan_documents
                    SET content=%s, filename=%s, category_id=%s
                    WHERE id=%s
                """
                cur.execute(update_sql, (
                    form_data['content'],
                    form_data['filename'],
                    form_data['category']['id'],
                    self.document['id']
                ))
            self._handle_tags(self.document['id'], form_data['tags'])
            messagebox.showinfo("成功", "文档更新成功！")
            return True
        finally:
            conn.close()

    def _handle_tags(self, doc_id, tags_text):
        if tags_text:
            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
            if tags:
                try:
                    old_tags = self.document_manager.get_document_tags(doc_id)
                    if old_tags:
                        self.document_manager.remove_tags(doc_id, old_tags)
                    self.document_manager.add_tags(doc_id, tags)
                except Exception as e:
                    print(f"[WARNING] 标签更新失败: {e}")

    def execute_document(self):
        """独立线程执行文档，日志弹窗（非模态），CLI风格，线程结束主动关闭gRPC"""
        doc = self.document
        if not doc:
            messagebox.showerror("执行失败", "未指定要执行的文档。")
            return

        from managers.category_manager import CategoryManager
        from managers.log_manager import LogManager
        from grpc_client.client import GrpcClient
        import time, json

        # 获取文档分类
        category_id = doc.get('category_id')
        category = None
        if category_id and hasattr(self, 'form') and self.form and hasattr(self.form, 'category_manager'):
            category = self.form.category_manager.get_category(category_id)
        elif category_id:
            try:
                category_manager = CategoryManager()
                category = category_manager.get_category(category_id)
            except Exception:
                pass
        if category is None:
            messagebox.showerror("执行失败", "无法获取文档分类。")
            return

        method = category.get('message_method', 'PlanExecuteRequest')
        prompt_template = category.get('prompt_template', '')
        env_str = self.project.get('dev_environment', '')
        prompt = doc['content']
        if '{doc}' in prompt_template or '{env}' in prompt_template:
            prompt = prompt_template.replace('{doc}', doc['content']).replace('{env}', env_str)
        grpc_server_addr = self.project.get('grpc_server_address', '127.0.0.1:50051')

        doc_name = doc.get("filename", "文档")
        log_win = CLIExecuteLogWindow(self.form.parent if self.form else None, title=f"执行日志（{doc_name}）")
        log_win.show_log(f"连接 gRPC 服务: {grpc_server_addr}")

        def run_execute():
            client = None
            try:
                feedbacks = []
                log_id = None

                def feedback_callback(feedback):
                    log_text = format_feedback_log(feedback)
                    log_win.show_log(log_text)
                    feedbacks.append(feedback)

                # 构造请求参数
                if method == "PlanGetRequest":
                    request_data = {
                        'prompt': prompt,
                        'model': '',
                        'llm_url': '',
                    }
                elif method == "PlanExecuteRequest":
                    request_data = {
                        'prompt': prompt,
                        'project_id': str(self.project['id'])
                    }
                elif method == "PlanThenExecuteRequest":
                    request_data = {
                        'prompt': prompt,
                        'model': '',
                        'llm_url': '',
                        'project_id': str(self.project['id'])
                    }
                else:
                    log_win.show_log(f"未知的gRPC方法: {method}", "error")
                    return

                log_manager = LogManager()
                doc_id = doc.get('id')
                log_id = log_manager.create_log(doc_id, len(prompt.encode('utf-8')))
                log_win.show_log(f"开始执行（方法: {method}）...", "info")

                client = GrpcClient(grpc_server_addr)
                client.send_request(
                    method_name=method,
                    request_data=request_data,
                    callback=feedback_callback
                )

                log_win.show_log("执行完成。", "success")

                log_manager.update_log(
                    log_id,
                    duration_ms=None,
                    server_response=json.dumps(feedbacks, ensure_ascii=False),
                    has_error=any(f.get('status') == 'failed' for f in feedbacks),
                    error_message="\n".join(f.get("error", "") for f in feedbacks if f.get("error")),
                    status="completed" if not any(f.get('status') == 'failed' for f in feedbacks) else "failed",
                    completed_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                )
            except Exception as e:
                log_win.show_log(f"执行出错: {e}", "error")
                import traceback
                log_win.show_log(traceback.format_exc(), "error")
            finally:
                if client is not None:
                    try:
                        client.close()
                        log_win.show_log("gRPC连接已关闭。", "info")
                    except Exception as ex:
                        log_win.show_log(f"关闭gRPC连接异常: {ex}", "warning")

        Thread(target=run_execute, daemon=True).start()

    def view_history(self):
        if self.document:
            from ui.history_dialog import HistoryDialog
            HistoryDialog(self.form.parent if self.form else None, self.document_manager, self.document)

class CLIExecuteLogWindow:
    """CLI风格执行日志弹窗（非模态），可多开，线程安全"""
    def __init__(self, parent, title="执行日志"):
        self.top = Toplevel(parent) if parent else Toplevel()
        self.top.title(title)
        self.text = scrolledtext.ScrolledText(self.top, width=100, height=32, state=DISABLED, font=("Consolas", 10))
        self.text.pack(expand=True, fill='both')
        self.top.transient(parent)
        self.top.focus_set()
        self.show_log("执行准备中...\n")

    def show_log(self, msg, level="info"):
        self.text.config(state=NORMAL)
        if isinstance(msg, str):
            self.text.insert(END, msg + "\n")
        elif isinstance(msg, dict):
            self.text.insert(END, str(msg) + "\n")
        self.text.see(END)
        self.text.config(state=DISABLED)
        self.top.update()

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

    if feedback.get("action_index", 0) < 0:
        step_type = "📝 计划"
    else:
        step_type = f"🔧 步骤 {feedback.get('step_index', 1)}/{feedback.get('total_steps', 1)}"

    lines = [f"{icon} [{status_label}] {step_type} - {feedback.get('step_description', '')}"]
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