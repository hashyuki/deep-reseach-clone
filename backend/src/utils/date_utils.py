"""日付関連のユーティリティ関数"""

from datetime import datetime


def get_current_date():
    """現在の日付を読みやすい形式で取得"""
    return datetime.now().strftime("%Y年%m月%d日")