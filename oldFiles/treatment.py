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
    price: float = 0.0
    should_admit: bool = False


class MedicalService:
    def __init__(self, record_id, type_service, owner_obj, doctor_obj, pet_obj, symptom, medicine, vaccine, price, should_admit):
        self.__record_id = record_id
        self.__type_service = type_service
        self.__owner_obj = owner_obj
        self.__doctor_obj = doctor_obj
        self.__pet_obj = pet_obj
        self.__symptom = symptom
        self.__medicine = medicine
        self.__vaccine = vaccine
        self.__price = price
        self.__should_admit = should_admit

    @staticmethod
    def create_medical_service(record_id, type_service, owner_obj, doctor_obj, pet_obj, symptom, medicine, vaccine, price, should_admit):
        medical_service = MedicalService(
            record_id, type_service, owner_obj, doctor_obj, pet_obj, symptom, medicine, vaccine, price, should_admit)
        return medical_service

    def change_dict(self):
        return {
            "Id": self.__record_id,
            "Service": self.__type_service,
            "Owner ID": self.__owner_obj.customer_id,
            "Doctor": self.__doctor_obj.doctor_id,
            "Pet": self.__pet_obj.pet_name,
            "Symptom": self.__symptom,
            "Medicine": self.__medicine,
            "Vaccine": self.__vaccine,
            "Price": self.__price,
            "Should Admit": self.__should_admit
        }


class Doctor:
    Type = "Doctor"

    def __init__(self, doctor_id):
        self.__doctor_id = doctor_id
        self.__medical_service = []

    @property
    def doctor_id(self):
        return self.__doctor_id

    def start_medical_service(self, data: TreatmentRequest, clinic_obj):
        customer = clinic_obj.check_user(data.owner_id)
        if customer == None:
            return f"User is not found"

        pet = clinic_obj.check_pet_from_customer(customer, data.pet_name)
        if pet == None:
            return f"Pet is not found"

        symptom = data.symptom
        medicine = data.medicine
        vaccine = data.vaccine
        price = data.price
        should_admit = data.should_admit

        record_id = str(uuid.uuid4())

        medical_service = MedicalService.create_medical_service(
            record_id,
            data.type_service,
            customer,   # customer object
            self,       # doctor object
            pet,        # pet object
            symptom,
            medicine,
            vaccine,
            price,
            should_admit
        )

        self.__medical_service.append(medical_service)  # keep at Doctor

        unpaid_service = pet.search_unpaid_service()

        # check unpaid service
        if unpaid_service:
            unpaid_service.append_service(medical_service)

        else:
            new_big_service = Service()  # สร้างกล่องใหญ่
            new_big_service.append_service(
                medical_service)  # เพิ่ม sub service ลง

            pet.append_big_service(new_big_service)

        return medical_service


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

    def medical_treatment(self, data: TreatmentRequest, doctor_obj):

        medical_service = doctor_obj.start_medical_service(data, self)

        if isinstance(medical_service, MedicalService):
            self.__medical_service.append(
                medical_service)  # keep at Clinic

            return {"Status": "Success", "Data": medical_service.change_dict()}
        else:
            return {"Status": "Error", "Message": medical_service}

    def get_all_medical_record(self):  # object -> dict
        all_med_service = []
        for med in self.__medical_service:
            med_service = med.change_dict()
            all_med_service.append(med_service)
        return all_med_service

    def delete_medical_record(self, id):
        for med in self.__medical_service:
            if str(med.change_dict()["Id"]) == str(id):
                self.__medical_service.remove(med)

                return {
                    "Data": f"Medical record with id {id} has been deleted"
                }
        return {
            "Data": f"This Medical record with id {id} is not found!"
        }


class Service:
    def __init__(self):
        self.__sub_service = []
        self.__is_paid = False

    @property
    def is_paid(self):
        return self.__is_paid

    def mark_is_paid(self):
        self.__is_paid = True

    def append_service(self, sub_service):
        self.__sub_service.append(sub_service)
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
        self.__service = []
        self.__medical_record = []

    @property
    def pet_name(self):
        return self.__pet_name

    def search_unpaid_service(self):
        for service in self.__service:
            if service.is_paid == False:
                return service
        return None

    # สร้างกล่องใหม่ที่ pet หมอคนสั่งการให้ pet(เจ้าของข้อมูล)ทำ หมอไปยุ่งไม่ได้
    def append_big_service(self, new_service):
        self.__service.append(new_service)

    # สร้างเผื่อว่าอนาคตอยากค้นหาประวัติการรักษาเฉพาะอันไหนขึ้นมา
    def search_medical_record(self, record_id):
        for record in self.__medical_record:
            if str(record.change_dict()["Id"]) == str(record_id):
                return record
        return None


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


@app.post("/medical_treatment", tags=["Clinic Operation"])
async def add_medical_treatment(data: TreatmentRequest):
    doctor_obj = my_clinic.check_doctor_id(data.doctor_id)
    if not doctor_obj:
        return "Doctor is not found"

    medical_treatment = my_clinic.medical_treatment(data, doctor_obj)

    if medical_treatment["Status"] == "Success":
        return {
            "Message": "A medical treatment record has been added successfully!",
            "Data": medical_treatment["Data"]
        }
    else:
        return {
            "Message": medical_treatment["Message"]
        }


@app.get("/medical_treatment", tags=["Clinic Operation"])
async def get_medical_treatments():
    return {
        "Data": my_clinic.get_all_medical_record()
    }


@app.delete("/treatment", tags=["Clinic Operation"])
async def delete_medical_treatment(id: str):
    medical_treatment = my_clinic.delete_medical_record(id)
    return medical_treatment

if __name__ == "__main__":
    uvicorn.run("treatment:app", host="127.0.0.1",
                port=8000, log_level="info", reload=True)
