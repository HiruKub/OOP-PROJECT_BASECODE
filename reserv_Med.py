from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import uuid
from abc import ABC, abstractmethod

app = FastAPI()

class ReservationMedicalRequest(BaseModel):
    customer_id: str
    pet_id: str
    service_type: str 
    datetime_str: str


class Notification:
    def send_confirmation(self, method: str, reservation_id: str):
        print(f"[{method}] Sent confirmation for Reservation ID: {reservation_id}")
        return True


class Reservation(ABC):
    def __init__(self, reservation_id, customer, pet, time):
        self.reservation_id = reservation_id
        self.customer = customer
        self.pet = pet
        self.time = time
        self.status = "confirmed"
        self.service_type = "Medical"

    @abstractmethod
    def get_details(self):
        pass


class MedicalReservation(Reservation):
    def __init__(self, reservation_id, customer, pet, time, doctor):
        super().__init__(reservation_id, customer, pet, time)
        self.doctor = doctor

    def get_details(self):
        return f"[Medical Appointment] with {self.doctor.name} for {self.pet.name}"


class TimeSchedule:
    def __init__(self):
        self.__busy_slots = []

    def search_availability(self, time: str) -> bool:
        if time not in self.__busy_slots:
            return True
        return False

    def update_schedule(self, time: str) -> bool:
        if self.search_availability(time):
            self.__busy_slots.append(time)
            print(f"Schedule updated: Booked at {time}")
            return True
        else:
            print(f"Schedule update failed: {time} is already busy")
            return False


class Doctor:
    def __init__(self, doctor_id, name):
        self.__doctor_id = doctor_id
        self.__name = name
        self.__timeschedule = TimeSchedule()

    @property
    def doctor_id(self):
        return self.__doctor_id

    @property
    def name(self):
        return self.__name

    def get_avaliable_work(self, time: str) -> bool:
        return self.__timeschedule.search_availability(time)

    def update_timeslot(self, time: str) -> bool:
        return self.__timeschedule.update_schedule(time)


class Pet:
    def __init__(self, petID, name, pet_type, species, weight, customer_id, aggressive=False):
        self.__petID = petID
        self.__name = name
        self.__type = pet_type
        self.__species = species
        self.__weight = weight
        self.__customer_id = customer_id
        self.__aggressive = bool(aggressive)

    @property
    def id(self):
        return self.__petID

    @property
    def name(self):
        return self.__name


class Customer:
    def __init__(self, customer_id, name, phone_number, email):
        self.__customer_id = customer_id
        self.__name = name
        self.__phoneNumber = phone_number
        self.__email = email
        self.__pets = []
        self.__reservation_list = []

    def add_pet(self, pet: Pet):
        self.__pets.append(pet)

    def add_reservation(self, reservation: Reservation):
        self.__reservation_list.append(reservation)

    @property
    def email(self):
        return self.__email

    @property
    def phone(self):
        return self.__phoneNumber

    @property
    def name(self):
        return self.__name

    @property
    def id(self):
        return self.__customer_id


class Clinic:
    def __init__(self):
        self.__list_customers = []
        self.__pets = []
        self.__employees = []
        self.__reservation_list = []
        self.__notification = Notification()
        self._setup_dummy_data()

    def _setup_dummy_data(self):
        self.__employees.append(Doctor("D01", "Dr.習近平"))
        
        c1 = Customer("C01", "无规矩不成方圆", "0999999999", "无规矩@email.com")
        p1 = Pet("P01", "惩前毖后", "狗", "Golden Retriever", 25, "C01")
        c1.add_pet(p1)
        
        self.__list_customers.append(c1)
        self.__pets.append(p1)

    def get_customer_info(self, customer_id: str):
        for c in self.__list_customers:
            if c.id == customer_id:
                return c
        return None

    def get_pet_info(self, pet_id: str):
        for p in self.__pets:
            if p.id == pet_id:
                return p
        return None

    def create_reservation(self, customer_id: str, pet_id: str, service_type: str, time: str):
        if service_type != "Medical":
            return {"status": "fail", "message": "This endpoint only supports Medical reservations."}

        customer = self.get_customer_info(customer_id)
        if not customer:
            return {"status": "fail", "message": "Customer not found"}

        pet = self.get_pet_info(pet_id)
        if not pet:
            return {"status": "fail", "message": "Pet not found"}

        resource = None

        for doctor in self.__employees:
            if isinstance(doctor, Doctor):
                if doctor.get_avaliable_work(time):
                    if doctor.update_timeslot(time):
                        resource = doctor
                        break

        if resource:
            reservation_id = str(uuid.uuid1())[:8]
            
            new_reservation = MedicalReservation(reservation_id, customer, pet, time, resource)
            
            self.__reservation_list.append(new_reservation)
            
            customer.add_reservation(new_reservation)

            if customer.email:
                self.__notification.send_confirmation("EMAIL", reservation_id)
            elif customer.phone:
                self.__notification.send_confirmation("SMS", reservation_id)

            return {
                "status": "success",
                "customer_name": customer.name,
                "detail": new_reservation.get_details(),
                "time": time,
                "payment": "Pay Later"
            }
        else:
            return {
                "status": "fail",
                "message": f"No available doctor for Medical at {time}"
            }

clinic_sys = Clinic()

@app.get("/")
def read_root():
    return {"status": "早上好"}

@app.post("/Reservation", tags=["Reservation"])
async def make_reservation(req: ReservationMedicalRequest):
    result = clinic_sys.create_reservation(
        req.customer_id,
        req.pet_id,
        req.service_type,
        req.datetime_str
    )
    return result


if __name__ == "__main__":
    uvicorn.run("reserv_Med:app", host="127.0.0.1", port=8000, reload=True)