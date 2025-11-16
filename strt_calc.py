import sys
#import math
import numpy as np
import sympy as sp

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QComboBox
)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# попытаться заменить
# безопасное пространство имён для eval
_SAFE_DICT = {
    'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
    'arcsin': np.arcsin, 'arccos': np.arccos, 'arctan': np.arctan,
    'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
    'exp': np.exp, 'log': np.log, 'log10': np.log10, 'sqrt': np.sqrt,
    'abs': np.abs, 'pi': np.pi, 'e': np.e,
    'floor': np.floor, 'ceil': np.ceil,
    'np': np,
}

class MplWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # поле ввода и кнопка
        self.input = QLineEdit()
        self.input.setPlaceholderText("Введите функцию от x, например: sin(x) или x**2")
        self.btn = QPushButton("Построить")
        self.status = QLabel("")  # для сообщений об ошибке
        self.changecolor = QComboBox()  # выбираем цвет
        self.changestyle = QComboBox()  # выбираем стиль

        self.changecolor.addItem("blue")  # пока так, т.к передаем напрямую в  plot
        self.changecolor.addItem("red")
        self.changecolor.addItem("green")

        self.changestyle.addItem("solid")
        self.changestyle.addItem("dashed")
        self.changestyle.addItem("dashdot")

        controls = QHBoxLayout()
        controls.addWidget(self.input)
        controls.addWidget(self.btn)
        controls.addWidget(self.changecolor)
        controls.addWidget(self.changestyle)
        

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addLayout(controls)
        layout.addWidget(self.canvas)
        layout.addWidget(self.status)
        self.setLayout(layout)

        self.btn.clicked.connect(self.on_plot)

        # начальный график
        self.plot_default()

    def plot_default(self):
        x = np.linspace(-2*10, 2*10, 400)
        y = np.sin(x)
        self._draw(x, y, title="Исходный график: sin(x)")

    def _draw(self, x, y, lnstl='dashdot', lnwdth=1.5, clr='black', title=""):
        #тоже бы убрать отсюда
        chngdstyle = self.changestyle.currentText()
        chngdcolor = self.changecolor.currentText()

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(x, y, linestyle=chngdstyle, linewidth=lnwdth, color=chngdcolor)
        ax.grid(True)
        ax.set_title(title)
        self.canvas.draw()
        self.status.setText("")

    def on_plot(self):
        expr = self.input.text().strip()
        if not expr:
            self.status.setText("Введите выражение функции.")
            return

        # создать x и попытаться вычислить y = expr
        x = np.linspace(-100, 100, 800)
        local_dict = {'x': x}
        local_dict.update(_SAFE_DICT)

        try:
            # запрещаем доступ к глобальным именам через eval(..., {"__builtins__": None}, ...)
            y = eval(expr, {"__builtins__": None}, local_dict)
            # привести к numpy array для корректного построения
            y = np.array(y, dtype=float)
            if y.shape != x.shape and y.size not in (x.size,):
                # попытка векторизовать скаляр результата
                if y.size == 1:
                    y = np.full_like(x, float(y))
                else:
                    raise ValueError("Размер y не совпадает с x")
            self._draw(x, y, title=f"y = {expr}")
        except Exception as e:
            self.status.setText(f"Ошибка: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matplotlib в PyQt6 — ввод функции")
        widget = MplWidget(self)
        self.setCentralWidget(widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
