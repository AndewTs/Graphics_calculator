from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QDialog
)
from PyQt6.QtGui import QAction

from src.mpl_widget import MplWidget
from src.dialogs import HistoryDialog
from src.file_module import FileModule

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
        # Задаем хоткеи ко всем действия так
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
        """Загружает функции из файла и добавляет их на график"""
        try:
            functions = FileModule.load_functions(self)
            if functions:
                # Очищаем текущие графики
                self.mpl_widget.clear_all_functions()
                
                # Добавляем каждую функцию
                success_count = 0
                for func in functions:
                    try:
                        # Устанавливаем функцию в поле ввода
                        self.mpl_widget.input.setText(func)
                        # Пытаемся построить график
                        if self.mpl_widget.on_plot_silent():
                            success_count += 1
                    except Exception as e:
                        print(f"Ошибка при построении функции {func}: {e}")
                        continue
                
                # Показываем результат
                if success_count > 0:
                    QMessageBox.information(self, "Успех", 
                                          f"Успешно загружено {success_count} из {len(functions)} функций")
                else:
                    QMessageBox.warning(self, "Предупреждение", 
                                      "Не удалось загрузить ни одну функцию")
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить функции: {str(e)}")
    
    def save_functions(self):
        """Сохраняет текущие функции в файл"""
        try:
            # Получаем список функций из виджета
            functions = []
            for func_info in self.mpl_widget.current_functions:
                functions.append(func_info['expression'])
            
            FileModule.save_functions(self, functions)
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить функции: {str(e)}")
    
    def export_image(self):
        """Экспортирует текущий график в файл изображения"""
        try:
            FileModule.export_plot(self, self.mpl_widget.canvas)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать изображение: {str(e)}")
                
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
