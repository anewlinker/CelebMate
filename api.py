from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import shutil
from dotenv import load_dotenv
from data_manager import DataManager
from image_generator import ImageGenerator
from openai import OpenAI

app = FastAPI(title="CelebMate API v2")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

ONW_DIR = os.getenv("ONW_DIR", "./data")
EXCEL_PATH = os.path.join(ONW_DIR, os.getenv("EXCEL_FILENAME", "roster.xlsx"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./result")

if not os.path.exists(ONW_DIR):
    os.makedirs(ONW_DIR)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

data_manager = DataManager(EXCEL_PATH)
image_generator = ImageGenerator(OUTPUT_DIR)

class GenerateRequest(BaseModel):
    member_name: str
    member_rank: str = ""
    message: str
    event_type: str = "생일"

class MessageRequest(BaseModel):
    member_name: str
    member_rank: str = ""
    event_type: str
    custom_prompt: str = ""
    api_key: str

@app.get("/api/events")
def get_events():
    birthdays = data_manager.get_upcoming_events(event_type="생일", days=30)
    promotions = data_manager.get_upcoming_events(event_type="승진", days=30)
    return {"birthdays": birthdays, "promotions": promotions}

@app.post("/api/upload/roster")
async def upload_roster(file: UploadFile = File(...)):
    try:
        with open(EXCEL_PATH, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        data_manager.load_data()
        return {"success": True, "message": "명부가 업데이트 되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload/photo")
async def upload_photos(files: List[UploadFile] = File(...)):
    try:
        uploaded_names = []
        for file in files:
            ext = os.path.splitext(file.filename)[1].lower()
            if not ext:
                ext = ".jpg"
            name = os.path.splitext(file.filename)[0]
            save_path = os.path.join(ONW_DIR, f"{name}{ext}")
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_names.append(name)
        return {"success": True, "message": f"{len(uploaded_names)}장의 사진이 업로드 되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate_message")
def generate_message(req: MessageRequest):
    if not req.api_key:
        raise HTTPException(status_code=400, detail="API Key is required")
    
    try:
        if req.api_key.startswith("sk-or-"):
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=req.api_key,
            )
            model_name = "google/gemini-2.5-flash"
        else:
            client = OpenAI(api_key=req.api_key)
            model_name = "gpt-3.5-turbo"

        rank = req.member_rank
        if rank in ["9급", "8급", "7급", "6급"]:
            title = "주무관"
        elif rank == "5급":
            title = "사무관"
        elif rank == "4급":
            title = "서기관"
        elif rank == "3급":
            title = "부이사관"
        else:
            title = rank if rank else "직원"

        if req.custom_prompt:
            prompt = f"회사 동료 '{req.member_name} {title}'에게 보낼 축하 메시지를 작성해줘. 참고할 사유는 '{req.custom_prompt}'야. 1~2줄짜리 짧고 센스있는 문구로 화려하게 작성해줘. 너무 길지 않게 해줘."
        else:
            prompt = f"회사 동료 '{req.member_name} {title}'의 '{req.event_type}' 축하 포스터에 들어갈 1~2줄짜리 짧고 센스있는 문구를 작성해줘. 영화 포스터나 웹툰 대사처럼 임팩트 있게 해줘. 너무 길지 않게 해줘."
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "너는 사내 이벤트를 기획하고 동료들의 기운을 북돋아주는 분위기 메이커야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        message = response.choices[0].message.content.strip()
        return {"success": True, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
def generate_poster(req: GenerateRequest):
    photo_path_jpg = os.path.join(ONW_DIR, f"{req.member_name}.jpg")
    photo_path_png = os.path.join(ONW_DIR, f"{req.member_name}.png")
    
    photo_path = photo_path_jpg
    if not os.path.exists(photo_path) and os.path.exists(photo_path_png):
        photo_path = photo_path_png
        
    output_filenames = []
    result_paths = []
    
    # Generate 4 styles
    templates = ["template_1.png", "template_2.png", "template_3.png", "template_4.png"]
    for i, t_name in enumerate(templates, 1):
        t_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", t_name)
        out_name = f"{req.member_name}_{req.event_type}_스타일{i}.png"
        res_path = image_generator.generate_poster(photo_path, req.message, out_name, req.member_name, req.event_type, req.member_rank, template_path=t_path)
        if res_path:
            output_filenames.append(out_name)
            result_paths.append(res_path)
            
    if result_paths:
        return {"success": True, "filenames": output_filenames, "paths": result_paths}
    
    raise HTTPException(status_code=500, detail="Failed to generate poster")

@app.get("/images/{filename}")
def get_image(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Image not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
