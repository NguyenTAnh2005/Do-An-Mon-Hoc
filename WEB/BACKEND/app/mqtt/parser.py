# File bóc tách topic để sác định loại tin được gửi đến

from typing import Optional

def parse_topic(topic: str) -> Optional[tuple[str, Optional[str]]]:
    parts = topic.split("/")
    if len(parts) < 3 or parts[0] != "school":
        return None
    # VD topic: "school/area1/fill_level/organic"
    # loại tin nhắn 
    kind = parts[2]
    sub = parts[3] if len(parts) == 4 else None 

    return kind, sub
