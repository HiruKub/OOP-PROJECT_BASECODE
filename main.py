from system_class import *
from fastmcp import FastMCP

mcp = FastMCP("Demo")
clinic_sys = Clinic()

# fast api

@mcp.tool()
def root() -> dict:
    """Start Program"""
    return {"Pet Shop": "Online"}

@mcp.tool()
def add_card_information(customer_id :str , money : float) :
    """add card information after register customer"""
    result = clinic_sys.register_card(customer_id ,money)
    return result

@mcp.tool()
def make_register(data: RegisterRequest):
    """register customer information"""
    register_customer = clinic_sys.register_customer(data)
    return register_customer


@mcp.tool()
def make_register_pet(data: RegisterPetRequest):
    """register pet information after register customer"""
    register_pet = clinic_sys.register_pet(data)
    return register_pet


@mcp.tool()
def make_reservation(req: ReservationRequest):
    """make an reservation by customer_id and pet_id"""
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

@mcp.tool()
def get_all_reservations(customer_id: str):
    """show detail of all reservation that customer have"""
    result = clinic_sys.get_customer_reservations(customer_id)
    return result

@mcp.tool()
def cancel_reservation(customer_id: str, pet_id: str, reservation_id: str):
    """cancel reservation after make reservation"""
    result = clinic_sys.cancel_reservation(customer_id, pet_id, reservation_id)
    return result

@mcp.tool()
def calculate_price(
    customer_id: str,
    use_cp: bool = False,
    use_rw_card: bool = False
):
    """calculate total price which already use discount by customer_id after make service"""
    price = clinic_sys.start_calculate_total_price(customer_id, use_cp, use_rw_card)
    return str(price)

@mcp.tool()
def check_pet_services(pet_id: str):
    """check all service and price but not use discount yet"""
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

@mcp.tool()
def payment(customer_id: str, req: PaymentRequest):
    """start to pay after make service"""
    result = clinic_sys.start_payment(
        customer_id,
        req.payment_type,
        req.card_ID,
        req.use_cp,
        req.use_rw_card,
        req.money
    )
    return (result)

@mcp.tool()
def record_grooming_service(customer_id :str ,pet_id : str) :
    """make grooming service after reservation or walkin"""
    result = clinic_sys.record_service(customer_id,pet_id)
    return result

@mcp.tool()
def add_medical_treatment(data: TreatmentRequest):
    """make medical treatment(after medical reservation) you will role as doctor"""
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

@mcp.tool()
async def get_medical_treatments():
    """get all medical treatment after make medical"""
    return {
        "Data": clinic_sys.get_all_medical_record()
    }


@mcp.tool()
async def add_admit(data: AdmitRequest):
    """admit pet to room (hotel service) after make an medical service"""
    admit = clinic_sys.start_pet_admit(data)
    return admit


@mcp.tool()
def show_all_point_in_account(customer_id: str):
    """show all point in member by customer_id"""
    result = clinic_sys.show_all_point_in_member(customer_id)
    return result


@mcp.tool()
def exchage_coupon(customer_id: str):
    """exchange point to coupon"""
    result = clinic_sys.point_to_coupon(customer_id)
    return result

@mcp.tool()
def reward_card_count (customer_id : str) :
    """show count for use service in our clinic that collect in rewards card"""
    count = clinic_sys.reward_card_count(customer_id)
    return str(count)

# def main():
#     print("Hello from oop-project-basecode!")


# if __name__ == "__main__":
#     main()

if __name__ == "__main__":
    mcp.run()

# docker run -it --rm pet-clinic-mcp
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
