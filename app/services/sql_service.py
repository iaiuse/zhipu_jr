from typing import List, Dict
import sqlite3  # 或其他数据库客户端

class SQLService:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_fields(self, tables: List[str]) -> Dict[str, List[Dict]]:
        """获取指定表的字段信息
        Args:
            tables: 表名列表
        Returns:
            {表名: [{字段名, 类型, 描述}, ...]}
        """
        fields = {}
        for table in tables:
            fields[table] = self._get_table_schema(table)
        return fields
    
    def generate_sql(self, question: str, tables: List[str], fields: Dict) -> str:
        """生成SQL语句"""
        prompt = f"""
        问题：{question}
        相关表：{tables}
        字段信息：{fields}
        
        请生成对应的SQL语句：
        """
        # 调用LLM生成SQL
        return self._call_llm(prompt)
    
    def execute_sql(self, sql: str) -> Dict:
        """执行SQL语句并返回结果"""
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            return {
                "status": "success",
                "data": results
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            } 