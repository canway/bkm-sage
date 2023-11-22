from dataclasses import dataclass


@dataclass
class SageException(BaseException):
    message: str = "Sage执行异常"
    code: str = "9999500"
