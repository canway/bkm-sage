import abc
import enum
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from traceback import print_exc
from typing import Callable, Dict, List, Optional, Tuple

from bkm_sage.actuator.config import default_config
from bkm_sage.actuator.exception import SageException

ACTION_OK_CODE = "1010200"
ACTION_FAILED_CODE = "1010500"


class ActionStatus(enum.Enum):
    OK = "ok"
    FAILED = "failed"


@dataclass
class ActionLog:
    content: str
    level: int = logging.INFO
    timestamp: int = field(default_factory=lambda: time.time())

    def print(self):
        return f"{format_ts(self.timestamp)} [{logging.getLevelName(self.level)}] {self.content}"


@dataclass
class ActionState:
    start_at: int = field(default_factory=lambda: time.time())
    end_at: int = None
    status: ActionStatus = None
    code: str = None
    error: str = None
    logs: List[ActionLog] = field(default_factory=list)

    def set_ok(self):
        self.end_at = time.time()
        self.status = ActionStatus.OK
        self.code = ACTION_OK_CODE
        self.logger.success("status={}, code={}".format(self.status, self.code))

    def set_failed(self, code: str = None, error: str = None):
        self.end_at = time.time()
        self.status = ActionStatus.FAILED
        self.code = code if code is not None else ACTION_FAILED_CODE
        self.error = error
        self.logger.error("status={}, code={}, error={}".format(self.status, self.code, self.error))

    def closed(self):
        return self.end_at is not None

    def log(self, msg, level: int = logging.INFO):
        if default_config.save_action_messages:
            self.logs.append(ActionLog(content=msg, level=level))
        self.logger.log(level, msg)

    @property
    def logger(self):
        return default_config.logger


@dataclass
class ActuatorState:
    status: ActionStatus = None
    code: str = None
    start_at: int = field(default_factory=lambda: time.time())
    end_at: int = 0
    action_state: Dict[str, ActionState] = field(default_factory=dict)


@dataclass
class ActuatorContext:
    params: Dict = field(default_factory=dict)


@dataclass
class ActuatorOption:
    name: str
    help: str = ""
    actions: List["Action"] = field(default_factory=list)
    interceptors: List[Callable] = None
    timeout: int = None
    info: Dict = None
    params: List["ActionParam"] = field(default_factory=list)
    short_help: str = ""


@dataclass
class ActionOption:
    name: str
    exec: Callable[[ActionState, ActuatorContext], None]
    timeout: int = None
    interceptors: List[Callable] = None


class ActionParamType(enum.Enum):
    STRING = "string"
    BOOL = "bool"
    INTEGER = "int"
    FLOAT = "float"


ActionParamTypeFuncMapping = {
    ActionParamType.STRING: str,
    ActionParamType.BOOL: bool,
    ActionParamType.INTEGER: int,
    ActionParamType.FLOAT: float,
}


@dataclass
class ActionParam:
    name: str
    type: ActionParamType
    required: bool = False
    default: any = None
    help: str = ""
    is_flag: bool = False
    flag_value: str = ""


@dataclass
class GenericActuator(metaclass=abc.ABCMeta):
    cfg: ActuatorOption
    started: bool = False
    state: ActuatorState = field(default_factory=lambda: ActuatorState())
    context: ActuatorContext = field(default_factory=lambda: ActuatorContext())

    def start(self, **kwargs):
        """目前仅支持同步任务，直接调用 exec 即可，暂时不做长任务状态跟踪和同步锁设计"""
        self.started = True
        # 清洗用户输入参数
        cleaned_kwargs = {}
        for param_option in self.cfg.params:
            if param_option.required:
                if param_option.name not in kwargs:
                    raise SageException("Parameter({}) is required, must pass".format(param_option.name))
            val = kwargs.get(param_option.name, param_option.default)
            if val is not None:
                val = ActionParamTypeFuncMapping[param_option.type](val)
            cleaned_kwargs[param_option.name] = val
        self.context.params.update(cleaned_kwargs)
        self.exec()
        self.started = False

    def stop(self):
        self.started = False

    @abc.abstractmethod
    def exec(self):
        NotImplemented

    def __call__(self, **kwargs):
        return self.start(**kwargs)


class GenericAction(metaclass=abc.ABCMeta):
    pass


@dataclass
class Action(GenericAction):
    cfg: ActionOption


@dataclass
class Actuator(GenericActuator):
    def exec(self):
        for action in self.cfg.actions:
            action_state = ActionState()
            self.logger.info("Start to check {}".format(action.cfg.name))
            try:
                action.cfg.exec(action_state, self.context)
                action_state.set_ok()
            except BaseException as err:
                print_exc()
                code, message = format_err(err)
                action_state.set_failed(code, message)
            self.state.action_state[action.cfg.name] = action_state
            self.logger.info("Finish to check {}".format(action.cfg.name))
            self.logger.enter()
        self.merge_state()
        self.logger.enter()
        self.logger.info("All results: \n{}".format(json.dumps(self.get_result(), indent=4)))

    def merge_state(self):
        """合并最终结论"""
        self.logger.info("Start merge results")
        for action_state in self.state.action_state.values():
            if action_state.status == ActionStatus.FAILED:
                self.state.status = ActionStatus.FAILED
                self.state.code = action_state.code
                self.state.end_at = time.time()
                self.logger.error("status={}, code={}".format(self.state.status, self.state.code))
                return
        self.state.status = ActionStatus.OK
        self.state.code = ACTION_OK_CODE
        self.state.end_at = time.time()
        self.logger.success("status={}, code={}".format(self.state.status, self.state.code))

    def get_result(self):
        return {
            "status": self.state.status.value,
            "code": self.state.code,
            "timestamp": format_ts(self.state.end_at),
            "details": {
                name: {
                    "statue": action_state.status.value,
                    "code": action_state.code,
                    "timestamp": format_ts(action_state.end_at),
                    "messages": [log.print() for log in action_state.logs],
                }
                for name, action_state in self.state.action_state.items()
            },
        }

    @property
    def logger(self):
        return default_config.logger


def format_ts(ts: int) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def format_err(err: BaseException) -> Tuple[Optional[str], str]:
    code = getattr(err, "code", None)
    message = getattr(err, "message", str(err))
    return code, message


@dataclass
class ProxyActuatorOption(ActuatorOption):
    exec: Callable[[ActuatorContext], None] = None


@dataclass
class ProxyActuator(GenericActuator):
    """代理执行器，只需声明执行函数的入口"""

    cfg: ProxyActuatorOption

    def exec(self):
        return self.cfg.exec(self.context)
