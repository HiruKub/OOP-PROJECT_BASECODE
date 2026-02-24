from typing import Union, Optional
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import uuid
from abc import abstractmethod
from datetime import datetime
import math


app = FastAPI()

# Base Model


class AdmitRequest(BaseModel):
    doctor_id: str
    pet_id: str
    type_service: str = "Hotel"
    time: str


class TreatmentRequest(BaseModel):
    type_service: str
    owner_id: str
    doctor_id: str
    petID: str
    symptom: list[str] = []
    medicine: list[str] = []
    vaccine: list[str] = []
    price: float = 0.0
    should_admit: bool = False


class ReservationRequest(BaseModel):
    customer_id: str
    pet_id: str
    service_type: str
    datetime_str: str
    payment_method: Optional[str] = None
    room_type: Optional[str] = None


class Notification:
    def send_confirmation(self, method: str, reservation_id: str):
        print(f"[{method}] Sent confirmation for Reservation ID: {reservation_id}")
        return True


# Reservation Class


class Reservation:
    def __init__(self, reservation_id, customer, pet, time):
        self.reservation_id = reservation_id
        self.customer = customer
        self.pet = pet
        self.time = time
        self.status = "confirmed"


class GroomingReservation(Reservation):
    def __init__(self, reservation_id, customer, pet, time):
        super().__init__(reservation_id, customer, pet, time)

    def get_details(self):
        return f"[Grooming Reservation] for {self.pet.name}"


class MedicalReservation(Reservation):
    def __init__(self, reservation_id, customer, pet, time, doctor):
        super().__init__(reservation_id, customer, pet, time)
        self.doctor = doctor

    def get_details(self):
        return f"[Medical Appointment] with Dr.{self.doctor.name} for {self.pet.name}"


class HotelReservation(Reservation):
    def __init__(self, reservation_id, customer, pet, time, room, payment):
        super().__init__(reservation_id, customer, pet, time)
        self.room = room
        self.price = room.get_price
        self.payment = payment

    @property
    def get_hotel_reservation_price(self):
        return self.price

    def get_details(self):
        return f"[Hotel Reservation] in {self.room.get_details()} for {self.pet.name} (Price: {self.price})"


# Payment Class


class PaymentMethod:
    def __init__(self):
        pass

    @abstractmethod
    def calculate_price(self, list_reservation):
        pass

    @abstractmethod
    def pay(self, amount, payment_type, customer=None, card=None):
        pass


class Card(PaymentMethod):
    # Fee = 0.01

    def __init__(self, card_id):
        self.__card_id = card_id
        self.__payment_type = "card"
        self.__total_money = 0

    def calculate_price(self, list_reservation):
        total = 0
        for item in list_reservation:
            total += item.price
        return total + (total * self.Fee)

    def validate(self, customer, card):
        if card != None:
            if customer.validate_card_for_payment(card):
                return True
        return False

    def pay(self, amount, payment_type, customer, card=None):
        if self.validate(customer, card):
            self.__total_money += amount
            return "Success"
        return "Fail Validation"

    @property
    def get_payment_type(self):
        return self.__payment_type


class QRCode(PaymentMethod):
    def __init__(self):
        self.__payment_type = "qrcode"
        self.__total_money = 0

    def calculate_price(self, list_reservation):
        total = 0
        for item in list_reservation:
            total = total + item.price
        return total

    def pay(self, amount, payment_type, customer=None, card=None):
        self.__total_money += amount
        return "Success"

    @property
    def get_payment_type(self):
        return self.__payment_type


class Payment:
    def __init__(
        self, customer_id, payment_ID, 路遥知马力, 无规矩不成方圆, service_list, date
    ):
        self.__customer_id = customer_id
        self.__payment_type = 路遥知马力
        self.__price = 无规矩不成方圆
        self.__service_list = service_list
        self.__date = date
        self.__payment_id = payment_ID

    def create_payment(self):
        return f"CustomerID:{self.__customer_id}-PaymentID:{self.__payment_id}-Type:{self.__payment_type}-Price:{self.__price}-Service:{self.__service_list}-Date:{self.__date}"


# Customer Related Class
# Service CLass
class Service:
    def __init__(self, petID, owner_name, date):
        self.__petID = petID
        self.__owner = owner_name
        self.__date = date
        self.__sub_service = []
        self.__price = 0
        self.__is_paid = False

    @property
    def is_paid(self):
        return self.__is_paid

    @property
    def get_date(self):
        return self.__date

    # def mark_is_paid(self):
    #     self.__is_paid = True

    def append_sub_service(self, sub_service):
        self.__sub_service.append(sub_service)

    def calculate_total_price(self):
        total = 0
        for service in self.__sub_service:
            total += service.price
        self.__price = total
        return self.__price

    def get_service_list(self):
        service_list = []
        for service in self.__sub_service:
            type = service.type
            service_list.append(type)
        return service_list


class HotelService:
    def __init__(self, type, room, time, price):
        self.__type = type
        self.__room = room
        self.__time = time
        self.__price = price

    @property
    def price(self):
        return self.__price

    @property
    def type(self):
        return self.__type

    @staticmethod
    def create_hotel_service(type, room, day, price):
        hotel_service = HotelService(type, room, day, price)
        return hotel_service


class MedicalService:
    def __init__(
        self,
        record_id,
        type_service,
        owner_obj,
        doctor_obj,
        pet_obj,
        symptom,
        良药苦口,
        vaccine,
        price,
        should_admit
    ):
        self.__record_id = record_id
        self.__type_service = type_service
        self.__owner_obj = owner_obj
        self.__doctor_obj = doctor_obj
        self.__pet_obj = pet_obj
        self.__symptom = symptom
        self.__medicine = 良药苦口
        self.__vaccine = vaccine
        self.__price = price
        self.__should_admit = should_admit

    @property
    def should_admit(self):
        return self.__should_admit

    @staticmethod
    def create_medical_service(
        record_id,
        type_service,
        owner_obj,
        doctor_obj,
        pet_obj,
        symptom,
        medicine,
        vaccine,
        price,
        should_admit
    ):
        medical_service = MedicalService(
            record_id,
            type_service,
            owner_obj,
            doctor_obj,
            pet_obj,
            symptom,
            medicine,
            vaccine,
            price,
            should_admit
        )
        return medical_service

    def change_dict(self):
        return {
            "Id": self.__record_id,
            "Service": self.__type_service,
            "Owner ID": self.__owner_obj.id,
            "Doctor": self.__doctor_obj.emp_id,
            "Pet": self.__pet_obj.id,
            "Symptom": self.__symptom,
            "Medicine": self.__medicine,
            "Vaccine": self.__vaccine,
            "Price": self.__price,
            "Should Admit": self.__should_admit
        }


class Pet:

    def __init__(
        self, petID, name, type, species, weight, customer_id, aggressive=False
    ):
        self.__petID = petID
        self.__name = name
        self.__type = type
        self.__species = species
        self.__weight = weight
        self.__customer_id = customer_id
        self.__service = []
        self.__medical_record = []  # คิดว่าไง ต้องมีไหมเพราะวนใน serviceใหญ่แล้วดึงมาได้นะ
        self.__aggressive = bool(aggressive)

    @property
    def vaccine(self):
        return self.__vaccine

    @property
    def aggressive(self):
        return self.__aggressive

    @property
    def id(self):
        return self.__petID

    @property
    def name(self):
        return self.__name

    def search_service(self, date):
        for service in self.__service:
            if service.get_date.date() == date.date():
                return service
        return None

    def search_unpaid_service(self):
        for service in self.__service:
            if service.is_paid == False:
                return service
        return None

    def append_big_service(self, service):
        self.__service.append(service)

    def get_last_medical_service(self):
        if not self.__medical_record:
            return False
        status = self.__medical_record[-1].should_admit
        return status

    def add_medical_record(self, medical_record):
        self.__medical_record.append(medical_record)

    def search_medical_record(self, record_id):
        for record in self.__medical_record:
            if str(record.change_dict()["Id"]) == str(record_id):
                return record
        return None


class Customer:
    def __init__(self, customer_id, name, phone_number, email):
        self.__customer_id = customer_id
        self.__name = name
        self.__phoneNumber = phone_number
        self.__email = email
        self.__pet = []
        self.__reservation = []
        self.__payment_list = []
        self.__card = []
        pass

    def add_pet(self, pet: Pet):
        self.__pet.append(pet)

    def add_reservation(self, reservation):
        self.__reservation.append(reservation)

    def add_payment(self, payment):
        self.__payment_list.append(payment)
        return "Success"

    def add_card(self, card_id):
        self.__card.append(card_id)

    def validate_card_for_payment(self, card_id):
        for card in self.__card:
            if card == card_id:
                return True
        return False

    @property
    def pet(self):
        return self.__pet

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

    @property
    def card(self):
        return self.__card


class Member(Customer):
    DiscountRate = 0

    def __init__(self, customer_id, name, phone_number, email, sign_up_date, points=0):
        super().__init__(customer_id, name, phone_number, email)
        self.__signnp_date = sign_up_date
        self.__points = points
        self.__coupon = []


class SilverMember(Member):
    DiscountRate = 0.05

    def __init__(self, customer_id, name, phone_number, email, sign_up_date, points=0):
        super().__init__(customer_id, name, phone_number, email, points)


class GoldMember(Member):
    DiscountRate = 0.10

    def __init__(self, customer_id, name, phone_number, email, sign_up_date, points=0):
        super().__init__(customer_id, name, phone_number, email, points)


class PlatinumMember(Member):
    DiscountRate = 0.10

    def __init__(self, customer_id, name, phone_number, email, sign_up_date, points=0):
        super().__init__(customer_id, name, phone_number, email, points)


# Employee Related Class


class TimeSchedule:
    def __init__(self):
        # ["2023-10-27 10:00", "2023-10-27 11:00"]
        self.__busy_slots = []

    def search_availability(self, time: str):
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


class Employee:
    Type = None

    def __init__(self, emp_id, name):
        self.__employee_id = emp_id
        self.__name = name
        self.__workschedule = TimeSchedule()

    @property
    def name(self):
        return self.__name

    @property
    def emp_id(self):
        return self.__employee_id

    def get_avaliable_work(self, time: str):
        return self.__workschedule.search_availability(time)
        pass

    def update_timeslot(self, time: str):
        return self.__workschedule.update_schedule(time)


# class Worker(Employee):
#     Type = "Worker"

#     def __init__(self, emp_id, name, skill="General"):
#         super().__init__(emp_id, name)
#         self.__skill = skill


class Doctor(Employee):
    Type = "Doctor"

    def __init__(self, emp_id, name):
        super().__init__(emp_id, name)
        self.__medical_service = []

    def check_should_admit(self, pet):
        status = pet.get_last_medical_service()
        return status

    def start_medical_service(self, data: TreatmentRequest, clinic_obj):
        customer = clinic_obj.get_customer_info(data.owner_id)
        if customer == None:
            return f"User is not found"

        pet = clinic_obj.get_pet_info(data.petID)
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
            unpaid_service.append_sub_service(medical_service)

        else:
            new_big_service = Service(
                pet.id, customer.name, datetime.now())  # สร้างกล่องใหญ่
            new_big_service.append_sub_service(
                medical_service)  # เพิ่ม sub service ลง

            pet.append_big_service(new_big_service)

        return medical_service

    def start_pet_admit(self, pet_obj, clinic_obj, type, time):
        should_admit = self.check_should_admit(pet_obj)
        if should_admit == True:
            result = clinic_obj.pet_admit(type, time, pet_obj)

            if result == "Admit is complete":
                return {
                    "status": "Admit is complete",
                    "message": "Successfully admitted",
                }
            else:  # no room
                return {
                    "status": "Admit is failed",
                    "message": "No available rooms at the selected time",
                }
        else:
            return {
                "status": "Admit is failed",
                "message": "Admission rejected",
            }

# Room


class Room:
    price_per_day = 0

    def __init__(self, room_id, room_type):
        self.__room_id = room_id
        self.__room_type = room_type
        self.__busy_slot = []

    def get_details(self):
        return f"ID: {self.__room_id}, Type: {self.__room_type}"

    @property
    def get_price(self):
        return self.price_per_day

    @property
    def busy_slot(self):
        return self.__busy_slot

    @property
    def room_type(self):
        return self.__room_type

    def check_availability(self, time: str):
        if time not in self.__busy_slot:
            return True
        return False

    def book_room(self, time: str):
        if self.check_availability(time):
            self.__busy_slot.append(time)
            return True
        return False


class PrivateRoom(Room):
    price_per_day = 1500

    def __init__(self, room_id):
        super().__init__(room_id, "privateroom")


class ShareRoom(Room):
    price_per_day = 500

    def __init__(self, room_id):
        super().__init__(room_id, "shareroom")


# Clinic Controller Class
class Clinic:
    def __init__(self):
        self.__customer = []
        self.__stocks = []
        self.__employee = []
        self.__rooms = []
        self.__customer_payment = []
        self.__reservation = []
        self.__grooming_history = []
        self.__medical_record = []
        self.__pet = []
        self.__medical_service = []
        self.__notification = Notification()
        self._setup_dummy_data()

    def _setup_dummy_data(self):
        self.__employee.append(Doctor("D01", "Dr.Strange"))
        self.__rooms.append(PrivateRoom("R01"))
        self.__rooms.append(ShareRoom("R02"))
        payment = None
        c1 = Customer("C01", "Pingtale", "0999999999", "pingtale@email.com")
        p1 = Pet("P01", "Niggy", "Dog", "Golden", 25, "C01")
        c1.add_pet(p1)
        c1.add_card("1234-5678")
        self.__customer.append(c1)
        self.__pet = [p1]

        # เพิ่มประวัติการรักษา
        medical_record = MedicalService(
            record_id="1234",
            type_service="Medical",
            owner_obj=c1,
            doctor_obj=Doctor("D01", "Dr.Strange"),
            pet_obj=p1,
            symptom=["เมาแฟบ", "เบื่อแล้วชีวิตนี้"],
            良药苦口=["ยาม้า"],
            vaccine=[],
            price=1000000.0,
            should_admit=True
        )

        p1.add_medical_record(medical_record)

        # # test api medical treatment (medical treatment ตอน get all)
        # self.__medical_service.append(medical_record)

        # สร้างกล่อง Service test api (admit)
        dummy_big_service = Service(
            p1.id, c1.name, datetime.now())
        dummy_big_service.append_sub_service(medical_record)
        p1.append_big_service(dummy_big_service)

    def get_pet_info(self, petID):
        for i in self.__pet:
            if i.id == petID:
                return i
        return None

    def get_customer_info(self, customer_id):
        for i in self.__customer:
            if i.id == customer_id:
                return i
        return None

    def get_doctor_info(self, doctor_id):
        for d in self.__employee:
            if d.emp_id == doctor_id:
                return d
        return None

    def create_reservation(
        self,
        customer_id,
        pet_id,
        service_type,
        time,
        payment_method=None,
        room_type=None,
    ):
        resource = None
        price = 0
        customer = self.get_customer_info(customer_id)
        pet = self.get_pet_info(pet_id)
        payment_obj = None

        if service_type == "Grooming":
            resource = "Grooming"

        elif service_type == "Hotel":
            if not payment_method:
                return {
                    "status": "fail",
                    "message": "Hotel reservation requires a payment method (e.g., 'card' or 'qrcode')",
                }

            if not room_type:
                return {
                    "status": "fail",
                    "massage": "Hotel Required Room type PrivateRoom or ShareRoom",
                }
            if payment_method.lower() == "card":
                payment_obj = Card()
            elif payment_method.lower() == "qrcode":
                payment_obj = QRCode()
            else:
                return {"status": "fail", "message": "Invalid payment method"}

            for room in self.__rooms:
                if not room.is_full and room_type.lower() == room.room_type:
                    if room.book_room():
                        resource = room
                        price = room.get_price
                        if isinstance(payment_obj, Card):
                            if customer.card:
                                card_to_use = customer.card[0]
                            else:
                                return None
                            pay_result = payment_obj.pay(
                                price, payment_method, customer, card_to_use
                            )

                        elif isinstance(payment_obj, QRCode):
                            pay_result = payment_obj.pay(price, payment_method)

                        if pay_result != "Success":
                            room._is_full = False
                            resource = None
                            return {
                                "status": "fail",
                                "message": "Payment failed. Room reservation cancelled.",
                            }
                        break

        elif service_type == "Medical":
            for emp in self.__employee:
                if emp.Type == "Doctor" and emp.get_avaliable_work(time):
                    if emp.update_timeslot(time):
                        resource = emp
                        break

        if resource:
            reservation_id = str(uuid.uuid1())[:8]
            if service_type == "Grooming":
                new_reservation = GroomingReservation(
                    reservation_id, customer, pet, time
                )

            elif service_type == "Hotel":
                new_reservation = HotelReservation(
                    reservation_id,
                    customer,
                    pet,
                    time,
                    resource,
                    payment_method,
                )

            elif service_type == "Medical":
                new_reservation = MedicalReservation(
                    reservation_id, customer, pet, time, resource
                )

            self.__reservation.append(new_reservation)
            customer.add_reservation(new_reservation)

            if customer.email:
                self.__notification.send_confirmation("EMAIL", reservation_id)
            else:
                self.__notification.send_confirmation("SMS", reservation_id)

            if service_type == "Hotel":
                return {
                    "status": "success",
                    "customer_name": customer.name,
                    "detail": new_reservation.get_details(),
                    "time": time,
                    "payment": "PAID",
                }

            else:
                return {
                    "status": "success",
                    "customer_name": customer.name,
                    "detail": new_reservation.get_details(),
                    "time": time,
                    "payment": "Pay Later",
                }
        else:
            return {
                "status": "fail",
                "message": f"No available resource for {service_type} at {time}",
            }

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

    def pet_admit(self, type, time, pet_obj):
        unpaid_service = pet_obj.search_unpaid_service()

        # เช็คว่า medical treatment มารึยัง
        if unpaid_service == None:
            return "Medical record is not found"

        for room in self.__rooms:
            if room.book_room(time):
                price = room.get_price
                hotel_service = HotelService.create_hotel_service(
                    type, room, time, price)

                unpaid_service.append_sub_service(hotel_service)
                return "Admit is complete"

        return "No room available"


# fast api


clinic_sys = Clinic()


@app.get("/", tags=['root'])
async def root() -> dict:
    return {"Pet Shop": "Online"}


@app.post("/Reservation", tags=["Reservation"])
async def make_reservation(req: ReservationRequest):
    result = clinic_sys.create_reservation(
        req.customer_id,
        req.pet_id,
        req.service_type,
        req.datetime_str,
        req.payment_method,
        req.room_type,
    )
    return result


@app.post("/medical_treatment", tags=["Medical Treatment"])
async def add_medical_treatment(data: TreatmentRequest):
    doctor_obj = clinic_sys.get_doctor_info(data.doctor_id)
    if not doctor_obj:
        return "Doctor is not found"

    medical_treatment = clinic_sys.medical_treatment(data, doctor_obj)

    if medical_treatment["Status"] == "Success":
        return {
            "Message": "A medical treatment record has been added successfully!",
            "Data": medical_treatment["Data"]
        }
    else:
        return {
            "Message": medical_treatment["Message"]
        }


@app.get("/medical_treatment", tags=["Medical Treatment"])
async def get_medical_treatments():
    return {
        "Data": clinic_sys.get_all_medical_record()
    }


@app.post("/admit", tags=["Admit"])
async def add_admit(data: AdmitRequest):
    doctor_obj = clinic_sys.get_doctor_info(data.doctor_id)
    pet_obj = clinic_sys.get_pet_info(data.pet_id)

    if doctor_obj == None:
        return "Doctor is not found"
    if pet_obj == None:
        return "Pet is not found"

    result = doctor_obj.start_pet_admit(
        pet_obj, clinic_sys, data.type_service, data.time)
    return result

# def main():
#     print("Hello from oop-project-basecode!")


# if __name__ == "__main__":
#     main()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1",
                port=8000, log_level="info", reload=True)
