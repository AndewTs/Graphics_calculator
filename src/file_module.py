from PyQt6.QtWidgets import QFileDialog, QMessageBox
import os

class FileModule:
    @staticmethod
    def load_functions(parent):
        """Загружает функции из файла с улучшенной обработкой ошибок"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                parent, "Загрузить функции", "", 
                "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)"
            )
            
            if not file_path:
                return []
            
            # Проверяем существование файла
            if not os.path.exists(file_path):
                QMessageBox.warning(parent, "Ошибка", f"Файл не найден: {file_path}")
                return []
            
            functions = []
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    func = line.strip()
                    
                    # Пропускаем пустые строки и комментарии
                    if not func or func.startswith('#'):
                        continue
                    
                    # Проверяем корректность функции перед добавлением
                    try:
                        # Простая проверка - пытаемся разобрать функцию
                        if FileModule.is_valid_function(func):
                            functions.append(func)
                        else:
                            QMessageBox.warning(parent, "Предупреждение", 
                                              f"Строка {line_num} содержит некорректную функцию: {func}")
                    except Exception as e:
                        QMessageBox.warning(parent, "Ошибка", 
                                          f"Ошибка в строке {line_num}: {func}\n{str(e)}")
            
            if not functions:
                QMessageBox.information(parent, "Информация", "Не найдено корректных функций в файле")
            
            return functions
            
        except UnicodeDecodeError:
            QMessageBox.critical(parent, "Ошибка", "Не удалось прочитать файл. Проверьте кодировку.")
            return []
        except Exception as e:
            QMessageBox.critical(parent, "Ошибка", f"Ошибка загрузки файла: {str(e)}")
            return []
    
    @staticmethod
    def is_valid_function(func_text):
        """Проверяет, является ли строка корректной функцией"""
        if not func_text or not isinstance(func_text, str):
            return False
        
        # Базовые проверки
        if len(func_text.strip()) == 0:
            return False
        
        # Проверяем наличие переменной x
        if 'x' not in func_text:
            return False
        
        # Проверяем на наличие опасных конструкций (базовая безопасность)
        dangerous_keywords = ['import', 'exec', 'eval', '__', 'open', 'file']
        for keyword in dangerous_keywords:
            if keyword in func_text:
                return False
        
        return True
    
    @staticmethod
    def save_functions(parent, functions):
        """Сохраняет функции в файл"""
        try:
            if not functions:
                QMessageBox.warning(parent, "Предупреждение", "Нет функций для сохранения")
                return
            
            file_path, _ = QFileDialog.getSaveFileName(
                parent, "Сохранить функции", "functions.txt", 
                "Text Files (*.txt);;CSV Files (*.csv);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write("# Список функций для графического калькулятора\n")
                    file.write("# Каждая функция должна быть на отдельной строке\n")
                    file.write("# Комментарии начинаются с символа #\n\n")
                    
                    for func in functions:
                        if hasattr(func, 'expression'):
                            # Если переданы объекты функций
                            file.write(f"{func['expression']}\n")
                        else:
                            # Если переданы простые строки
                            file.write(f"{func}\n")
                
                QMessageBox.information(parent, "Успех", f"Функции сохранены в файл: {file_path}")
                
        except Exception as e:
            QMessageBox.critical(parent, "Ошибка", f"Ошибка сохранения файла: {str(e)}")
    
    @staticmethod
    def export_plot(parent, canvas):
        """Экспортирует график в файл изображения"""
        try:
            file_path, selected_filter = QFileDialog.getSaveFileName(
                parent, "Сохранить изображение", "graph",
                "PNG Files (*.png);;JPEG Files (*.jpg);;PDF Files (*.pdf);;SVG Files (*.svg);;All Files (*)"
            )
            
            if file_path:
                # Определяем формат из выбранного фильтра
                if "PNG" in selected_filter:
                    if not file_path.lower().endswith('.png'):
                        file_path += '.png'
                elif "JPEG" in selected_filter:
                    if not file_path.lower().endswith(('.jpg', '.jpeg')):
                        file_path += '.jpg'
                elif "PDF" in selected_filter:
                    if not file_path.lower().endswith('.pdf'):
                        file_path += '.pdf'
                elif "SVG" in selected_filter:
                    if not file_path.lower().endswith('.svg'):
                        file_path += '.svg'
                
                canvas.figure.savefig(file_path, dpi=300, bbox_inches='tight', 
                                    facecolor='white', edgecolor='none')
                QMessageBox.information(parent, "Успех", f"График сохранен в файл: {file_path}")
                
        except Exception as e:
            QMessageBox.critical(parent, "Ошибка", f"Ошибка экспорта изображения: {str(e)}")