from pydantic import BaseModel
from enum import StrEnum

class DeterministicPreTTSPreprocessingResponse(BaseModel):
    formatted_text: str
    replaced_entities: list[tuple[str, str, str]]

class EntityType(StrEnum):
    DATE = "date"
    TIME = "time"
    CURRENCY = "currency"
    NUM_WITH_WORDS = "num_with_words"
    PHONE_NUMBERS = "phone_numbers"
    DECIMAL = "decimal"
    ORDINAL = "ordinal"
    VEHICLE_NUMBER = "vehicle_number"
    ALPHANUMERICS = "alphanumerics"
    NON_COMMA_NUMBERS = "non_comma_numbers"
    ACRONYMS_READ_OUT = "acronyms_read_out"
