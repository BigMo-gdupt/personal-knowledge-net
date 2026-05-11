"""
邮件发送工具：通过 QQ 邮箱 SMTP 发送邮件。
支持发送纯文本和 HTML 格式邮件。

使用方式：
    python send_email.py --subject "测试" --body "你好" --type text
    python send_email.py --subject "测试" --body "<h1>你好</h1>" --type html
"""

import smtplib
import argparse
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime


# ============ 配置 ============
CONFIG_FILE = Path(__file__).parent / "_config" / "email_config.json"
DEFAULT_SMTP_SERVER = "smtp.qq.com"
DEFAULT_SMTP_PORT = 465
# ================================


def load_config() -> dict:
    """加载邮件配置。优先从配置文件读取，否则使用默认值。"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def send_email(
    subject: str,
    body: str,
    body_type: str = "html",
    config: dict = None,
) -> bool:
    """
    通过 QQ 邮箱 SMTP 发送邮件。

    Args:
        subject: 邮件主题
        body: 邮件正文
        body_type: 正文类型，"text" 或 "html"
        config: 配置字典，包含 sender, password, receiver

    Returns:
        True 表示发送成功
    """
    if config is None:
        config = load_config()

    sender = config.get("sender", "")
    password = config.get("password", "")
    receiver = config.get("receiver", sender)

    if not sender or not password:
        print("[错误] 未配置发件人邮箱或授权码，请检查 _config/email_config.json")
        return False

    # 构建邮件
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject

    msg.attach(MIMEText(body, body_type, "utf-8"))

    # 发送
    smtp_server = config.get("smtp_server", DEFAULT_SMTP_SERVER)
    smtp_port = config.get("smtp_port", DEFAULT_SMTP_PORT)

    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
            server.starttls()

        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        print(f"✅ 邮件发送成功 → {receiver}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("[错误] SMTP 认证失败，请检查授权码是否正确")
        return False
    except Exception as e:
        print(f"[错误] 邮件发送失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="通过 QQ 邮箱发送邮件")
    parser.add_argument("--subject", required=True, help="邮件主题")
    parser.add_argument("--body", required=True, help="邮件正文")
    parser.add_argument("--type", default="html", choices=["text", "html"], help="正文类型")
    args = parser.parse_args()

    success = send_email(args.subject, args.body, args.type)
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
