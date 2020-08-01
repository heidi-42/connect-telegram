from heidi.data import SuperGroup

from handlers.select.markup import SUPERGROUP


def find_by_id(id, iterable):
    for group in iterable:
        if group.id == id:
            return group


def mark_as_selected(ctx, key):
    if isinstance(key, SuperGroup):
        contents = ctx.supergroups[key]
        is_selected = all(group in ctx.selected for group in contents)

        if not is_selected:
            for group in contents:
                ctx.selected.add(group)
        else:
            for group in contents:
                ctx.selected.remove(group)
    else:  # if `heidi.data.Group`
        if key in ctx.selected:
            ctx.selected.remove(key)
        else:
            ctx.selected.add(key)


def where_subscribers(ctx):
    groups = []
    supergroups = {}

    for group in ctx.groups:
        if group in ctx.subscribers:
            groups.append(group)
    groups.sort(key=lambda group: group.alias)

    for group in groups:
        for supergroup, contents in ctx.supergroups.items():
            if group in contents:
                if supergroup not in supergroups:
                    supergroups[supergroup] = []
                supergroups[supergroup].append(group)
    return groups, supergroups


def validate_and_decompose(callback_data):
    parts = callback_data.split(':')
    if len(parts) != 2:
        return None, None

    if not parts[1].isdigit():
        return None, None

    return parts[0] == SUPERGROUP, int(parts[1])
