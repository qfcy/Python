import os
for file in os.listdir('.'):
    if file.lower().endswith('.bat'):
        with open(file,'rb') as f:
            data=f.read()
        data=data.replace(b'a:',b'c:').replace(b'A:',b'C:')
        with open(file,'wb') as f:
            f.write(data)
        
