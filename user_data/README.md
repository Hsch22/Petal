# 用户数据目录

此目录用于存储用户信息和聊天历史记录。

## 目录结构

- `user_info.json`: 存储用户基本信息，包括用户ID、用户名、偏好设置等
- `chat_history/`: 存储聊天历史记录的目录
  - 每个聊天会话以JSON文件形式存储，文件名格式为`chat_[时间戳].json`

## 数据格式

### user_info.json

```json
{
  "user_id": "唯一用户ID",
  "username": "用户名",
  "created_at": "创建时间",
  "last_login": "最后登录时间",
  "preferences": {
    "theme": "主题",
    "font_size": "字体大小"
  },
  "chat_sessions": [
    {
      "id": "聊天会话ID",
      "created_at": "创建时间",
      "last_updated": "最后更新时间",
      "title": "聊天标题"
    }
  ]
}
```

### 聊天历史文件 (chat_[时间戳].json)

```json
[
  ["用户消息1", "用户消息2", ...],
  ["AI回复1", "AI回复2", ...]
]
```

## 注意事项

- 请勿手动修改这些文件，以免造成数据损坏
- 如需备份用户数据，请复制整个`user_data`目录
- 如需重置用户数据，可以删除`user_info.json`文件，系统会自动创建新的用户信息