from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import uuid

app = FastAPI()


class TreatmentRequest(BaseModel):
    type_service: str
    owner_name: str
    doctor_id: str
    pet_name: str
    symptom: list[str] = []
    medicine: list[str] = []
    vaccine: list[str] = []
    amount: float | None = 0.0


class TreatmentService:
    def __init__(self, record_id, type_service, owner_name, doctor_id, pet_name, symptom, medicine, vaccine, amount):
        self.__record_id = record_id
        self.__type_service = type_service
        self.__owner_name = owner_name
        self.__doctor_id = doctor_id
        self.__pet_name = pet_name
        self.__symptom = symptom
        self.__medicine = medicine
        self.__vaccine = vaccine
        self.__amount = amount

    @staticmethod
    def create_treatment_service(record_id, type_service, owner_name, doctor_id, pet_name, symptom, medicine, vaccine, amount):
        treatment_service = TreatmentService(
            record_id, type_service, owner_name, doctor_id, pet_name, symptom, medicine, vaccine, amount)
        return treatment_service

    def change_dict(self):
        return {
            "Id": self.__record_id,
            "Service": self.__type_service,
            "Owner": self.__owner_name,
            "Doctor": self.__doctor_id,
            "Pet": self.__pet_name,
            "Symptom": self.__symptom,
            "Medicine": self.__medicine,
            "Vaccine": self.__vaccine,
            "Amount": self.__amount
        }


class Doctor:
    def __init__(self, doctor_id):
        self.__doctor_id = doctor_id

    @property
    def doctor_id(self):
        return self.__doctor_id

    def start_treatment_service(self, data: TreatmentRequest, clinic_obj):
        user = clinic_obj.check_user(data.owner_name)
        if user == None:
            return f"User is not found"

        doc = clinic_obj.check_doctor_id(data.doctor_id)
        if doc == None:
            return f"Doctor is not found"

        pet = clinic_obj.check_pet_from_customer(user, data.pet_name)
        if pet == None:
            return f"Pet is not found"

        symptom = data.symptom
        medicine = data.medicine
        vaccine = data.vaccine
        amount = data.amount

        record_id = str(uuid.uuid4())

        treatment_service = TreatmentService.create_treatment_service(
            record_id,
            data.type_service,
            data.owner_name,
            data.doctor_id,
            data.pet_name,
            symptom,
            medicine,
            vaccine,
            amount
        )
        return treatment_service


class Clinic:
    def __init__(self, name):
        self.__name = name
        self.__customers = []
        self.__employees = []
        self.__medical_service = []

    def add_customer(self, customer_obj):
        self.__customers.append(customer_obj)

    def add_employee(self, employee_obj):
        self.__employees.append(employee_obj)

    def check_user(self, user):
        for c in self.__customers:
            if c.customer_name == user:
                return c
        return None

    def check_doctor_id(self, doctor_id):
        for d in self.__employees:
            if d.doctor_id == doctor_id:
                return d
        return None

    def check_pet_from_customer(self, customer_obj, pet):
        if customer_obj:  # check ว่าไม่ None
            return customer_obj.check_pet(pet)
        return None

    def treatment(self, data: TreatmentRequest, doctor_obj):
        treatment_service = doctor_obj.start_treatment_service(data, self)
        if isinstance(treatment_service, TreatmentService):
            self.__medical_service.append(treatment_service)
            return {"Status": "Success", "Data": treatment_service.change_dict()}
        else:
            return {"Status": "Error"}

    def get_all_treatment_record(self):  # object -> dict
        all_med_service = []
        for med in self.__medical_service:
            med_service = med.change_dict()
            all_med_service.append(med_service)
        return all_med_service

    def delete_treatment_record(self, id):
        for med in self.__medical_service:
            if str(med.change_dict()["Id"]) == str(id):
                self.__medical_service.remove(med)

                return {
                    "Data": f"Treatment record with id {id} has been deleted"
                }
        return {
            "Data": f"This Treatment record with id {id} is not found!"
        }


class Customer:
    def __init__(self, customer_name):
        self.__customer_name = customer_name
        self.__pets = []

    @property
    def customer_name(self):
        return self.__customer_name

    def add_pet(self, pet):
        self.__pets.append(pet)

    def check_pet(self, pet):
        for p in self.__pets:
            if p.pet_name == pet:
                return p
        return None


class Pet:
    def __init__(self, pet_name):
        self.__pet_name = pet_name

    @property
    def pet_name(self):
        return self.__pet_name


my_clinic = Clinic("PetShop")
doctor = Doctor("D01")
my_clinic.add_employee(doctor)
customer = Customer("Open")
pet = Pet("Mumu")
customer.add_pet(pet)
my_clinic.add_customer(customer)


@app.get("/", tags=['root'])
async def root() -> dict:
    return {"Pet Shop": "Online"}


@app.post("/treatment", tags=["Clinic Operation"])
async def add_treatment(data: TreatmentRequest):
    doctor_obj = my_clinic.check_doctor_id(data.doctor_id)
    if not doctor_obj:
        return "Error"

    treatment = my_clinic.treatment(data, doctor_obj)

    return {
        "Messege": "A treatment record has been added successfully!",
        "Data": treatment
    }


@app.get("/treatment", tags=["Clinic Operation"])
async def get_treatments():
    return {
        "Data": my_clinic.get_all_treatment_record()
    }


@app.delete("/treatment", tags=["Clinic Operation"])
async def delete_treatment(id: str):
    treatment = my_clinic.delete_treatment_record(id)
    return treatment

if __name__ == "__main__":
    uvicorn.run("treatment:app", host="127.0.0.1",
                port=8000, log_level="info", reload=True)
