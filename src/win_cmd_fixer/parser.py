from .commands import Command


def fix_cmd(text: str) -> str:
    """main function"""
    remaining = text
    output = []
    while remaining:
        first, others = remaining.split(' ', 1)
        if cmd_cls := Command.get_command(first):
            first_cmd, remaining = cmd_cls.parse_next(others)
            output.append(first_cmd)
        else:
            output.append(remaining)  # Cannot parse {first} yet, I'm developing...
            break
    return ' '.join(output)
