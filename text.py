import re

from num2words import num2words

from heidi.etext import access, delivery, general

# SECTION: General

YAY, NAY = 'Да', 'Нет'
SUPPORT_EMAIL = 'my@boris.wtf'
PWA_LINK = '< классное PWA-приложение / будущее >'

# SECTION: Errors

NICE_TRY = 'Хорошая попытка'

THINK_AGAIN = 'Подумайте еще'

EPERM = '''Я такого не умею или вам такое нельзя:(
Попробуйте почитать хелпарик - /help'''

CHOCO_AWAITS = f'Поздравляю! Вы выйграли вкуснейшую шоколадку! Для получения запечатлейте последние пять минут своей невероятной жизни в тексте и отправьте на {SUPPORT_EMAIL}.'

CODE_ERROR = '''Я таких не выписывала или это было слишком давно.
Попробуйте ввести код еще раз или:
1) запросите новый командой /repeat;
2) сотрите мне память командой /reset.'''

localized = {
    access.UNKNOWN_EMAIL:
    f'''Хм... вроде и похоже, но в деканатских данных таких нет.
Введите чего-нибудь другое или напишите специально обученной команде решателей всяческих проблем на {SUPPORT_EMAIL} – разберемся.''',
    access.CONTACT_EXISTS: CHOCO_AWAITS,
    access.BAD_CODE: CODE_ERROR,
    access.NO_CODE: CHOCO_AWAITS,
    access.CODE_NOT_FOUND: CODE_ERROR,
    general.VALIDATION_ERROR: THINK_AGAIN,
    # TODO: Limit exceeded
    delivery.HISTORY_KEY_NOT_FOUND: CHOCO_AWAITS,
}

SOMETHING_AWFUL = \
    '''Чего-то где-то сломалось. Я знаю. Наверное. Заходите позже.'''

# MARK: handlers.setup

ALREADY_ACQUAINTED = 'Мы уже начали'

CONFIRMATION_CODE_SENT = 'Введите код подтверждения из письма'

CONFIRMATION_CODE_SENT_AGAIN = 'Отправили код еще раз, можете вводить'

RESET = r'Нормально же общались ┐(￣ヘ￣;)┌'

CONFIRMATION_DONE = \
    '''Узнала. Согласна. Жду. 
Если вам нужна помощь – наберите /help.'''

# MARK: handlers.select

SESSION_EXPIRED = 'Это слишком старая кнопка. Не надо больше на неё нажимать.'

NO_OWNERSHIP = \
    f'''За вами не закреплено ни единой учебной группы.
Попробуйте написать нам на {SUPPORT_EMAIL}.'''

# TODO: Or create virtual group in the PWA-application -> link
NO_SUBSCRIBERS = \
    f'''В закрепленных за вами группах нет подписанных студентов(9(9(
Подсказка: Заставьте их подписаться!'''

# SECTION: handlers.setup

ACQUAINTANCE = [
    'Мы не знакомы', 'Расскажите немного о себе',
    'Начните с Военмеховской почты'
]

# SECTION: handlers.unlink

UNLINK_WARNING = '''Я вас забуду, а потом просто так не вспомню, вы уверены?'''

UNLINK_FINISH = '''(*-_-)'''

UNLINK_CANCELLED = '''Куда же вы без меня;3'''

# SECTION: handlers.select

SELECT_DONE_BTN = 'Готово'
SELECT_GROUP_BTN = 'Группы'
SELECT_SGROUP_BTN = 'Потоки'

SELECT_HEADER = \
    '''Выберите получателей. Выделение можно снять повторным нажатием.'''

NOTHING_SELECTED = 'Вы ничего не выбрали – я ничего не отправлю.'


def closed_select(selected):
    recipients = ', '.join(group.alias for group in selected)
    return \
        f'''Список групп-получателей: {recipients}
Введите текст сообщения.
_* Если вы вдруг ошиблись, передумали или еще чего – используйте команду /cancel._'''


DELIVERY_CANCELLED = 'Доставка отменена'
DELIVERY_QUEUED = 'Сообщение передано в доставку'


def delivery_feedback(scheduled, deliver_at, all_couriers_ok, recipients):
    recipients = any(recipient['received_in'] for recipient in recipients)

    if scheduled:
        fmt = deliver_at.strftime('%H:%M %d.%m')
        return f'Доставят в {fmt}'

    if all_couriers_ok and recipients:
        return 'Все кто хотел - получили, кто не хотел - не получит'
    elif not all_couriers_ok and recipients:
        return 'Кто-то чего-то получил, но один из курьеров потерялся в пути'
    elif not all_couriers_ok and not recipients:
        return 'Все сломалось и никто ничего не получил'
    else:
        return 'Никто ничего не получил, но так и должно быть'


def ru_number_and_noun(nominative, genitive, plural, number):
    if number == 1:
        return nominative

    number_repr, noun = str(number), None
    if number_repr.endswith('1'):
        if number_repr.endswith('11'):
            noun = plural
        else:
            noun = nominative
    else:
        for suffix in ['2', '3', '4']:
            if number_repr.endswith(suffix) and \
                    not number_repr.endswith('1' + suffix):
                noun = genitive

        if noun != genitive:
            noun = plural
    return f'{num2words(number, lang="ru")} {noun}'


def queue_limit_exceeded(limit):
    minutes = limit.ttl // 60
    hours, minutes_mod = divmod(minutes, 60)
    if hours:
        if minutes_mod > 30:
            hours += 1

        cooldown = ru_number_and_noun('час', 'часа', 'часов', hours)
    else:
        if minutes:
            cooldown = ru_number_and_noun('минуту', 'минуты', 'минут', minutes)
        else:
            cooldown = ru_number_and_noun('секунду', 'секунды', 'секунд',
                                          limit.ttl)

        cooldown = re.sub(r'один(?![а-яА-Я])', 'одну', cooldown)
        cooldown = re.sub(r'два(?![а-яА-Я])', 'две', cooldown)

    ru_limit = '%s в сутки' % ru_number_and_noun('сообщение', 'сообщения',
                                                 'сообщений', limit.daily)

    ru_limit = re.sub(r'один(?![а-яА-Я])', 'одно', ru_limit)
    return f'''Вы превысили лимит на оповещение - {ru_limit}.

Попробуйте снова через {cooldown}.'''


# SECTION: handlers.help

HELP_STRANGER = '/start'

HELP_STUDENT = \
'''Огорчаю новостями об отмене пар.

Использование: `/команда`

*# Команды*
Регистронезависимы.

/unlink
Делает страшные вещи.

/help
Выводит вот это вот все.'''


HELP_TRAINER = \
'''Передаю заинтересованным студентам ваши слова.

Использование: `/команда`

*# Команды*
Регистронезависимы.

/select
Осуществляет оповещение с предварительным выбором адресатов через набор специальных кнопок.

/unlink
Делает страшные вещи.

/help
Выводит вот это вот все.'''

HELP_STAFF = HELP_TRAINER


def help(role):
    if role == 'student':
        return HELP_STUDENT
    elif role == 'trainer':
        return HELP_TRAINER
    elif role == 'staff':
        return HELP_STAFF
    else:
        return HELP_STRANGER
