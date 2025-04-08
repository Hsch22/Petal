import os
import json
import datetime
from pathlib import Path

class UserInfo:
    """
    用户信息管理类，负责存储和读取用户信息
    """
    def __init__(self, config):
        self.config = config
        self.user_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'user_data')
        self.ensure_user_data_dir()
        self.user_info_file = os.path.join(self.user_data_dir, 'user_info.json')
        self.chat_history_dir = os.path.join(self.user_data_dir, 'chat_history')
        self.ensure_chat_history_dir()
        self.user_info = self.load_user_info()
    
    def ensure_user_data_dir(self):
        """
        确保用户数据目录存在
        """
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)
    
    def ensure_chat_history_dir(self):
        """
        确保聊天历史目录存在
        """
        if not os.path.exists(self.chat_history_dir):
            os.makedirs(self.chat_history_dir)
    
    def load_user_info(self):
        """
        加载用户信息，如果文件不存在则创建默认信息
        """
        if os.path.exists(self.user_info_file):
            try:
                with open(self.user_info_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载用户信息失败: {e}")
                return self.create_default_user_info()
        else:
            return self.create_default_user_info()
    
    def create_default_user_info(self):
        """
        创建默认用户信息 - 单用户模式
        """
        default_info = {
            "username": "用户",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "preferences": {
                "theme": "light",
                "font_size": "medium"
            },
            "chat_sessions": []
        }
        self.save_user_info(default_info)
        return default_info
    
    def save_user_info(self, user_info=None):
        """
        保存用户信息
        """
        if user_info is None:
            user_info = self.user_info
        
        try:
            with open(self.user_info_file, 'w', encoding='utf-8') as f:
                json.dump(user_info, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存用户信息失败: {e}")
            return False
    
    def update_user_info(self, key, value):
        """
        更新用户信息
        """
        self.user_info[key] = value
        return self.save_user_info()
    
    def get_user_info(self, key=None):
        """
        获取用户信息，如果key为None则返回所有信息
        """
        if key is None:
            return self.user_info
        return self.user_info.get(key)
    
    def save_chat_history(self, chat_id, history):
        """
        保存聊天历史
        """
        if not chat_id:
            chat_id = f"chat_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        chat_file = os.path.join(self.chat_history_dir, f"{chat_id}.json")
        
        try:
            with open(chat_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=4)
            
            # 更新用户信息中的聊天会话列表
            chat_sessions = self.user_info.get("chat_sessions", [])
            
            # 检查是否已存在该会话
            session_exists = False
            for session in chat_sessions:
                if session.get("id") == chat_id:
                    session["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    session_exists = True
                    break
            
            # 如果不存在则添加新会话
            if not session_exists:
                chat_sessions.append({
                    "id": chat_id,
                    "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "title": f"聊天 {len(chat_sessions) + 1}"
                })
            
            self.user_info["chat_sessions"] = chat_sessions
            self.save_user_info()
            
            return True
        except Exception as e:
            print(f"保存聊天历史失败: {e}")
            return False
    
    def load_chat_history(self, chat_id):
        """
        加载聊天历史
        """
        chat_file = os.path.join(self.chat_history_dir, f"{chat_id}.json")
        
        if os.path.exists(chat_file):
            try:
                with open(chat_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载聊天历史失败: {e}")
                return []
        else:
            return []
    
    def get_all_chat_sessions(self):
        """
        获取所有聊天会话
        """
        return self.user_info.get("chat_sessions", [])
    
    def delete_chat_session(self, chat_id):
        """
        删除聊天会话
        """
        chat_file = os.path.join(self.chat_history_dir, f"{chat_id}.json")
        
        # 删除文件
        if os.path.exists(chat_file):
            try:
                os.remove(chat_file)
            except Exception as e:
                print(f"删除聊天历史文件失败: {e}")
                return False
        
        # 更新用户信息
        chat_sessions = self.user_info.get("chat_sessions", [])
        self.user_info["chat_sessions"] = [session for session in chat_sessions if session.get("id") != chat_id]
        self.save_user_info()
        
        return True