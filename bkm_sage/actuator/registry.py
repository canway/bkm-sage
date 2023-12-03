from typing import Callable, Dict, List

from bkm_sage.actuator.actions import (
    Action,
    ActionOption,
    ActionParam,
    ActionParamType,
    ActionState,
    Actuator,
    ActuatorContext,
    ActuatorOption,
    ProxyActuator,
    ProxyActuatorOption,
)
from bkm_sage.actuator.config import default_config


class ActuatorRegistry:
    _singleton = None

    def __new__(cls, *args, **kwargs):
        if cls._singleton is None:
            cls._singleton = super(ActuatorRegistry, cls).__new__(cls, *args, **kwargs)
        return cls._singleton

    def __init__(self):
        self.data: Dict[str, Actuator] = {}

    def new_actuator(self, option: ActuatorOption) -> Actuator:
        act = Actuator(cfg=option)
        self.data[option.name] = act
        return act

    def new_proxy_actuator(self, option: ProxyActuatorOption) -> ProxyActuator:
        act = ProxyActuator(cfg=option)
        self.data[option.name] = act
        return act

    @classmethod
    def set_logger(cls, logger):
        default_config.logger = logger

    @classmethod
    def set_default_config(cls, config: Dict):
        default_config.update(config)

    @classmethod
    def with_option(
        cls,
        name: str,
        help: str = "",
        short_help: str = "",
        params: List[ActionParam] = None,
        actions: List[ActionOption] = None,
    ) -> ActuatorOption:
        option = ActuatorOption(name=name, help=help, short_help=short_help)
        if params is not None:
            option.params = params
        if actions is not None:
            option.actions = [Action(cfg=opt) for opt in actions]
        return option

    @classmethod
    def with_proxy_option(
        cls,
        name: str,
        exec: Callable[[ActuatorContext], None],
        help: str = "",
        short_help: str = "",
        params: List[ActionParam] = None,
    ) -> ProxyActuatorOption:
        option = ProxyActuatorOption(name=name, help=help, exec=exec, short_help=short_help)
        if params is not None:
            option.params = params
        return option

    @classmethod
    def with_param(
        cls,
        name: str,
        type: str,
        default: any = None,
        help: str = "",
        required: bool = False,
    ) -> ActionParam:
        return ActionParam(name=name, type=ActionParamType(type), default=default, help=help, required=required)

    @classmethod
    def with_action(cls, name: str, exec: Callable[[ActionState, ActuatorContext], None]) -> ActionOption:
        return ActionOption(name=name, exec=exec)
