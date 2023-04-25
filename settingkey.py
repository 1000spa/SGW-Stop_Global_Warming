import string
import random

def randomstring(l:int):
    string_pool = string.ascii_uppercase + string.digits
    result = "" 
    for i in range(l) :
        result += random.choice(string_pool) # 랜덤한 문자열 하나 선택
    return result