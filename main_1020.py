# main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import re
from typing import List, Optional
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# html, css 읽어오기 - 파일트리에서 불러옴------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# .env 파일 읽어오기 (API 키 등)---------------------------------------
load_dotenv()

# FastAPI 앱 생성 ---------------------------------------------------
app = FastAPI(
    title="증상 매칭 솔루션 API",
    description="질환/병원/영양제 매칭 솔루션의 백엔드 API입니다.",
    version="1.0.0"
)

# DB 연결 설정
# =============================================================================
DB_CONFIG = {
    "host": "152.70.37.199",
    "database": "postgres",
    "user": "test01",
    "password": "test1234",
    "port": 5432
}
# Pydantic 모델
# =============================================================================
class SymptomQuery(BaseModel):
    query: str
    method: Optional[str] = "keyword"
    limit: Optional[int] = 5

class DiseaseMatch(BaseModel):
    disease: str
    symptoms: List[str]
    reference: Optional[str]
    score: float

class SearchResponse(BaseModel):
    success: bool
    message: str
    matches: List[DiseaseMatch]


# 라우트
# =============================================================================
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """메인 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api")
def root():
    return {
        "message": "질환 증상 매칭 API",
        "status": "running",
        "endpoints": {
            "검색": "POST /search",
            "문서": "GET /docs"
        }
    }

@app.get("/health")
def health_check():
    """서버 상태 확인"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# =============================================================================
# 키워드 기반 검색
# =============================================================================
def find_disease_by_keywords(user_input: str, limit: int = 5):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        keywords = re.findall(r'[\w가-힣]+', user_input.lower())
        
        if not keywords:
            return []
        
        cur.execute("""
            SELECT 
                disease,
                symptoms,
                ref,
                (
                    SELECT COUNT(*)
                    FROM unnest(symptoms) AS symptom
                    WHERE symptom ILIKE ANY(%s)
                ) as match_count
            FROM disease_symptoms
            WHERE EXISTS (
                SELECT 1
                FROM unnest(symptoms) AS symptom
                WHERE symptom ILIKE ANY(%s)
            )
            ORDER BY match_count DESC
            LIMIT %s
        """, ([f'%{kw}%' for kw in keywords], [f'%{kw}%' for kw in keywords], limit))
        
        results = cur.fetchall()
        return results
        
    finally:
        cur.close()
        conn.close()

# =============================================================================
# 전문 검색
# =============================================================================
def find_disease_by_fulltext(user_input: str, limit: int = 5):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT 
                disease,
                symptoms,
                ref,
                ts_rank(
                    to_tsvector('simple', array_to_string(symptoms, ' ')),
                    plainto_tsquery('simple', %s)
                ) as relevance
            FROM disease_symptoms
            WHERE to_tsvector('simple', array_to_string(symptoms, ' ')) 
                  @@ plainto_tsquery('simple', %s)
            ORDER BY relevance DESC
            LIMIT %s
        """, (user_input, user_input, limit))
        
        results = cur.fetchall()
        return results
        
    finally:
        cur.close()
        conn.close()

# =============================================================================
# 검색 API
# =============================================================================
@app.post("/search", response_model=SearchResponse)
async def search_disease(query: SymptomQuery):
    """증상 입력으로 질환 검색"""
    
    if not query.query.strip():
        raise HTTPException(status_code=400, detail="검색어를 입력해주세요")
    
    try:
        # 검색 방법 선택
        if query.method == "fulltext":
            results = find_disease_by_fulltext(query.query, query.limit)
            score_key = "relevance"
        else:
            results = find_disease_by_keywords(query.query, query.limit)
            score_key = "match_count"
        
        if not results:
            return SearchResponse(
                success=False,
                message="입력하신 증상과 일치하는 질환을 찾을 수 없습니다.",
                matches=[]
            )
        
        matches = [
            DiseaseMatch(
                disease=r["disease"],
                symptoms=r["symptoms"],
                reference=r["ref"],
                score=float(r[score_key])
            )
            for r in results
        ]
        
        return SearchResponse(
            success=True,
            message=f"{len(matches)}개의 관련 질환을 찾았습니다.",
            matches=matches
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류 발생: {str(e)}")

# =============================================================================
# 전체 질환 목록 검색
# =============================================================================
@app.get("/diseases")
async def get_all_diseases(limit: int = 100):
    """DB에 저장된 모든 질환 목록 조회"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT disease, symptoms, ref
            FROM disease_symptoms
            ORDER BY disease
            LIMIT %s
        """, (limit,))
        
        results = cur.fetchall()
        
        return {
            "total": len(results),
            "diseases": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        cur.close()
        conn.close()

# =============================================================================
emb = GoogleGenerativeAIEmbeddings(model="text-embedding-004")

def embed_show(text: str):
    vec = emb.embed_query(text)
    return vec[:5], len(vec)



@app.post("/embed")
async def embed_post(req: EmbedReq):
    head, dim = embed_show(req.text)
    try:

        return JSONResponse({"input": req.text, "dim": dim, "head": head})
        print (JSONResponse)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




#1. 입력 받은 값 벡터화
#2. DB 데이터 벡터화
#3. 1&2 유사도 계산



# 실행 명령어
# uvicorn main:app --reload --host __.__.__.__ --port 5501
# 
# 파일 구조:
# project/
# ├── main.py
# ├── templates/
# │   └── index.html
# └── static/
#     └── style.css
# =============================================================================
