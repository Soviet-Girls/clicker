import re

def is_ton_address(address):
 return bool(re.match(r'^(0|-1):([ a-f0-9]{64}|[A-F0-9]{64})$', address))

# Пример использования
address = 'UQBLE_NwghO1xylZkkLfERWI5du0q5iZZ_9-v4gM-zlanAmf'
print(is_ton_address(address))