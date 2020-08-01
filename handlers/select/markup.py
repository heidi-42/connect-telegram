from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import text

GROUP = 'GROUP'
SUPERGROUP = 'SUPERGROUP'
DONE = 'DONE'


def inline_button(contents, callback_data):
    return InlineKeyboardButton(contents, callback_data=callback_data)


def select_button(group, is_selected, is_super=False):
    contents = group.alias
    if is_selected:
        contents = f'[{contents}]'

    kind = SUPERGROUP if is_super else GROUP
    return inline_button(contents, f'{kind}:{group.id}')


def render(ctx):
    if ctx.selected_tab == GROUP:
        return groups_markup(ctx.groups,
                             ctx.selected,
                             include_tab_switch=len(ctx.supergroups) > 0)
    else:
        return supergroups_markup(ctx.supergroups, ctx.selected)


ROW_CAPACITY = 4
SHORT_MAX_CHARS = 7


def groups_markup(groups, selected, include_tab_switch):
    markup = InlineKeyboardMarkup(row_width=ROW_CAPACITY)

    def to_select_button(group):
        return select_button(group, group in selected)

    for group in filter(lambda g: len(g.alias) <= SHORT_MAX_CHARS, groups):
        markup.add(to_select_button(group))

    for group in filter(lambda g: len(g.alias) > SHORT_MAX_CHARS, groups):
        markup.row(to_select_button(group))

    markup.row(inline_button(text.SELECT_DONE_BTN, DONE))
    if include_tab_switch:
        markup.add(inline_button(text.SELECT_SGROUP_BTN, SUPERGROUP))

    return markup


def supergroups_markup(supergroups, selected):
    markup = InlineKeyboardMarkup()

    def to_group_button(supergroup, contents):
        is_selected = all(group in selected for group in contents)
        return select_button(supergroup, is_selected, True)

    for supergroup, contents in supergroups.items():
        markup.row(to_group_button(supergroup, contents))

    markup.row(inline_button(text.SELECT_DONE_BTN, DONE))
    markup.add(inline_button(text.SELECT_GROUP_BTN, GROUP))
    return markup
