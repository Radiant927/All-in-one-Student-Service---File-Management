"""微信通知服务（企业微信群机器人 Webhook）

文档：https://developer.work.weixin.qq.com/document/path/91770
支持的消息类型：text / markdown / image / news / file 等
"""
from typing import Optional
import requests

from app.config import settings
from app.models import Transfer, Campus


def _send_webhook(payload: dict) -> bool:
    """发送 Webhook 请求到企业微信机器人

    返回 True 表示发送成功，失败不抛异常（避免影响主业务）
    """
    webhook_url = settings.WECHAT_WEBHOOK_URL
    if not webhook_url:
        # 没配置就不发，开发环境可以跳过
        return False

    try:
        resp = requests.post(webhook_url, json=payload, timeout=5)
        result = resp.json()
        return result.get("errcode") == 0
    except Exception:
        # 任何网络错误都静默处理，不影响主流程
        return False


def send_text(content: str, mentioned_mobile_list: Optional[list] = None) -> bool:
    """发送纯文本消息

    mentioned_mobile_list: 要@的手机号列表，如 ["13800001111"]
    """
    payload = {
        "msgtype": "text",
        "text": {
            "content": content,
        }
    }
    if mentioned_mobile_list:
        payload["text"]["mentioned_mobile_list"] = mentioned_mobile_list
    return _send_webhook(payload)


def send_markdown(content: str) -> bool:
    """发送 Markdown 格式消息（支持加粗、链接、颜色等）

    注意：企业微信 Markdown 是子集，不支持所有语法
    """
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": content,
        }
    }
    return _send_webhook(payload)


# ---------- 业务场景通知 ----------

def _campus_name(campus: Campus) -> str:
    return "南海校区" if campus == Campus.NANHAI else "石牌校区"


def _urgency_label(urgency) -> str:
    mapping = {"normal": "普通", "urgent": "加急", "critical": "<font color=\"warning\">特急</font>"}
    return mapping.get(urgency.value if hasattr(urgency, 'value') else urgency, "普通")


def notify_new_transfer(transfer: Transfer) -> bool:
    """通知：新转交单发起"""
    from_name = _campus_name(transfer.from_campus)
    to_name = _campus_name(transfer.to_campus)

    content = f"""### 📨 新文件转交通知

**编号**：{transfer.transfer_no}
**标题**：{transfer.title}
**方向**：{from_name} → {to_name}
**紧急程度**：{_urgency_label(transfer.urgency)}
**转交同学**：{transfer.courier_name}
**接收人**：{transfer.receiver_name}
**发车时间**：{transfer.depart_time.strftime('%Y-%m-%d %H:%M')}
**预计到达**：{transfer.estimate_arrive_time.strftime('%Y-%m-%d %H:%M') if transfer.estimate_arrive_time else '-'}
**文件数量**：{len(transfer.files)} 份

请 {to_name} 负责人注意查收，收到后在系统中确认。
"""
    return send_markdown(content)


def notify_transfer_confirmed(transfer: Transfer) -> bool:
    """通知：转交单已被确认收到"""
    from_name = _campus_name(transfer.from_campus)
    to_name = _campus_name(transfer.to_campus)

    content = f"""### ✅ 文件已签收

**编号**：{transfer.transfer_no}
**标题**：{transfer.title}
**方向**：{from_name} → {to_name}
**确认时间**：{transfer.confirm_time.strftime('%Y-%m-%d %H:%M') if transfer.confirm_time else '-'}
**收件留言**：{transfer.confirm_message or '（无）'}

{from_name} 发起人请知悉，流程已闭环。
"""
    return send_markdown(content)


def notify_transfer_exception(transfer: Transfer) -> bool:
    """通知：转交单异常"""
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
    """通知：转交单逾期未确认"""
    from_name = _campus_name(transfer.from_campus)
    to_name = _campus_name(transfer.to_campus)

    content = f"""### ⏰ 逾期提醒

**编号**：{transfer.transfer_no}
**标题**：{transfer.title}
**方向**：{from_name} → {to_name}
**预计到达**：{transfer.estimate_arrive_time.strftime('%Y-%m-%d %H:%M') if transfer.estimate_arrive_time else '-'}

已超过预计到达时间，{to_name} 负责人请尽快确认是否收到。
"""
    return send_markdown(content)
