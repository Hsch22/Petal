from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QTextEdit, QPushButton, QDateTimeEdit, QMessageBox, 
                           QScrollArea, QWidget, QFormLayout)
from PyQt5.QtCore import QDateTime, Qt

class ImportScheduleDialog(QDialog):
    """
    导入日程对话框，允许用户直接在界面中输入多个日程项目
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.schedules = []  # 存储用户输入的日程列表
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("导入日程")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        main_layout = QVBoxLayout()
        
        # 创建滚动区域来容纳多个日程表单
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.form_layout = QVBoxLayout(scroll_content)
        
        # 添加第一个日程表单
        self.add_schedule_form()
        
        scroll_area.setWidget(scroll_content)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        add_form_btn = QPushButton("添加更多日程")
        add_form_btn.clicked.connect(self.add_schedule_form)
        
        import_btn = QPushButton("导入")
        import_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(add_form_btn)
        button_layout.addStretch()
        button_layout.addWidget(import_btn)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addWidget(scroll_area)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def add_schedule_form(self):
        """
        添加一个新的日程表单
        """
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题
        title_edit = QLineEdit()
        form_layout.addRow("标题:", title_edit)
        
        # 时间
        datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        datetime_edit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        datetime_edit.setCalendarPopup(True)
        form_layout.addRow("时间:", datetime_edit)
        
        # 地点
        location_edit = QLineEdit()
        form_layout.addRow("地点:", location_edit)
        
        # 描述
        description_edit = QTextEdit()
        description_edit.setMaximumHeight(100)
        form_layout.addRow("描述:", description_edit)
        
        # 删除按钮
        delete_btn = QPushButton("删除此日程")
        delete_btn.clicked.connect(lambda: self.remove_schedule_form(form_widget))
        form_layout.addRow("", delete_btn)
        
        # 分隔线
        separator = QWidget()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background-color: #cccccc;")
        
        # 将表单和分隔线添加到主布局
        self.form_layout.addWidget(form_widget)
        self.form_layout.addWidget(separator)
        
        # 保存表单控件的引用
        form_widget.title_edit = title_edit
        form_widget.datetime_edit = datetime_edit
        form_widget.location_edit = location_edit
        form_widget.description_edit = description_edit
    
    def remove_schedule_form(self, form_widget):
        """
        删除一个日程表单
        """
        # 获取分隔线（表单后面的下一个widget）
        index = self.form_layout.indexOf(form_widget)
        if index >= 0:
            # 删除表单
            form_widget.deleteLater()
            
            # 如果不是最后一个表单，也删除分隔线
            if index + 1 < self.form_layout.count():
                separator = self.form_layout.itemAt(index).widget()
                if separator:
                    separator.deleteLater()
    
    def collect_schedules(self):
        """
        收集所有表单中的日程数据
        """
        schedules = []
        
        # 遍历所有表单控件
        for i in range(self.form_layout.count()):
            widget = self.form_layout.itemAt(i).widget()
            
            # 跳过分隔线
            if widget and hasattr(widget, 'title_edit'):
                title = widget.title_edit.text()
                start_time = widget.datetime_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")
                location = widget.location_edit.text()
                description = widget.description_edit.toPlainText()
                
                # 只添加有标题的日程
                if title:
                    schedules.append({
                        "title": title,
                        "start_time": start_time,
                        "location": location,
                        "description": description
                    })
        
        return schedules
    
    def validate(self):
        """
        验证输入
        """
        # 检查是否至少有一个有效的日程（有标题的日程）
        for i in range(self.form_layout.count()):
            widget = self.form_layout.itemAt(i).widget()
            
            if widget and hasattr(widget, 'title_edit') and widget.title_edit.text():
                return True
        
        QMessageBox.warning(self, "警告", "请至少输入一个有效的日程（包含标题）！")
        return False
    
    def accept(self):
        """
        确认按钮点击事件
        """
        if self.validate():
            self.schedules = self.collect_schedules()
            super().accept()