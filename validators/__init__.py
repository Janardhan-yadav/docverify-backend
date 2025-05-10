from .hall_ticket import validate as hall_ticket_validate
from .rank_card import validate as rank_card_validate
from .allotment_order import validate as allotment_order_validate
from .tenth_memo import validate as tenth_memo_validate
from .caste_certificate import validate as caste_certificate_validate
from .income_certificate import validate as income_certificate_validate

hall_ticket = type('Validator', (), {'validate': hall_ticket_validate})
rank_card = type('Validator', (), {'validate': rank_card_validate})
allotment_order = type('Validator', (), {'validate': allotment_order_validate})
tenth_memo = type('Validator', (), {'validate': tenth_memo_validate})
caste_certificate = type('Validator', (), {'validate': caste_certificate_validate})
income_certificate = type('Validator', (), {'validate': income_certificate_validate})