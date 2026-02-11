from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict
import uvicorn
import datetime
import uuid

app = FastAPI(title="Vet Clinic System")

# ----------
# BaseModel
# ----------

class MedicineItem(BaseModel):
    name: str
    amount: int

class TreatmentRequest(BaseModel):
    owner_name: str
    owner_email: str
    pet_name: str
    doctor_id: str
    service_type: str
    medicines: List[MedicineItem]

class BillModel(BaseModel):
    bill_id: str
    record_id: str
    total_amount: float
    details: List[Dict]
    status: str

# -----------------
# Class and method
# -----------------

class Stock:
    def __init__(self):
        self._inventory = {
            "Rabies Vaccine": {"qty": 10, "price": 350},
            "Paracetamol": {"qty": 50, "price": 10},
            "Amoxicillin": {"qty": 30, "price": 15},
            "Shampoo": {"qty": 20, "price": 150}
        }

    def get_price(self, name: str) -> float:
        return self._inventory.get(name, {}).get("price", 0.0)

    def validate_and_deduct(self, medicines: List[MedicineItem]):
        for med in medicines:
            if med.name not in self._inventory:
                raise HTTPException(status_code=404, detail=f"Medicine '{med.name}' not found.")
            if self._inventory[med.name]["qty"] < med.amount:
                raise HTTPException(status_code=400, detail=f"Not enough stock for '{med.name}'.")
        
        for med in medicines:
            self._inventory[med.name]["qty"] -= med.amount
        
        return True

class MedicalRecord:
    def __init__(self):
        self._records = {}

    def create_record(self, data: TreatmentRequest) -> str:
        record_id = str(uuid.uuid4())
        self._records[record_id] = {
            "id": record_id,
            "date": datetime.datetime.now(),
            **data.dict(), # unpack ข้อมูลจาก Pydantic
            "status": "Pending Payment"
        }
        return record_id

    def get_record(self, record_id: str) -> dict:
        record = self._records.get(record_id)
        if not record:
            raise HTTPException(status_code=404, detail="Medical record not found.")
        return record

class Notification:
    def __init__(self):
        self.sent_emails = []

    def send_email(self, email: str, subject: str, body: str):
        self.sent_emails.append({
            "to": email,
            "subject": subject,
            "time": datetime.datetime.now()
        })

    def get_sent_emails(self, email: str):
        return [log for log in self.sent_emails if log['to'] == email]

class Bill:
    def __init__(self):
        self._bills = {}
        self.BASE_SERVICE_FEE = 200.0

    def generate_bill(self, record: dict, stock_service: Stock) -> BillModel:
        total = self.BASE_SERVICE_FEE
        details = [{"item": "Service Fee", "qty": 1, "total": self.BASE_SERVICE_FEE}]

        for med in record['medicines']:
            name = med['name']
            amount = med['amount']
            price = stock_service.get_price(name)
            line_total = price * amount
            
            total += line_total
            details.append({"item": name, "qty": amount, "total": line_total})
            
        bill_id = f"BILL-{record['id'][:8]}"
        bill = BillModel(
            bill_id=bill_id,
            record_id=record['id'],
            total_amount=total,
            details=details,
            status="Generated"
        )
        
        self._bills[bill_id] = bill
        return bill
    
# --------
# FastAPI
# --------

stock_service = Stock()
record_service = MedicalRecord()
billing_service = Bill()
notification_service = Notification()

@app.get("/")
def root():
    return {"Welcome to Vet Clinic API"}

@app.post("/treatments", status_code=201)
def create_treatment(request: TreatmentRequest):
    
    stock_service.validate_and_deduct(request.medicines)
    record_id = record_service.create_record(request)
    
    return {
        "status": "success", 
        "record_id": record_id, 
        "message": "Treatment recorded & Stock updated."
    }

@app.post("/bills/{record_id}/process", response_model=BillModel)
def process_bill_and_notify(record_id: str, background_tasks: BackgroundTasks):
    record = record_service.get_record(record_id)
    bill = billing_service.generate_bill(record, stock_service)
    
    owner_email = record['owner_email']
    pet_name = record['pet_name']
    
    email_subject = f"Invoice for {pet_name}"
    email_body = f"Bill ready. Total: {bill.total_amount} THB"

    background_tasks.add_task(
        notification_service.send_email, 
        owner_email,
        email_subject, 
        email_body
    )

    return bill

@app.get("/customer/inbox/{email}")
def check_customer_inbox(email: str):
    msgs = notification_service.get_sent_emails(email)
    return {"email": email, "messages": msgs}

@app.get("/stock")
def check_stock_inventory():
    return stock_service._inventory

if __name__ == "__main__":
    uvicorn.run("pharmacy:app", host="127.0.0.1", port=8000, reload=True)