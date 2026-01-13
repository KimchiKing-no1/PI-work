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
    content: Union[dict, str]     # JSON(dict) 또는 TXT(str)

# =========================
# 저장 엔드포인트
# =========================
@app.post("/save_result")
async def save_result(data: SimulationResult):
    try:
        # -------------------------
        # 파일명 결정
        # -------------------------
        if data.filename:
            filename = data.filename
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"state_{timestamp}"

        # -------------------------
        # TXT 저장
        # -------------------------
        if isinstance(data.content, str):
            if not filename.endswith(".txt"):
                filename = filename.replace(".json", "")
                filename += ".txt"

            file_path = os.path.join(SAVE_FOLDER, filename)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(data.content)

        # -------------------------
        # JSON 저장
        # -------------------------
        else:
            if not filename.endswith(".json"):
                filename = filename.replace(".txt", "")
                filename += ".json"

            file_path = os.path.join(SAVE_FOLDER, filename)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data.content, f, indent=4, ensure_ascii=False)

        # -------------------------
        # 성공 응답
        # -------------------------
        return {
            "status": "success",
            "saved_as": filename,
            "path": file_path
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 서버 실행
# =========================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
