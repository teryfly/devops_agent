# Category Management Module
import os
import sys
import pymysql

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import get_connection

class CategoryManager:
    def create_category(self, name, prompt_template, message_method, auto_save_category_id=None, is_builtin=False):
        sql = """
            INSERT INTO plan_categories (name, prompt_template, message_method, auto_save_category_id, is_builtin)
            VALUES (%s, %s, %s, %s, %s)
        """
        conn = get_connection()
        if not conn:
            raise Exception("Database connection failed")
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (name, prompt_template, message_method, auto_save_category_id, is_builtin))
                return cur.lastrowid
        finally:
            conn.close()

    def update_category(self, category_id, **kwargs):
        if not kwargs:
            return False
            
        fields = []
        values = []
        for k, v in kwargs.items():
            fields.append(f"`{k}`=%s")
            values.append(v)
        
        sql = f"UPDATE plan_categories SET {', '.join(fields)} WHERE id=%s"
        values.append(category_id)
        
        conn = get_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                return cur.rowcount > 0
        finally:
            conn.close()

    def delete_category(self, category_id):
        # Check if it's a built-in category
        sql_check = "SELECT is_builtin FROM plan_categories WHERE id=%s"
        conn = get_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute(sql_check, (category_id,))
                row = cur.fetchone()
                if row and row[0]:
                    return False  # Cannot delete built-in categories
                
                sql = "DELETE FROM plan_categories WHERE id=%s"
                cur.execute(sql, (category_id,))
                return cur.rowcount > 0
        finally:
            conn.close()

    def get_category(self, category_id):
        sql = "SELECT * FROM plan_categories WHERE id=%s"
        conn = get_connection()
        if not conn:
            return None
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute(sql, (category_id,))
                return cur.fetchone()
        finally:
            conn.close()

    def list_categories(self):
        sql = "SELECT * FROM plan_categories ORDER BY is_builtin DESC, name"
        conn = get_connection()
        if not conn:
            return []
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()
        finally:
            conn.close()

    def get_builtin_categories(self):
        sql = "SELECT * FROM plan_categories WHERE is_builtin=TRUE ORDER BY name"
        conn = get_connection()
        if not conn:
            return []
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()
        finally:
            conn.close()