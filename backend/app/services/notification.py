"""微信通知服务（企业微信群机器人 Webhook）"""
from typing import Optional
import requests
from app.config import settings
from app.models import Transfer, Campus

def _send_webhook(payload: dict) -> bool:
    webhook_url = settings.WECHAT_WEBHOOK_URL
    if not webhook_url:
        return False
    try:
        resp = requests.post(webhook_url, json=payload, timeout=5)
        result = resp.json()
        return result.get("errcode") == 0
    except Exception:
        return False

def send_text(content: str, mentioned_mobile_list: Optional[list] = None) -> bool:
    payload = {"msgtype": "text", "text": {"content": content}}
    if mentioned_mobile_list:
        payload["text"]["mentioned_mobile_list"] = mentioned_mobile_list
    return _send_webhook(payload)

def send_markdown(content: str) -> bool:
    payload = {"msgtype": "markdown", "markdown": {"content": content}}
    return _send_webhook(payload)

def _campus_name(campus: Campus) -> str:
    return "南海校区" if campus == Campus.NANHAI else "石牌校区"

def _urgency_label(urgency) -> str:
    mapping = {"normal": "普通", "urgent": "加急", "critical": "<font color=\"warning\">特急</font>"}
    return mapping.get(urgency.value if hasattr(urgency, 'value') else urgency, "普通")

def _fmt_time(dt) -> str:
    if not dt:
        return '-'
    if isinstance(dt, str):
        return dt
    return dt.strftime('%Y-%m-%d %H:%M')

def notify_new_transfer(transfer: Transfer) -> bool:
    from_name = _campus_name(transfer.from_campus)
    to_name = _campus_name(transfer.to_campus)
    content = f"""### 📨 新文件转交通知

**编号**：{transfer.transfer_no}
**标题**：{transfer.title}
**方向**：{from_name} → {to_name}
**紧急程度**：{_urgency_label(transfer.urgency)}
**转交同学**：{transfer.courier_name}
**接收人**：{transfer.receiver_name}
**发车时间**：{_fmt_time(transfer.depart_time)}
**预计到达**：{_fmt_time(transfer.estimate_arrive_time)}
**文件数量**：{len(transfer.files)} 份

请 {to_name} 负责人注意查收，收到后在系统中确认。
"""
    return send_markdown(content)

def notify_transfer_confirmed(transfer: Transfer) -> bool:
    from_name = _campus_name(transfer.from_campus)
    to_name = _campus_name(transfer.to_campus)
    content = f"""### ✅ 文件已签收

**编号**：{transfer.transfer_no}
**标题**：{transfer.title}
**方向**：{from_name} → {to_name}
**确认时间**：{_fmt_time(transfer.confirm_time)}
**收件留言**：{transfer.confirm_message or '（无）'}

{from_name} 发起人请知悉，流程已闭环。
"""
    return send_markdown(content)

def notify_transfer_exception(transfer: Transfer) -> bool:
    from_name = _campus_name(transfer.from_campus)
    to_name = _campus_name(transfer.to_campus)
    content = f"""### ⚠️ 文件异常提醒

**编号**：{transfer.transfer_no}
**标题**：{transfer.title}
**方向**：{from_name} → {to_name}
**异常说明**：{transfer.exception_note or '（未填写）'}

请 {from_name} 负责人尽快核实并处理。
"""
    return send_markdown(content)

def notify_overdue(transfer: Transfer) -> bool:
    from_name = _campus_name(transfer.from_campus)
    to_name = _campus_name(transfer.to_campus)
    content = f"""### ⏰ 逾期提醒

**编号**：{transfer.transfer_no}
**标题**：{transfer.title}
**方向**：{from_name} → {to_name}
**预计到达**：{_fmt_time(transfer.estimate_arrive_time)}

已超过预计到达时间，{to_name} 负责人请尽快确认是否收到。
"""
    return send_markdown(content)