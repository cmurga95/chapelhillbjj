from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os
from supabase import create_client, Client
import asyncio
import uvicorn 
import datetime
# from decouple import config
from fastapi.middleware.cors import CORSMiddleware
# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Models
class CheckIn(BaseModel):
    client: str
    member_status: str
    session_datetime: str
    checkin_datetime: str
    session_type: str
    coach_name: str
    assistant_coach_name: str
    session_category_name: str
    session_title: str
    plan_package: str

class SessionList(BaseModel):
    sessions: List[CheckIn]


app = FastAPI()

memory_db = {
        "client": "test",
    "member_status": "test",
    "session_datetime": "test",
    "checkin_datetime": "test",
    "session_type": "test",
    "coach_name": "test",
    "assistant_coach_name": "test",
    "session_category_name": "test",
    "session_title": "test",
    "plan_package": "test",
}
# Routes
@app.get("/")
async def read_root():
    return {"status": "API is running!"}

@app.get("/checkins")
def get_checkins():
    try:
        data = supabase.table("checkins").select("*").execute()
        if data.data:
            return data.data
        else:
            return SessionList(sessions=[])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/checkins_kids")
def get_checkins_kids():
    try:
        data = supabase.table("checkins").select("*").eq("plan_package","Youth Jiu Jitsu Membership").execute()
        if data.data:
            return data.data
        else:
            return ("No data found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/checkins_kids_view")
def get_checkins_kids_view():
    try:
        data = supabase.table("kids_checkins_summary").select("*").execute()
        if data.data:
            return data.data
        else:
            return ("No data found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@app.get("/kids")
def get_checkins_kids():
    try:
        data = supabase.table("kids").select("*").execute()
        if data.data:
            return data.data
        else:
            return ("No data found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

class PromotionUpdate(BaseModel):
    client: str
    field: str # Or use datetime.date if you prefer
    value: datetime.date  # Or use datetime.date if you prefer

@app.patch("/kids/update-promotion-date")
def update_promotion_date(data: PromotionUpdate):
    try:
        data = (
        supabase.table("kids")
        .update(
            {"last_promotion_date": data.value.isoformat()})
        .eq("client", data.client)
        .execute()
        )
        if data.data:
            return {"status": "success", "updated": data.data}
        else:
            raise HTTPException(status_code=404, detail="Client not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RankUpdate(BaseModel):
    client: str
    field: datetime.date # Or use datetime.date if you prefer
    value: str

@app.patch("/kids/update-rank")
def update_promotion_rank(data: RankUpdate):
    try:
        data = (
        supabase.table("kids")
        .update(
            {"current_rank": data.value})
        .eq("client", data.client)
        .execute()
        )
        if data.data:
            return {"status": "success", "updated": data.data}
        else:
            raise HTTPException(status_code=404, detail="Client not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   
    
class StripesUpdate(BaseModel):
    client: str
    field: str # Or use datetime.date if you prefer
    value: int

@app.patch("/kids/update-stripes")
def update_promotion_stripes(data: StripesUpdate):
    try:
        data = (
        supabase.table("kids")
        .update(
            {"stripes": data.value})
        .eq("client", data.client)
        .execute()
        )
        if data.data:
            return {"status": "success", "updated": data.data}
        else:
            raise HTTPException(status_code=404, detail="Client not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))   
    
class StartDateUpdate(BaseModel):
    client: str
    field: str # Or use datetime.date if you prefer
    value: datetime.date  # Or use datetime.date if you prefer

@app.patch("/kids/update-start_date")
def update_start_date(data: StartDateUpdate):
    try:
        data = (
        supabase.table("kids")
        .update(
            {"start_date": data.value.isoformat()})
        .eq("client", data.client)
        .execute()
        )
        if data.data:
            return {"status": "success", "updated": data.data}
        else:
            raise HTTPException(status_code=404, detail="Client not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  