import io
import os
import torch
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone


SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

EXPECTED_USERNAME = os.getenv("AUTH_USERNAME")
EXPECTED_PASSWORD = os.getenv("AUTH_PASSWORD")

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

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") != EXPECTED_USERNAME:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")

@app.post("/login")
async def login(credentials: LoginRequest):
    if credentials.username != EXPECTED_USERNAME or credentials.password != EXPECTED_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid username or password")
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

@app.post("/translate")
async def translate_text(request: TranslationRequest, _: str = Depends(verify_token)):
    translated = translator(f'>>pob<< {request.text}', max_length=512)[0]['translation_text']
    return {"original": request.text, "translated": translated}