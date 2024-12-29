# app/api/qa_system.py
from typing import Dict, Any
import pandas as pd
from ..utils.data_access import DataAccessUtils
from ..models.question_types import QuestionClassifier
import logging

class QASystem:
    def __init__(self, access_token: str):
        self.data_utils = DataAccessUtils(access_token)
        self.question_classifier = QuestionClassifier()
        self.logger = logging.getLogger(__name__)

    async def process_question(self, question: str) -> Dict[str, Any]:
        try:
            # 1. 分类问题类型
            question_type = self.question_classifier.classify(question)
            
            # 2. 根据问题类型选择处理策略
            if question_type == "basic":
                return await self._handle_basic_query(question)
            elif question_type == "statistical":
                return await self._handle_statistical_query(question)
            else:  # complex
                return await self._handle_complex_query(question)
                
        except Exception as e:
            self.logger.error(f"Error processing question: {str(e)}")
            return {
                "error": str(e),
                "status": "error"
            }

    async def _handle_basic_query(self, question: str) -> Dict[str, Any]:
        """处理基础查询，如股票基本信息、当日行情等"""
        # 示例实现
        if "股票代码" in question:
            # 提取股票名称
            company_name = question.split("的")[0]
            sql = f"""
            SELECT SecuCode, ChiName 
            FROM constantdb.secumain 
            WHERE ChiName LIKE '%{company_name}%'
            """
            result = await self.data_utils.execute_query(sql)
            return {
                "answer": f"该公司的股票代码是: {result[0]['SecuCode']}",
                "data": result,
                "type": "basic"
            }
        
        # 可以添加更多基础查询类型

    async def _handle_statistical_query(self, question: str) -> Dict[str, Any]:
        """处理统计分析查询，如涨跌统计、成交量分析等"""
        try:
            if "涨停" in question:
                # 提取时间范围
                # TODO: 使用更好的时间提取方法
                sql = """
                SELECT 
                    COUNT(*) as limit_up_count,
                    STRING_AGG(sm.SecuAbbr, ',') as stock_names
                FROM astockmarketquotesdb.qt_dailyquote qt
                JOIN constantdb.secumain sm ON qt.InnerCode = sm.InnerCode
                WHERE qt.ChangePCT >= 9.9
                AND qt.TradingDay BETWEEN '2021-01-01' AND '2021-12-31'
                """
                result = await self.data_utils.execute_query(sql)
                return {
                    "answer": f"涨停股票数量: {result[0]['limit_up_count']}, 包括: {result[0]['stock_names']}",
                    "data": result,
                    "type": "statistical"
                }
        except Exception as e:
            self.logger.error(f"Error in statistical query: {str(e)}")
            raise

    async def _handle_complex_query(self, question: str) -> Dict[str, Any]:
        """处理复杂查询，如多维度分析、跨表关联等"""
        try:
            if "财务分析" in question:
                # 示例：计算行业平均值和公司对比
                sql = """
                SELECT 
                    sm.SecuAbbr,
                    bs.TotalAssets,
                    bs.TotalLiability,
                    bs.TotalLiability / bs.TotalAssets as debt_ratio
                FROM astockfinancedb.lc_balancesheetall bs
                JOIN constantdb.secumain sm ON bs.CompanyCode = sm.CompanyCode
                WHERE bs.EndDate = '2021-12-31'
                ORDER BY debt_ratio DESC
                LIMIT 10
                """
                result = await self.data_utils.execute_query(sql)
                
                # 处理数据
                df = pd.DataFrame(result)
                analysis = {
                    "avg_debt_ratio": df['debt_ratio'].mean(),
                    "max_debt_ratio": df['debt_ratio'].max(),
                    "min_debt_ratio": df['debt_ratio'].min()
                }
                
                return {
                    "answer": f"行业平均资产负债率为: {analysis['avg_debt_ratio']:.2%}",
                    "data": result,
                    "analysis": analysis,
                    "type": "complex"
                }
        except Exception as e:
            self.logger.error(f"Error in complex query: {str(e)}")
            raise

# app/models/question_types.py
class QuestionClassifier:
    def __init__(self):
        # 定义关键词字典
        self.keywords = {
            "basic": ["股票代码", "股票名称", "收盘价", "开盘价", "最高价", "最低价"],
            "statistical": ["平均", "总计", "涨停", "跌停", "换手率", "成交量"],
            "complex": ["财务分析", "行业对比", "趋势分析", "风险评估"]
        }

    def classify(self, question: str) -> str:
        """根据问题内容分类"""
        # 简单的关键词匹配
        for q_type, keywords in self.keywords.items():
            if any(keyword in question for keyword in keywords):
                return q_type
        return "basic"  # 默认为基础查询