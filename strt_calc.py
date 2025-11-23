import sys
import numpy as np
import sympy as sp # Символьный анализ может быть полезен, но не используется напрямую для определения асимптот в этой версии.

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QComboBox, QSlider, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# Безопасное пространство имён для eval - расширено для большей функциональности
_SAFE_DICT = {
    'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'cot': lambda x: 1/np.tan(x),
    'arcsin': np.arcsin, 'arccos': np.arccos, 'arctan': np.arctan,
    'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
    'exp': np.exp, 'log': np.log, 'log10': np.log10, 'log2': np.log2,
    'sqrt': np.sqrt, 'cbrt': np.cbrt, # Кубический корень
    'abs': np.abs, 'pi': np.pi, 'e': np.e,
    'floor': np.floor, 'ceil': np.ceil, 'round': np.round,
    'sign': np.sign,
    'np': np, # Доступ к модулю numpy
}

class MplWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 4))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ax = self.figure.add_subplot(111) # Добавляем subplot сразу

        # Поле ввода функции
        self.input = QLineEdit()
        self.input.setPlaceholderText("Введите функцию от x, например: 1/(x-2) или tan(x)")
        self.btn = QPushButton("Построить")
        self.status = QLabel("")  # для сообщений об ошибке

        # Выбор цвета
        self.changecolor = QComboBox()
        self.changecolor.addItem("Синий")
        self.changecolor.addItem("Красный")
        self.changecolor.addItem("Зеленый")
        self.changecolor.addItem("Черный") # Добавил Черный

        # Выбор стиля линии
        self.changestyle = QComboBox()
        self.changestyle.addItem("Сплошная")
        self.changestyle.addItem("Пунктирная")
        self.changestyle.addItem("Точка-штрих")
        self.changestyle.addItem("Точечная") # Добавил новый стиль

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

        # Подключение сигналов
        self.btn.clicked.connect(self.on_plot)
        self.chngAlpha.valueChanged.connect(self.on_plot)
        self.changecolor.currentTextChanged.connect(self.on_plot)
        self.changestyle.currentTextChanged.connect(self.on_plot)

        # Начальный график
        self.input.setText("sin(x)")
        self.on_plot() # Вызываем построение при запуске для заданной функции

    def on_plot(self):
        expression = self.input.text()
        x_min = -10
        x_max = 10
        num_points = 1000
        
        x = np.linspace(x_min, x_max, num_points)
        y = np.zeros_like(x, dtype=float)
        
        try:
            # Используем vectorize для более быстрого вычисления функции для всего массива
            # Создаем "безопасную" функцию, которая возвращает NaN при ошибках
            def safe_eval(expr, val, safe_dict):
                try:
                    return eval(expr, {"x": val, **safe_dict})
                except (ZeroDivisionError, ValueError, OverflowError): # Обрабатываем типичные ошибки
                    return np.nan
            
            # Векторизуем safe_eval для применения ко всему массиву x
            vectorized_func = np.vectorize(lambda val: safe_eval(expression, val, _SAFE_DICT))
            y = vectorized_func(x)

            self.status.setText("") # Очищаем статус об ошибке, если успешно
            
        except Exception as e:
            self.status.setText(f"Ошибка в выражении или при вычислении: {e}")
            return
        
        alpha_value = self.chngAlpha.value() / 100.0 # Получаем значение для alphas
        
        # Передаем y_min и y_max в функцию отрисовки для установки пределов y
        self._draw(x, y, 
                   title=f"График: {expression}", 
                   alpha=alpha_value,
                   y_min=-10, y_max=10)

    def _draw(self, x, y, lnwdth=1.5, title="", alpha=1.0, y_min=-10, y_max=10):
        # Очищаем предыдущий график
        self.ax.clear()

        chngdstyle_map = {
            "Сплошная": '-',
            "Пунктирная": '--',
            "Точка-штрих": '-.',
            "Точечная": ':'
        }
        chngdcolor_map = {
            "Синий": 'blue',
            "Красный": 'red',
            "Зеленый": 'green',
            "Черный": 'black'
        }

        chngdstyle = chngdstyle_map.get(self.changestyle.currentText(), '-')
        chngdcolor = chngdcolor_map.get(self.changecolor.currentText(), 'blue')

        # Заменяем значения, которые выходят за пределы y_min/y_max, на NaN.
        y_clipped = np.copy(y)
        y_clipped[y_clipped < y_min] = np.nan
        y_clipped[y_clipped > y_max] = np.nan
        
        # Теперь рисуем график с использованием np.nan
        self.ax.plot(x, y_clipped, color=chngdcolor, linestyle=chngdstyle,
                     linewidth=lnwdth, alpha=alpha, label=title)

        self.ax.set_title(title)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.grid(True)
        self.ax.legend()
        
        self.ax.set_xlim(x[0], x[-1])
        self.ax.set_ylim(y_min, y_max) # Устанавливаем пределы Y
        self.figure.tight_layout() # Автоматическая настройка полей
        self.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Построитель графиков функций")
        self.mpl_widget = MplWidget()
        self.setCentralWidget(self.mpl_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
