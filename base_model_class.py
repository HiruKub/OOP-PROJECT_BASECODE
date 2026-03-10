from pydantic import BaseModel
from typing import Optional
# Base Model


class RegisterRequest(BaseModel):
    customer_name: str
    phone_number: str
    email: str
    customer_tier : str


class RegisterPetRequest(BaseModel):
    pet_name: str
    type_pet: str
    species: str
    weight: str
    customer_id: str
    aggressive: bool = False


class AdmitRequest(BaseModel):
    doctor_id: str
    petID: str
    type_service: str = "Hotel"


class TreatmentRequest(BaseModel):
    owner_id: str
    doctor_id: str
    petID: str
    symptom: list[str] = []
    medicine: list[str] = []
    vaccine: list[str] = []
    price: float = 0.0
    should_admit: bool = False


class ReservationRequest(BaseModel):
    customer_id: str
    pet_id: str
    service_type: str
    datetime_start_str: str
    datetime_end_str: Optional[str] = None
    room_type: Optional[str] = None
    payment_method: Optional[str] = None
    card_id: Optional[str] = None


class PaymentRequest(BaseModel):
    payment_type: str
    card_ID: str | None = None
    use_cp: bool = False
    use_rw_card: bool = False
    money: float | None = None
