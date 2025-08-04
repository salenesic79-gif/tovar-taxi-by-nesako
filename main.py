from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="TovarTaxi by NESAKO")

# ---------------------- MODELI ----------------------

class User(BaseModel):
    id: int
    name: str
    role: str  # 'driver' ili 'client'
    rating: float = 0.0
    is_blocked: bool = False

class Shipment(BaseModel):
    id: int
    client_id: int
    driver_id: Optional[int] = None
    status: str = "pending"
    scheduled_time: Optional[str] = None
    qr_code: Optional[str] = None

class Feedback(BaseModel):
    user_id: int
    shipment_id: int
    rating: int
    comment: Optional[str] = ""

class Violation(BaseModel):
    user_id: int
    reason: str

class Stats(BaseModel):
    user_id: int
    deliveries: int
    rating: float
    earnings: float

# ---------------------- MOCK BAZE ----------------------

users: List[User] = []
shipments: List[Shipment] = []
violations: List[Violation] = []
feedbacks: List[Feedback] = []
stats: List[Stats] = []

# ---------------------- API RUTE ----------------------

@app.get("/")
def welcome():
    return {"msg": "Dobrodošli u TovarTaxi by NESAKO"}

@app.post("/register")
def register_user(user: User):
    users.append(user)
    return {"status": "registered", "user_id": user.id}

@app.post("/shipment/create")
def create_shipment(shipment: Shipment):
    shipments.append(shipment)
    return {"status": "shipment_created", "shipment_id": shipment.id}

@app.post("/shipment/scan")
def scan_qr(shipment_id: int):
    for shipment in shipments:
        if shipment.id == shipment_id:
            shipment.status = "picked"
            return {"status": "scanned", "shipment": shipment}
    raise HTTPException(status_code=404, detail="Shipment not found")

@app.post("/feedback")
def leave_feedback(f: Feedback):
    feedbacks.append(f)
    return {"status": "feedback_saved"}

@app.get("/stats/{user_id}")
def get_stats(user_id: int):
    for s in stats:
        if s.user_id == user_id:
            return s
    raise HTTPException(status_code=404, detail="No stats found")

@app.post("/report-violation")
def report_violation(v: Violation):
    violations.append(v)
    return {"status": "violation_reported"}

@app.get("/admin/violations")
def list_violations():
    return violations

@app.get("/admin/users")
def list_users():
    return users

@app.post("/admin/block")
def block_user(user_id: int):
    for u in users:
        if u.id == user_id:
            u.is_blocked = True
            return {"status": "blocked"}
    raise HTTPException(status_code=404, detail="User not found")

# ---------------------- TODO ----------------------
# Dodati kasnije:
# - Interni chat
# - Kalendar isporuka
# - Fakture
# - Statistika sa grafikom
# - Offline mod
# - API integracije
# - Sigurnost i crna lista

# ---------------------- START KOMANDA ----------------------
# Pokreni aplikaciju lokalno:
# uvicorn main:app --host=0.0.0.0 --port=10000