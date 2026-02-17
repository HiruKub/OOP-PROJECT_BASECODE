from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import uuid

app = FastAPI()


class TreatmentRequest(BaseModel):
    type_service: str
    owner_id: str
    doctor_id: str
    pet_name: str
    symptom: list[str] = []
    medicine: list[str] = []
    vaccine: list[str] = []
    price: float | None = 0.0


class TreatmentService:
    def __init__(self, record_id, type_service, owner_id, doctor_id, pet_name, symptom, medicine, vaccine, price):
        self.__record_id = record_id
        self.__type_service = type_service
        self.__owner_id = owner_id
        self.__doctor_id = doctor_id
        self.__pet_name = pet_name
        self.__symptom = symptom
        self.__medicine = medicine
        self.__vaccine = vaccine
        self.__price = price

    @staticmethod
    def create_treatment_service(record_id, type_service, owner_id, doctor_id, pet_name, symptom, medicine, vaccine, price):
        treatment_service = TreatmentService(
            record_id, type_service, owner_id, doctor_id, pet_name, symptom, medicine, vaccine, price)
        return treatment_service

    def change_dict(self):
        return {
            "Id": self.__record_id,
            "Service": self.__type_service,
            "Owner ID": self.__owner_id,
            "Doctor": self.__doctor_id,
            "Pet": self.__pet_name,
            "Symptom": self.__symptom,
            "Medicine": self.__medicine,
            "Vaccine": self.__vaccine,
            "Price": self.__price
        }


class Doctor:
    def __init__(self, doctor_id):
        self.__doctor_id = doctor_id
        self.__treatment_service = []

    @property
    def doctor_id(self):
        return self.__doctor_id

    def start_treatment_service(self, data: TreatmentRequest, clinic_obj):
        user = clinic_obj.check_user(data.owner_id)
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
        price = data.price

        record_id = str(uuid.uuid4())

        treatment_service = TreatmentService.create_treatment_service(
            record_id,
            data.type_service,
            data.owner_id,
            data.doctor_id,
            data.pet_name,
            symptom,
            medicine,
            vaccine,
            price
        )
        self.__treatment_service.append(treatment_service)  # keep at Doctor

        add_status = pet.search_lastest_service().add_treatment_service(treatment_service)

        print(f"Status from pet: {add_status}")

        return treatment_service


class Clinic:
    def __init__(self, name):
        self.__name = name
        self.__customers = []
        self.__employees = []
        self.__treatment_service = []

    def add_customer(self, customer_obj):
        self.__customers.append(customer_obj)

    def add_employee(self, employee_obj):
        self.__employees.append(employee_obj)

    def check_user(self, user):
        for c in self.__customers:
            if c.customer_id == user:
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
            self.__treatment_service.append(
                treatment_service)  # keep at Clinic

            return {"Status": "Success", "Data": treatment_service.change_dict()}
        else:
            return {"Status": "Error", "Message": treatment_service}

    def get_all_treatment_record(self):  # object -> dict
        all_med_service = []
        for med in self.__treatment_service:
            med_service = med.change_dict()
            all_med_service.append(med_service)
        return all_med_service

    def delete_treatment_record(self, id):
        for med in self.__treatment_service:
            if str(med.change_dict()["Id"]) == str(id):
                self.__treatment_service.remove(med)

                return {
                    "Data": f"Treatment record with id {id} has been deleted"
                }
        return {
            "Data": f"This Treatment record with id {id} is not found!"
        }


class Service:
    def __init__(self):
        self.__sub_service = []

    def add_treatment_service(self, treatment_service):
        self.__sub_service.append(treatment_service)
        return "Add complete"


class Customer:
    def __init__(self, customer_id):
        self.__customer_id = customer_id
        self.__pets = []

    @property
    def customer_id(self):
        return self.__customer_id

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
        self.__services = []

    @property
    def pet_name(self):
        return self.__pet_name

    def create_new_service(self):
        new_service = Service()
        self.__services.append(new_service)

    def search_lastest_service(self):
        if len(self.__services) == 0:
            self.create_new_service()

        return self.__services[-1]


my_clinic = Clinic("PetShop")

doc1 = Doctor("D01")
doc2 = Doctor("D02")
my_clinic.add_employee(doc1)
my_clinic.add_employee(doc2)

customer1 = Customer("C01")
pet1 = Pet("Mumu")
pet2 = Pet("Mala")
customer1.add_pet(pet1)
customer1.add_pet(pet2)
my_clinic.add_customer(customer1)

customer2 = Customer("C02")
pet3 = Pet("Mimi")
customer2.add_pet(pet3)
my_clinic.add_customer(customer2)


@app.get("/", tags=['root'])
async def root() -> dict:
    return {"Pet Shop": "Online"}


@app.post("/treatment", tags=["Clinic Operation"])
async def add_treatment(data: TreatmentRequest):
    doctor_obj = my_clinic.check_doctor_id(data.doctor_id)
    if not doctor_obj:
        return "Doctor is not found"

    treatment = my_clinic.treatment(data, doctor_obj)

    if treatment["Status"] == "Success":
        return {
            "Message": "A treatment record has been added successfully!",
            "Data": treatment["Data"]
        }
    else:
        return {
            "Message": treatment["Message"]
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
