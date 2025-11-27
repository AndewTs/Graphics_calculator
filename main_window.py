from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QDialog
)
from PyQt6.QtGui import QAction

from mpl_widget import MplWidget
from dialogs import HistoryDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Графический калькулятор V.1")
        self.setGeometry(100, 100, 1200, 800)
        
        self.mpl_widget = MplWidget()
        self.setCentralWidget(self.mpl_widget)
        
        # Создание меню
        self.create_menu()
        
    def create_menu(self):
        menubar = self.menuBar()
        
        # Меню для работы с файлами
        file_menu = menubar.addMenu('Файл')
        
        load_action = QAction('Загрузить функции...', self)
        # Таким образом задаем хоткеи
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self.load_functions)
        file_menu.addAction(load_action)
        
        save_action = QAction('Сохранить функции...', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_functions)
        file_menu.addAction(save_action)
        
        export_action = QAction('Сохранить изображение...', self)
        export_action.triggered.connect(self.export_image)
        file_menu.addAction(export_action)
        
        # Меню для запуска анализа функции
        analysis_menu = menubar.addMenu('Анализ')
        
        analyze_action = QAction('Анализ функции', self)
        analyze_action.setShortcut('Ctrl+A')
        analyze_action.triggered.connect(self.mpl_widget.on_analyze)
        analysis_menu.addAction(analyze_action)
        
        # Меню истории запросов
        history_menu = menubar.addMenu('История')
        
        history_action = QAction('Просмотреть историю', self)
        history_action.setShortcut('Ctrl+H')
        history_action.triggered.connect(self.show_history)
        history_menu.addAction(history_action)
        
    def load_functions(self):
        # Открываем диалоговое окно для выбора файла
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Загрузить функции", "", 
            "Text Files (*.txt);;CSV Files (*.csv)"
        )
        # Открываем файл и читаем функции
        if file_path:
            try:
                functions = []
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        func = line.strip()
                        if func and not func.startswith('#'):
                            functions.append(func)
                
                # Очищаем текущие графики и строим новые из файла
                self.mpl_widget.current_functions.clear()
                self.mpl_widget.function_list.clear()
                
                for func in functions:
                    self.mpl_widget.on_plot()
                    
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить функции: {str(e)}")
                
    def save_functions(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить функции", "", 
            "Text Files (*.txt);;CSV Files (*.csv)"
        )
        # Уже сохраняем функции
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    for func in self.mpl_widget.current_functions:
                        file.write(func + '\n')
                # Выводим QMessageBox для сообщения об успехе или ошибке
                QMessageBox.information(self, "Успех", "Функции успешно сохранены")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить функции: {str(e)}")
                
    def export_image(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить изображение", "",
            "PNG Files (*.png);;JPEG Files (*.jpg);;PDF Files (*.pdf);;SVG Files (*.svg)"
        )
        
        if file_path:
            try:
                # С помощью встроенной matplotlib функции сохраняем изображение функции
                self.mpl_widget.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Успех", "Изображение успешно сохранено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изображение: {str(e)}")
                
    def show_history(self):
        try:
            # Вызываем из модуля работы с БД функцию на получение истории
            history = self.mpl_widget.database_module.get_history()
            # Диалоговое окно для удобства (эта информация уже бы не поместилась в стандартном окне)
            dialog = HistoryDialog(self, history)
            # Проверяем, что операция успешно принята
            if dialog.exec() == QDialog.DialogCode.Accepted:
                if hasattr(dialog, 'selected_function'):
                    # задаем функцию в поле ввода
                    self.mpl_widget.input.setText(dialog.selected_function)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки истории: {str(e)}")
