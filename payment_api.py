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
        
class Customer :
    def __init__(self,name,id):
        self.__name =name
        self.__customer_id = id
        self.__card = []
        self.__reservation = []
        self.__pick_date = []
        self.__payment_list = []

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
        self.__payment_method = []

    def add_customer(self,customer) :
        self.__list_customer.append(customer)

    def add_payment_method(self,payment_method) :
        self.__payment_method.append(payment_method)

    def search_customer(self,customer_id):
        for customer in self.__list_customer :
            if customer.get_id == customer_id :
                return customer
        return "Not Found"
    
    def create_payment(self,customer_id,payment_type,price,service_list,today,point=0) :
        payment_ID = self.generate_ID()
        payment = Payment(customer_id,payment_ID,payment_type,price,service_list,today,point)
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
            list_reservation = customer.search_reservation(today) 

            if len(list_reservation) == 0 :
                return "Not have"
            else : 
                method = self.check_payment_type(payment_type)
                if method == None : 
                    return "Payment type not supported"
                price = method.calculate_price(list_reservation)
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
                        service_list = []
                        for service in list_reservation :
                            service_list.append(service.get_service)
                        payment = self.create_payment(customer_id,payment_type,new_price,service_list,today,point)
                        
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
        return "Invalid card"
    
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
    def __init__(self,customer_id,payment_ID,payment_type,price,service_list,date,point) :
        self.__customer_id = customer_id
        self.__payment_type = payment_type
        self.__price = price
        self.__service_list = service_list
        self.__date = date
        self.__payment_id = payment_ID
        self.__point = point
    
    def create_payment(self) :
        return f"CustomerID:{self.__customer_id}-PaymentID:{self.__payment_id}-Type:{self.__payment_type}-Price:{self.__price}-Service:{self.__service_list}-Date:{self.__date}-Point:{self.__point}"
        
clinic = Clinic("PetShop") 

Bam = Customer("bam","123445")
Bam.add_card("Card123")
clinic.add_customer(Bam)

Peem = GoldMember("peem","123456", datetime(2025, 11, 11))
Peem.add_card("Card555")
clinic.add_customer(Peem)

today = datetime.now()
reservation1 = Reservation("rx122",Bam,"Bath",4500,today)
reservation = Reservation("rx122",Bam,"Treatment",5500,today)

reservation2 = Reservation("ry123",Peem,"Treatment",6000,today)
reservation3 = Reservation("ry123",Peem,"Boarding",6000,today)

CardPayment = Card()
QRCodePayment = QRCode()
clinic.add_payment_method(CardPayment)
clinic.add_payment_method(QRCodePayment)

clinic.add_point(Peem,12000)
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