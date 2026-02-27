import typing as tp

from .args import split_args


class Command:
    _names = {}
    names: list[str] = []

    def __init_subclass__(cls, **kwargs):
        for n in cls.names:
            cls._names[n] = cls

    @classmethod
    def get_command(cls, name: str) -> tp.Optional['Command']:
        return cls._names.get(name)

    @classmethod
    def parse_next(cls, text: str) -> tp.Tuple[str, str]:
        raise NotImplementedError()


class DIR(Command):
    """
    Display a list of files and subfolders.

    Syntax
      DIR [pathname(s)] [display_format] [file_attributes] [sorted] [time] [options]
    """
    names = ['dir', 'DIR']

    @classmethod
    def parse_next(cls, text: str) -> tp.Tuple[str, str]:
        assert text
        parts = split_args(text)
        args = []
        in_pathname = False
        contain_tail = False
        i = 0
        for i, p in enumerate(parts):
            if p and p[0] in ['&', '|', '>', '<', ';']:
                contain_tail = True
                break
            elif not in_pathname and not p.startswith('/'):
                in_pathname = True
                args.append(p)
            elif in_pathname and not p.startswith('/'):
                in_pathname = True
                args[-1] += f" {p}"
            elif in_pathname:  # and p.startswith('/')
                in_pathname = False
                args[-1] = f'"{args[-1]}"'
                args.append(p)
            elif p in cls._names:
                contain_tail = True
                break
            else:
                args.append(p)
        if in_pathname:  # last pathname
            args[-1] = f'"{args[-1]}"'

        remaining = parts[i:] if contain_tail else parts[i + 1:]
        return f'dir {" ".join(args)}', " ".join(remaining)
