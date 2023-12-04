import click

from bkm_sage.actuator.actions import ActionParamType, Actuator
from bkm_sage.actuator.registry import ActuatorRegistry

ActionParamTypeClickMapping = {
    ActionParamType.BOOL: click.BOOL,
    ActionParamType.STRING: click.STRING,
    ActionParamType.INTEGER: click.INT,
    ActionParamType.FLOAT: click.FLOAT,
}


class ActuatorClickAdapter:
    def __init__(self, act: Actuator):
        self.act = act

    def to_command(self) -> click.Command:
        _comm = self.act
        _comm.__name__ = self.act.cfg.name
        _comm.__doc__ = self.act.cfg.help
        for param_option in self.act.cfg.params:
            _comm = click.option(
                *param_option.decls,
                default=param_option.default,
                required=param_option.required,
                type=ActionParamTypeClickMapping[param_option.type],
                help=f"{'「必填」' if param_option.required else '「选填」'} {param_option.help}",
                is_flag=param_option.is_flag,
                flag_value=param_option.flag_value,
            )(_comm)
        return click.command(short_help=self.act.cfg.short_help)(_comm)


class ActuatorRegistryClickAdapter:
    def __init__(self, registry: ActuatorRegistry):
        self.registry = registry

    def to_group(self, name: str, help: str) -> click.Command:
        fake_func = lambda: None
        fake_func.__name__ = name
        fake_func.__doc__ = help
        group = click.group()(fake_func)
        for act_name, act in self.registry.data.items():
            group.add_command(ActuatorClickAdapter(act).to_command(), act_name)
        return group
