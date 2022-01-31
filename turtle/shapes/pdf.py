from reportlab.graphics.shapes import Drawing,PolyLine
from reportlab.graphics import renderPDF
from turtle import *
import 房子

delay(0)
penup()
goto(400,300)
begin_poly()
房子.draw(60)
end_poly()
d=Drawing(window_width(),window_height())
s=get_poly()
print(s)
p=PolyLine(s)
d.add(p)

renderPDF.drawToFile(d, '房子.pdf')
