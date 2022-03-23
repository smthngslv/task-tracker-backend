from email.message import EmailMessage

import aiosmtplib


class Email:
    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        self.__host = host
        self.__port = port

        self.__username = username
        self.__password = password

    async def send(self, to: str, content: str) -> None:
        message = EmailMessage()
        message['From'] = self.__username
        message['To'] = to
        message['Subject'] = 'Task Tracker'
        message.set_content(content)

        await aiosmtplib.send(
            message,
            hostname=self.__host,
            port=self.__port,
            username=self.__username,
            password=self.__password,
            use_tls=True
        )
