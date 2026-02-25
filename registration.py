from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Registration System")

# -----------------------------
# Base model
# -----------------------------

class CustomerRequest(BaseModel):
    customer_id: str
    name: str
    phone_number: str
    email: str

class PetRequest(BaseModel):
    petID: str
    name: str
    type: str
    species: str
    weight: float
    customer_id: str
    aggressive: bool = False

class CardRequest(BaseModel):
    customer_id: str
    card_id: str

# -----------------------------
# Classes
# -----------------------------

class Card:
    def __init__(self, card_id: str):
        self.__card_id = card_id
        
    @property
    def get_id(self):
        return self.__card_id

class Pet:
    def __init__(self, petID, name, type, species, weight, customer_id, aggressive=False):
        self.__petID = petID
        self.__name = name
        self.__type = type
        self.__species = species
        self.__weight = weight
        self.__customer_id = customer_id
        self.__aggressive = bool(aggressive)
        
    @property
    def petID(self):
        return self.__petID

    @property
    def name(self):
        return self.__name

    @property
    def type(self):
        return self.__type

class Customer:
    def __init__(self, customer_id, name, phone_number, email):
        self.__customer_id = customer_id
        self.__name = name
        self.__phone_number = phone_number
        self.__email = email
        self.__pets = []
        self.__cards = []

    def add_pet(self, pet: Pet):
        self.__pets.append(pet)

    def add_card(self, card: Card):
        self.__cards.append(card)
        
    @property
    def customer_id(self):
        return self.__customer_id

    @property
    def name(self):
        return self.__name
    
    @property
    def phone_number(self):
        return self.__phone_number
    
    @property
    def email(self):
        return self.__email
    
    @property
    def pets(self):
        return self.__pets
    
    @property
    def cards(self):
        return self.__cards

class Clinic:
    def __init__(self):
        self.__customers = []
        self.__pets = []

    def get_customer_info(self, customer_id: Customer):
        for customer in self.__customers:
            if customer.customer_id == customer_id:
                return customer
        return None

    def get_pet_info(self, petID: Pet) :
        for pet in self.__pets:
            if pet.petID == petID:
                return pet
        return None

    def add_customer(self, customer_id, name, phone_number, email):
        if self.get_customer_info(customer_id):
            return {"status": "fail", "message": f"Customer ID '{customer_id}' already exists."}
        
        new_customer = Customer(customer_id, name, phone_number, email)
        self.__customers.append(new_customer)
        return {"status": "success", "message": f"Customer '{name}' added successfully."}

    def add_pet(self, petID, name, type, species, weight, customer_id, aggressive):
        customer = self.get_customer_info(customer_id)
        if not customer:
            return {"status": "fail", "message": f"Customer ID '{customer_id}' not found."}
        
        if self.get_pet_info(petID):
            return {"status": "fail", "message": f"Pet ID '{petID}' already exists."}

        new_pet = Pet(petID, name, type, species, weight, customer_id, aggressive)
        self.__pets.append(new_pet) 
        customer.add_pet(new_pet)
        return {"status": "success", "message": f"Pet '{name}' added to customer '{customer.name}'."}

    def add_payment_card(self, customer_id, card_id):
        customer = self.get_customer_info(customer_id)
        if not customer:
            return {"status": "fail", "message": f"Customer ID '{customer_id}' not found."}
        
        for card in customer.cards:
            if card.get_id == card_id:
                return {"status": "fail", "message": f"Card '{card_id}' already added to this customer."}

        new_card = Card(card_id) 
        customer.add_card(new_card)
        return {"status": "success", "message": f"Card '{card_id}' added to customer '{customer.name}'."}


clinic_sys = Clinic()

# -----------------------------
# FAST API
# -----------------------------

@app.get("/")
async def root():
    return {"message": "Welcome to registration system"}

@app.post("/customer", tags=["Customer Management"])
async def create_customer(req: CustomerRequest):
    result = clinic_sys.add_customer(
        req.customer_id, req.name, req.phone_number, req.email
    )
    return result

@app.post("/pet", tags=["Customer Management"])
async def create_pet(req: PetRequest):
    result = clinic_sys.add_pet(
        req.petID, req.name, req.type, req.species, req.weight, req.customer_id, req.aggressive
    )
    return result

@app.post("/customer/card", tags=["Customer Management"])
async def add_customer_card(req: CardRequest):
    result = clinic_sys.add_payment_card(
        req.customer_id, req.card_id
    )
    return result

@app.get("/customer/{customer_id}", tags=["Customer Info"])
async def get_customer(customer_id):
    customer = clinic_sys.get_customer_info(customer_id)
    if not customer:
        return "Customer not found"
    
    return {
        "status": "success",
        "customer_id": customer.customer_id,
        "name": customer.name,
        "phone_number": customer.phone_number,
        "email": customer.email,
        "pets": [
            {"petID": pet.petID, "name": pet.name, "type": pet.type} 
            for pet in customer.pets
        ],
        "cards": [card.get_id for card in customer.cards] 
    }


if __name__ == "__main__":
    uvicorn.run("registration:app", host="127.0.0.1", port=8000, reload=True)