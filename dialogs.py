from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox, 
    QListWidget, QPushButton, QHBoxLayout, QMessageBox
)

class AnalysisDialog(QDialog):
    def __init__(self, parent=None, analysis_text=""):
        super().__init__(parent)
        self.setWindowTitle("Анализ функции")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout()
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(analysis_text)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        
        self.setLayout(layout)

class HistoryDialog(QDialog):
    def __init__(self, parent=None, history_data=None):
        super().__init__(parent)
        self.setWindowTitle("История запросов")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        
        self.list_widget = QListWidget()
        if history_data:
            for item in history_data:
                self.list_widget.addItem(f"{item[2]} - {item[1]}")
        layout.addWidget(self.list_widget)
        
        button_layout = QHBoxLayout()
        self.load_btn = QPushButton("Загрузить выбранное")
        self.close_btn = QPushButton("Закрыть")
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        self.load_btn.clicked.connect(self.load_selected)
        self.close_btn.clicked.connect(self.reject)
        
    def load_selected(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            # Извлекаем текст функции из элемента списка
            function_text = selected_item.text().split(" - ", 1)[1]
            self.selected_function = function_text
            self.accept()
        else:
            QMessageBox.warning(self, "Предупреждение", "Выберите функцию из списка")