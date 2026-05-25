from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QPainterPath
from PyQt6.QtCore import Qt, QRectF

def get_icon(name, color="#94a3b8"):
    """
    Generates a crisp, monochromatic SVG-like icon using native QPainter.
    Matches standard 'Feather' or 'Lucide' styling (24x24, 2px stroke, round caps).
    """
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    pen = QPen(QColor(color))
    pen.setWidth(2)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    
    if name == "dashboard":
        painter.drawRect(3, 3, 7, 9)
        painter.drawRect(14, 3, 7, 5)
        painter.drawRect(14, 12, 7, 9)
        painter.drawRect(3, 16, 7, 5)
        
    elif name == "security":
        path = QPainterPath()
        path.moveTo(12, 2)
        path.lineTo(20, 5)
        path.lineTo(20, 11)
        path.cubicTo(20, 18, 12, 22, 12, 22)
        path.cubicTo(4, 18, 4, 11, 4, 11)
        path.lineTo(4, 5)
        path.closeSubpath()
        painter.drawPath(path)
        
    elif name == "analytics":
        painter.drawLine(3, 21, 21, 21)
        painter.drawLine(3, 21, 3, 3)
        path = QPainterPath()
        path.moveTo(3, 15)
        path.lineTo(9, 9)
        path.lineTo(15, 13)
        path.lineTo(21, 5)
        painter.drawPath(path)
        
    elif name == "twin":
        painter.drawEllipse(6, 6, 8, 8)
        painter.drawEllipse(10, 10, 8, 8)
        
    elif name == "settings":
        painter.drawEllipse(9, 9, 6, 6)
        painter.drawLine(12, 2, 12, 5)
        painter.drawLine(12, 19, 12, 22)
        painter.drawLine(2, 12, 5, 12)
        painter.drawLine(19, 12, 22, 12)
        painter.drawLine(4, 4, 6, 6)
        painter.drawLine(18, 18, 20, 20)
        painter.drawLine(4, 20, 6, 18)
        painter.drawLine(18, 6, 20, 4)
        
    elif name == "cpu":
        painter.drawRect(4, 4, 16, 16)
        painter.drawRect(8, 8, 8, 8)
        for i in range(3):
            painter.drawLine(2, 8 + i*4, 4, 8 + i*4)
            painter.drawLine(20, 8 + i*4, 22, 8 + i*4)
            painter.drawLine(8 + i*4, 2, 8 + i*4, 4)
            painter.drawLine(8 + i*4, 20, 8 + i*4, 22)
            
    elif name == "ram":
        painter.drawRect(2, 6, 20, 12)
        for i in range(4):
            painter.drawLine(5 + i*4, 6, 5 + i*4, 9)
            painter.drawLine(6 + i*4, 18, 6 + i*4, 15)
            
    elif name == "health":
        path = QPainterPath()
        path.moveTo(12, 21)
        path.cubicTo(12, 21, 3, 15, 3, 8)
        path.cubicTo(3, 5, 5.5, 3, 8, 3)
        path.cubicTo(10, 3, 11.5, 4, 12, 5.5)
        path.cubicTo(12.5, 4, 14, 3, 16, 3)
        path.cubicTo(18.5, 3, 21, 5, 21, 8)
        path.cubicTo(21, 15, 12, 21, 12, 21)
        painter.drawPath(path)
        
    elif name == "alert":
        path = QPainterPath()
        path.moveTo(12, 2)
        path.lineTo(2, 20)
        path.lineTo(22, 20)
        path.closeSubpath()
        painter.drawPath(path)
        painter.drawLine(12, 9, 12, 15)
        painter.drawLine(12, 17, 12, 17.5)
        
    elif name == "check":
        painter.drawLine(4, 12, 9, 17)
        painter.drawLine(9, 17, 20, 6)

    painter.end()
    return QIcon(pixmap)
