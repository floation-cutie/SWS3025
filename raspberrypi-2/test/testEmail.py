import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 邮箱服务器
smtp_server = 'smtp.qq.com'
# 发件人邮箱
from_addr = 'Sender\'s email.com'
# 邮箱授权码
password = 'Your password'
# 收件人邮箱
to_addr = 'Recipient\'s email.com'
# 邮件内容
text = 'Hello, this is a test email from Python.'
msg = MIMEText(text, 'plain', 'utf-8')

# 邮件头信息
msg['From'] = Header(from_addr)
msg['To'] = Header(to_addr)
msg['Subject'] = Header('Python SMTP 邮件测试')

try:
    # 创建 SMTP 对象
    server = smtplib.SMTP_SSL(smtp_server, 465)
    # 登录邮箱
    server.login(from_addr, password)
    # 发送邮件
    server.sendmail(from_addr, [to_addr], msg.as_string())
    print("邮件发送成功")
except Exception as e:
    print("邮件发送失败", e)
finally:
    # 断开服务器连接
    server.quit()

