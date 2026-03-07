from typing import Union, Optional
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import math


app = FastAPI()

# Base Model


class AdmitRequest(BaseModel):
    doctor_id: str
    petID: str
    type_service: str = "Hotel"


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
    datetime_start_str: str
    datetime_end_str: Optional[str] = None
    room_type: Optional[str] = None
    payment_method: Optional[str] = None
    card_id: Optional[str] = None


class PaymentRequest(BaseModel):
    payment_type: str
    card_ID: str | None = None
    use_cp: bool = False
    money: float | None = None


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
    def __init__(self, reservation_id, customer, pet, time_start, time_end, room, total_price, payment):
        super().__init__(reservation_id, customer, pet, time_start)
        self.room = room
        self.price = total_price
        self.payment = payment

    @property
    def get_hotel_reservation_price(self):
        return self.price

    def get_details(self):
        return f"[Hotel Reservation] in {self.room.get_details()} for {self.pet.name} (Price: {self.price})"


# Payment Class


class PaymentMethod(ABC):
    @abstractmethod
    def validate_money(self, total_price, money=None):
        pass


class Card(PaymentMethod):
    # Fee = 0.01

    def __init__(self, card_id):
        self.__card_id = card_id
        self.__payment_type = "card"
        self.__total_money = 0

    def validate_money(self, total_price, money=None):
        if self.__total_money >= total_price:
            return "enough"
        else:
            return "not enough"

    @property
    def total_card_money(self):
        return self.__total_money

    @total_card_money.setter
    def total_card_money(self, money):
        self.__total_money = money

    @property
    def get_payment_type(self):
        return self.__payment_type

    @property
    def get_id(self):
        return self.__card_id

    def deposit(self, money):
        self.__total_money += money


class QRCode(PaymentMethod):
    def __init__(self, id):
        self.__payment_type = "qrcode"
        self.__total_money = 0
        self.__qrcodeID = id

    def validate_money(self, total_price, money):
        if money == total_price:
            return True
        else:
            return False

    @property
    def get_payment_type(self):
        return self.__payment_type


class Payment:
    def __init__(self, customer_id, payment_ID, method, price, service_list, date, point):
        self.__customer_id = customer_id
        self.__payment_type = method.get_payment_type
        self.__price = price
        self.__service_list = service_list
        self.__date = date
        self.__payment_id = payment_ID
        self.__point = point
        self.__payment_method = []

    def create_payment_slip(self):
        return f"CustomerID:{self.__customer_id}-PaymentID:{self.__payment_id}-Type:{self.__payment_type}-Price:{self.__price}-Pet_Service:{self.__service_list}-Date:{self.__date}-Point:{self.__point}"


# Customer Related Class
# Service CLass
class Service:
    def __init__(self, pet_id, owner_id, date):
        self.__pet_name = pet_id
        self.__owner = owner_id
        self.__date = date
        self.__sub_service = []
        self.__price = 0
        self.__is_paid = False

    @property
    def price(self):
        return self.__price

    @property
    def get_date(self):
        return self.__date

    @property
    def is_paid(self):
        return self.__is_paid

    def append_sub_service(self, sub_service):
        self.__sub_service.append(sub_service)

    def calculate_total_price(self):
        total = 0
        for service in self.__sub_service:
            if isinstance(service, HotelService):
                service.calculate_hotel_service_price()
                
                if service.is_from_reservation:
                    continue
                
            total += service.price
        self.__price = total
        return self.__price

    def get_service_list(self):
        service_list = []
        for service in self.__sub_service:
            type = service.type
            service_list.append(type)
        return service_list

    def check_has_medical_service(self):
        for service in self.__sub_service:
            if isinstance(service, MedicalService):
                return True
        return False

# ขอเพิ่ม Service คร่าวๆ ไว้ใช้ตอน Payment


class GroomingService:
    def __init__(self, price):
        self.__type_service = "grooming"
        self.__price = price

    @property
    def price(self):
        return self.__price

    @property
    def type(self):
        return self.__type_service


class HotelService:
    def __init__(self, room, entry_date, exit_date, price, from_reservation = False):
        self.__type_service = "hotel"
        self.__room = room
        self.__entry_date = entry_date
        self.__exit_date = exit_date
        self.__price = 0
        self.__from_reservation = from_reservation
        self.calculate_hotel_service_price()

    @property
    def price(self):
        return self.__price

    @property
    def is_from_reservation(self):
        return self.__from_reservation
    
    @property
    def type(self):
        return self.__type_service

    def calculate_hotel_service_price(self):
        diff = self.__exit_date.date() - self.__entry_date.date()
        price = self.__room.get_price * diff.days
        self.__price = price


class MedicalService:
    def __init__(
        self,
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

    @property
    def should_admit(self):
        return self.__should_admit

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
        self.__medical_record = []
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

    def search_unpaid_service(self):
        for service in self.__service:
            if service.is_paid == False:
                return service
        return None

    def append_big_service(self, service):
        self.__service.append(service)

    # สร้างเผื่อว่าอนาคตอยากค้นหาประวัติการรักษาเฉพาะอันไหนขึ้นมา
    def search_medical_record(self, record_id):
        for record in self.__medical_record:
            if str(record.change_dict()["Id"]) == str(record_id):
                return record
        return None

    def get_last_medical_service_should_admit(self):
        if not self.__medical_record:
            return False
        status = self.__medical_record[-1].should_admit
        return status

    def add_medical_record(self, medical_record):
        self.__medical_record.append(medical_record)



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

    def add_card(self, card: Card):
        self.__card.append(card)

    def search_card(self, card_id):
        for card in self.__card:
            if card.get_id == card_id:
                return card
        return None

    def deposit_to_card(self, cardID, money):
        card = self.search_card(cardID)
        card.deposit(money)

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

    def __init__(self, customer_id, name, phone_number, email, sign_up_date, tier, rate, point=0):
        super().__init__(customer_id, name, phone_number, email)
        self.__signnp_date = sign_up_date
        self.__point = point
        self.__coupon = []
        self.__tier = tier
        self.__rate = rate

    @property
    def point(self):
        return self.__point

    @property
    def get_tier(self):
        return self.__tier

    @property
    def get_rate(self):
        return self.__rate

    def add_point(self, point):
        self.__point += point

    def remove_point(self, point):
        self.__point -= point

    def add_coupon(self, coupon):
        self.__coupon.append(coupon)

    def get_coupon(self):
        if self.__coupon:
            return self.__coupon[0]
        else:
            return None

    def delete_coupon(self):
        self.__coupon.pop(0)


class SilverMember(Member):
    DiscountRate = 0.01

    def __init__(self, customer_id, name, phone_number, email, sign_up_date, point=0):
        super().__init__(customer_id, name, phone_number, email,
                         sign_up_date, "silver", self.DiscountRate, point)


class GoldMember(Member):
    DiscountRate = 0.05

    def __init__(self, customer_id, name, phone_number, email, sign_up_date, point=0):
        super().__init__(customer_id, name, phone_number, email,
                         sign_up_date, "gold", self.DiscountRate, point)


class PlatinumMember(Member):
    DiscountRate = 0.1

    def __init__(self, customer_id, name, phone_number, email, sign_up_date, point=0):
        super().__init__(customer_id, name, phone_number, email,
                         sign_up_date, "platinum", self.DiscountRate, point)


class Coupon():
    def __init__(self, id):
        self.__coupon_id = id
        self.__discount = 10

    @property
    def use_coupon(self):
        return self.__discount

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
        status = pet.get_last_medical_service_should_admit()
        return status

    def create_medical_service(self, data: TreatmentRequest, clinic_obj):

        customer = clinic_obj.get_customer_info(data.owner_id)
        pet = clinic_obj.get_pet_info(data.petID)

        record_id = clinic_obj.generate_ID()

        symptom = data.symptom
        medicine = data.medicine
        vaccine = data.vaccine
        price = data.price
        should_admit = data.should_admit

        medical_service = MedicalService(
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

        self.__medical_service.append(medical_service)

        return medical_service


# Room


class Room:
    price_per_day = 0

    def __init__(self, room_id, room_type, capacity=1):
        self.__room_id = room_id
        self.__room_type = room_type
        self.__capacity = capacity
        self.__busy_slot = []  # [(start_dt,end_dt)]

    def get_details(self):
        return f"ID: {self.__room_id}, Type: {self.__room_type}"

    @property
    def room_id(self):
        return self.__room_id

    @property
    def get_price(self):
        return self.price_per_day

    @property
    def busy_slot(self):
        return self.__busy_slot

    @property
    def room_type(self):
        return self.__room_type

    def check_availability(self, time_start: datetime, time_end: datetime):
        overlap_count = 0
        # check Overlap
        for busy_start, busy_end in self.__busy_slot:
            if time_start < busy_end and time_end > busy_start:
                overlap_count += 1

        if overlap_count < self.__capacity:
            return True
        return False

    def book_room(self, time_start: datetime, time_end: datetime):
        if self.check_availability(time_start, time_end):
            self.__busy_slot.append((time_start, time_end))
            return True
        return False


class PrivateRoom(Room):
    price_per_day = 1500

    def __init__(self, room_id):
        super().__init__(room_id, "privateroom", capacity=1)


class ShareRoom(Room):
    price_per_day = 500

    def __init__(self, room_id):
        super().__init__(room_id, "shareroom", capacity=10)


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
        c1.add_card(Card("1234-5678"))
        c1.deposit_to_card("1234-5678", 50000)
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
            medicine=["ยาม้า"],
            vaccine=[],
            price=1000000.0,
            should_admit=True
        )

        p1.add_medical_record(medical_record)

        # # test api medical treatment (medical treatment ตอน get all)
        self.__medical_service.append(medical_record)

        # สร้างกล่อง Service test api (admit)
        dummy_big_service = Service(
            p1.id, c1.name, datetime.now())
        dummy_big_service.append_sub_service(medical_record)
        p1.append_big_service(dummy_big_service)

        # ส่วนของ payment

        Bam = Customer("123445", "bam", "025687525", "Bam@gmail.com")
        Peem = GoldMember("123456", "peem", "0225556666",
                          "Peem@gmail.com", datetime(2025, 11, 11))

        Bam_Card = Card("Card123")
        Peem_Card = Card("Card555")

        Bam.add_card(Bam_Card)
        Bam.deposit_to_card("Card123", 50000)
        Peem.add_card(Peem_Card)
        Peem.deposit_to_card("Card555", 50000)

        self.add_customer(Bam)
        self.add_customer(Peem)

        Golden = Pet("P02", "golden", "Dog", "Golden", 25, "123445")
        Corgi = Pet("P03", "corgi",  "Dog", "Corgi",  12, "123456")
        Husky = Pet("P04", "husky",  "Dog", "Husky",  20, "123456")

        self.add_pet(Golden)
        self.add_pet(Corgi)
        self.add_pet(Husky)

        Bam.add_pet(Golden)
        Peem.add_pet(Corgi)
        Peem.add_pet(Husky)

        today = datetime.now()

        self.record_service("P02", "123445", "grooming", 2000, today)
        self.record_service("P02", "123445", "hotel", 5000,
                            today, today + timedelta(days=3), "R01")

        self.record_service("P04", "123456", "grooming", 2000, today)
        self.record_service("P03", "123456", "grooming", 2000, today)
        self.record_service("P04", "123456", "hotel", 5000,
                            today, today + timedelta(days=3), "R01")

        self.add_point(Peem, 50000)
        self.point_to_coupon("123456")
        self.point_to_coupon("123456")
        self.point_to_coupon("123456")
        self.point_to_coupon("123456")
        self.point_to_coupon("123456")

    # make service ในส่วน Grooming หรือ Boarding
    def record_service(self, pet_id, customer_id, type, price, entry_date, exit_date=None, room_id=None):
        pet = self.get_pet_info(pet_id)
        if pet == None:
            return "Not found"
        else:
            big_service = pet.search_unpaid_service()
            should_create_big_service = False
            if big_service == None:
                should_create_big_service = True
                big_service = Service(pet_id, customer_id, entry_date)

            if type == "grooming":
                grooming = GroomingService(price)
                big_service.append_sub_service(grooming)

            elif type == "hotel":
                room = None
                for r in self.__rooms:
                    if r.room_id == room_id:
                        room = r

                if room != None:
                    hotel = HotelService(room, entry_date, exit_date, price)
                    big_service.append_sub_service(hotel)

        if (should_create_big_service):
            pet.append_big_service(big_service)

    def add_pet(self, pet):
        self.__pet.append(pet)

    def add_customer(self, customer):
        self.__customer.append(customer)

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

    def check_member(self, customer):
        if isinstance(customer, Member):
            return True
        else:
            return False

    def get_payment_method_object(self, customer, payment_type, card_ID=None):
        payment_type = payment_type.lower()
        if payment_type == "qrcode":
            id = self.generate_ID()
            method = QRCode(id)
        elif payment_type == "card":
            method = customer.search_card(card_ID)
        return method

    def generate_ID(self):
        ID = uuid.uuid4().hex[:8]
        return ID

    def sum_price_in_each_service(self, service_list):
        sum_price = 0
        for service in service_list:
            service.calculate_total_price()
            price = service.price
            sum_price += price
        return sum_price

    def calculate_discount(self, customer, price):
        rate = customer.get_rate
        discount = rate * price
        return discount

    def calculate_point(self, price):
        rate = 0.01
        point = rate * price
        point_int = math.floor(point)
        return point_int

    def add_point(self, customer, price):
        if self.check_member(customer):
            point = self.calculate_point(price)
            customer.add_point(point)
            return point
        else:
            return 0

    def create_coupon(self):
        id = self.generate_ID()
        coupon = Coupon(id)
        return coupon

    def show_all_point_in_member(self, customer_id):
        customer = self.get_customer_info(customer_id)
        if customer != None:
            if self.check_member(customer):
                return customer.point
            else:
                return "Not Member"
        else:
            return "Not found customer"

    def point_to_coupon(self, customer_id):
        customer = self.get_customer_info(customer_id)
        if customer != None:
            if self.check_member(customer):
                point = customer.point
                if point >= 50:
                    coupon = self.create_coupon()
                    customer.add_coupon(coupon)
                    customer.remove_point(50)
                    return "Success"
                else:
                    return "Not enough point"
            else:
                return "Not Member"
        else:
            return "Not found customer"

    def get_coupon(self, customer):
        coupon = customer.get_coupon()
        if coupon != None:
            discount = coupon.use_coupon
            customer.delete_coupon()
            return discount
        else:
            return "Not Have Coupon"

    def calculate_total_price(self, customer, sum_price, use_cp):
        member = self.check_member(customer)
        discount = 0
        if member == False:
            if use_cp == True:
                return "Not a member"
        elif member == True:
            discount += self.calculate_discount(customer, sum_price)
            if use_cp:
                coupon_discount = self.get_coupon(customer)
                if coupon_discount == "Not Have Coupon":
                    return "Not Have Coupon"
                discount += coupon_discount
        total_price = sum_price - discount
        return total_price

    def pay(self, total_price, method, money=None):
        if method.get_payment_type == "qrcode":
            result = method.validate_money(total_price, money)
            if result == False:
                return "Invalid money"
        if method.get_payment_type == "card":
            result = method.validate_money(total_price)
            if result == "not enough":
                return "Card not have enough money"
            money = method.total_card_money
            method.total_card_money = money - 50
        return "Success"

    def create_service_and_pet_list(self, pet_list, service_list):
        list_pet_and_service = []
        for pet in pet_list:
            service = pet.search_unpaid_service()
            if service != None:
                service_list = service.get_service_list()
                list_pet_and_service.append([pet.name, service_list])
        return list_pet_and_service

    def create_payment(self, customer_id, method, price, list_pet_and_service, today, point=0):
        payment_ID = self.generate_ID()
        payment = Payment(customer_id, payment_ID, method,
                          price, list_pet_and_service, today, point)
        return payment

    def start_payment(self, customer_id, payment_type, card_ID=None, use_cp=False, money=None):
        customer = self.get_customer_info(customer_id)

        if (customer == None):
            return "Customer not found"

        pet_list = customer.pet

        service_list = []
        for pet in pet_list:
            service = pet.search_unpaid_service()
            if service is not None:
                service_list.append(service)
        sum_price = self.sum_price_in_each_service(service_list)

        total_price = self.calculate_total_price(customer, sum_price, use_cp)
        if total_price == "Not Have Coupon":
            return "Not Have Coupon"
        elif total_price == "Not a member":
            return "Not a member"

        method = self.get_payment_method_object(
            customer, payment_type, card_ID)
        if method == None:
            return "Invalid CardID"

        result = self.pay(total_price, method, money)
        if result == "Invalid money":
            return "Invalid money"
        elif result == "Card not have enough money":
            return "Card not have enough money"

        point = self.add_point(customer, total_price)
        list_pet_and_service = self.create_service_and_pet_list(
            pet_list, service_list)
        today = datetime.today()
        payment = self.create_payment(
            customer_id, method, total_price, list_pet_and_service, today, point)
        customer.add_payment(payment)
        payment_slip = payment.create_payment_slip()
        return payment_slip

    # เปลี่ยน str ให้กลายเป็น time object
    # หากไม่ได้ใส่ time_end มาให้
    def convert_str_to_time(self, time_start: str, time_end: str):
        time_format = "%Y-%m-%d %H:%M"
        start_dt = datetime.strptime(time_start, time_format)

        if time_end:
            end_dt = datetime.strptime(time_end, time_format)
        else:
            end_dt = start_dt + timedelta(hours=1)

        return start_dt, end_dt

    def create_reservation(
        self,
        customer_id,
        pet_id,
        service_type,
        time_start,
        time_end=None,
        room_type=None,
        payment_method=None,
        card_id=None,
    ):
        resource = None
        price = 0
        customer = self.get_customer_info(customer_id)
        pet = self.get_pet_info(pet_id)
        payment_obj = None

        start_dt, end_dt = self.convert_str_to_time(time_start, time_end)

        if service_type == "Grooming":
            resource = "Grooming"

        elif service_type == "Hotel":
            if not payment_method:
                return {
                    "status": "fail",
                    "message": "Hotel reservation requires a payment method (e.g., 'card' or 'qrcode')",
                }

            if not time_end:
                return {
                    "status": "fail",
                    "message": "Hotel reservation requires a checkout time",
                }

            if not room_type:
                return {
                    "status": "fail",
                    "massage": "Hotel Required Room type PrivateRoom or ShareRoom",
                }

            if payment_method.lower() == "card":
                if not customer.card:
                    return {"status": "fail", "message": "Customer has no card."}
                if card_id == None:
                    return {"status": "fail", "message": "Require CardID."}
            elif payment_method.lower() == "qrcode":
                pass
            else:
                return {"status": "fail", "message": "Invalid payment method"}

            original_time_duration = end_dt - start_dt
            staying_time = max(1, original_time_duration.days)

            for room in self.__rooms:
                if room_type.lower() == room.room_type and room.book_room(start_dt, end_dt):
                    resource = room
                    price = room.get_price * staying_time

                    # print(f"days {original_time_duration.days}")
                    # print(f"staying time {staying_time}")
                    # print(f"price {price}")

                    payment_obj = self.get_payment_method_object(
                        customer, payment_method, card_id)

                    if payment_obj == None:
                        room.busy_slot.remove(time_start, time_end)
                        resource = None
                        return {
                            "status": "fail",
                            "message": "CardID Not Found.",
                        }

                    pay_result = self.pay(price, payment_obj, price)

                    if pay_result != "Success":
                        room.busy_slot.remove((start_dt, end_dt))
                        resource = None
                        return {
                            "status": "fail",
                            "message": "Payment failed. Room reservation cancelled.",
                        }

                    # Payment Record
                    today = datetime.today()
                    payment_ID = self.generate_ID()
                    point = self.add_point(customer, price)
                    payment_record = Payment(
                        customer_id=customer.id,
                        payment_ID=payment_ID,
                        method=payment_obj,
                        price=price,
                        service_list=[
                            f"Pre-paid Hotel ({room.get_details()})"],
                        date=today,
                        point=point
                    )
                    customer.add_payment(payment_record)
                    big_service = Service(pet_id,customer_id,start_dt)
                    hotel_service_with_reservation = HotelService(resource,start_dt,end_dt,price,True)
                    big_service.append_sub_service(hotel_service_with_reservation)
                    pet.append_big_service(big_service)
                    break

        elif service_type == "Medical":
            for emp in self.__employee:
                if emp.Type == "Doctor" and emp.get_avaliable_work(time_start):
                    if emp.update_timeslot(time_start):
                        resource = emp
                        break

        if resource:
            reservation_id = str(uuid.uuid1())[:8]
            if service_type == "Grooming":
                new_reservation = GroomingReservation(
                    reservation_id, customer, pet, start_dt
                )

            elif service_type == "Hotel":
                new_reservation = HotelReservation(
                    reservation_id,
                    customer,
                    pet,
                    start_dt.date(),
                    end_dt.date(),
                    resource,
                    price,
                    payment_method,
                )

                # pet.add_boarding_service(resource)

            elif service_type == "Medical":
                new_reservation = MedicalReservation(
                    reservation_id, customer, pet, start_dt, resource
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
                    "date_start": start_dt.date(),
                    "Check_Out_Date": end_dt.date(),
                    "payment": "PAID",
                }

            else:
                return {
                    "status": "success",
                    "customer_name": customer.name,
                    "detail": new_reservation.get_details(),
                    "time": start_dt,
                    "payment": "Pay Later",
                }
        else:
            return {
                "status": "fail",
                "message": f"No available resource for {service_type} at {start_dt}",
            }

    def medical_treatment(self, data: TreatmentRequest):
        doctor = self.get_doctor_info(data.doctor_id)
        customer = self.get_customer_info(data.owner_id)
        pet = self.get_pet_info(data.petID)

        if doctor == None:
            return {"Status": "Error", "Message": "Doctor is not found"}
        if customer == None:
            return {"Status": "Error", "Message": "Customer is not found"}
        if pet == None:
            return {"Status": "Error", "Message": "Pet is not found"}

        medical_service = doctor.create_medical_service(data, self)

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

        if medical_service.should_admit == True:
            admit_data = AdmitRequest(
                doctor_id=data.doctor_id,
                petID=data.petID,
                type_service="Hotel",
            )
            self.start_pet_admit(admit_data)

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

    def start_pet_admit(self, data: AdmitRequest):
        pet = self.get_pet_info(data.petID)
        if pet == None:
            return {"Status": "Error", "Message": "Pet is not found"}

        unpaid_service = pet.search_unpaid_service()
        has_medical_service = False

        if unpaid_service:
            # เช็คว่า service ล่าสุดเป็น medical มั้ย
            has_medical_service = unpaid_service.check_has_medical_service()

        if not has_medical_service:
            return {
                "status": "Admit is failed",
                "message": "No active medical service session found for this pet"
            }

        resource = None
        time_start = datetime.now()
        time_end = time_start + timedelta(days=1)
        staying_time = 1
        price = 0

        for room in self.__rooms:
            if room.room_type == "privateroom":
                if room.book_room(time_start, time_end):
                    resource = room
                    price = room.get_price * staying_time
                    break

        if resource:
            hotel_service = HotelService(resource, time_start, time_end, price)
            unpaid_service.append_sub_service(hotel_service)

            return {
                "status": "Admit is complete",
                "message": "Successfully admitted",
            }

        else:
            return {
                "status": "Admit is failed",
                "message": "No private room available at the selected time"
            }

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
        req.datetime_start_str,
        req.datetime_end_str,
        req.room_type,
        req.payment_method,
        req.card_id
    )
    return result


@app.post("/payment/{customer_id}", tags=["Payment"])
def payment(customer_id: str, req: PaymentRequest):
    result = clinic_sys.start_payment(
        customer_id,
        req.payment_type,
        req.card_ID,
        req.use_cp,
        req.money
    )
    return (result)


@app.post("/medical_treatment", tags=["Medical Treatment"])
async def add_medical_treatment(data: TreatmentRequest):

    medical_treatment = clinic_sys.medical_treatment(data)

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
    admit = clinic_sys.start_pet_admit(data)
    return admit


@app.get("/exchange_coupon", tags=["exchange coupon"])
def show_all_point_in_account(customer_id: str):
    result = clinic_sys.show_all_point_in_member(customer_id)
    return result


@app.post("/exchange_coupon", tags=["exchange coupon"])
def exchage_coupon(customer_id: str):
    result = clinic_sys.point_to_coupon(customer_id)
    return result

# def main():
#     print("Hello from oop-project-basecode!")


# if __name__ == "__main__":
#     main()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1",
                port=8000, log_level="info", reload=True)

# fastapi dev main.py

# จอง Hotel (จ่ายผ่าน QRCode)
# {
#   "customer_id": "C01",
#   "pet_id": "P01",
#   "service_type": "Hotel",
#   "datetime_str": "2023-10-27 10:00",
#   "room_type": "PrivateRoom",
#   "payment_method": "qrcode",
#   "card_id": ""
# }
# จอง Medical / Grooming (ไม่มี payment_method)
# {
#   "customer_id": "C01",
#   "pet_id": "P01",
#   "service_type": "Medical",
#   "datetime_str": "2023-10-27 10:00"
# }
