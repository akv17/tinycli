import inspect
import dataclasses
import typing
import re


def _none_if_empty(v):
    return v if v is not inspect._empty else None


@dataclasses.dataclass
class ParamSignature:
    name: str
    annotation: typing.Any = None
    default: typing.Any = None

    def generate_help(self):
        msg = f'{self.name}'
        if self.annotation is not None:
            msg = f'{msg}: {self.annotation}'
        if self.default is not None:
            msg = f'{msg} (default={self.default})'
        return msg
    
    def match(self, value):
        pass


@dataclasses.dataclass
class Signature:
    params: list[ParamSignature]
    docstr: str = dataclasses.field(repr=False)

    @classmethod
    def from_func(cls, func):
        sig = inspect.signature(func)
        params = [
            ParamSignature(
                name=p.name,
                annotation=_none_if_empty(p.annotation),
                default=_none_if_empty(p.default),
            )
            for p in sig.parameters.values()
        ]
        docstr = func.__doc__
        ob = cls(params=params, docstr=docstr)
        return ob

    def generate_help(self):
        msg = '\n'.join([
            self.docstr,
            '\nParameters:',
            '\n'.join(' ' * 4 + p.generate_help() for p in self.params)
        ])
        return msg


@dataclasses.dataclass
class ParamInput:
    name: str
    value: typing.Any


class InputParsingError(Exception): pass


def parse_input(cmd):
    """
    val
    name=val
    -name=val
    --name=val
    """
    chunks = cmd.split()
    key = None
    val = None
    parsed = []
    trailing = False
    for ch in chunks:
        if '=' in ch:
            parts = ch.split('=')
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) < 2:
                key = parts[0]
                msg = f'value not passed for param \'{key}\''
                raise InputParsingError(msg)
            key = parts[0].lstrip('-')
            val = '='.join(parts[1:])
            parsed.append((key, val))
            key, val = None, None
        elif trailing and not ch.startswith('-'):
            val = ch
            parsed.append((key, val))
            key, val = None, None
            trailing = False
        elif trailing and ch.startswith('-'):
            msg = f'value not passed for param \'{key}\''
            raise InputParsingError(msg)
        elif ch.startswith('-'):
            key = ch.lstrip('-')
            trailing = True
        else:
            key = None
            val = ch
            parsed.append((key, val))
            key, val = None, None
    if trailing:
        msg = f'value not passed for param \'{key}\''
        raise InputParsingError(msg)
    return parsed


def autocommand(func):
    sig = Signature.from_func(func)
    def wrapper():
        import sys
        cmd = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else ''
        cmd = cmd.strip()
        if cmd == '--help':
            msg = sig.generate_help()
            print(msg)
            exit()
        params_in = parse_input(cmd)
        print(params_in)
    return wrapper
