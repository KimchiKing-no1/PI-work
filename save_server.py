import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
from datetime import datetime
from typing import Union

app = FastAPI()

# =========================
# 저장할 폴더 경로
# =========================
SAVE_FOLDER = "./simulation_results"

if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# =========================
# GPT가 보낼 데이터 형식
# =========================
class SimulationResult(BaseModel):
    filename: str | None = None   # 저장할 파일명 (옵션)
    content: Union[dict, list, str]    # JSON(dict) 또는 TXT(str)

# =========================
# 저장 엔드포인트
# =========================
@app.post("/save_result")
async def save_result(data: SimulationResult):
    try:
        # 1. 파일명 결정 (기존 로직 + .json 강제 통일)
        if data.filename:
            filename = data.filename
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"state_{timestamp}"

        # 파일명이 .txt로 들어오거나 확장자가 없으면 .json으로 변경
        if filename.endswith(".txt"):
            filename = filename.replace(".txt", ".json")
        if not filename.endswith(".json"):
            filename += ".json"

        # 2. 내용 처리 (핵심 변경 부분 ⭐)
        final_content = data.content

        # 만약 내용이 문자열(String)로 왔다면?
        if isinstance(final_content, str):
            try:
                # 문자열 안에 JSON이 숨어있나 파싱 시도
                final_content = json.loads(final_content)
            except json.JSONDecodeError:
                # 진짜 그냥 텍스트라면 JSON 객체로 감싸기
                final_content = {"raw_text_content": final_content}

        # 3. 파일 저장 (무조건 json.dump로 저장)
        file_path = os.path.join(SAVE_FOLDER, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(final_content, f, indent=4, ensure_ascii=False)
            
        print(f"✅ JSON 저장 완료: {file_path}")
        return {"status": "success", "saved_as": filename}

    except Exception as e:
        print(f"❌ 저장 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 서버 실행
# =========================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

