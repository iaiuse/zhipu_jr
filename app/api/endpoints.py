from fastapi import APIRouter, Depends
from app.services.question_service import QuestionService
from app.services.sql_service import SQLService

router = APIRouter()

@router.post("/analyze_tables")
async def analyze_tables(question: str, api_key: str):
    service = QuestionService(api_key)
    return service.analyze_tables(question)

@router.post("/get_fields")
async def get_fields(tables: List[str]):
    service = SQLService(get_db())
    return service.get_fields(tables)

@router.post("/generate_sql")
async def generate_sql(question: str, tables: List[str], fields: Dict):
    service = SQLService(get_db())
    return service.generate_sql(question, tables, fields)

@router.post("/execute_sql")
async def execute_sql(sql: str):
    service = SQLService(get_db())
    return service.execute_sql(sql) 