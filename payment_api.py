from fastapi import FastAPI
import uvicorn
from datetime import datetime
import uuid

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
        self.__reservation = []
        self.__pick_date = []
        self.__transaction_list = []
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
    
    def add_transaction(self,transaction) :
        self.__transaction_list.append(transaction)
        return "Success"
            

class Clinic :
    def __init__(self,name) :
        self.__name = name
        self.__list_customer = []
        self.__payment = None
    def add_customer(self,customer) :
        self.__list_customer.append(customer)
    def add_payment(self,payment) :
        self.__payment = payment
    def search_customer(self,customer_id):
        for customer in self.__list_customer :
            if customer.get_id == customer_id :
                return customer
        return "Not Found"
    def create_transaction(self,customer_id,payment_type,price,service_list,today) :
        transaction_ID = self.generate_ID()
        bill = Bill(customer_id,transaction_ID,payment_type,price,service_list,today)
        return bill.create_bill()
    def generate_ID(self) :
        ID = uuid.uuid4().hex[:8]
        return ID
    def start_payment(self,customer_id,payment_type) :
        customer = self.search_customer(customer_id)
        if (customer != "Not Found") :
            today = datetime.today() # 2026-02-08 21:30:15.123456
            list_reservation = customer.search_reservation(today) 
            if len(list_reservation) == 0 :
                return "Not have"
            else : 
                price = self.__payment.calculate_price(list_reservation)
                if price > 0 :
                    if(self.__payment.pay(price,payment_type) == "Success" ):
                        service_list = []
                        for service in list_reservation :
                            service_list.append(service.get_service)
                        transaction = self.create_transaction(customer_id,payment_type,price,service_list,today)
                        if(customer.add_transaction(transaction) == "Success" ):
                            return transaction
                        

class Payment :
    def __init__(self):
        self.__total_money = 0
    def calculate_price(self,list_reservation) :
        total = 0
        for item in list_reservation :
            total = total + item.get_money
        return total
    def pay(self,amount,payment_type) :
        self.__total_money += amount
        return "Success"

class Bill :
    def __init__(self,customer_id,transaction_ID,payment_type,price,service_list,date) :
        self.__customer_id = customer_id
        self.__payment_type = payment_type
        self.__price = price
        self.__service_list = service_list
        self.__date = date
        self.__transaction_id = transaction_ID
    
    def create_bill(self) :
        return f"CustomerID:{self.__customer_id}-TransactionID:{self.__transaction_id}-Type:{self.__payment_type}-Price:{self.__price}-Service:{self.__service_list}-Date:{self.__date}"
    
        
clinic = Clinic("PetShop") 
Bam = Customer("bam","123445")
clinic.add_customer(Bam)
today = datetime.now()
reservation1 = Reservation("rx122",Bam,"Bath",4500,today)
reservation = Reservation("rx122",Bam,"Treatment",5500,today)
payment =Payment()
clinic.add_payment(payment)


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/payment/{customer_id}") 
def payment(customer_id : str , payment_type : str) :
    return (clinic.start_payment(customer_id,payment_type))

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: str | None = None):
#     return {"item_id": item_id, "q": q}

# @app.get("/test")
# def read_root(request:str , reply:str):
#     return{"Request":request,"Reply":reply}

if __name__ == "__main__" :
    uvicorn.run("payment_api:app",host="127.0.0.1",port=8000,reload=True)