from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()


class TreatmentRequest(BaseModel):
    owner_name: str
    doctor_id: str
    pet_name: str
    type_service: str
    symptom: str
    amount: float


class Customer:
    def __init__(self, customer_id, customer_name, call, email):
        self.__customer_id = customer_id
        self.__customer_name = customer_name
        self.__call = call
        self.__email = email
        self.__pets = []
        self.__current_reservation = None
        self.__is_check_in = False

    @property
    def customer_name(self):
        return self.__customer_name

    def add_pet(self, pet):
        self.__pets.append(pet)

    def check_pet(self, pet):
        for p in self.__pets:
            if p.name == pet:
                return p
        return None


class Notification:
    # def __init__(self, message):
    #     self.__message = message
    #     self.__sent_time = datetime.now()

    @staticmethod
    def create_notification(message):
        sent_time = datetime.now()
        return f"Service is done: {message} (at {sent_time})"


class MedicalRecord:
    def __init__(self, record_id, owner_name, doctor_id, pet_name, type_service, symptom, amount):
        self.__record_id = record_id
        self.__owner_name = owner_name
        self.__doctor_id = doctor_id
        self.__pet_name = pet_name
        self.__type_service = type_service
        self.__symptom = symptom
        self.__amount = amount

    @staticmethod
    def create_med_history(record_id, owner_name, doctor_id, pet_name, type_service, symptom, amount, pet_obj):
        record = MedicalRecord(record_id, owner_name, doctor_id,
                               pet_name, type_service, symptom, amount)  # พิมพ์ใบเสร็จ
        pet_obj.add_medical_record(record)  # เก็บลง Pet
        return record

    def change_dict(self):
        return {
            "Id": self.__record_id,
            "Owner": self.__owner_name,
            "Doctor": self.__doctor_id,
            "Pet": self.__pet_name,
            "Service": self.__type_service,
            "Symptom": self.__symptom,
            "Amount": self.__amount
        }


class Clinic:
    ID = 1

    def __init__(self, user):
        self.__user = user
        self.__customers = []     # list
        self.__stocks = []           # list
        self.__employees = []     # list
        self.__rooms = []             # list
        self.__bills = []             # list
        self.__reservations = []           # list
        self.__grooming_history = []  # list
        self.__medical_record = []      # list

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

    def add_customer(self, customer_obj):
        self.__customers.append(customer_obj)

    def add_employee(self, employee_obj):
        self.__employees.append(employee_obj)

    def treatment(self, data: TreatmentRequest, doctor_obj):
        record = doctor_obj.start_treatment(data, self)
        if isinstance(record, MedicalRecord):
            self.__medical_record.append(record)
            noti = Notification.create_notification(
                f"Treatment {data.pet_name} success")
            return {"Status": "Service is done",
                    "Notification": noti}
        return {"Status": "Error"}

    def get_all_treatment_record(self):  # object -> dict
        all_records = []
        for med_rec in self.__medical_record:
            record = med_rec.change_dict()
            all_records.append(record)
        return all_records

    def delete_treatment_record(self, id):
        for record in self.__medical_record:
            if int(record.change_dict()["Id"]) == int(id):
                self.__medical_record.remove(record)

                return {
                    "Data": f"Treatment record with id {id} has been deleted"
                }
        return {
            "Data": f"This Treatment record with id {id} is not found!"
        }


class Doctor:
    def __init__(self, doctor_id, name, license, proficiency):
        self.__doctor_id = doctor_id
        self.__name = name
        self.__license = license
        self.__proficiency = proficiency
        self.__medical_record = []

    @property
    def doctor_id(self):
        return self.__doctor_id

    def start_treatment(self, data: TreatmentRequest, clinic_obj):
        user = clinic_obj.check_user(data.owner_name)
        if user == None:
            return f"User is not found"

        doc = clinic_obj.check_doctor_id(data.doctor_id)
        if doc == None:
            return f"Doctor is not found"

        pet = clinic_obj.check_pet_from_customer(user, data.pet_name)
        if pet == None:
            return f"Pet is not found"

        pet.update_symptom(data.symptom)

        record = MedicalRecord.create_med_history(
            clinic_obj.ID,
            data.owner_name,
            data.doctor_id,
            data.pet_name,
            data.type_service,
            data.symptom,
            data.amount,
            pet
        )

        clinic_obj.ID += 1

        return record


class Pet:
    def __init__(self, name, type, species, weight, customer_id, is_aggressive):
        self.__name = name
        self.__type = type
        self.__species = species
        self.__weight = weight
        self.__customer_id = customer_id
        self.__symptom = ""
        self.__medical_record = []

    @property
    def name(self):
        return self.__name

    @property
    def customer_id(self):
        return self.__customer_id

    def add_medical_record(self, treatment):     # เก็บ medical record
        self.__medical_record.append(treatment)
        return "Add Complete"

    def update_symptom(self, symptom):
        self.__symptom = symptom
        return "Update complete"


my_clinic = Clinic("PetShop")

doctor = Doctor("D01", "Sorawit", "123", "Internal Medicine")
my_clinic.add_employee(doctor)

customer = Customer("C01", "A", "1112", "A@gmail.com")
pet = Pet("B", "Cat", "Bombay", 4.5, "C01", False)
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
async def delete_treatment(id: int):
    treatment = my_clinic.delete_treatment_record(id)
    return treatment

if __name__ == "__main__":
    uvicorn.run("treatment:app", host="127.0.0.1",
                port=8000, log_level="info", reload=True)
