import sys,os,timer,encodings

def writesymbols(filename,encoding='utf-8'):
    f=open(filename,'wb')
    try:
        for i in range(55296):
            f.write(bytes(chr(i),encoding=encoding,errors="replace"))
    except LookupError:pass
    finally:f.close()

def main():
    t=timer.Timer()
    try:
        os.mkdir("%s\symbols"%sys.path[0])
    except FileExistsError:pass
    if len(sys.argv)==2:
        filename="%s\symbols\symbol_%s.txt"%(sys.path[0],sys.argv[1])
        print("writing:%s"%filename)
        writesymbols(filename,encoding=sys.argv[1])
    else:
        for coding in encodings.aliases.aliases.values():
            filename="%s\symbols\symbol_%s.txt"%(sys.path[0],coding)
            print("writing:%s"%filename)
            writesymbols(filename,encoding=coding)
        t.printtime()

if __name__=="__main__":main()