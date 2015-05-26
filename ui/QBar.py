from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QFont, QPen


class QBar(QWidget):
    """
    Custom QWidget that draws a bar.
    """

    def __init__(self, value, maximum,
                 bar_color=Qt.gray, normal_color=Qt.green, exceed_color=Qt.red):
        """
        :param value: current value of bar
        :param maximum: the value of full bar
        :param bar_color: color of unfilled bar
        :param normal_color: bar fill color
        :param exceed_color: bar fill color if value exceed maximum
        """

        super().__init__()

        self.setMinimumSize(1, 30)
        self.value = value
        self.max = maximum
        self.bar_color = bar_color
        self.normal_color = normal_color
        self.exceed_color = exceed_color

    def paintEvent(self, e):

        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        # Calculate the size of widget
        size = self.size()
        w = size.width()
        h = size.height()

        # Color the bar
        if self.value <= self.max:
            # Color the part till break point
            break_point = int(((w / self.max) * self.value))
            qp.setPen(Qt.white)
            qp.setBrush(self.normal_color)
            qp.drawRect(0, 0, break_point, h)
            # Color the rest of the bar with bar color
            qp.setBrush(self.bar_color)
            qp.drawRect(break_point, 0, w, h)
        else:
            # Color the part till break point
            break_point = int(((w / self.value) * self.max))
            qp.setPen(Qt.white)
            qp.setBrush(self.normal_color)
            qp.drawRect(0, 0, break_point, h)
            # Color the exceeding part
            qp.setBrush(self.exceed_color)
            qp.drawRect(break_point, 0, w, h)

        # Draw container rectangle
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        qp.setPen(pen)
        qp.setBrush(Qt.NoBrush)
        qp.drawRect(0, 0, w-1, h-1)

        # Print the maximum value at the center
        font = QFont('Serif', 7, QFont.Light)
        qp.setFont(font)
        qp.drawText(w/2, h/2, '{} / {}'.format(self.value, self.max))
