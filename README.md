# CelebMate (셀럽메이트) 🎨

행정기관 및 동호회, 회사 등에서 승진/생일/환영 등 기념일을 축하하기 위해 **AI 카피라이트와 고해상도 합성 포스터를 자동 생성해주는 웹 서비스**입니다.

## 🚀 기능 (Features)
- **AI 기반 자동 누끼 및 포스터 합성**: 업로드된 인물 사진에서 배경을 자동으로 제거(rembg)하고 선택한 템플릿에 맞게 포스터를 렌더링합니다.
- **LLM 카피라이트 생성**: OpenRouter (Google Gemini / OpenAI GPT) API를 활용해 대상자에게 보내는 짧고 강렬한 축하 멘트를 자동으로 생성해 줍니다.
- **4종 멀티 렌더링**: 공식 포스터부터 다꾸/시네마틱 스타일까지 한 번의 클릭으로 4가지 컨셉의 포스터가 동시에 생성됩니다.

## 🛠️ 기술 스택 (Tech Stack)
- **Frontend**: React (Vite)
- **Backend**: FastAPI (Python), Uvicorn
- **AI & Image**: `rembg` (U-2-Net 배경 제거), `Pillow` (이미지 합성), `OpenAI` 라이브러리 (OpenRouter 연동)

## ⚙️ 설치 및 환경설정 (Installation & Setup)

이 프로젝트는 민감 데이터 및 하드코딩된 로컬 경로 유출을 방지하기 위해 `python-dotenv`를 사용합니다.

1. **저장소 클론 및 패키지 설치**
   ```bash
   git clone https://github.com/USERNAME/CelebMate.git
   cd CelebMate
   
   # Backend 패키지 설치
   pip install -r requirements.txt
   
   # Frontend 패키지 설치
   cd frontend
   npm install
   ```

2. **환경변수 설정 (.env)**
   프로젝트 루트에 `.env` 파일을 생성하고( `.env.example` 참고) 아래 항목들을 본인 PC의 실제 경로로 수정합니다.
   ```ini
   ONW_DIR=C:\Your\Path\To\DataFolder
   EXCEL_FILENAME=roster.xlsx
   OUTPUT_DIR=C:\Your\Path\To\ResultFolder
   ```
   > **주의**: 데이터(`*.xlsx`, 사진)와 `.env` 파일은 `.gitignore`에 등록되어 GitHub에 올라가지 않습니다.

## ▶️ 실행 방법 (How to Run)

1. **백엔드 서버 (FastAPI) 실행**
   ```bash
   python api.py
   # http://localhost:8000
   ```

2. **프론트엔드 서버 (React) 실행**
   ```bash
   cd frontend
   npm run dev
   # http://localhost:5173
   ```
