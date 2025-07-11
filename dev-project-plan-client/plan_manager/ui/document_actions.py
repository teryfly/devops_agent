from tkinter import messagebox
from threading import Thread

from .cli_execute_log_window import CLIExecuteLogWindow
from .feedback_format import format_feedback_log

class DocumentActions:
    def __init__(self, document_manager, form, project, document=None):
        self.document_manager = document_manager
        self.form = form  # 可以为 None
        self.project = project
        self.document = document
        self.is_editing = document is not None

    def save_document(self):
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
        """
        根据文档所属分类的 Method 字段选择 gRPC 方法执行，弹出 CLI 风格日志窗口
        """
        doc = self.document
        if not doc:
            messagebox.showerror("执行失败", "未指定要执行的文档。")
            return

        # 1. 获取文档所属分类对象
        category_id = doc.get('category_id')
        category = None
        if category_id and hasattr(self, 'form') and self.form and hasattr(self.form, 'category_manager'):
            category = self.form.category_manager.get_category(category_id)
        elif category_id:
            from managers.category_manager import CategoryManager
            try:
                category_manager = CategoryManager()
                category = category_manager.get_category(category_id)
            except Exception:
                pass
        if category is None:
            messagebox.showerror("执行失败", "无法获取文档分类。")
            return

        # 2. 获取 Method 字段决定 gRPC 方法
        method = category.get('message_method', 'PlanExecuteRequest')
        prompt_template = category.get('prompt_template', '')
        env_str = self.project.get('dev_environment', '')
        prompt = doc['content']
        if '{doc}' in prompt_template or '{env}' in prompt_template:
            prompt = prompt_template.replace('{doc}', doc['content']).replace('{env}', env_str)
        grpc_server_addr = self.project.get('grpc_server_address', '127.0.0.1:50051')

        # LLM 配置
        llm_model = self.project.get('llm_model', '') if self.project else ''
        llm_url = self.project.get('llm_url', '') if self.project else ''

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

                # 根据 Method 构造参数
                request_data = {}
                if method == "PlanGetRequest":
                    request_data = {
                        'prompt': prompt,
                        'model': llm_model,
                        'llm_url': llm_url,
                    }
                elif method == "PlanExecuteRequest":
                    request_data = {
                        'prompt': prompt,
                        'project_id': str(self.project['id'])
                    }
                elif method == "PlanThenExecuteRequest":
                    request_data = {
                        'prompt': prompt,
                        'model': llm_model,
                        'llm_url': llm_url,
                        'project_id': str(self.project['id'])
                    }
                else:
                    log_win.show_log(f"未知的gRPC方法: {method}", "error")
                    return

                from managers.log_manager import LogManager
                log_manager = LogManager()
                doc_id = doc.get('id')
                log_id = log_manager.create_log(doc_id, len(prompt.encode('utf-8')))
                log_win.show_log(f"开始执行（方法: {method}）...", "info")

                from grpc_client.client import GrpcClient
                client = GrpcClient(grpc_server_addr, llm_model=llm_model, llm_url=llm_url)
                client.send_request(
                    method_name=method,
                    request_data=request_data,
                    callback=feedback_callback
                )

                log_win.show_log("执行完成。", "success")

                import time, json
                log_manager.update_log(
                    log_id,
                    duration_ms=None,
                    server_response=json.dumps(feedbacks, ensure_ascii=False),
                    has_error=any(f.get('status') == 'failed' for f in feedbacks),
                    error_message="\n".join(f.get("error", "") for f in feedbacks if f.get("error")),
                    status="completed" if not any(f.get('status') == 'failed' for f in feedbacks) else "failed",
                    completed_time=time.strftime('%Y-%m-%d %H:%M:%S'),
                )

                # --------- 修正版：遍历所有feedbacks，找到complete_plan ---------
                try:
                    # 获取第一个非空complete_plan内容
                    complete_plan_content = None
                    for fb in feedbacks:
                        c = fb.get("complete_plan", "")
                        if c:
                            complete_plan_content = c
                            break
                    if complete_plan_content:
                        # 获取当前文档分类
                        category_id = doc.get('category_id')
                        category = None
                        if category_id:
                            if hasattr(self, 'form') and self.form and hasattr(self.form, 'category_manager'):
                                category = self.form.category_manager.get_category(category_id)
                            else:
                                from managers.category_manager import CategoryManager
                                category = CategoryManager().get_category(category_id)
                        if category:
                            auto_save_category_id = category.get('auto_save_category_id')
                            if auto_save_category_id:
                                # 获取目标分类
                                if hasattr(self, 'form') and self.form and hasattr(self.form, 'category_manager'):
                                    target_category = self.form.category_manager.get_category(auto_save_category_id)
                                else:
                                    from managers.category_manager import CategoryManager
                                    target_category = CategoryManager().get_category(auto_save_category_id)
                                if target_category:
                                    self.document_manager.create_document(
                                        project_id=self.project['id'],
                                        category_id=target_category['id'],
                                        filename=doc['filename'],
                                        content=complete_plan_content,
                                        source='server'
                                    )
                                    log_win.show_log(f"自动保存完整计划到分类『{target_category['name']}』成功。", "success")
                except Exception as ex:
                    log_win.show_log(f"自动保存完整计划失败: {ex}", "error")
                # ------------------------------------------------------------

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