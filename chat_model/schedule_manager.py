import os
import json
import datetime
from pathlib import Path
from PyQt5.QtCore import QTimer, QDateTime

class ScheduleManager:
    """
    日程管理类，负责存储、加载和提醒用户的日程安排
    """
    def __init__(self, config, desktop_pet=None):
        self.config = config
        self.desktop_pet = desktop_pet
        self.user_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'user_data')
        self.ensure_user_data_dir()
        self.schedule_file = os.path.join(self.user_data_dir, 'schedule.json')
        self.schedules = self.load_schedules()
        self.reminder_timers = {}
        
        # 初始化定时器，每分钟检查一次是否有需要提醒的日程
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_schedules)
        self.check_timer.start(60000)  # 60000毫秒 = 1分钟
        
        # 立即检查一次日程
        self.check_schedules()
    
    def ensure_user_data_dir(self):
        """
        确保用户数据目录存在
        """
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)
    
    def load_schedules(self):
        """
        加载日程信息，如果文件不存在则创建空列表
        """
        if os.path.exists(self.schedule_file):
            try:
                with open(self.schedule_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载日程信息失败: {e}")
                return []
        else:
            return []
    
    def save_schedules(self):
        """
        保存日程信息
        """
        try:
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump(self.schedules, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存日程信息失败: {e}")
            return False
    
    def add_schedule(self, title, start_time, description="", location=""):
        """
        添加新日程
        :param title: 日程标题
        :param start_time: 开始时间，格式为"YYYY-MM-DD HH:MM:SS"
        :param description: 日程描述
        :param location: 地点
        :return: 是否添加成功
        """
        try:
            # 验证时间格式
            datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            
            new_schedule = {
                "title": title,
                "start_time": start_time,
                "description": description,
                "location": location,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.schedules.append(new_schedule)
            success = self.save_schedules()
            
            if success:
                # 设置提醒
                self.set_reminder(new_schedule)
            
            return success
        except ValueError:
            print("时间格式错误，请使用YYYY-MM-DD HH:MM:SS格式")
            return False
        except Exception as e:
            print(f"添加日程失败: {e}")
            return False
    
    def update_schedule(self, title, start_time, **kwargs):
        """
        更新日程信息
        :param title: 日程标题
        :param start_time: 日程开始时间
        :param kwargs: 要更新的字段，可以包括新的title, start_time, description, location
        :return: 是否更新成功
        """
        try:
            for i, schedule in enumerate(self.schedules):
                if schedule["title"] == title and schedule["start_time"] == start_time:
                    # 如果更新了开始时间，验证格式
                    if "start_time" in kwargs:
                        datetime.datetime.strptime(kwargs["start_time"], "%Y-%m-%d %H:%M:%S")
                    
                    # 更新字段
                    for key, value in kwargs.items():
                        if key in ["title", "start_time", "description", "location"]:
                            schedule[key] = value
                    
                    self.schedules[i] = schedule
                    success = self.save_schedules()
                    
                    if success and "start_time" in kwargs:
                        # 如果更新了开始时间，重新设置提醒
                        # 使用标题和旧的开始时间组合作为键
                        timer_key = f"{title}_{start_time}"
                        if timer_key in self.reminder_timers and self.reminder_timers[timer_key].isActive():
                            self.reminder_timers[timer_key].stop()
                        self.set_reminder(schedule)
                    
                    return success
            
            print(f"未找到标题为'{title}'且开始时间为'{start_time}'的日程")
            return False
        except ValueError:
            print("时间格式错误，请使用YYYY-MM-DD HH:MM:SS格式")
            return False
        except Exception as e:
            print(f"更新日程失败: {e}")
            return False
    
    def delete_schedule(self, title, start_time):
        """
        删除日程
        :param title: 日程标题
        :param start_time: 日程开始时间
        :return: 是否删除成功
        """
        try:
            for i, schedule in enumerate(self.schedules):
                if schedule["title"] == title and schedule["start_time"] == start_time:
                    # 停止提醒定时器
                    timer_key = f"{title}_{start_time}"
                    if timer_key in self.reminder_timers and self.reminder_timers[timer_key].isActive():
                        self.reminder_timers[timer_key].stop()
                        del self.reminder_timers[timer_key]
                    
                    # 删除日程
                    self.schedules.pop(i)
                    return self.save_schedules()
            
            print(f"未找到标题为'{title}'且开始时间为'{start_time}'的日程")
            return False
        except Exception as e:
            print(f"删除日程失败: {e}")
            return False
    
    def get_all_schedules(self):
        """
        获取所有日程
        :return: 日程列表
        """
        return self.schedules
    
    def get_schedule_by_title_and_time(self, title, start_time):
        """
        根据标题和开始时间获取日程
        :param title: 日程标题
        :param start_time: 开始时间
        :return: 日程信息或None
        """
        for schedule in self.schedules:
            if schedule["title"] == title and schedule["start_time"] == start_time:
                return schedule
        return None
    
    def set_reminder(self, schedule):
        """
        设置日程提醒
        :param schedule: 日程信息
        """
        try:
            start_time = datetime.datetime.strptime(schedule["start_time"], "%Y-%m-%d %H:%M:%S")
            reminder_time = start_time - datetime.timedelta(minutes=15)  # 提前15分钟提醒
            
            # 如果提醒时间已经过去，则不设置提醒
            if reminder_time < datetime.datetime.now():
                return
            
            # 计算当前时间到提醒时间的毫秒数
            now = datetime.datetime.now()
            delta_ms = int((reminder_time - now).total_seconds() * 1000)
            
            # 创建定时器
            timer = QTimer()
            timer.setSingleShot(True)  # 只触发一次
            timer.timeout.connect(lambda: self.show_reminder(schedule))
            timer.start(delta_ms)
            
            # 保存定时器引用，使用标题和开始时间的组合作为键
            timer_key = f"{schedule['title']}_{schedule['start_time']}"
            self.reminder_timers[timer_key] = timer
        except Exception as e:
            print(f"设置提醒失败: {e}")
    
    def show_reminder(self, schedule):
        """
        显示提醒
        :param schedule: 日程信息
        """
        print(f"[DEBUG] 尝试显示提醒，桌宠对象存在: {self.desktop_pet is not None}")
        if self.desktop_pet:
            title = schedule["title"]
            start_time = schedule["start_time"]
            location = schedule["location"]
            description = schedule["description"]
            
            # 构建提醒消息
            message = f"提醒：{title}将在15分钟后开始\n时间：{start_time}"
            if location:
                message += f"\n地点：{location}"
            if description:
                message += f"\n描述：{description}"
            
            # 创建一个回调函数，用于在用户关闭提醒后删除该日程
            def on_reminder_closed():
                print(f"[DEBUG] 用户关闭了日程提醒，准备删除日程: {title}_{start_time}")
                self.delete_schedule(title, start_time)
                print(f"[DEBUG] 日程已删除: {title}_{start_time}")
            
            # 显示提醒，传递is_schedule_reminder=True参数使气泡持续显示并有关闭按钮，同时传递回调函数
            print(f"[DEBUG] 发送气泡提醒: {message}")
            self.desktop_pet.show_bubble(message, is_schedule_reminder=True, on_close_callback=on_reminder_closed)
            
            # 确保这个日程被记录为已提醒，防止重复提醒
            timer_key = f"{title}_{start_time}"
            if timer_key not in self.reminder_timers:
                self.reminder_timers[timer_key] = "reminded"
        else:
            print(f"[DEBUG] 无法显示提醒，桌宠对象不存在")
    
    def check_schedules(self):
        """
        检查是否有需要提醒的日程
        """
        now = datetime.datetime.now()
        print(f"[DEBUG] 检查日程提醒，当前时间: {now}")
        
        for schedule in self.schedules:
            try:
                title = schedule["title"]
                start_time = schedule["start_time"]
                start_time_dt = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                reminder_time = start_time_dt - datetime.timedelta(minutes=15)  # 提前15分钟提醒
                
                # 如果当前时间接近提醒时间（误差在1分钟内），且没有设置过提醒，则显示提醒
                time_diff = (reminder_time - now).total_seconds()
                timer_key = f"{title}_{start_time}"
                print(f"[DEBUG] 日程 '{title}' 的提醒时间差: {time_diff}秒, 是否在提醒列表中: {timer_key in self.reminder_timers}")
                
                # 修改条件：如果时间差在-300到300秒之间（允许前后5分钟误差），且没有设置过提醒，则显示提醒
                if -300 <= time_diff <= 300 and timer_key not in self.reminder_timers:
                    print(f"[DEBUG] 触发日程提醒: {title}")
                    self.show_reminder(schedule)
            except Exception as e:
                print(f"检查日程失败: {e}")

    
    def import_schedules_from_file(self, file_path):
        """
        从文件导入日程
        :param file_path: 文件路径，支持JSON格式
        :return: 是否导入成功
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_schedules = json.load(f)
            
            # 验证导入的数据格式
            if not isinstance(imported_schedules, list):
                print("导入失败：数据格式错误，应为日程列表")
                return False
            
            for schedule in imported_schedules:
                if not all(key in schedule for key in ["title", "start_time"]):
                    print("导入失败：日程数据缺少必要字段")
                    return False
                
                # 验证时间格式
                try:
                    datetime.datetime.strptime(schedule["start_time"], "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    print("导入失败：时间格式错误，请使用YYYY-MM-DD HH:MM:SS格式")
                    return False
            
            # 合并日程，不再分配ID
            for schedule in imported_schedules:
                # 添加创建时间
                schedule["created_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.schedules.append(schedule)
                self.set_reminder(schedule)
            
            return self.save_schedules()
        except Exception as e:
            print(f"导入日程失败: {e}")
            return False
    
    def export_schedules_to_file(self, file_path):
        """
        导出日程到文件
        :param file_path: 文件路径，支持JSON格式
        :return: 是否导出成功
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.schedules, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"导出日程失败: {e}")