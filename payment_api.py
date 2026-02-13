from fastapi import FastAPI
import uvicorn
from datetime import datetime
import uuid
from abc import ABC, abstractmethod

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
        self.__id = id
        self.__card = []
        self.__reservation = []
        self.__pick_date = []
        self.__payment_list = []
    @property
    def get_id(self):
        return self.__id
    
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
    
    def create_payment(self,customer_id,payment_type,price,service_list,today) :
        payment_ID = self.generate_ID()
        payment = Payment(customer_id,payment_ID,payment_type,price,service_list,today)
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
    
    def start_payment(self,customer_id,payment_type,card=None) :
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
                
                if price > 0 :
                    if(method.pay(price,payment_type,customer,card) == "Success" ):
                        service_list = []
                        for service in list_reservation :
                            service_list.append(service.get_service)
                        payment = self.create_payment(customer_id,payment_type,price,service_list,today)
                        
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
    
     
clinic = Clinic("PetShop") 

Bam = Customer("bam","123445")
Bam.add_card("Card123")
clinic.add_customer(Bam)

today = datetime.now()
reservation1 = Reservation("rx122",Bam,"Bath",4500,today)
reservation = Reservation("rx122",Bam,"Treatment",5500,today)

CardPayment = Card()
QRCodePayment = QRCode()
clinic.add_payment_method(CardPayment)
clinic.add_payment_method(QRCodePayment)



@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/payment/{customer_id}") 
def payment(customer_id : str , payment_type : str , card_ID : str|None = None ) :
    return (clinic.start_payment(customer_id,payment_type,card_ID))

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}

# @app.get("/test")
# def read_root(request:str , reply:str):
#     return{"Request":request,"Reply":reply}

if __name__ == "__main__" :
    uvicorn.run("payment_api:app",host="127.0.0.1",port=8000,reload=True)