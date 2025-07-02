from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os
from supabase import create_client, Client
import datetime
import pandas as pd

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

def get_checkins():
    try:
        data = supabase.table("checkins").select("*").execute()
        if data.data:
            return data.data
        else:
            raise (data.error, data.status_code)
    except Exception as e:
        raise (data.error, data.status_code, e)
    
def get_checkins_kids():
    try:
        data = supabase.table("checkins").select("*").eq("plan_package","Youth Jiu Jitsu Membership").execute()
        if data.data:
            return data.data
        else:
            print("No data found")
    except Exception as e:
        print(e)
    
def get_checkins_kids_view():
    try:
        data = supabase.table("kids_checkins_summary").select("*").execute()
        if data.data:
            return data.data
        else:
            print("No data found")
    except Exception as e:
        print(e)
    

def get_checkins_kids():
    try:
        data = supabase.table("kids").select("*").execute()
        if data.data:
            return data.data
        else:
            print("No data found")
    except Exception as e:
        print(e)
    

class PromotionUpdate(BaseModel):
    client: str
    field: str # Or use datetime.date if you prefer
    value: datetime.date  # Or use datetime.date if you prefer

def update_promotion_date(data):
    try:
        data = (
        supabase.table("kids")
        .update(
            {"last_promotion_date": pd.to_datetime(data['value']).isoformat()})
        .eq("client", data['client'])
        .execute()
        )
        if data.data:
            return {"status": "success", "updated": data.data}
        else:
            print("No data found")
    except Exception as e:
        print(e)

class RankUpdate(BaseModel):
    client: str
    field: str # Or use datetime.date if you prefer
    value: str

def update_promotion_rank(data):
    try:
        data = (
        supabase.table("kids")
        .update(
            {"current_rank": data['value']})
        .eq("client", data['client'])
        .execute()
        )
        if data.data:
            return {"status": "success", "updated": data.data}
        else:
            print("No data found")
    except Exception as e:
        print(e)
    
class StripesUpdate(BaseModel):
    client: str
    field: str # Or use datetime.date if you prefer
    value: int

def update_promotion_stripes(data):
    try:
        data = (
        supabase.table("kids")
        .update(
            {"stripes": data['value']})
        .eq("client", data['client'])
        .execute()
        )
        if data.data:
            return {"status": "success", "updated": data.data}
        else:
            print("No data found")
    except Exception as e:
        print(e)
    
class StartDateUpdate(BaseModel):
    client: str
    field: str # Or use datetime.date if you prefer
    value: datetime.date  # Or use datetime.date if you prefer

def update_start_date(data):
    try:
        data = (
        supabase.table("kids")
        .update(
            {"start_date": pd.to_datetime(data['value']).isoformat()})
        .eq("client", data['client'])
        .execute()
        )
        if data.data:
            return {"status": "success", "updated": data.data}
        else:
            print("No data found")
    except Exception as e:
        print(e)
    
