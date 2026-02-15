from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import uuid
from abc import abstractmethod

app = FastAPI()

class ReservationRequest(BaseModel):
    customer_id: str
    pet_id: str
    service_type: str
    datetime_str: str


class Notification:
    def send_confirmation(self, method: str, reservation_id: str):
        print(
            f"[{method}] Sent confirmation for Reservation ID: {reservation_id}"
        )
        return True


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

class MedicalReservation(Reservation):
    def __init__(self, reservation_id, customer, pet, time, doctor):
        super().__init__(reservation_id, customer, pet, time)
        self.doctor = doctor

class HotelReservation(Reservation):
    def __init__(self, reservation_id, customer, pet, time, room, payment):
        super().__init__(reservation_id, customer, pet, time)
        self.room = room
        self.price = room.get_price
        self.payment = payment
    @property
    def get_hotel_reservation_price(self):
        return self.price
    
class PaymentMethod:
    def __init__(self):
        pass
    
    @abstractmethod
    def calculate_price(self,list_reservation) :
        pass
    @abstractmethod
    def pay(self,amount,payment_type,customer = None,card = None) :
        pass

class Card (PaymentMethod) :
    Fee = 0.01

    def __init__(self):
        self.__payment_type = "card"
        self.__total_money = 0

    def calculate_price(self,list_reservation) :
        total = 0
        for item in list_reservation :
            total = total + item.get_money
        return (total*0.01)+total
    
    def validate(self,customer,card) :
        if card != None :
            if customer.validate_card_for_payment(card) :
                return True
        return False
    
    def pay(self,amount,payment_type,customer,card = None) :
        if self.validate(customer,card) :
            self.__total_money += amount
            return "Success"
    
    @property
    def get_payment_type (self) :
        return self.__payment_type
        
    
class QRCode (PaymentMethod) :
    def __init__(self):
        self.__payment_type = "qrcode"
        self.__total_money = 0

    def calculate_price(self,list_reservation) :
        total = 0
        for item in list_reservation :
            total = total + item.get_money
        return total
    
    def pay(self,amount,payment_type,customer=None,card=None) :
        self.__total_money += amount
        return "Success"
    
    @property
    def get_payment_type (self) :
        return self.__payment_type

class Payment :
    def __init__(self,customer_id,payment_ID,payment_type,price,service_list,date) :
        self.__customer_id = customer_id
        self.__payment_type = payment_type
        self.__price = price
        self.__service_list = service_list
        self.__date = date
        self.__payment_id = payment_ID
    
    def create_payment(self) :
        return f"CustomerID:{self.__customer_id}-PaymentID:{self.__payment_id}-Type:{self.__payment_type}-Price:{self.__price}-Service:{self.__service_list}-Date:{self.__date}"
    
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
        self.__vaccine = []
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

class Customer:
    def __init__(self, customer_id, name, phone_number, email):
        self.__customer_id = customer_id
        self.__name = name
        self.__phoneNumber = phone_number
        self.__email = email
        self.__pet = []
        self.__reservation = []
        pass

    def add_pet(self, pet: Pet):
        self.__pet.append(pet)

    def add_reservation(self,reservation):
        self.__reservation.append(reservation)
        
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

class Member(Customer):
    DiscountRate = 0
    def __init__(self, customer_id, name, phone_number, email, points = 0):
        super().__init__(customer_id, name, phone_number, email)
        self.__points = points
        
class SilverMember(Member):
    DiscountRate = 0.05
    def __init__(self, customer_id, name, phone_number, email, points = 0):
        super().__init__(customer_id, name, phone_number, email,points)

class GoldMember(Member):
    DiscountRate = 0.10
    def __init__(self, customer_id, name, phone_number, email, points=0):
        super().__init__(customer_id, name, phone_number, email, points)


class PlatinumMember(Member):
    DiscountRate = 0.10
    def __init__(self, customer_id, name, phone_number, email, points=0):
        super().__init__(customer_id, name, phone_number, email, points)

class WorkSchedule:
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
        self.__workschedule = WorkSchedule()

    @property
    def name(self):
        return self.__name

    def get_avaliable_work(self, time: str):
        return self.__workschedule.search_availability(time)
        pass
    
    def update_timeslot(self, time: str):
        return self.__workschedule.update_schedule(time)



class Worker(Employee):
    Type = "Worker"

    def __init__(self, emp_id, name, skill="General"):
        super().__init__(emp_id, name)
        self.__skill = skill


class Doctor(Employee):
    Type = "Doctor"

    def __init__(self, emp_id, name, speciality="General"):
        super().__init__(emp_id, name)
        self.__skill = speciality

    pass


class Room:
    price_per_day = 0

    def __init__(self, room_id, room_type, full=False):
        self._room_id = room_id
        self._room_type = room_type
        self._is_full = bool(full)

    def get_details(self):
        return (
            f"ID: {self._room_id}, Type: {self._room_type}, Price: {self.price_per_day}"
        )

    @property
    def get_price(self):
        return self.price_per_day

    @property
    def is_full(self):
        return self._is_full
    
    def book_room(self):
        if not self._is_full:
            self._is_full = True
            return True
        return False


class PrivateRoom(Room):
    price_per_day = 1500

    def __init__(self, room_id):
        super().__init__(room_id, "PrivateRoom")


class ShareRoom(Room):
    price_per_day = 500

    def __init__(self, room_id):
        super().__init__(room_id, "ShareRoom")


class Clinic:
    def __init__(self):
        self.__customer = []
        self.__stocks = []
        self.__employee = []
        self.__rooms = []
        self.__bills = []
        self.__reservation = []
        self.__grooming_history = []
        self.__medical_record = []
        self.__pet = []
        self.__notification = Notification()
        self._setup_dummy_data()
    
    def _setup_dummy_data(self):
        self.__employee.append(Worker("W01", "P'Somchai"))
        self.__employee.append(Doctor("D01", "Dr.Strange"))
        self.__rooms.append(PrivateRoom("R01"))
        self.__rooms.append(ShareRoom("R02"))
        c1 = Customer("C01", "Pingtale", "0999999999", "pingtale@email.com")
        p1 = Pet("P01", "Niggy", "Dog", "Golden", 25, "C01")
        c1.add_pet(p1)
        self.__customer.append(c1)
        self.__pet = [p1]

    def get_pet_info(self, petID):
        for i in self.__pet:
            if i.id == petID:
                return i
        return None
        
    def get_customer_info(self,customer_id):
        for i in self.__customer:
            if i.id == customer_id:
                return i
        return None
        

    def create_reservation(self, customer_id, pet_id, service_type, time):
        resource = None
        price = 0
        customer = self.get_customer_info(customer_id)
        pet = self.get_pet_info(pet_id)
        if service_type == "Grooming":
            for emp in self.__employee:
                if emp.Type == "Worker" and emp.get_avaliable_work(time):
                    if emp.update_timeslot(time):
                        resource = emp
                        price = 500
                        if pet.aggressive:
                            price += (price*0.3)
                        break
                
        elif service_type == "Hotel":
            for room in self.__rooms:
                if not room.is_full:
                    if room.book_room():
                        resource = room
                        price = room.get_price
                        break

            
        elif service_type == "Medical":
            for emp in self.__employee:
                if emp.Type == "Doctor" and emp.get_avaliable_work(time):
                    if emp.update_timeslot(time):
                        resource = emp
                        price = 1500
                        if pet.aggressive:
                            price += (price*0.3)
                        break
        
        if resource:
            reservation_id = str(uuid.uuid1())[:8]
            new_reservation = Reservation(reservation_id, customer, pet, time)
            self.__reservation.append(new_reservation)
            customer.add_reservation(new_reservation)
            if customer.email:
                self.__notification.send_confirmation("EMAIL", reservation_id)
            else:
                self.__notification.send_confirmation("SMS", reservation_id)
            return {
                "status" : "success",
                "customer_name" : customer.name,
                "pet_name" : pet.name,
                "reservation_id": reservation_id,
                "service" : service_type,
                "time" : time
            }
        else:
            return {"status": "fail", "message": f"No available resource for {service_type} at {time}"}


# -----------------------------------------------
# FastAPI

clinic_sys = Clinic()
@app.get("/")
def read_root():
    return {"Hello": "Kub"}

@app.post("/Reservation", tags=["Reservation"])
async def make_reservation(req: ReservationRequest):
    result = clinic_sys.create_reservation(
        req.customer_id, 
        req.pet_id, 
        req.service_type, 
        req.datetime_str
    )
    return result


if __name__ == "__main__":
    uvicorn.run("Reservation:app", host="127.0.0.1", port=8000, reload=True)

# fastapi dev Reservation.py