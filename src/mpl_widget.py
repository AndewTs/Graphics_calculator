import numpy as np
import sympy as sp

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QPushButton, QLabel, QComboBox, QSlider, QDoubleSpinBox,
    QGroupBox, QListWidget, QColorDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from src.database_module import DatabaseModule
from src.analysis_module import AnalysisModule
from src.dialogs import AnalysisDialog

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
        
        # Инициализация модулей
        self.analysis_module = AnalysisModule()
        self.database_module = DatabaseModule()
        self.current_functions = []  # Список словарей с информацией о функциях
        self.current_color = "blue"
        self.current_style = "Сплошная"
        self.current_alpha = 1.0
        
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.ax = self.figure.add_subplot(111)
        
        self.status = QLabel("")  # для сообщений об ошибке

        # Создаем основную компоновку
        main_layout = QVBoxLayout()
        
        # ВЕРХНЯЯ ПАНЕЛЬ УПРАВЛЕНИЯ
        control_panel = QWidget()
        control_layout = QVBoxLayout()
        control_panel.setLayout(control_layout)
        
        # Группа для ввода функции
        input_group = QGroupBox("Ввод функции")
        input_layout = QHBoxLayout()
        
        self.input = QLineEdit()
        self.input.setPlaceholderText("Введите функцию от x, например: 1/(x-2) или tan(x)")
        self.btn = QPushButton("Построить")
        self.analyze_btn = QPushButton("Анализ функции")
        
        input_layout.addWidget(self.input)
        input_layout.addWidget(self.btn)
        input_layout.addWidget(self.analyze_btn)
        
        input_group.setLayout(input_layout)
        control_layout.addWidget(input_group)
        
        # Группа для настроек графика
        settings_group = QGroupBox("Настройки графика (для новых функций)")
        settings_layout = QGridLayout()
        
        # Строка 1: Цвет и стиль
        settings_layout.addWidget(QLabel("Цвет:"), 0, 0)
        self.changecolor = QComboBox()
        self.changecolor.addItems(["Синий", "Красный", "Зеленый", "Черный", "Фиолетовый", "Оранжевый"])
        settings_layout.addWidget(self.changecolor, 0, 1)
        
        self.changeColorBtn = QPushButton("Выбрать цвет")
        settings_layout.addWidget(self.changeColorBtn, 0, 2)
        
        settings_layout.addWidget(QLabel("Стиль:"), 0, 3)
        self.changestyle = QComboBox()
        self.changestyle.addItems(["Сплошная", "Пунктирная", "Точка-штрих", "Точечная"])
        settings_layout.addWidget(self.changestyle, 0, 4)
        
        # Строка 2: Прозрачность
        settings_layout.addWidget(QLabel("Прозрачность:"), 1, 0)
        self.chngAlpha = QSlider(Qt.Orientation.Horizontal)
        self.chngAlpha.setMinimum(10)
        self.chngAlpha.setMaximum(100)
        self.chngAlpha.setValue(100)
        self.chngAlpha.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.chngAlpha.setTickInterval(10)
        settings_layout.addWidget(self.chngAlpha, 1, 1, 1, 2)
        
        self.alphaLabel = QLabel("100%")
        settings_layout.addWidget(self.alphaLabel, 1, 3)
        
        settings_group.setLayout(settings_layout)
        control_layout.addWidget(settings_group)
        
        # Группа для диапазонов
        range_group = QGroupBox("Диапазоны осей")
        range_layout = QGridLayout()
        
        # Строка 1: Диапазон X
        range_layout.addWidget(QLabel("X мин:"), 0, 0)
        self.x_min_spin = QDoubleSpinBox()
        self.x_min_spin.setRange(-1000.0, 1000.0)
        self.x_min_spin.setValue(-10.0)
        self.x_min_spin.setSingleStep(1.0)
        range_layout.addWidget(self.x_min_spin, 0, 1)
        
        range_layout.addWidget(QLabel("X макс:"), 0, 2)
        self.x_max_spin = QDoubleSpinBox()
        self.x_max_spin.setRange(-1000.0, 1000.0)
        self.x_max_spin.setValue(10.0)
        self.x_max_spin.setSingleStep(1.0)
        range_layout.addWidget(self.x_max_spin, 0, 3)
        
        range_layout.addWidget(QLabel("Точек:"), 0, 4)
        self.x_points_spin = QDoubleSpinBox()
        self.x_points_spin.setRange(100, 10000)
        self.x_points_spin.setValue(1000)
        self.x_points_spin.setSingleStep(500)
        range_layout.addWidget(self.x_points_spin, 0, 5)
        
        # Строка 2: Диапазон Y
        range_layout.addWidget(QLabel("Y мин:"), 1, 0)
        self.y_min_spin = QDoubleSpinBox()
        self.y_min_spin.setRange(-1000.0, 1000.0)
        self.y_min_spin.setValue(-10.0)
        self.y_min_spin.setSingleStep(1.0)
        range_layout.addWidget(self.y_min_spin, 1, 1)
        
        range_layout.addWidget(QLabel("Y макс:"), 1, 2)
        self.y_max_spin = QDoubleSpinBox()
        self.y_max_spin.setRange(-1000.0, 1000.0)
        self.y_max_spin.setValue(10.0)
        self.y_max_spin.setSingleStep(1.0)
        range_layout.addWidget(self.y_max_spin, 1, 3)
        
        range_group.setLayout(range_layout)
        control_layout.addWidget(range_group)
        
        # Группа для списка функций
        functions_group = QGroupBox("Построенные функции")
        functions_layout = QVBoxLayout()
        
        self.function_list = QListWidget()
        functions_layout.addWidget(self.function_list)
        
        # Кнопки для управления функциями
        function_buttons_layout = QHBoxLayout()
        self.update_style_btn = QPushButton("Обновить стиль")
        self.remove_function_btn = QPushButton("Удалить")
        self.clear_all_btn = QPushButton("Очистить все")
        function_buttons_layout.addWidget(self.update_style_btn)
        function_buttons_layout.addWidget(self.remove_function_btn)
        function_buttons_layout.addWidget(self.clear_all_btn)
        
        functions_layout.addLayout(function_buttons_layout)
        functions_group.setLayout(functions_layout)
        control_layout.addWidget(functions_group)
        
        # Добавляем панель управления в основную компоновку
        main_layout.addWidget(control_panel)
        
        # НИЖНЯЯ ПАНЕЛЬ - ГРАФИК
        graph_panel = QWidget()
        graph_layout = QVBoxLayout()
        graph_panel.setLayout(graph_layout)
        
        graph_layout.addWidget(self.toolbar)
        graph_layout.addWidget(self.canvas)
        graph_layout.addWidget(self.status)
        
        main_layout.addWidget(graph_panel)
        
        self.setLayout(main_layout)

        # Подключение сигналов
        self.btn.clicked.connect(self.on_plot)
        self.analyze_btn.clicked.connect(self.on_analyze)
        self.chngAlpha.valueChanged.connect(self.on_alpha_changed)
        self.changecolor.currentTextChanged.connect(self.on_color_changed)
        self.changestyle.currentTextChanged.connect(self.on_style_changed)
        self.changeColorBtn.clicked.connect(self.on_color_dialog)
        self.x_min_spin.valueChanged.connect(self.redraw_all)
        self.x_max_spin.valueChanged.connect(self.redraw_all)
        self.y_min_spin.valueChanged.connect(self.redraw_all)
        self.y_max_spin.valueChanged.connect(self.redraw_all)
        self.x_points_spin.valueChanged.connect(self.redraw_all)
        self.function_list.itemClicked.connect(self.on_function_selected)
        self.update_style_btn.clicked.connect(self.update_selected_function_style)
        self.remove_function_btn.clicked.connect(self.remove_selected_function)
        self.clear_all_btn.clicked.connect(self.clear_all_functions)
        self.input.returnPressed.connect(self.on_plot)

        # Начальный график
        self.input.setText("x**2")
        self.on_plot()

    def on_alpha_changed(self, value):
        self.alphaLabel.setText(f"{value}%")
        self.current_alpha = value / 100.0

    def on_color_changed(self):
        color_map = {
            "Синий": "blue",
            "Красный": "red", 
            "Зеленый": "green",
            "Черный": "black",
            "Фиолетовый": "purple",
            "Оранжевый": "orange"
        }
        self.current_color = color_map.get(self.changecolor.currentText(), "blue")

    def on_style_changed(self):
        self.current_style = self.changestyle.currentText()

    def on_color_dialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color.name()
            # Обновляем комбобокс, чтобы отображать выбранный цвет
            color_name_map = {
                "blue": "Синий",
                "red": "Красный",
                "green": "Зеленый", 
                "black": "Черный",
                "purple": "Фиолетовый",
                "orange": "Оранжевый"
            }
            color_name = color_name_map.get(color.name(), "Синий")
            index = self.changecolor.findText(color_name)
            if index >= 0:
                self.changecolor.setCurrentIndex(index)

    def on_analyze(self):
        func_text = self.input.text().strip()
        if not func_text:
            QMessageBox.warning(self, "Ошибка", "Введите функцию для анализа")
            return
            
        try:
            analysis_result = self.analysis_module.analyze_function(func_text)
            dialog = AnalysisDialog(self, analysis_result)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка анализа: {str(e)}")

    def on_plot(self):
        expression = self.input.text().strip()
        if not expression:
            return
            
        # Создаем словарь с информацией о функции
        function_info = {
            'expression': expression,
            'color': self.current_color,
            'style': self.current_style,
            'alpha': self.current_alpha
        }
        
        # Добавляем функцию в список
        self.current_functions.append(function_info)
        
        # Добавляем в список отображения
        display_text = f"{expression} (цвет: {self.get_color_name(self.current_color)}, стиль: {self.current_style})"
        self.function_list.addItem(display_text)
        
        # Сохраняем в историю
        self.database_module.save_query(expression)
        
        # Перерисовываем все графики
        self.redraw_all()
        
        # Очищаем поле ввода
        self.input.clear()

    def get_color_name(self, color_value):
        """Преобразует значение цвета в читаемое имя"""
        color_map = {
            "blue": "Синий",
            "red": "Красный", 
            "green": "Зеленый",
            "black": "Черный",
            "purple": "Фиолетовый",
            "orange": "Оранжевый"
        }
        return color_map.get(color_value, color_value)

    def redraw_all(self):
        """Перерисовывает все графики функций"""
        # Очищаем предыдущий график
        self.ax.clear()
        
        x_min = self.x_min_spin.value()
        x_max = self.x_max_spin.value()
        num_points = int(self.x_points_spin.value())
        y_min = self.y_min_spin.value()
        y_max = self.y_max_spin.value()
        
        # Проверка на корректность диапазона
        if x_min >= x_max:
            self.status.setText("Ошибка: X_min должен быть меньше X_max.")
            return

        x = np.linspace(x_min, x_max, num_points)
        
        # Строим все функции
        for i, function_info in enumerate(self.current_functions):
            try:
                expression = function_info['expression']
                
                # Вычисляем значения функции
                y = self.evaluate_function(expression, x)
                
                # Получаем настройки стиля из информации о функции
                color = function_info['color']
                style = function_info['style']
                alpha = function_info['alpha']
                
                # Отрисовываем функцию
                self.plot_single_function(x, y, expression, color, style, alpha, y_min, y_max)
                
            except Exception as e:
                self.status.setText(f"Ошибка при построении {expression}: {e}")
                # Удаляем проблемную функцию из списка
                self.current_functions.pop(i)
                # Удаляем из списка отображения
                self.function_list.takeItem(i)
                return
        
        self.ax.set_title("Графики функций")
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.grid(True)
        self.ax.legend()
        
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.figure.tight_layout()
        self.canvas.draw()
        self.status.setText("")

    def evaluate_function(self, expression, x):
        """Вычисляет значения функции для массива x"""
        def safe_eval(expr, val, safe_dict):
            try:
                return eval(expr, {"x": val, **safe_dict})
            except (ZeroDivisionError, ValueError, OverflowError):
                self.status.setText('Ошибка при построении')
                raise Exception('Знаменатель равен 0')
        
        # Векторизуем safe_eval для применения ко всему массиву x
        vectorized_func = np.vectorize(lambda val: safe_eval(expression, val, _SAFE_DICT))
        return vectorized_func(x)

    def plot_single_function(self, x, y, expression, color, style, alpha, y_min, y_max):
        """Отрисовывает одну функцию на графике"""
        style_map = {
            "Сплошная": '-',
            "Пунктирная": '--',
            "Точка-штрих": '-.',
            "Точечная": ':'
        }

        linestyle = style_map.get(style, '-')

        # Заменяем значения, которые выходят за пределы y_min/y_max, на NaN
        y_clipped = np.copy(y)
        y_clipped[y_clipped < y_min] = np.nan
        y_clipped[y_clipped > y_max] = np.nan
        
        # Разбиваем график на непрерывные сегменты для избежания соединения асимптот
        segments = self._split_into_segments(x, y_clipped)
        
        # Строим каждый сегмент отдельно
        for seg_x, seg_y in segments:
            if len(seg_x) > 1:
                self.ax.plot(seg_x, seg_y, color=color, linestyle=linestyle,
                           linewidth=1.5, alpha=alpha, label=expression)

    def _split_into_segments(self, x_vals, y_vals):
        """Разбивает данные на непрерывные сегменты, разделяя в точках разрыва"""
        segments = []
        current_segment_x = []
        current_segment_y = []
        
        for i in range(len(x_vals)):
            if not np.isnan(y_vals[i]):
                current_segment_x.append(x_vals[i])
                current_segment_y.append(y_vals[i])
            else:
                if current_segment_x:
                    segments.append((current_segment_x, current_segment_y))
                    current_segment_x = []
                    current_segment_y = []
        
        if current_segment_x:
            segments.append((current_segment_x, current_segment_y))
            
        return segments

    def on_function_selected(self, item):
        """При выборе функции из списка обновляем панель управления её параметрами"""
        index = self.function_list.row(item)
        if 0 <= index < len(self.current_functions):
            function_info = self.current_functions[index]
            
            # Устанавливаем параметры выбранной функции в панель управления
            self.input.setText(function_info['expression'])
            
            # Устанавливаем цвет
            color_name = self.get_color_name(function_info['color'])
            color_index = self.changecolor.findText(color_name)
            if color_index >= 0:
                self.changecolor.setCurrentIndex(color_index)
            
            # Устанавливаем стиль
            style_index = self.changestyle.findText(function_info['style'])
            if style_index >= 0:
                self.changestyle.setCurrentIndex(style_index)
            
            # Устанавливаем прозрачность
            alpha_value = int(function_info['alpha'] * 100)
            self.chngAlpha.setValue(alpha_value)
            self.alphaLabel.setText(f"{alpha_value}%")
            
            # Обновляем текущие значения
            self.current_color = function_info['color']
            self.current_style = function_info['style']
            self.current_alpha = function_info['alpha']

    def update_selected_function_style(self):
        """Обновляет стиль выбранной функции"""
        selected_items = self.function_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Выберите функцию для обновления стиля")
            return
            
        for item in selected_items:
            index = self.function_list.row(item)
            if 0 <= index < len(self.current_functions):
                # Обновляем информацию о функции
                self.current_functions[index]['color'] = self.current_color
                self.current_functions[index]['style'] = self.current_style
                self.current_functions[index]['alpha'] = self.current_alpha
                
                # Обновляем отображение в списке
                expression = self.current_functions[index]['expression']
                display_text = f"{expression} (цвет: {self.get_color_name(self.current_color)}, стиль: {self.current_style})"
                item.setText(display_text)
        
        # Перерисовываем графики
        self.redraw_all()

    def remove_selected_function(self):
        """Удаляет выбранную функцию из списка и перерисовывает графики"""
        selected_items = self.function_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Выберите функцию для удаления")
            return
            
        # Удаляем в обратном порядке, чтобы индексы не сдвигались
        for item in reversed(selected_items):
            index = self.function_list.row(item)
            if 0 <= index < len(self.current_functions):
                self.current_functions.pop(index)
                self.function_list.takeItem(index)
        
        # Перерисовываем графики
        self.redraw_all()

    def clear_all_functions(self):
        """Удаляет все функции и очищает график"""
        self.current_functions.clear()
        self.function_list.clear()
        self.redraw_all()

    