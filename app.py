import io
import os
import torch
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import List


SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

API_USERNAME = os.getenv("AUTH_USERNAME")
API_PASSWORD = os.getenv("AUTH_PASSWORD")

class LoginRequest(BaseModel):
    username: str
    password: str

class TranslationRequest(BaseModel):
    text: str

security = HTTPBearer()
app = FastAPI()
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base", use_fast=False)
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to("cpu")
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-en-pt")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # trocar pelo domain do frontend depois
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") != API_USERNAME:
            raise HTTPException(status_code=401, detail="Autenticação inválida")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

@app.post("/login")
async def login(credentials: LoginRequest):
    if credentials.username != API_USERNAME or credentials.password != API_PASSWORD:
        raise HTTPException(status_code=401, detail="Usuario ou senha inválidos")
    token = create_access_token(data={"sub": credentials.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/caption")
async def generate_caption(file: UploadFile = File(...), _: str = Depends(verify_token)):
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    inputs = processor(images=image, return_tensors="pt")
    output = model.generate(**inputs)
    caption_en = processor.decode(output[0], skip_special_tokens=True)

    caption_pt = translator(f'>>pob<< {caption_en}', max_length=512)[0]['translation_text']
    return {"original": caption_en, "translated": caption_pt}

@app.post("/batchcaption")
async def generate_captions(files: List[UploadFile] = File(...), _: str = Depends(verify_token)):
    results = []
    images = []

    for file in files[:4]:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        images.append(image)

    inputs = processor(images=images, return_tensors="pt", padding=True)
    outputs = model.generate(**inputs)

    for output in outputs:
        caption_en = processor.decode(output, skip_special_tokens=True)
        caption_pt = translator(f'>>pob<< {caption_en}', max_length=512)[0]['translation_text']
        results.append({"original": caption_en, "translated": caption_pt})

    return results

@app.post("/translate")
async def translate_text(request: TranslationRequest, _: str = Depends(verify_token)):
    translated = translator(f'>>pob<< {request.text}', max_length=512)[0]['translation_text']
    return {"original": request.text, "translated": translated}