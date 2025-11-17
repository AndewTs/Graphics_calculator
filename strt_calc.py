import sys
import numpy as np
# sympy по-прежнему импортирован, но не используется в этом фрагменте
import sympy as sp 

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QComboBox, QSlider
)
from PyQt6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# Безопасное пространство имён для eval
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

        # Поле ввода и кнопка
        self.input = QLineEdit()
        self.input.setPlaceholderText("Введите функцию от x, например: sin(x) или x**2")
        self.btn = QPushButton("Построить")
        self.status = QLabel("")  # для сообщений об ошибке

        self.changecolor = QComboBox()  # выбираем цвет
        self.changecolor.addItem("Черный")
        self.changecolor.addItem("Красный")
        self.changecolor.addItem("Зеленый")

        self.changestyle = QComboBox()  # выбираем стиль
        self.changestyle.addItem("Сплошная")
        self.changestyle.addItem("Прерывистая")
        self.changestyle.addItem("Точка с запятой")

        # Ползунок для регулирования прозрачности 
        self.chngAlpha = QSlider(Qt.Orientation.Horizontal) 
        self.chngAlpha.setMinimum(0)
        self.chngAlpha.setMaximum(100) # Максимум 100 для удобства (0.00-1.00)
        self.chngAlpha.setValue(100) # Начальное значение - полностью непрозрачный (1.0)
        self.chngAlpha.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.chngAlpha.setTickInterval(10)
        self.alphaLabel = QLabel("Прозрачность:")

        alphaLayout = QHBoxLayout()
        alphaLayout.addWidget(self.alphaLabel)
        alphaLayout.addWidget(self.chngAlpha)

        controls = QHBoxLayout()
        controls.addWidget(self.input)
        controls.addWidget(self.btn)
        controls.addWidget(self.changecolor)
        controls.addWidget(self.changestyle)
        
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addLayout(controls)
        layout.addLayout(alphaLayout) 
        layout.addWidget(self.canvas)
        layout.addWidget(self.status)
        self.setLayout(layout)

        self.btn.clicked.connect(self.on_plot)
        # Подключаем сигнал ползунка к on_plot для обновления графика
        self.chngAlpha.valueChanged.connect(self.on_plot) 
        self.changecolor.currentTextChanged.connect(self.on_plot) # Обновление при смене цвета
        self.changestyle.currentTextChanged.connect(self.on_plot) # Обновление при смене стиля

        # Начальный график
        self.plot_default()

    def plot_default(self):
        x = np.linspace(-2*10, 2*10, 400)
        y = np.sin(x)
        # Получаем текущее значение прозрачности из ползунка
        alpha_value = self.chngAlpha.value() / 100.0 
        self._draw(x, y, title="Исходный график: sin(x)", alpha=alpha_value)

    def _draw(self, x, y, lnwdth=1.5, title="", alpha=1.0): # Добавляем параметр alpha
        chngdstyle = self.changestyle.currentText()
        chngdcolor = self.changecolor.currentText()

        linestyles = {'Сплошная': 'solid', 'Прерывистая': 'dashed', 'Точка с запятой': 'dashdot'}
        colors = {'Черный': 'black', 'Красный': 'red', 'Зеленый': 'green'}

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        # Передаем alpha в функцию plot
        ax.plot(x, y, linestyle=linestyles[chngdstyle], linewidth=lnwdth, color=colors[chngdcolor], alpha=alpha) 
        ax.grid(True)
        ax.set_title(title)
        self.canvas.draw()
        self.status.setText("")

    def on_plot(self):
        expr = self.input.text().strip()
        if not expr:
            # Если поле ввода пусто, но вызывается on_plot (например, от ползунка)
            # и предыдущий график был, мы хотим его перерисовать с новой прозрачностью.
            # Если графика еще нет или была ошибка, то просто выходим.
            if hasattr(self, '_last_x') and hasattr(self, '_last_y'):
                alpha_value = self.chngAlpha.value() / 100.0
                self._draw(self._last_x, self._last_y, title=self._last_title, alpha=alpha_value)
            else:
                self.status.setText("Введите выражение функции.")
            return

        x = np.linspace(-100, 100, 800)
        local_dict = {'x': x}
        local_dict.update(_SAFE_DICT)

        alpha_value = self.chngAlpha.value() / 100.0 # Получаем значение из ползунка

        try:
            # Вычисление выражения; используем eval в ограниченном окружении
            y = eval(expr, {"__builtins__": None}, local_dict)

            # Проверка, что y - это числовой массив
            if not isinstance(y, (np.ndarray, list, tuple)):
                self.status.setText("Выражение должно возвращать числовой массив.")
                return
            
            # Сохраняем последние данные для перерисовки при изменении ползунка
            self._last_x = x
            self._last_y = y
            self._last_title = f"График: {expr}"

            self._draw(x, y, title=self._last_title, alpha=alpha_value)
        except Exception as e:
            self.status.setText(f"Ошибка в выражении: {e}")
            # Очищаем сохраненные данные, если была ошибка
            if hasattr(self, '_last_x'):
                del self._last_x
            if hasattr(self, '_last_y'):
                del self._last_y
            if hasattr(self, '_last_title'):
                del self._last_title

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Графический калькулятор")
        self.setGeometry(100, 100, 800, 600)

        self.mplwidget = MplWidget()
        self.setCentralWidget(self.mplwidget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
