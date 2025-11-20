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
    def __init__(self, parent=None):  # Исправлено: изменён init на __init__
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
        x = np.linspace(-2 * np.pi, 2 * np.pi, 400)
        y = np.sin(x)
        # Получаем текущее значение прозрачности из ползунка
        alpha_value = self.chngAlpha.value() / 100.0 
        self._draw(x, y, title="Исходный график: sin(x)", alpha=alpha_value)

    def _draw(self, x, y, lnwdth=1.5, title="", alpha=1.0): # Добавляем параметр alpha
        chngdstyle = self.changestyle.currentText()
        chngdcolor = self.changecolor.currentText()

        linestyles = {'Сплошная': 'solid', 'Прерывистая': 'dashed', 'Точка с запятой': 'dashdot'}
        colors = {'Черный': 'black', 'Красный': 'red', 'Зеленый': 'green'}
        
        self.figure.clear()  # Очищаем предыдущий график
        ax = self.figure.add_subplot(111)
        
        # Строим график с выбранными параметрами
        ax.plot(x, y, 
                color=colors.get(chngdcolor, 'black'), 
                linestyle=linestyles.get(chngdstyle, 'solid'),
                linewidth=lnwdth,
                alpha=alpha)  
        
        ax.set_title(title)
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")
        ax.grid(True)
        self.canvas.draw()  # Обновляем плоскость

    def on_plot(self):
        expression_str = self.input.text()
        if not expression_str:
            self.plot_default() # Если поле пустое, показываем график по умолчанию
            return
        
        # Определяем диапазон для x. Можно сделать его настраиваемым.
        x = np.linspace(-10, 10, 400) 

        try:
            # Создаем локальное пространство имен для eval, включая x
            local_dict = {'x': x}
            # Объединяем безопасные функции с локальными переменными
            plotting_scope = {**_SAFE_DICT, **local_dict}
            
            # Безопасное вычисление выражения
            y = eval(expression_str, {"__builtins__": None}, plotting_scope)
            
            if not isinstance(y, (np.ndarray, list)):
                raise ValueError("Выражение должно возвращать массив значений.")

            # Получаем текущее значение прозрачности из ползунка
            alpha_value = self.chngAlpha.value() / 100.0

            # Вызываем отрисовку
            self._draw(x, y, title=f"График: {expression_str}", alpha=alpha_value)
            self.status.setText("") # Очистить сообщение об ошибке, если всё успешно
        except (SyntaxError, NameError, TypeError, ValueError) as e:
            self.status.setText(f"Ошибка в выражении: {e}")
        except Exception as e:
            self.status.setText(f"Неизвестная ошибка: {e}")
        if '/0' in expression_str:
            self.status.setText(f"Деление на 0")
            self.plot_default() # Если делим на 0, показываем график по умолчанию
            return

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Построитель графиков функций")        
        self.mpl_widget = MplWidget()
        self.setCentralWidget(self.mpl_widget)

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
