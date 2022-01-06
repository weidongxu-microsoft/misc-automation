import pyotp

totp = pyotp.TOTP('secret')
print(totp.now())
