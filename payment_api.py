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
    def price(self) :
        return self.__price

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
    
    def add_card(self,card) :
        self.__card.append(card) 

    def search_card(self,card_id) :
        for card in self.__card :
            if card.get_id == card_id :
                return card
        return None
    
    def deposit_to_card(self,cardID,money) :
        card = self.search_card(cardID)
        card.deposit(money)
    
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

    def add_point(self,point) :
        self.__point += point

    def remove_point(self,point) :
        self.__point -= point

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
    def use_coupon(self) :
        return self.__discount
        
class Clinic :
    def __init__(self,name) :
        self.__name = name
        self.__list_customer = []
        self.__list_pet = []
        # self.__payment_method = []
    
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

    # def add_payment_method(self,payment_method) :
    #     self.__payment_method.append(payment_method)

    def search_customer(self,customer_id):
        for customer in self.__list_customer :
            if customer.get_id == customer_id :
                return customer
        return "Not Found"
    
    def sum_price_in_each_service(self,service_list) :
        sum_price = 0
        for service in service_list :
            service.calculate_total_price()
            price = service.price
            sum_price += price
        return sum_price
    
    def calculate_total_price(self,customer,sum_price,use_cp) :
        member = self.check_member(customer)
        discount = 0
        if member == False :
            if use_cp == True :
                return "Not a member"
        elif member == True :
            discount += self.calculate_discount(customer,sum_price)
            if use_cp :
                coupon_discount = self.get_coupon(customer)
                if coupon_discount == "Not Have Coupon" :
                    return "Not Have Coupon"
                discount += coupon_discount
        total_price = sum_price - discount
        return total_price
    
    def create_service_and_pet_list(self,pet_list,service_list) :#TODO Check THIS
        list_pet_and_service = []
        for pet in pet_list :
            service = pet.search_service(today)
            if service != None :
                service_list = service.get_service_list()
                list_pet_and_service.append([pet.name, service_list])
        return list_pet_and_service

    def create_payment(self,customer_id,method,price,list_pet_and_service,today,point=0) :
        payment_ID = self.generate_ID()
        payment = Payment(customer_id,payment_ID,method,price,list_pet_and_service,today,point)
        return payment.create_payment()
    
    def generate_ID(self) :
        ID = uuid.uuid4().hex[:8]
        return ID
    
    def check_payment_type(self,customer,payment_type,card_ID = None) :
        payment_type = payment_type.lower()
        if payment_type == "qrcode" :
            ID = self.generate_ID()
            method = QRCode(ID)
        elif payment_type == "card" :
            method = customer.search_card(card_ID)
        return method
    
    def pay(self,total_price,method,money=None) :
        if method.get_payment_type == "qrcode" :
            result = method.validate_money(total_price,money) 
            if result == False :
                return "Invalid money"
        if method.get_payment_type == "card" :
            result = method.validate_money(total_price)
            if result == "not enough" :
                return "Card not have enough money"
        return "Success"

    
    def check_member(self,customer) :
        if isinstance(customer,Member) :
            return True
        else :
            return False

    def calculate_discount(self,customer,price) :
        rate = customer.get_rate
        discount = rate * price
        return discount  
        

    def calculate_point(self,price) :
        rate = 0.01
        point = rate * price
        point_int = math.floor(point)
        return point_int
        
    def add_point (self,customer,price) :
        if self.check_member(customer) :
            point = self.calculate_point(price) 
            customer.add_point(point)
            return point
        else :
            return 0
        
    def create_coupon(self) :
        id = self.generate_ID()
        coupon = Coupon(id)
        return coupon

    def point_to_coupon (self,customer_id) :
        customer = self.search_customer(customer_id) 
        if customer != "Not Found" :
            if self.check_member(customer) :
                point = customer.point 
                if point >= 50 :
                    coupon = self.create_coupon()
                    customer.add_coupon(coupon)
                    customer.remove_point(50)
                    return "Success"
                else :
                    return "Not enough point"
            else :
                return "Not Member"
        else :
            return "Not found customer"
      
    def get_coupon (self,customer) :
        coupon = customer.get_coupon()
        if coupon != None :
            discount = coupon.use_coupon
            customer.delete_coupon()
            return discount
        else : 
            return "Not Have Coupon"
    
    def start_payment(self,customer_id,payment_type,card_ID=None,use_cp=False,money=None) :
        customer = self.search_customer(customer_id)
        
        if (customer == "Not Found") :
            return "Customer not found"
        
        pet_list = customer.get_pet
        today = datetime.today()

        service_list = []
        for pet in pet_list :
            service = pet.search_service(today)
            service_list.append(service)
        sum_price = self.sum_price_in_each_service(service_list)
        
        total_price = self.calculate_total_price(customer,sum_price,use_cp)
        if total_price == "Not Have Coupon" :
            return "Not Have Coupon"
        elif total_price == "Not a member" :
            return "Not a member"

        method = self.check_payment_type(customer,payment_type,card_ID)
        if method == None :
            return "Invalid CardID"
        
        result = self.pay(total_price,method,money)
        if result == "Invalid money" :
            return "Invalid money"
        elif result == "Card not have enough money" :
            return "Card not have enough money"
        
        point = self.add_point(customer,total_price) 
        list_pet_and_service = self.create_service_and_pet_list(pet_list,service_list)
        payment = self.create_payment(customer_id,method,total_price,list_pet_and_service,today,point)
        customer.add_payment(payment)
        return payment           

class PaymentMethod(ABC) :

    # @abstractmethod
    # def calculate_price(self,list_reservation) :
    #     pass
    # @abstractmethod
    # def pay(self,amount,payment_type,customer = None,card = None) :
    #     pass

    @abstractmethod
    def validate_money(self,total_price,money=None) :
        pass

class Card (PaymentMethod) :
    # Fee = 0.01

    def __init__(self,cardID):
        self.__payment_type = "card"
        self.__total_money = 0
        self.__cardID = cardID
        
    def validate_money(self,total_price,money=None) :
        if self.__total_money >= total_price :
            self.__total_money -= total_price
            return "enough"
        else :
            return "not enough"
        
    def add_money_to_card(self,money) :
        self.__total_money += money
        
    # def calculate_price(self,pet_list,today) :
    #     price = 0
    #     for pet in pet_list :
    #         service = pet.search_service(today)
    #         if service != None :
    #             sub_price = service.calculate_total_price()
    #             price += sub_price
    #     return (price*0.01)+price
    
    # def validate(self,customer,card) :
    #     if card != None :
    #         if customer.validate_card_for_payment(card) :
    #             return True
    #     return False
    
    # def pay(self,amount,payment_type,customer,card = None) :
    #     if self.validate(customer,card) :
    #         self.__total_money += amount
    #         return "Success"
    #     return "Invalid card"
    
    @property
    def get_payment_type (self) :
        return self.__payment_type
    
    @property
    def get_id (self) :
        return self.__cardID
    
    def deposit (self,money) :
        self.__total_money += money
        
    
class QRCode (PaymentMethod) :
    def __init__(self,id):
        self.__payment_type = "qrcode"
        self.__total_money = 0
        self.__qrcodeID = id

    def validate_money(self,total_price,money) :
        if money == total_price :
            return True
        else :
            return False

    # def calculate_price(self,pet_list,today) :
    #     price = 0
    #     for pet in pet_list :
    #         service = pet.search_service(today)
    #         if service != None :
    #             sub_price = service.calculate_total_price()
    #             price += sub_price
    #     return price
    
    # def pay(self,amount,payment_type,customer=None,card=None) :
    #     self.__total_money += amount
    #     return "Success"
    
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
        return f"CustomerID:{self.__customer_id}-PaymentID:{self.__payment_id}-Type:{self.__payment_type}-Price:{self.__price}-Pet_Service:{self.__service_list}-Date:{self.__date}-Point:{self.__point}"
        
clinic = Clinic("PetShop") 

Bam = Customer("bam","123445")
Bam_Card = Card("Card123")
Bam.add_card(Bam_Card)
Bam.deposit_to_card("Card123",50000)
clinic.add_customer(Bam)
Golden = Pet("golden","123445")
clinic.add_pet(Golden)
Bam.add_pet(Golden)

Peem = GoldMember("peem","123456", datetime(2025, 11, 11))
Peem_Card = Card("Card555")
Peem.add_card(Peem_Card)
Peem.deposit_to_card("Card555",50000)
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

# CardPayment = Card()
# QRCodePayment = QRCode()
# clinic.add_payment_method(CardPayment)
# clinic.add_payment_method(QRCodePayment)

clinic.add_point(Peem,12000)
clinic.point_to_coupon("123456")
clinic.point_to_coupon("123456")
clinic.point_to_coupon("123456")
clinic.point_to_coupon("123456")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/payment/{customer_id}") 
def payment(customer_id : str , payment_type : str , card_ID : str|None = None ,use_cp: bool = False , money : float = None) :
    return (clinic.start_payment(customer_id,payment_type,card_ID,use_cp,money))

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}

# @app.get("/test")
# def read_root(request:str , reply:str):
#     return{"Request":request,"Reply":reply}

if __name__ == "__main__" :
    uvicorn.run("payment_api:app",host="127.0.0.1",port=8000,reload=True)