import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import math
from base_model_class import *


class Notification:
    def send_confirmation(self, method: str, reservation_id: str):
        print(f"[{method}] Sent confirmation for Reservation ID: {reservation_id}")
        return True


# Reservation Class


class Reservation(ABC):
    def __init__(self, reservation_id, customer, pet, time):
        self.reservation_id = reservation_id
        self.customer = customer
        self.pet = pet
        self.time = time
        self.status = "confirmed"
        
    @abstractmethod
    def get_details(self):
        pass
    
    @property
    def id(self):
        return self.reservation_id


class GroomingReservation(Reservation):
    def __init__(self, reservation_id, customer, pet, time):
        super().__init__(reservation_id, customer, pet, time)

    def get_details(self):
        return f"[Grooming Reservation] for {self.pet.name}"


class MedicalReservation(Reservation):
    def __init__(self, reservation_id, customer, pet, time_start, time_end, doctor):
        super().__init__(reservation_id, customer, pet, time_start)
        self.time_end = time_end
        self.__doctor = doctor 

    @property
    def doctor(self):
        return self.__doctor
        
    @property
    def get_time_start_and_end(self):
        return self.time, self.time_end
        
    def get_details(self):
        return f"[Medical Appointment] with Dr.{self.__doctor.name} for {self.pet.name}"


class HotelReservation(Reservation):
    def __init__(self, reservation_id, customer, pet, time_start, time_end, room, total_price, payment):
        super().__init__(reservation_id, customer, pet, time_start)
        self.time_end = time_end
        self.room = room
        self.price = total_price
        self.payment = payment

    @property
    def get_hotel_reservation_price(self):
        return self.price
    
    @property
    def get_time_start_and_end(self):
        return self.time , self.time_end

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
    def __init__(self, customer_id, payment_ID, method, price, pet_service_list, date, point):
        self.__customer_id = customer_id
        self.__payment_id = payment_ID
        self.__payment_type = method.get_payment_type
        self.__price = price
        self.__pet_service_list = pet_service_list
        self.__date = date
        self.__point = point
        # self.__payment_method = []

    def create_payment_slip(self):
        return f"CustomerID:{self.__customer_id}-PaymentID:{self.__payment_id}-Type:{self.__payment_type}-Price:{self.__price}-Pet_Service:{self.__pet_service_list}-Date:{self.__date}-Point:{self.__point}"


# Customer Related Class
# Service CLass
class RecordService:
    def __init__(self, date):
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
    
    @property
    def sub_service(self):
        return self.__sub_service
    
    @is_paid.setter
    def is_paid (self,paid = True) :
        self.__is_paid = paid

    def append_sub_service(self, sub_service):
        self.__sub_service.append(sub_service)

    def calculate_total_price(self):
        total = 0
        for service in self.__sub_service:
            if isinstance(service, HotelService):
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
    
    def check_has_grooming_service(self) :
        for service in self.__sub_service:
            if isinstance(service, GroomingService):
                return True
        return False
    
    def check_has_hotel_admit_service(self) :
        for service in self.__sub_service:
            if isinstance(service, HotelService) and service.is_from_reservation == False:
                return True
        return False

# ขอเพิ่ม Service คร่าวๆ ไว้ใช้ตอน Payment

class Service :
    def __init__(self,type_service,price) :
        self.__type_service = type_service
        self.__price = price

    @property
    def price(self):
        return self.__price
    
    @property
    def type(self):
        return self.__type_service

class GroomingService(Service):
    BasePrice = 2000
    def __init__(self, pet):
        price = self.calculate_grooming_service_price(pet)
        super().__init__("Grooming",price)
    
    def calculate_grooming_service_price (self,pet) :
        price = self.BasePrice
        aggressive = pet.aggressive
        if aggressive :
            price += 500
        return price

class HotelService(Service):
    def __init__(self, room, entry_date, exit_date, price, from_reservation = False):
        super().__init__("Hotel",price)
        self.__room = room
        self.__entry_date = entry_date
        self.__exit_date = exit_date
        self.__from_reservation = from_reservation

    @property
    def is_from_reservation(self):
        return self.__from_reservation

class MedicalService(Service):
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
        super().__init__(type_service,price)
        self.__record_id = record_id
        self.__owner_obj = owner_obj
        self.__doctor_obj = doctor_obj
        self.__pet_obj = pet_obj
        self.__symptom = symptom
        self.__medicine = medicine
        self.__vaccine = vaccine
        self.__should_admit = should_admit

    @property
    def should_admit(self):
        return self.__should_admit
    
    def change_dict(self):
        return {
            "Id": self.__record_id,
            "Service": super().type,
            "Owner ID": self.__owner_obj.id,
            "Doctor": self.__doctor_obj.emp_id,
            "Pet": self.__pet_obj.id,
            "Symptom": self.__symptom,
            "Medicine": self.__medicine,
            "Vaccine": self.__vaccine,
            "Price": self.price,
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
    def service(self):
        return self.__service

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

    def add_pet(self, pet: Pet):
        self.__pet.append(pet)

    def add_reservation(self, reservation):
        self.__reservation.append(reservation)

    def add_payment(self, payment):
        self.__payment_list.append(payment)
        return "Success"

    def add_card(self, card: Card):
        self.__card.append(card)

    def get_pet_info(self, pet_id):
        for pet in self.__pet:
            if pet.id == pet_id:
                return pet
        return None

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
    
    @property
    def reservation(self):
        return self.__reservation


class Member(Customer):
    DiscountRate = 0

    def __init__(self, customer_id, name, phone_number, email, sign_up_date, tier, rate, point=0):
        super().__init__(customer_id, name, phone_number, email)
        self.__signup_date = sign_up_date
        self.__point = point
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

class SilverMember(Member):
    # DiscountRate = 0.01

    def __init__(self, customer_id, name, phone_number, email, sign_up_date, point=0):
        super().__init__(customer_id, name, phone_number, email, sign_up_date, "silver", 0.01, point)
        self.__discount_limit_per_year = 6
        self.__count_for_use_discount = 0

    def check_is_limit(self) :
        if self.__count_for_use_discount < self.__discount_limit_per_year :
            return False
        else :
            return True
        
    def add_count_for_use_discount (self) :
        if not self.check_is_limit():
            self.__count_for_use_discount += 1
        
class GoldMember(Member):
    # DiscountRate = 0.05

    def __init__(self, customer_id, name, phone_number, email, sign_up_date, point=0):
        super().__init__(customer_id, name, phone_number, email, sign_up_date, "gold", 0.05, point)
        self.__coupon = []

    def add_coupon(self,coupon) :
        self.__coupon.append(coupon)

    def get_coupon(self):
        if self.__coupon:
            return self.__coupon[0]
        else:
            return None

    def delete_coupon(self):
        try:
            self.__coupon.pop(0)
        except IndexError:
            return "No coupon"

class PlatinumMember(Member):
    # DiscountRate = 0.1

    def __init__(self, customer_id, name, phone_number, email, sign_up_date, point=0):
        super().__init__(customer_id, name, phone_number, email, sign_up_date, "platinum", 0.1, point)
        self.__coupon = []
        self.__rewards_card = None
        
    def add_coupon(self,coupon) :
        self.__coupon.append(coupon)

    def get_coupon(self) :
        if self.__coupon :
            return self.__coupon[0]
        else :
            return None
    
    def delete_coupon(self) :
        self.__coupon.pop(0)

    def add_rewards_card(self,rewards_card) :
        self.__rewards_card = rewards_card

    @property
    def get_rewards_card(self) :
        if self.__rewards_card is not None :
            return self.__rewards_card
        else :
            return "Not have rewards card"
    
    def use_rewards_card (self,pay = False) :
        if self.__rewards_card is not None :
            if self.__rewards_card.check_available() == True :
                if pay :
                    self.delete_reward_card()
                return True
        return False
    
    def delete_reward_card(self) :
        self.__rewards_card = None

    def add_count_to_rewards_card(self) :
        if self.__rewards_card == None :
            rewards_card = RewardsCard()
            self.add_rewards_card(rewards_card)
        else :
            self.__rewards_card.add_count()

class RewardsCard :
    def __init__(self):
        self.__count_for_use_service = 1

    def add_count(self) :
        if self.__count_for_use_service < 10 :
            self.__count_for_use_service += 1

    def check_available(self) :
        if self.__count_for_use_service == 10 :
            return True
        else :
            return False
        
    @property
    def count (self) :
        return self.__count_for_use_service

class Coupon :
    def __init__(self, id):
        self.__coupon_id = id
        self.__discount = 10

    @property
    def use_coupon(self):
        return self.__discount

# Employee Related Class


class TimeSchedule:
    def __init__(self, capacity=1):
        self.__busy_slots = [] # เก็บเป็น Tuple: [(start_dt, end_dt)]
        self.__capacity = capacity
        
        
    @property
    def busy_slot(self):
        return self.__busy_slots

    def check_availability(self, time_start: datetime, time_end: datetime) -> bool:
        overlap_count = 0
        for busy_start, busy_end in self.__busy_slots:
            # เช็คว่าเวลาทับซ้อนกันไหม
            if time_start < busy_end and time_end > busy_start:
                overlap_count += 1
                
        if overlap_count < self.__capacity:
            return True
        return False

    def add_schedule(self, time_start: datetime, time_end: datetime) -> bool:
        if self.check_availability(time_start, time_end):
            self.__busy_slots.append((time_start, time_end))
            return True
        return False
        
    def remove_schedule(self, time_start: datetime, time_end: datetime):
        try:
            self.__busy_slots.remove((time_start, time_end))
        except ValueError:
            pass


class Employee:
    Type = None

    def __init__(self, emp_id, name):
        self.__employee_id = emp_id
        self.__name = name
        self.__workschedule = TimeSchedule(capacity=1)

    @property
    def name(self):
        return self.__name

    @property
    def emp_id(self):
        return self.__employee_id

    def get_avaliable_work(self, time_start: datetime, time_end: datetime):
        return self.__workschedule.check_availability(time_start, time_end)

    def update_timeslot(self, time_start: datetime, time_end: datetime):
        return self.__workschedule.add_schedule(time_start, time_end)
        
    def free_timeslot(self, time_start: datetime, time_end: datetime):
        self.__workschedule.remove_schedule(time_start, time_end)


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
        
        if customer == None:
            return {"Status": "Error", "Message": "Customer is not found"}
        
        pet = customer.get_pet_info(data.petID)
        if pet == None :
            return {"Status": "Error", "Message": "Pet does not belong to owner"}

        record_id = clinic_obj.generate_ID()

        symptom = data.symptom
        medicine = data.medicine
        vaccine = data.vaccine
        price = data.price
        should_admit = data.should_admit

        medical_service = MedicalService(
            record_id,
            "Medical",
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


class Room(ABC):
    price_per_day = 0

    def __init__(self, room_id, room_type, capacity=1):
        self.__room_id = room_id
        self.__room_type = room_type
        self.__capacity = capacity
        self.__schedule = TimeSchedule(capacity=self.__capacity)

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
        return self.__schedule.busy_slot

    @property
    def room_type(self):
        return self.__room_type

    def check_availability(self, time_start: datetime, time_end: datetime):
        return self.__schedule.check_availability(time_start, time_end)

    def book_room(self, time_start: datetime, time_end: datetime):
        return self.__schedule.add_schedule(time_start, time_end)
        
    def cancel_room(self, time_start: datetime, time_end: datetime):
        self.__schedule.remove_schedule(time_start, time_end)


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
        self.__rooms.append(PrivateRoom("PR01"))
        self.__rooms.append(PrivateRoom("PR02"))
        self.__rooms.append(PrivateRoom("PR03"))
        self.__rooms.append(ShareRoom("SR01"))
        self.__rooms.append(ShareRoom("SR02"))
        
        # payment = None
        c1 = PlatinumMember("C01", "Pingtale", "0999999999", "pingtale@email.com", datetime.now().date())
        p1 = Pet("P01", "Niggy", "Dog", "Golden", 25, "C01")
        c1.add_pet(p1)
        c1.add_card(Card("1234-5678"))
        c1.deposit_to_card("1234-5678", 50000)
        self.add_customer(c1) 
        self.add_pet(p1)
        self.add_point(c1, 50000)
        for i in range(5) :
            self.point_to_coupon("C01")

        for i in range(9) :
            c1.add_count_to_rewards_card()

        c2 = SilverMember("C02", "Donoka", "0888888888", "donoka@gmail.com", datetime.now().date())
        p2 = Pet("P02", "Muffy", "Cat", "Siamese", 15, "C02")
        c2.add_pet(p2)
        c2.add_card(Card("1111-1111"))
        c2.deposit_to_card("1111-1111", 50000)
        self.add_customer(c2)
        self.add_pet(p2)
        for i in range(5) :
            c2.add_count_for_use_discount()

    # make service ในส่วน Grooming หรือ Boarding
    def record_service(self, customer_id ,pet_id):
        customer = self.get_customer_info(customer_id)
        pet = customer.get_pet_info(pet_id)
        if pet == None :
            return {"Status": "Error", "Message": "Pet does not belong to owner"}
        
        grooming = GroomingService(pet)
        big_service = pet.search_unpaid_service()
        
        if big_service == None:
            big_service = RecordService(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            pet.append_big_service(big_service)
        if big_service.check_has_grooming_service() :
            return {"Status": "Error", "Message": "Grooming service for today already create"}
        big_service.append_sub_service(grooming)
        
        return {
                    "status": "success",
                    "customer_id": customer_id,
                    "pet_id": pet.id,
                    "service": "grooming",
                }

    def register_card(self,customer_id,money) :
        customer = self.get_customer_info(customer_id)
        if customer == None :
            return {
                "Status": "fail",
                "Message": "Please register customer first !",
            }
        card_id = self.generate_ID()
        card = Card(card_id)
        card.deposit(money)
        customer.add_card(card)
        return {
                    "Status": "success",
                    "Customer_id": customer_id,
                    "Card_id": card_id,
                    "Money" : money
                }

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
        
    
    def get_customer_reservations(self, customer_id: str):
        customer = self.get_customer_info(customer_id)
        if not customer:
            return {"status": "fail", "message": "Customer not found"}

        res_list = []
        for res in customer.reservation:
            res_info = {
                "reservation_id": res.id,
                "pet_name": res.pet.name,
                "status": res.status,
                "details": res.get_details() 
            }

            # แยกเก็บข้อมูลเฉพาะทางของแต่ละบริการ
            if isinstance(res, HotelReservation):
                start_dt, end_dt = res.get_time_start_and_end
                res_info["type"] = "Hotel"
                res_info["check_in"] = start_dt.strftime("%Y-%m-%d") 
                res_info["check_out"] = end_dt.strftime("%Y-%m-%d") 
                res_info["price"] = res.price
                res_info["payment_status"] = "PAID"
                
            elif isinstance(res, MedicalReservation):
                start_dt, end_dt = res.get_time_start_and_end
                res_info["type"] = "Medical"
                res_info["appointment_time"] = start_dt.strftime("%Y-%m-%d %H:%M") 
                res_info["doctor"] = res.doctor.name
                
            elif isinstance(res, GroomingReservation):
                res_info["type"] = "Grooming"
                res_info["time"] = res.time.strftime("%Y-%m-%d %H:%M") 

            res_list.append(res_info)

        return {
            "status": "success",
            "customer_id": customer.id,
            "customer_name": customer.name,
            "total_reservations": len(res_list),
            "reservations": res_list
        }

    def register_customer(self, data: RegisterRequest):
        customer_id = self.generate_ID()
        if data.customer_tier.lower() == "silver" :
            customer = SilverMember(customer_id, data.customer_name,
                            data.phone_number, data.email, datetime.now().date())
        elif data.customer_tier.lower() == "gold" :
            customer = GoldMember(customer_id, data.customer_name,
                            data.phone_number, data.email, datetime.now().date())
        elif data.customer_tier.lower() == "platinum" :
            customer = PlatinumMember(customer_id, data.customer_name,
                            data.phone_number, data.email, datetime.now().date())
        elif data.customer_tier.lower() == None :
            customer = Customer(customer_id, data.customer_name,
                                data.phone_number, data.email)
        else :
            return {
                "Status" : "fail",
                "Message" : "invalid tier (tier must be silver/gold/platinum)"
            }
        self.__customer.append(customer)
        return {
            "Status": "success",
            "Customer_id": customer_id,
            "Customer_name": data.customer_name,
            "Phone_number": data.phone_number,
            "Email": data.email,
            "Tier" : data.customer_tier
        }

    def register_pet(self, data: RegisterPetRequest):
        customer = self.get_customer_info(data.customer_id)
        if customer:
            petID = self.generate_ID()
            pet = Pet(petID, data.pet_name, data.type_pet, data.species,
                      data.weight, data.customer_id, data.aggressive)
            customer.add_pet(pet)
            self.__pet.append(pet)

            return {
                "Status": "success",
                "Pet_id": petID,
                "Pet_name": data.pet_name,
                "Type_pet": data.type_pet,
                "Species": data.species,
                "Weight": data.weight,
                "Customer_id": data.customer_id,
                "Aggressive": data.aggressive,
            }
        else:
            return {
                "Status": "fail",
                "Message": "Please register customer first !",
            }

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
    
    def calculate_point(self,price) :
        rate = 0.01
        point = rate * price
        point_int = math.floor(point)
        return point_int

    def add_point(self, customer, price):
        if self.check_member(customer):
            point = self.calculate_point(price)
            if point >= 0 :
                customer.add_point(point)
            else :
                point = 0
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
                tier = customer.get_tier
                if tier == "silver" :
                    return "silver tier cannot use coupon"
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
        
    def reward_card_count(self,customer_id) :
        customer = self.get_customer_info(customer_id)
        member = self.check_member(customer)
        if member :
            tier = customer.get_tier
            if tier == "platinum" :
                rewards_card = customer.get_rewards_card
                if type(rewards_card) is str:
                    return rewards_card
                return rewards_card.count
            else :
                return "Not platinum tier"
        else :
            return "Not member"
      
    def calculate_price_with_discount(self,price,discount) :
        if discount <= price :
            new_price = price - discount
        else :
            new_price = 0
        return new_price
    
    def pay(self,total_price,method,money=None) :
        if method.get_payment_type == "qrcode" :
            result = method.validate_money(total_price,money) 
            if result == False :
                return "Invalid money"
        if method.get_payment_type == "card":
            result = method.validate_money(total_price)
            if result == "not enough":
                return "Card not have enough money"
            money = method.total_card_money
            method.total_card_money = money - total_price
        return "Success"
    
    def set_paid_to_service(self,service) :
        service.is_paid = True

    def create_service_and_pet_list(self, pet_list):
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

    def start_calculate_total_price(self,customer_id,use_cp,use_rw_card,pay=False) :
        customer = self.get_customer_info(customer_id)
        if (customer == None) :
            return "Customer not found"

        pet_list = customer.pet

        price = 0
        for pet in pet_list :
            service = pet.search_unpaid_service()
            if service is not None:
                service.calculate_total_price()
                price += service.price

        if price == 0 :
            return "No order to pay"
        
        member = self.check_member(customer)
        if member == False :
            if use_cp == True or use_rw_card == True :
                return "Not a member"
        else :
            tier = customer.get_tier
            rate = customer.get_rate
            if tier == "silver" :
                is_limit = customer.check_is_limit()
                if is_limit == True :
                    return price
            discount = price*rate
            price = self.calculate_price_with_discount(price,discount)
            if use_rw_card == True :
                if tier == "silver" or tier == "gold" :
                    return "silver/gold cannot use reward card"
                result = customer.use_rewards_card(pay)
                if result == True :
                    price = 0
                    return price 
                else :
                    return "rewards card not available(Must collect more than 10 times)"
            if use_cp == True :
                if tier == "silver" :
                    return "silver tier cannot use coupon"
                coupon = customer.get_coupon()
                if coupon == None :
                    return "not have coupon" 
                else :
                    discount = coupon.use_coupon
                price = self.calculate_price_with_discount(price,discount)
        return price
    
    def start_payment(self,customer_id,payment_type,card_ID=None,use_cp=False,use_rw_card=False,money=None) :
        price = self.start_calculate_total_price(customer_id,use_cp,use_rw_card,pay=True)
        if type(price) is str:
            return price
        
        customer = self.get_customer_info(customer_id)
        method = self.get_payment_method_object(customer,payment_type,card_ID)
        if method == None :
            return "Invalid CardID"

        result = self.pay(price,method,money)
        if result != "Success":
            return result
        
        member = self.check_member(customer)
        if member :
            point = self.add_point(customer,price) 
            tier = customer.get_tier
            if tier == "platinum" :
                customer.add_count_to_rewards_card()
            elif tier == "silver" :
                customer.add_count_for_use_discount()
        pet_list = customer.pet
        pet_service_list = self.create_service_and_pet_list(pet_list)
        for pet in pet_list :
            service = pet.search_unpaid_service()
            self.set_paid_to_service(service)
        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payment = self.create_payment(customer_id,method,price,pet_service_list,today,point)
        customer.add_payment(payment)
        payment_slip = payment.create_payment_slip()
        return payment_slip

    # เปลี่ยน str ให้กลายเป็น time object
    # หากไม่ได้ใส่ time_end มาให้
    def convert_str_to_time(self, time_start: str, time_end: str):
        time_format = "%Y-%m-%d %H:%M"
        try:
            start_dt = datetime.strptime(time_start, time_format)
            if time_end:
                end_dt = datetime.strptime(time_end, time_format)
            else:
                end_dt = start_dt + timedelta(hours=1)
            return start_dt, end_dt
        except ValueError:
            return None, None

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
        money=None
    ):
        resource = None
        price = 0
        customer = self.get_customer_info(customer_id)
        pet = customer.get_pet_info(pet_id)
        if pet == None :
            return {"Status": "Error", "Message": "Pet does not belong to owner"}
        payment_obj = None

        start_dt, end_dt = self.convert_str_to_time(time_start, time_end)

        if service_type.lower() == "grooming":
            resource = "Grooming"

        elif service_type.lower() == "hotel":
            
            for big_service in pet.service:
                if big_service.is_paid == False:
                    if "Hotel" in big_service.get_service_list():
                        return {
                            "status": "fail", 
                            "message": f"Pet '{pet.name}' already has a hotel reservation"
                        }

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
            staying_time = max(1, math.ceil(original_time_duration / timedelta(days=1)))

            # เผื่อใส่ไม่ตรง format
            room_type = room_type.lower()
            # Not have VIP or let Vip be privateroom
            # We only have privateroom and shareroom.
            if room_type == "private":
                room_type = "privateroom"
            elif room_type == "share":
                room_type = "shareroom"

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
                        room.cancel_room(start_dt, end_dt)
                        resource = None
                        return {
                            "status": "fail",
                            "message": "CardID Not Found.",
                        }

                    pay_result = self.pay(price, payment_obj, price)

                    if pay_result != "Success":
                        room.cancel_room(start_dt, end_dt)
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
                        pet_service_list=[
                            f"Pre-paid Hotel ({room.get_details()})"],
                        date=today,
                        point=point
                    )
                    customer.add_payment(payment_record)
                    big_service = RecordService(start_dt)
                    hotel_service_with_reservation = HotelService(resource,start_dt,end_dt,price,True)
                    big_service.append_sub_service(hotel_service_with_reservation)
                    pet.append_big_service(big_service)
                    break

        elif service_type.lower() == "medical":
            for emp in self.__employee:
                if emp.Type == "Doctor" and emp.get_avaliable_work(start_dt, end_dt):
                    if emp.update_timeslot(start_dt, end_dt):
                        resource = emp
                        break

        if resource:
            reservation_id = str(uuid.uuid1())[:8]
            if service_type.lower() == "grooming":
                new_reservation = GroomingReservation(
                    reservation_id, customer, pet, start_dt
                )

            elif service_type.lower() == "hotel":
                new_reservation = HotelReservation(
                    reservation_id,
                    customer,
                    pet,
                    start_dt,
                    end_dt,
                    resource,
                    price,
                    payment_method,
                )

                # pet.add_boarding_service(resource)

            elif service_type.lower() == "medical":
                new_reservation = MedicalReservation(
                    reservation_id, customer, pet, start_dt,end_dt, resource
                )

            self.__reservation.append(new_reservation)
            customer.add_reservation(new_reservation)

            if customer.email:
                self.__notification.send_confirmation("EMAIL", reservation_id)
            else:
                self.__notification.send_confirmation("SMS", reservation_id)

            if service_type.lower() == "hotel":
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

    def cancel_reservation(self,customer_id, pet_id,reservation_id):
        customer = self.get_customer_info(customer_id)
        if not customer:
            return {"status": "fail", "message": "Customer not found"}
        
        pet = customer.get_pet_info(pet_id)
        if not pet:
            return {"status": "fail", "message": "Pet not found"}
        
        for reservation in customer.reservation:
            if reservation.id == reservation_id:
                if isinstance(reservation,HotelReservation):
                    start_dt,end_dt = reservation.get_time_start_and_end
                    reservation.room.cancel_room(start_dt, end_dt)
                    for big_service in pet.service:
                        if big_service.is_paid == False:
                            service_to_remove = None
                            for sub_service in big_service.sub_service:
                                if sub_service.type == "Hotel" and sub_service.is_from_reservation:
                                    service_to_remove = sub_service
                                    break

                            if service_to_remove:
                                big_service.sub_service.remove(service_to_remove)
                                if len(big_service.sub_service) == 0:
                                    pet.service.remove(big_service)
                                break
                elif isinstance(reservation, MedicalReservation):
                    start_dt, end_dt = reservation.get_time_start_and_end
                    reservation.doctor.free_timeslot(start_dt, end_dt)
                
                else:
                    pass
                customer.reservation.remove(reservation)
                return {
                    "status": "success",
                    "message": f"Reservation {reservation_id} has been successfully cancelled."
                }
        else:
            return {
                "status" : "fail",
                "message" : f"{reservation_id} not found in any reservation in Pet : {pet.name}"
            }
        pass


    def medical_treatment(self, data: TreatmentRequest):
        doctor = self.get_doctor_info(data.doctor_id)
        customer = self.get_customer_info(data.owner_id)
        pet = customer.get_pet_info(data.petID)

        if doctor == None:
            return {"Status": "Error", "Message": "Doctor is not found"}
        if customer == None:
            return {"Status": "Error", "Message": "Customer is not found"}
        if pet == None :
            return {"Status": "Error", "Message": "Pet does not belong to owner"}

        medical_service = doctor.create_medical_service(data, self)

        unpaid_service = pet.search_unpaid_service()

        # check unpaid service
        if unpaid_service:
            if not unpaid_service.check_has_medical_service() :
                unpaid_service.append_sub_service(medical_service)
            else : 
                return {"Status": "Error", "Message": "Medical service for today already create"}

        else:
            #แก้datetimeให้รูปแบบเหมือน hotel service
            new_big_service = RecordService(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # สร้างกล่องใหญ่ 
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
        
        has_admit = unpaid_service.check_has_hotel_admit_service()
        if has_admit :
            return {"Status": "Error", "Message": "Admit service for today already create"}

        resource = None
        time_start = datetime.now().replace(microsecond=0)
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