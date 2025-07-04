# Project Management Module
import os
import sys
import pymysql

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import get_connection

class ProjectManager:
    def create_project(self, name, dev_environment, grpc_address):
        sql = """
            INSERT INTO projects (name, dev_environment, grpc_server_address)
            VALUES (%s, %s, %s)
        """
        conn = get_connection()
        if not conn:
            raise Exception("Database connection failed")
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (name, dev_environment, grpc_address))
                return cur.lastrowid
        finally:
            conn.close()

    def update_project(self, project_id, **kwargs):
        if not kwargs:
            return False
            
        fields = []
        values = []
        for k, v in kwargs.items():
            fields.append(f"`{k}`=%s")
            values.append(v)
        
        sql = f"UPDATE projects SET {', '.join(fields)} WHERE id=%s"
        values.append(project_id)
        
        conn = get_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute(sql, values)
                return cur.rowcount > 0
        finally:
            conn.close()

    def delete_project(self, project_id):
        sql = "DELETE FROM projects WHERE id=%s"
        conn = get_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (project_id,))
                return cur.rowcount > 0
        finally:
            conn.close()

    def get_project(self, project_id):
        sql = "SELECT * FROM projects WHERE id=%s"
        conn = get_connection()
        if not conn:
            return None
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute(sql, (project_id,))
                return cur.fetchone()
        finally:
            conn.close()

    def list_projects(self):
        sql = "SELECT * FROM projects ORDER BY created_time DESC"
        conn = get_connection()
        if not conn:
            return []
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute(sql)
                return cur.fetchall()
        finally:
            conn.close()