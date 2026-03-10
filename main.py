from fastapi import FastAPI
import uvicorn
from fastapi import Query
from system_class import *

app = FastAPI()
clinic_sys = Clinic()

# fast api

@app.get("/", tags=['root'])
async def root() -> dict:
    return {"Pet Shop": "Online"}

@app.post("/RegisterCard",tags=["Register"])
def add_card_information(customer_id :str , money : float) :
    result = clinic_sys.register_card(customer_id ,money)
    return result

@app.post("/RegisterCustomer", tags=["Register"])
async def make_register(data: RegisterRequest):
    register_customer = clinic_sys.register_customer(data)
    return register_customer


@app.post("/RegisterPet", tags=["Register"])
async def make_register_pet(data: RegisterPetRequest):
    register_pet = clinic_sys.register_pet(data)
    return register_pet


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
        req.card_id,
        req.money
    )
    return result

@app.get("/calculate_price/{customer_id}", tags=["Payment"])
def calculate_price(
    customer_id: str,
    use_cp: bool = Query(False),
    use_rw_card: bool = Query(False),
):
    price = clinic_sys.start_calculate_total_price(customer_id, use_cp, use_rw_card)
    return str(price)

@app.get("/pet/{pet_id}/services", tags=["Test & Check"])
def check_pet_services(pet_id: str):
    pet = clinic_sys.get_pet_info(pet_id)
    if not pet:
        return {"status": "fail", "message": "Pet not found"}

    service_history = []
    
    for idx, big_service in enumerate(pet.service):
        current_total_price = big_service.calculate_total_price()
        service_date = big_service.get_date
        if isinstance(service_date, datetime):
            formatted_date = service_date.strftime("%Y-%m-%d %H:%M")
        else:
            formatted_date = str(service_date)

        service_history.append({
            "bill_no": idx + 1,
            "date_created": formatted_date,
            "is_paid": big_service.is_paid,
            "services_inside": big_service.get_service_list(),
            "total_price_to_pay_now": current_total_price 
        })

    return {
        "status": "success(Found)",
        "pet_id": pet.id,
        "pet_name": pet.name,
        "total_service_boxes": len(pet.service),
        "history": service_history
    }

@app.post("/payment/{customer_id}", tags=["Payment"])
def payment(customer_id: str, req: PaymentRequest):
    result = clinic_sys.start_payment(
        customer_id,
        req.payment_type,
        req.card_ID,
        req.use_cp,
        req.use_rw_card,
        req.money
    )
    return (result)

@app.post("/grooming_record" ,  tags = ["Grooming Service"])
def record_grooming_service(customer_id :str ,pet_id : str) :
    result = clinic_sys.record_service(customer_id,pet_id)
    return result

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

@app.get("/rewarsd_card_count" , tags=["rewards card"])
def reward_card_count (customer_id : str) :
    count = clinic_sys.reward_card_count(customer_id)
    return str(count)

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

# ลงทะเบียนลูกค้า
# {
#   "customer_name": "Somsri",
#   "phone_number": "12345",
#   "email": "eiei@gmail.com"
# }

# ลงทะเบียนสัตว์
# {
#   "pet_name": "pingtale",
#   "type_pet": "ping",
#   "species": "tale",
#   "weight": "5",
#   "customer_id": "ลงลูกค้าก่อนค่อยcopyมาใส่",
#   "aggressive": true
# }
