from email.message import EmailMessage

import aiosmtplib


class Email:
    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        self.__host = host
        self.__port = port

        self.__username = username
        self.__password = password

    async def send(self, to: str, content: str, name: str = 'Task Tracker', subject: str = 'Task Tracker') -> None:
        message = EmailMessage()
        message['From'] = f'"{name}" <{self.__username}>'
        message['To'] = to
        message['Subject'] = subject
        message.set_content(content, subtype='html')

        await aiosmtplib.send(
            message,
            sender=message['From'],
            hostname=self.__host,
            port=self.__port,
            username=self.__username,
            password=self.__password,
            use_tls=True
        )
