import sys,os,ctypes
import pefile

def map_file_and_checksum(filename):
    imagehlp = ctypes.windll.imagehlp
    ULONG = ctypes.c_ulong
    LPSTR = ctypes.c_char_p
    LPDWORD = ctypes.POINTER(ctypes.c_ulong)

    MapFileAndCheckSum = imagehlp.MapFileAndCheckSumA
    MapFileAndCheckSum.argtypes = [LPSTR, LPDWORD, LPDWORD]
    MapFileAndCheckSum.restype = ULONG

    header_sum = ULONG()
    new_checksum = ULONG()

    result = MapFileAndCheckSum(filename.encode('ansi'), ctypes.byref(header_sum), ctypes.byref(new_checksum))
    if result == 0:
        return header_sum.value, new_checksum.value
    else:
        raise ctypes.WinError(result)

def scan_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'rb') as f:
                    data = f.read(2)
                    if data == b'MZ':
                        try:
                            pe = pefile.PE(filepath)
                            if pe.OPTIONAL_HEADER.CheckSum == 0:
                                print(f"File {filepath} has no checksum")
                                continue
                            header_sum, new_checksum = map_file_and_checksum(filepath)
                            if pe.OPTIONAL_HEADER.CheckSum != new_checksum:
                                print(f"""Checksum mismatch: {filepath} \
(original: {pe.OPTIONAL_HEADER.CheckSum} calculated: {new_checksum})""")
                            else:
                                print(f"Checksum match: {filepath}")
                        except Exception as e:
                            print(f"Failed to process {filepath}: {e}")
            except Exception as err:
                print(f"Failed to read {filepath}: {err} ({type(err).__name__})")

def print_help():
    print(f"Usage: python {sys.argv[0]} <directory>")
    print(f"Example: python {sys.argv[0]} C:\\Windows")

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print_help()
    else:
        directory = sys.argv[1]
        if not os.path.isdir(directory):
            print(f"{directory} is not a valid directory.")
        else:
            scan_directory(directory)