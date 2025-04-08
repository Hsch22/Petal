import os
import json
import datetime
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
                             QDateTimeEdit, QLineEdit, QTextEdit, QMessageBox)
# 注意：import_schedule_dialog 模块会在需要时动态导入
from PyQt5.QtCore import Qt, QDateTime

class ScheduleDialog(QDialog):
    """
    日程管理对话框，用于导入、查看和管理日程
    """
    def __init__(self, parent=None, schedule_manager=None):
        super().__init__(parent)
        self.schedule_manager = schedule_manager
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("日程管理")
        self.setMinimumSize(600, 400)
        
        # 主布局
        main_layout = QVBoxLayout()
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("批量添加日程")
        self.import_btn.clicked.connect(self.import_schedule)
        
        self.add_btn = QPushButton("添加日程")
        self.add_btn.clicked.connect(self.show_add_dialog)
        
        self.delete_btn = QPushButton("删除日程")
        self.delete_btn.clicked.connect(self.delete_schedule)
        
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.delete_btn)
        
        # 日程表格
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(4)
        self.schedule_table.setHorizontalHeaderLabels(["标题", "开始时间", "地点", "描述"])
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.schedule_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 设置表格为只读
        
        # 加载日程数据
        self.load_schedules()
        
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.schedule_table)
        
        self.setLayout(main_layout)
    
    def load_schedules(self):
        """
        加载日程数据到表格
        """
        if not self.schedule_manager:
            return
        
        schedules = self.schedule_manager.get_all_schedules()
        self.schedule_table.setRowCount(len(schedules))
        
        for row, schedule in enumerate(schedules):
            self.schedule_table.setItem(row, 0, QTableWidgetItem(schedule["title"]))
            self.schedule_table.setItem(row, 1, QTableWidgetItem(schedule["start_time"]))
            self.schedule_table.setItem(row, 2, QTableWidgetItem(schedule.get("location", "")))
            self.schedule_table.setItem(row, 3, QTableWidgetItem(schedule.get("description", "")))
    
    def import_schedule(self):
        """
        导入日程 - 通过对话框直接输入
        """
        from import_schedule_dialog import ImportScheduleDialog
        
        import_dialog = ImportScheduleDialog(self)
        if import_dialog.exec_() == QDialog.Accepted and self.schedule_manager:
            # 获取用户输入的日程列表
            schedules = import_dialog.schedules
            
            if schedules:
                # 添加每个日程
                success_count = 0
                for schedule in schedules:
                    if self.schedule_manager.add_schedule(
                        schedule["title"], 
                        schedule["start_time"], 
                        schedule["description"], 
                        schedule["location"]
                    ):
                        success_count += 1
                
                if success_count > 0:
                    QMessageBox.information(self, "导入成功", f"成功导入 {success_count} 个日程！")
                    self.load_schedules()  # 重新加载日程数据
                else:
                    QMessageBox.warning(self, "导入失败", "没有成功导入任何日程！")
            else:
                QMessageBox.warning(self, "导入取消", "没有输入任何日程！")
    
    def show_add_dialog(self):
        """
        显示添加日程对话框
        """
        add_dialog = AddScheduleDialog(self)
        if add_dialog.exec_() == QDialog.Accepted and self.schedule_manager:
            # 获取对话框中的数据
            title = add_dialog.title_edit.text()
            start_time = add_dialog.datetime_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")
            location = add_dialog.location_edit.text()
            description = add_dialog.description_edit.toPlainText()
            
            # 添加日程
            if self.schedule_manager.add_schedule(title, start_time, description, location):
                QMessageBox.information(self, "添加成功", "日程添加成功！")
                self.load_schedules()  # 重新加载日程数据
            else:
                QMessageBox.warning(self, "添加失败", "日程添加失败！")
    
    def delete_schedule(self):
        """
        删除选中的日程
        """
        selected_rows = self.schedule_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要删除的日程！")
            return
        
        # 获取选中行的标题和开始时间
        row = selected_rows[0].row()
        title = self.schedule_table.item(row, 1).text()
        start_time = self.schedule_table.item(row, 2).text()
        
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这个日程吗？", 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes and self.schedule_manager:
            if self.schedule_manager.delete_schedule(title, start_time):
                QMessageBox.information(self, "删除成功", "日程删除成功！")
                self.load_schedules()  # 重新加载日程数据
            else:
                QMessageBox.warning(self, "删除失败", "日程删除失败！")


class AddScheduleDialog(QDialog):
    """
    添加日程对话框
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("添加日程")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("标题:")
        self.title_edit = QLineEdit()
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_edit)
        
        # 时间
        time_layout = QHBoxLayout()
        time_label = QLabel("时间:")
        self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        self.datetime_edit.setCalendarPopup(True)
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.datetime_edit)
        
        # 地点
        location_layout = QHBoxLayout()
        location_label = QLabel("地点:")
        self.location_edit = QLineEdit()
        location_layout.addWidget(location_label)
        location_layout.addWidget(self.location_edit)
        
        # 描述
        description_layout = QVBoxLayout()
        description_label = QLabel("描述:")
        self.description_edit = QTextEdit()
        description_layout.addWidget(description_label)
        description_layout.addWidget(self.description_edit)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确定")
        self.cancel_btn = QPushButton("取消")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(title_layout)
        layout.addLayout(time_layout)
        layout.addLayout(location_layout)
        layout.addLayout(description_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def validate(self):
        """
        验证输入
        """
        if not self.title_edit.text():
            QMessageBox.warning(self, "警告", "请输入日程标题！")
            return False
        return True
    
    def accept(self):
        if self.validate():
            super().accept()