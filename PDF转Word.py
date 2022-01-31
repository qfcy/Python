from pdf2docx import Converter
from os.path import normpath
try:
    exec('import pip._vendor.colorama as colorama') # exec:避免增大pyinstaller文件体积
    colorama.init() # 支持彩色文字显示
except ImportError:pass

pdf_file = normpath(input('源pdf文件: ')).strip('"').strip()
default=pdf_file.lower().replace('.pdf','_转换.docx')
docx_file = \
    normpath(input('目标docx文件 ( 默认 %s): '%default) or default
             ).strip('"').strip()\

# convert pdf to docx
cv = Converter(pdf_file)
cv.convert(docx_file, start=0, end=None)
cv.close()
