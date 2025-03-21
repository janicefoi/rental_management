import bcrypt

password = "Janiceadmin@2014"
hashed_password = "$2b$12$x9QYSzS8JyU0Z19ay2.gL.JbmdrZlGmrgvkuqRm9x.2nT12Hh0cG2"

if bcrypt.checkpw(password.encode(), hashed_password.encode()):
    print("✅ Password matches!")
else:
    print("❌ Password does NOT match!")
