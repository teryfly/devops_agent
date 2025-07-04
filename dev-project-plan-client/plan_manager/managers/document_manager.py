# managers\document_manager.py 的修复版本 (添加 get_connection 方法)

import os
import sys
import pymysql
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import get_connection

class DocumentManager:
    def get_connection(self):
        """Get database connection (wrapper for compatibility)"""
        return get_connection()

    def create_document(self, project_id, category_id, filename, content, source='user', related_log_id=None):
        sql = """
            INSERT INTO plan_documents (project_id, category_id, filename, content, source, related_log_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        conn = get_connection()
        if not conn:
            raise Exception("Database connection failed")
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (project_id, category_id, filename, content, source, related_log_id))
                return cur.lastrowid
        finally:
            conn.close()

    def update_document_content(self, document_id, content):
        """Update document content directly (for editing, not versioning)"""
        sql = "UPDATE plan_documents SET content=%s WHERE id=%s"
        conn = get_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (content, document_id))
                return cur.rowcount > 0
        finally:
            conn.close()

    def create_document_version(self, document_id, content, source='server'):
        """Create a new version of the document (for execution results)"""
        doc = self.get_document(document_id)
        if not doc:
            return None
        
        new_version = doc['version'] + 1
        sql = """
            INSERT INTO plan_documents
                (project_id, category_id, filename, content, version, source, related_log_id)
            SELECT project_id, category_id, filename, %s, %s, %s, related_log_id
            FROM plan_documents WHERE id=%s
        """
        conn = get_connection()
        if not conn:
            return None
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (content, new_version, source, document_id))
                return cur.lastrowid
        finally:
            conn.close()

    # 保留原有的 update_document 方法，但重命名为更明确的名称
    def update_document(self, document_id, content):
        """Create a new version of the document (backwards compatibility)"""
        return self.create_document_version(document_id, content)

    def update_document_filename(self, document_id, filename):
        """Update document filename"""
        sql = "UPDATE plan_documents SET filename=%s WHERE id=%s"
        conn = get_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (filename, document_id))
                return cur.rowcount > 0
        finally:
            conn.close()

    def delete_document(self, document_id):
        sql = "DELETE FROM plan_documents WHERE id=%s"
        conn = get_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (document_id,))
                return cur.rowcount > 0
        finally:
            conn.close()

    def get_document(self, document_id, version=None):
        if version:
            # Get specific version by finding the document with same filename and version
            sql = """
                SELECT d2.* FROM plan_documents d1
                JOIN plan_documents d2 ON d1.filename = d2.filename 
                    AND d1.project_id = d2.project_id 
                    AND d1.category_id = d2.category_id
                WHERE d1.id=%s AND d2.version=%s
            """
            params = (document_id, version)
        else:
            # Get latest version
            sql = "SELECT * FROM plan_documents WHERE id=%s"
            params = (document_id,)
            
        conn = get_connection()
        if not conn:
            return None
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute(sql, params)
                return cur.fetchone()
        finally:
            conn.close()

    def get_document_version(self, document_id, version):
        """Get specific version of a document"""
        # First get the base document info
        base_doc = self.get_document(document_id)
        if not base_doc:
            return None
            
        sql = """
            SELECT * FROM plan_documents 
            WHERE filename=%s AND project_id=%s AND category_id=%s AND version=%s
        """
        conn = get_connection()
        if not conn:
            return None
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute(sql, (base_doc['filename'], base_doc['project_id'], base_doc['category_id'], version))
                return cur.fetchone()
        finally:
            conn.close()

    def get_document_versions(self, document_id):
        """Get all versions of a document"""
        base_doc = self.get_document(document_id)
        if not base_doc:
            return []
            
        sql = """
            SELECT * FROM plan_documents 
            WHERE filename=%s AND project_id=%s AND category_id=%s 
            ORDER BY version DESC
        """
        conn = get_connection()
        if not conn:
            return []
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute(sql, (base_doc['filename'], base_doc['project_id'], base_doc['category_id']))
                return cur.fetchall()
        finally:
            conn.close()

    def list_documents(self, project_id, category_id=None, tags=None):
        """List latest version of documents"""
        sql = """
            SELECT d1.* FROM plan_documents d1
            WHERE d1.project_id=%s 
            AND d1.id = (
                SELECT d2.id FROM plan_documents d2 
                WHERE d2.filename = d1.filename 
                AND d2.project_id = d1.project_id 
                AND d2.category_id = d1.category_id 
                ORDER BY d2.version DESC LIMIT 1
            )
        """
        params = [project_id]
        
        if category_id:
            sql += " AND d1.category_id=%s"
            params.append(category_id)
            
        sql += " ORDER BY d1.created_time DESC"
        
        conn = get_connection()
        if not conn:
            return []
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute(sql, tuple(params))
                docs = cur.fetchall()
        finally:
            conn.close()
            
        # Filter by tags if provided
        if tags:
            filtered_docs = []
            for doc in docs:
                doc_tags = self.get_document_tags(doc['id'])
                if set(tags).issubset(set(doc_tags)):
                    filtered_docs.append(doc)
            return filtered_docs
        
        return docs

    def get_documents_by_category(self, project_id, category_id):
        """Get latest version of documents for a specific category"""
        return self.list_documents(project_id, category_id)

    def search_content(self, project_id, search_text, category_id=None):
        sql = """
            SELECT d1.* FROM plan_documents d1
            WHERE d1.project_id=%s AND d1.content LIKE %s
            AND d1.id = (
                SELECT d2.id FROM plan_documents d2 
                WHERE d2.filename = d1.filename 
                AND d2.project_id = d1.project_id 
                AND d2.category_id = d1.category_id 
                ORDER BY d2.version DESC LIMIT 1
            )
        """
        params = [project_id, f"%{search_text}%"]
        
        if category_id:
            sql += " AND d1.category_id=%s"
            params.append(category_id)
            
        conn = get_connection()
        if not conn:
            return []
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute(sql, tuple(params))
                return cur.fetchall()
        finally:
            conn.close()

    def add_tags(self, document_id, tags):
        sql = "INSERT IGNORE INTO document_tags (document_id, tag_name) VALUES (%s, %s)"
        conn = get_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                for tag in tags:
                    cur.execute(sql, (document_id, tag))
            return True
        finally:
            conn.close()

    def remove_tags(self, document_id, tags):
        sql = "DELETE FROM document_tags WHERE document_id=%s AND tag_name=%s"
        conn = get_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                for tag in tags:
                    cur.execute(sql, (document_id, tag))
            return True
        finally:
            conn.close()

    def get_document_tags(self, document_id):
        sql = "SELECT tag_name FROM document_tags WHERE document_id=%s"
        conn = get_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (document_id,))
                return [row[0] for row in cur.fetchall()]
        finally:
            conn.close()

    def update_document_info(self, document_id, filename=None, content=None, category_id=None):
        """Update document information (filename, content, category) without creating new version"""
        if not any([filename, content, category_id]):
            return False
            
        fields = []
        values = []
        
        if filename is not None:
            fields.append("filename=%s")
            values.append(filename)
        if content is not None:
            fields.append("content=%s")
            values.append(content)
        if category_id is not None:
            fields.append("category_id=%s")
            values.append(category_id)
            
        sql = f"UPDATE plan_documents SET {', '.join(fields)} WHERE id=%s"
        values.append(document_id)
        
        conn = get_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                return cur.rowcount > 0
        finally:
            conn.close()