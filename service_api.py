from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# =============
#  Base Model
# =============

class TreatmentRequest(BaseModel):
    pet_name: str
    medicine: list[str]
    vaccine: list[str]
    price: float
    
class GroomingRequest(BaseModel):
    pet_name: str
    grooming_price: float

class BoardingRequest(BaseModel):
    pet_name: str
    boarding_price: float

# =========
#  Class
# =========
class Room:
    def __init__(self, room_id: str, room_price: float):
        self.__room_id = room_id
        self.__room_price = room_price

    @property
    def room_id(self):
        return self.__room_id

    @property
    def room_price(self):
        return self.__room_price

    def get_price(self) -> float:
        return self.__room_price


class Service:
    def __init__(self, type_service: str, price: float):
        self.__type_service = type_service
        self.__price = price

    @property
    def type_service(self):
        return self.__type_service

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, value: float):
        if value >= 0:
            self.__price = value

    def get_price(self) -> float:
        return self.__price

    @staticmethod
    def calculate_total_cost(services: list['Service']) -> float:
        total = 0.0
        for service in services:
            total += service.get_price()
        return total


class MedicalService(Service):
    def __init__(self, price: float, medicine: list[str], vaccine: list[str]):
        super().__init__(type_service="Medical", price=price)
        self.__medicine = medicine
        self.__vaccine = vaccine

    @property
    def medicine(self):
        return self.__medicine

    @property
    def vaccine(self):
        return self.__vaccine


class GroomingService(Service):
    def __init__(self, price: float):
        super().__init__(type_service="Grooming", price=price)


class BoardingService(Service):
    def __init__(self, price: float, room: Room):
        super().__init__(type_service="Boarding", price=price)
        self.__room = room

    @property
    def room(self):
        return self.__room

    def get_price(self) -> float:
        return self.price + self.__room.get_price()


class Pet:
    def __init__(self, name: str):
        self.__name = name
        self.__services: list[Service] = []
        self.__medical_records: list[MedicalService] = []

    @property
    def name(self):
        return self.__name

    def add_service(self, service: Service):
        self.__services.append(service)

    def add_medical_record(self, record: MedicalService):
        self.__medical_records.append(record)
        self.add_service(record)

    def get_services(self) -> list[Service]:
        return self.__services


class Doctor:
    def __init__(self, doctor_id: str, name: str):
        self.__doctor_id = doctor_id
        self.__name = name

    @property
    def doctor_id(self):
        return self.__doctor_id
    
    @property
    def name(self):
        return self.__name

    def start_treatment(self, pet: Pet, medicine: list[str], vaccine: list[str], price: float) -> MedicalService:
        medical_service = MedicalService(price=price, medicine=medicine, vaccine=vaccine)
        pet.add_medical_record(medical_service)
        return medical_service


class Clinic:
    def __init__(self, name: str):
        self.__name = name
        
    @property
    def name(self):
        return self.__name

    def start_payment(self, pet: Pet) -> float:
        services = pet.get_services()
        total_money = Service.calculate_total_cost(services)
        return total_money


# ==========
# FastAPI 
# ==========

app = FastAPI(title="Pet Clinic")

clinic = Clinic(name="Op Op Phee Clinic")
doctor_john = Doctor(doctor_id="D01", name="Dr. John")
room_a = Room(room_id="R01", room_price=500.0)
pets_db = {
    "Buddy": Pet(name="Buddy")
}


@app.get("/")
def read_root():
    return {"message": "Welcome to Happy Pet Clinic"}

@app.post("/MedicalService")
def start_treatment(req: TreatmentRequest):
    if req.pet_name not in pets_db:
        pets_db[req.pet_name] = Pet(name=req.pet_name)
    
    pet = pets_db[req.pet_name]
    
    med_service = doctor_john.start_treatment(
        pet=pet, 
        medicine=req.medicine, 
        vaccine=req.vaccine, 
        price=req.price
    )
    
    return {
        "status": "success",
        "message": f"Treatment completed for {pet.name} by {doctor_john.name}",
        "medical_record_added": {
            "type": med_service.type_service,
            "medicine": med_service.medicine,
            "vaccine": med_service.vaccine,
            "price": med_service.get_price()
        }
    }
    

@app.post("/GroomingService")
def add_grooming_service(req: GroomingRequest):
    if req.pet_name not in pets_db:
        raise HTTPException(status_code=404, detail="Pet not found. Please register first.")
    
    pet = pets_db[req.pet_name]
    
    grooming_service = GroomingService(price=req.grooming_price)
    pet.add_service(grooming_service)
    
    return {
        "status": "success",
        "message": f"Grooming service added for {pet.name}.",
        "grooming_cost": grooming_service.get_price()
    }

@app.post("/BoardingService")
def add_boarding_service(req: BoardingRequest):
    if req.pet_name not in pets_db:
        raise HTTPException(status_code=404, detail="Pet not found. Please do treatment or register first.")
    
    pet = pets_db[req.pet_name]
    boarding_service = BoardingService(price=req.boarding_price, room=room_a)
    pet.add_service(boarding_service)
    
    return {
        "status": "success",
        "message": f"Boarding service added for {pet.name}. Room price ({room_a.room_price}) included.",
        "total_boarding_cost": boarding_service.get_price()
    }

@app.get("/billing/{pet_name}")
def start_payment(pet_name: str):
    if pet_name not in pets_db:
        raise HTTPException(status_code=404, detail="Pet not found.")
    
    pet = pets_db[pet_name]
    
    total_amount = clinic.start_payment(pet)
    
    services_detail = []
    for svc in pet.get_services():
        services_detail.append({
            "service_type": svc.type_service,
            "price": svc.get_price()
        })
        
    return {
        "pet_name": pet.name,
        "services_list": services_detail,
        "total_amount": total_amount
    }
    
if __name__ == "__main__":
    uvicorn.run("service_api:app", host="127.0.0.1", port=8000, reload=True)