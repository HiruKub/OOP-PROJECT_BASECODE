from fastapi import FastAPI
import uvicorn
from datetime import datetime
import uuid
from abc import ABC, abstractmethod
import math

app = FastAPI()
class Reservation :
    def __init__(self,reservation_id,customer,service,money,date):
        self.__customer = customer
        self.__reservation_id = reservation_id
        self.__service = service
        self.__money = money
        self.__date = date
        self.add_reservation(customer) 
    def add_reservation(self,customer) :
        customer.set_reservation(self)
    @property
    def get_date(self) :
        return self.__date
    @property
    def get_money(self) :
        return self.__money
    @property
    def get_service(self) :
        return self.__service
    
class Service :
    def __init__(self,pet_name,owner_name,date) :
        self.__pet_name = pet_name
        self.__owner = owner_name
        self.__date = date 
        self.__service = []
        self.__price = 0

    @property
    def get_date(self) :
        return self.__date

    def append_service(self,service) :
        self.__service.append(service)

    def calculate_total_price(self) :
        total = 0
        for service in self.__service:
            total += service.price
        self.__price = total
        return self.__price
    
    def get_service_list (self) :
        service_list = []
        for service in self.__service :
            type = service.type
            service_list.append(type)
        return service_list

class GroomingService :
    def __init__(self,type,price) :
        self.__type = type
        self.__price = price

    @property
    def price(self) :
        return self.__price
    
    @property
    def type(self) :
        return self.__type

class BoardingService :
    def __init__(self,type,room,day,price) :
        self.__type = type
        self.__room = room
        self.__day = day
        self.__price = price

    @property
    def price(self) :
        return self.__price
    
    @property
    def type(self) :
        return self.__type

class MedicalService :
    def __init__(self,type,doctor_id,price) :
        self.__type = type
        self.__doctor_id = doctor_id
        self.__price = price

    @property
    def price(self) :
        return self.__price
    
    @property
    def type(self) :
        return self.__type
    
class Pet :
    def __init__(self,name,customer_id) :
        self.__name = name
        self.__customer_id = customer_id
        self.__service = []

    def search_service(self,date) :
        for service in self.__service :
            if service.get_date.date() == date.date() :
                return service
        return None
    
    def append_big_service (self,service) :
        self.__service.append(service)
    
    @property
    def name(self) :
        return self.__name
        
        
class Customer :
    def __init__(self,name,id):
        self.__name =name
        self.__customer_id = id
        self.__pet_list = []
        self.__card = []
        self.__reservation = []
        self.__pick_date = []
        self.__payment_list = []

    def add_pet(self,pet) :
        self.__pet_list.append(pet)

    @property
    def get_pet(self) :
        return self.__pet_list

    @property
    def get_id(self):
        return self.__customer_id
    
    def set_reservation(self,reservation) :
        self.__reservation.append(reservation)
    def search_reservation(self,date) :
        self.__pick_date = []
        for item in self.__reservation :
            if item.get_date.date() == date.date() :
                self.__pick_date.append(item)
        return self.__pick_date
    
    def add_payment(self,payment) :
        self.__payment_list.append(payment)
        return "Success"
    
    def add_card(self,card_id) :
        self.__card.append(card_id) 
    
    def validate_card_for_payment (self,card_id) :
        for card in self.__card :
            if card == card_id :
                return True
        return False
    

class Member(Customer) :
    def __init__ (self,name,customer_id,day) :
        super().__init__(name,customer_id)
        self.__signup_day = day
        self.__point = 0
        self.__coupon = []

    @property 
    def point(self) :
        return self.__point

    @point.setter 
    def point(self,point) :
        self.__point = point

    def add_coupon(self,coupon) :
        self.__coupon.append(coupon)

    def get_coupon(self) :
        if self.__coupon :
            return self.__coupon[0]
        else :
            return None
    
    def delete_coupon(self) :
        self.__coupon.pop(0)

class SilverMember(Member) :
    def __init__(self, name, customer_id, day):
        super().__init__(name, customer_id, day)
        self.__tier = "silver"
        self.__rate = 0.01

    @property
    def get_tier(self) :
        return self.__tier
    
    @property
    def get_rate(self) :
        return self.__rate

class GoldMember(Member) :
    def __init__(self, name, customer_id, day):
        super().__init__(name, customer_id, day)
        self.__tier = "gold"
        self.__rate = 0.05

    @property
    def get_tier(self) :
        return self.__tier
    
    @property
    def get_rate(self) :
        return self.__rate
    
class PlatinumMember(Member) :
    def __init__(self, name, customer_id, day):
        super().__init__(name, customer_id, day)
        self.__tier = "platinum"
        self.__rate = 0.1

    @property
    def get_tier(self) :
        return self.__tier
    
    @property
    def get_rate(self) :
        return self.__rate

class Coupon() :
    def __init__(self,id) :
        self.__coupon_id = id
        self.__discount = 10

    @property
    def discount(self) :
        return self.__discount
        
class Clinic :
    def __init__(self,name) :
        self.__name = name
        self.__list_customer = []
        self.__list_pet = []
        self.__payment_method = []
    
    def add_pet (self,pet) :
        self.__list_pet.append(pet)
    
    def search_pet_by_name (self,name) :
        for pet in self.__list_pet :
            if pet.name == name :
                return pet
        return "Not found"

    def record_service(self,pet_name,customer_name,date,type,price,room=None,doctor_id=None) :
        pet = self.search_pet_by_name(pet_name)
        if pet == "Not found" :
            return "Not found"
        else :
            big_service = pet.search_service(date)
            create =False
            if big_service == None :
                create = True
                big_service = self.create_service(pet_name,customer_name,date)

            if type == "grooming" :
                grooming = self.create_grooming_service(price)
                big_service.append_service(grooming)

            elif type == "boarding" :
                boarding = self.create_boarding_service(room,date,price)
                big_service.append_service(boarding)

            elif type == "treatment" :
                treatment = self.create_treatment_service(doctor_id,price)
                big_service.append_service(treatment)
        if(create) :
            pet.append_big_service(big_service)

    def create_service (self,pet_name,customer_name,date) :
        # service = Service("corgi","bam",datetime(11/11/2025))
        service = Service(pet_name,customer_name,date)
        return service

    def create_grooming_service(self,price) :
        grooming = GroomingService("grooming",price)
        return grooming

    def create_boarding_service(self,room,day,price) :
        boarding = BoardingService("boarding",room,day,price)
        return boarding
    
    def create_treatment_service (self,doctor_id,price) :
        treatment = MedicalService("treatment",doctor_id,price)
        return treatment

    def add_customer(self,customer) :
        self.__list_customer.append(customer)

    def add_payment_method(self,payment_method) :
        self.__payment_method.append(payment_method)

    def search_customer(self,customer_id):
        for customer in self.__list_customer :
            if customer.get_id == customer_id :
                return customer
        return "Not Found"
    
    def create_payment(self,customer_id,method,price,service_list,today,point=0) :
        payment_ID = self.generate_ID()
        payment = Payment(customer_id,payment_ID,method,price,service_list,today,point)
        return payment.create_payment()
    
    def generate_ID(self) :
        ID = uuid.uuid4().hex[:8]
        return ID
    
    def check_payment_type(self,payment_type) :
        payment_type = payment_type.lower()
        method = None
        for payment_method in self.__payment_method :
                    if payment_method.get_payment_type == payment_type :
                        method = payment_method
                        break
        return method
    
    def check_member(self,customer) :
        if isinstance(customer,Member) :
            return True
        else :
            return False

    def calculate_discount(self,customer_id,price) :
        customer = self.search_customer(customer_id)
        if customer != "Not Found" :
            if self.check_member(customer) :
                rate = customer.get_rate
                discount = rate * price
                return discount  
            else :
                return 0

    def calculate_point(self,price) :
        rate = 0.01
        point = rate * price
        point_int = math.floor(point)
        return point_int
        
    def add_point (self,customer,price) :
        if self.check_member(customer) :
            point = customer.point
            earn = self.calculate_point(price) 
            customer.point = point+earn
            return earn
        else :
            return 0
        
    def create_coupon(self) :
        id = self.generate_ID()
        coupon = Coupon(id)
        return coupon

    def get_coupon (self,customer_id) :
        customer = self.search_customer(customer_id) 
        if customer != "Not Found" :
            if self.check_member(customer) :
                point = customer.point 
                if point >= 50 :
                    coupon = self.create_coupon()
                    customer.add_coupon(coupon)
                    customer.point = point-50
                    return "Success"
                else :
                    return "Not enough point"
            else :
                return "Not Member"
        else :
            return "Not found customer"
      
    def use_coupon (self,customer) :
        coupon = customer.get_coupon()
        if coupon != None :
            discount = coupon.discount
            customer.delete_coupon()
            return discount
        else : 
            return "Not Have Coupon"
    
    def start_payment(self,customer_id,payment_type,card=None,use_cp=False) :
        customer = self.search_customer(customer_id)
        
        if (customer != "Not Found") :
            today = datetime.today() # 2026-02-08 21:30:15.123456
            # list_reservation = customer.search_reservation(today) 

            # if len(list_reservation) == 0 :
            #     return "Not have"
            # else : 
            pet_list = customer.get_pet 
           
            method = self.check_payment_type(payment_type)
            if method == None : 
                return "Payment type not supported"
            # price = method.calculate_price(list_reservation)

            price = method.calculate_price(pet_list,today)

            discount = self.calculate_discount(customer_id,price)
            cp_discount = 0
            if use_cp :
                if not self.check_member(customer):
                    return "Not Member"
                    
                cp_discount = self.use_coupon(customer)
                if cp_discount == "Not Have Coupon" :
                    return "Not Have Coupon"

            new_price = price - discount - cp_discount

            if new_price > 0 :
                
                pay_result = method.pay(new_price,payment_type,customer,card)
                if( pay_result == "Success" ):
                    point = self.add_point(customer,price)
                    # service_list = []
                    # for service in list_reservation :
                    #     service_list.append(service.get_service)
                    list_pet_and_service = []
                    for pet in pet_list :
                        service = pet.search_service(today)
                        if service != None :
                            service_list = service.get_service_list()
                            list_pet_and_service.append([pet.name, service_list])

                    payment = self.create_payment(customer_id,method,new_price,list_pet_and_service,today,point)
                        
                    if(customer.add_payment(payment) == "Success" ):
                        return payment
                    else :
                        return "cannot add payment"
                    
                else :
                    return "cannot pay"
                
            else :
                return "Not have order to pay" 
        else :
            return "Not Found Customer"                

class PaymentMethod(ABC) :

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

    def calculate_price(self,pet_list,today) :
        price = 0
        for pet in pet_list :
            service = pet.search_service(today)
            if service != None :
                sub_price = service.calculate_total_price()
                price += sub_price
        return (price*0.01)+price
    
    def validate(self,customer,card) :
        if card != None :
            if customer.validate_card_for_payment(card) :
                return True
        return False
    
    def pay(self,amount,payment_type,customer,card = None) :
        if self.validate(customer,card) :
            self.__total_money += amount
            return "Success"
        return "Invalid card"
    
    @property
    def get_payment_type (self) :
        return self.__payment_type
        
    
class QRCode (PaymentMethod) :
    def __init__(self):
        self.__payment_type = "qrcode"
        self.__total_money = 0

    def calculate_price(self,pet_list,today) :
        price = 0
        for pet in pet_list :
            service = pet.search_service(today)
            if service != None :
                sub_price = service.calculate_total_price()
                price += sub_price
        return price
    
    def pay(self,amount,payment_type,customer=None,card=None) :
        self.__total_money += amount
        return "Success"
    
    @property
    def get_payment_type (self) :
        return self.__payment_type

class Payment :
    def __init__(self,customer_id,payment_ID,method,price,service_list,date,point) :
        self.__customer_id = customer_id
        self.__payment_type = method.get_payment_type
        self.__price = price
        self.__service_list = service_list
        self.__date = date
        self.__payment_id = payment_ID
        self.__point = point
        self.__payment_method = []

    # def create_payment_method(self) :
    #     CardPayment = Card()
    #     QRCodePayment = QRCode()
    #     self.__payment_method.append(CardPayment)
    #     self.__payment_method.append(QRCodePayment)
    
    def create_payment(self) :
        return f"CustomerID:{self.__customer_id}-PaymentID:{self.__payment_id}-Type:{self.__payment_type}-Price:{self.__price}-Service:{self.__service_list}-Date:{self.__date}-Point:{self.__point}"
        
clinic = Clinic("PetShop") 

Bam = Customer("bam","123445")
Bam.add_card("Card123")
clinic.add_customer(Bam)
Golden = Pet("golden","123445")
clinic.add_pet(Golden)
Bam.add_pet(Golden)

Peem = GoldMember("peem","123456", datetime(2025, 11, 11))
Peem.add_card("Card555")
clinic.add_customer(Peem)
Corgi = Pet("corgi","123456")
clinic.add_pet(Corgi)
Peem.add_pet(Corgi)
Husky = Pet("husky","123456")
clinic.add_pet(Husky)
Peem.add_pet(Husky)

today = datetime.now()
# reservation1 = Reservation("rx122",Bam,"Bath",4500,today)
# reservation = Reservation("rx122",Bam,"Treatment",5500,today)

# reservation2 = Reservation("ry123",Peem,"Treatment",6000,today)
# reservation3 = Reservation("ry123",Peem,"Boarding",6000,today)

clinic.record_service("golden","bam",today,"grooming",2000)
clinic.record_service("golden","bam",today,"boarding",5000,"room1")

clinic.record_service("corgi","peem",today,"treatment",5500,doctor_id="DOCTOR123")
clinic.record_service("husky","peem",today,"grooming",2000)
clinic.record_service("husky","peem",today,"boarding",5000,"room1")

CardPayment = Card()
QRCodePayment = QRCode()
clinic.add_payment_method(CardPayment)
clinic.add_payment_method(QRCodePayment)

clinic.add_point(Peem,12000)
clinic.get_coupon("123456")
clinic.get_coupon("123456")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/payment/{customer_id}") 
def payment(customer_id : str , payment_type : str , card_ID : str|None = None ,use_cp: bool = False) :
    return (clinic.start_payment(customer_id,payment_type,card_ID,use_cp))

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}

# @app.get("/test")
# def read_root(request:str , reply:str):
#     return{"Request":request,"Reply":reply}

if __name__ == "__main__" :
    uvicorn.run("payment_api:app",host="127.0.0.1",port=8000,reload=True)