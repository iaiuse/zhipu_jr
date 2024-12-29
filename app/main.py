# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import streamlit as st
from pathlib import Path
import uvicorn

app = FastAPI(title="Finance QA System")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Finance QA System"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)