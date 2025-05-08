import sys,os,encodings

def writesymbols(filename,encoding='utf-8'):
    f=open(filename,'wb')
    try:
        for i in range(0x110000):
            f.write(bytes(chr(i),encoding=encoding,errors="replace"))
    except LookupError:pass
    # except UnicodeEncodeError:pass
    finally:f.close()

def main():
    try:
        os.mkdir("%s\symbols"%sys.path[0])
    except FileExistsError:pass
    if len(sys.argv)==2:
        filename="%s\symbols\symbol_%s.txt"%(sys.path[0],sys.argv[1])
        print("writing:%s"%filename)
        writesymbols(filename,encoding=sys.argv[1])
    else:
        codings = []
        for coding in ["utf-8"]+list(encodings.aliases.aliases.values()):
            if coding in codings:continue
            filename="%s\symbols\symbol_%s.txt"%(sys.path[0],coding)
            print("writing:%s"%filename)
            writesymbols(filename,encoding=coding)
            codings.append(coding)

if __name__=="__main__":main()