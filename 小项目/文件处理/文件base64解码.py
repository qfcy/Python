import binascii
s = binascii.a2b_base64(input())
with open('result','wb') as f:
    f.write(s)
