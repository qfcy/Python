import sys,qrcode

SYMBOLS=" ▀▄█"
REVERSED_SYMBOLS="█▄▀ "

def show_qrcode(matrix,symbols=SYMBOLS,file=None,fill=0):
    if file is None:file=sys.stdout
    empty_line=[fill]*len(matrix[0])
    for i in range(0,len(matrix),2):
        upper_line=matrix[i]
        lower_line=matrix[i+1] if i+1<len(matrix) else empty_line
        for upper,lower in zip(upper_line,lower_line):
            index = upper
            index |= lower << 1
            print(symbols[index],end="",file=file)
        print(file=file)

def make_qrcode(data):
    qr = qrcode.QRCode(
        version=1,  # 1到40的整数, 定义二维码的大小
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 纠错级别
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.get_matrix()

def main():
    while True:
        data=input("输入数据: ").strip()
        qr_code=make_qrcode(data)
        show_qrcode(qr_code,symbols=REVERSED_SYMBOLS,fill=1)
        #with open("output.txt","w",encoding="utf-8") as f:
        #    show_qrcode(qr_code,file=f)

if __name__=="__main__":main()
