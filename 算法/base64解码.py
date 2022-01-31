import binascii
s = binascii.a2b_base64(input())
with open('f','wb') as f:
    f.write(s)
