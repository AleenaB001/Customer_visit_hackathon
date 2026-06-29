from config import SN_INSTANCE, SN_USERNAME, SN_PASSWORD
from config import PROJECT_ID, LOCATION


print("INSTANCE :", repr(SN_INSTANCE))
print("USERNAME :", repr(SN_USERNAME))
print("PASSWORD :", repr(SN_PASSWORD))

from config import SN_PASSWORD

from config import PROJECT_ID, LOCATION

print(PROJECT_ID)
print(LOCATION)

print(repr(SN_PASSWORD))
print([ord(c) for c in SN_PASSWORD[:5]])