import re
import typing as tp

from .args import split_args

# types
TypeParsed = tp.Tuple[str, str]
TypFunc = tp.Callable[[str], TypeParsed]

# consts
_COMMAND_REGISTRY: tp.Dict[str, TypFunc] = {}
_SEPARATORS = ['&', '&&', '|', '||', '>', '>>', '<']


def get_parse_func(name: str) -> tp.Optional[TypFunc]:
    if name in _SEPARATORS:
        return parse_separator(name)
    elif name in _COMMAND_REGISTRY:
        return _COMMAND_REGISTRY[name]
    return None


def command(names: tp.List[str]):
    """command register"""

    def decorator(func):
        for name in names:
            _COMMAND_REGISTRY[name] = func
        return func

    return decorator


def parse_separator(name: str) -> tp.Optional[TypFunc]:
    """separators"""

    def inner(text: str):
        return name, text

    return inner


@command(names=['cd', 'CD'])
def parse_cd(text: str) -> TypeParsed:
    """
    Change Directory - Select a Folder (and drive)

    Syntax
      CD [/D] [drive:][path]
      CD [../..]
    """
    assert text
    parts = split_args(text)
    args = []
    in_pathname = False
    contain_tail = True
    i = 0
    for i, p in enumerate(parts):
        if p in _SEPARATORS:
            contain_tail = False
            break
        elif not in_pathname and not p.startswith('/'):
            in_pathname = True
            args.append(p)
        elif in_pathname and not p.startswith('/'):
            args[-1] += f' {p}'
        elif in_pathname:  # and p.startswith('/')
            in_pathname = False
            args[-1] = f'"{args[-1]}"'
            # args.append(p)  # not append /d
        elif p in _COMMAND_REGISTRY:
            contain_tail = False
            break
        else:
            pass  # not append /d
    if in_pathname:  # last pathname
        args[-1] = f'"{args[-1]}"'

    remaining = parts[i + 1:] if contain_tail else parts[i:]
    return f'cd /d {" ".join(args)}', " ".join(remaining)


@command(names=['copy', 'COPY'])
def parse_copy(text: str) -> TypeParsed:
    """
    Copy one or more files to another location.

    Syntax
      COPY [options] [/A|/B] source [/A|/B] [+ source2 [/A|/B]...] [destination [/A|/B]]

      COPY source1 + source2 destination [options]
    """
    assert text
    re_drive = re.compile(r'[A-Z]:\\')
    parts = split_args(text)
    args = []
    in_pathname = False
    contain_tail = True
    i = 0
    for i, p in enumerate(parts):
        out_pathname = p.startswith('/') or p == '+'
        if p in _SEPARATORS:
            contain_tail = False  # not contain current p
            break
        elif not in_pathname and not out_pathname:  # may not have quote
            in_pathname = True
            args.append(p)
        elif in_pathname and re_drive.search(p):  # next pathname
            args[-1] = f'"{args[-1]}"'
            args.append(p)
        elif in_pathname and not out_pathname:
            args[-1] += f' {p}'
        elif in_pathname:  # and out_pathname
            in_pathname = False
            args[-1] = f'"{args[-1]}"'
            args.append(p)
        elif p in _COMMAND_REGISTRY:
            contain_tail = False
            break
        else:
            args.append(p)
    if in_pathname:  # last pathname
        args[-1] = f'"{args[-1]}"'

    remaining = parts[i + 1:] if contain_tail else parts[i:]
    return f'copy {" ".join(args)}', " ".join(remaining)


@command(names=['del', 'DEL'])
def parse_del(text: str) -> TypeParsed:
    """
    Delete one or more files.

    Syntax
      DEL [options] [/A:file_attributes] files_to_delete
    """
    assert text
    re_drive = re.compile(r'[A-Z]:\\')
    parts = split_args(text)
    args = []
    in_pathname = False
    contain_tail = True
    i = 0
    for i, p in enumerate(parts):
        out_pathname = p.startswith('/')
        if p in _SEPARATORS:
            contain_tail = False  # not contain current p
            break
        elif not in_pathname and not out_pathname:  # may not have quote
            in_pathname = True
            args.append(p)
        elif in_pathname and re_drive.search(p):  # next pathname
            args[-1] = f'"{args[-1]}"'
            args.append(p)
        elif in_pathname and not out_pathname:
            args[-1] += f' {p}'
        elif in_pathname:  # and out_pathname
            in_pathname = False
            args[-1] = f'"{args[-1]}"'
            args.append(p)
        elif p in _COMMAND_REGISTRY:
            contain_tail = False
            break
        else:
            args.append(p)
    if in_pathname:  # last pathname
        args[-1] = f'"{args[-1]}"'

    remaining = parts[i + 1:] if contain_tail else parts[i:]
    return f'del {" ".join(args)}', " ".join(remaining)


@command(names=['dir', 'DIR'])
def parse_dir(text: str) -> TypeParsed:
    """
    Display a list of files and subfolders.

    Syntax
      DIR [pathname] [options]
      DIR [options] [pathname]
    """
    assert text
    parts = split_args(text)
    args = []
    in_pathname = False
    contain_tail = True
    i = 0
    for i, p in enumerate(parts):
        if p in _SEPARATORS:
            contain_tail = False  # not contain current p
            break
        elif not in_pathname and not p.startswith('/'):  # may not have quote
            in_pathname = True
            args.append(p)
        elif in_pathname and not p.startswith('/'):
            args[-1] += f' {p}'
        elif in_pathname:  # and p.startswith('/')
            in_pathname = False
            args[-1] = f'"{args[-1]}"'
            args.append(p)
        elif p in _COMMAND_REGISTRY:
            contain_tail = False
            break
        else:
            args.append(p)
    if in_pathname:  # last pathname
        args[-1] = f'"{args[-1]}"'

    remaining = parts[i + 1:] if contain_tail else parts[i:]
    return f'dir {" ".join(args)}', " ".join(remaining)


@command(names=['move', 'MOVE'])
def parse_move(text: str) -> TypeParsed:
    """
    Move a file from one folder to another.

    Syntax
      MOVE [options] [Source] [Target]
    """
    assert text
    re_drive = re.compile(r'[A-Z]:\\')
    parts = split_args(text)
    args = []
    in_pathname = False
    contain_tail = True
    i = 0
    for i, p in enumerate(parts):
        out_pathname = p.startswith('/')
        if p in _SEPARATORS:
            contain_tail = False  # not contain current p
            break
        elif not in_pathname and not out_pathname:  # may not have quote
            in_pathname = True
            args.append(p)
        elif in_pathname and re_drive.search(p):  # next pathname
            args[-1] = f'"{args[-1]}"'
            args.append(p)
        elif in_pathname and not out_pathname:
            args[-1] += f' {p}'
        elif in_pathname:  # and out_pathname
            in_pathname = False
            args[-1] = f'"{args[-1]}"'
            args.append(p)
        elif p in _COMMAND_REGISTRY:
            contain_tail = False
            break
        else:
            args.append(p)
    if in_pathname:  # last pathname
        args[-1] = f'"{args[-1]}"'

    remaining = parts[i + 1:] if contain_tail else parts[i:]
    return f'move {" ".join(args)}', " ".join(remaining)


@command(names=['type', 'TYPE'])
def parse_type(text: str) -> TypeParsed:
    """
    Display the contents of one or more text files.

    Syntax
      TYPE [drive:]pathname
      TYPE [drive:]pathname [drive:]pathname
    """
    assert text
    re_drive = re.compile(r'[A-Z]:\\')
    parts = split_args(text)
    args = []
    in_pathname = False
    contain_tail = True
    i = 0
    for i, p in enumerate(parts):
        if p in _SEPARATORS:
            contain_tail = False  # not contain current p
            break
        elif not in_pathname and re_drive.search(p):  # may not have quote
            in_pathname = True
            args.append(p)
        elif in_pathname and not re_drive.search(p):
            args[-1] += f' {p}'
        elif in_pathname:  # and re_drive.search(p)
            args[-1] = f'"{args[-1]}"'
            args.append(p)
        elif p in _COMMAND_REGISTRY:
            contain_tail = False
            break
        else:
            args.append(p)
    if in_pathname:  # last pathname
        args[-1] = f'"{args[-1]}"'

    remaining = parts[i + 1:] if contain_tail else parts[i:]
    return f'type {" ".join(args)}', " ".join(remaining)
