from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import ReplyKeyboardMarkup, KeyboardButton
import json



cancel_text = "Пожалуй, я передумал(а)"
nearby_text = "Есть что-нибудь рядом?"
welcome_text = "Внести запись"

welcome_buttons = [welcome_text, nearby_text]
keyboard_welcome = ReplyKeyboardMarkup.from_column(welcome_buttons, resize_keyboard=True)

size1 = "3 - 4 человека"
size2 = "4 - 5 человек"
size3 = "6 - 7 человек"

sizes = dict({
    1: size1,
    2: size2, 
    3: size3
})

size_buttons = [size1, size2, size3, cancel_text]
keyboard_size = ReplyKeyboardMarkup.from_column(size_buttons, resize_keyboard=True)

type1 = "Больше мелкого: пакеты, бутылки и т.п."
type2 = "Больше крупного: бытовая техника, мебель, стройматериалы..."

types = dict({
    1: "мелкий мусор - пакеты, бутылки и т.п.",
    2: "крупный мусор - бытовая техника, мебель, стройматериалы"
})

type_buttons = [type1, type2, cancel_text]
keyboard_type = ReplyKeyboardMarkup.from_column(type_buttons, resize_keyboard=True)

yes = "Да!"
no = "Нет, продолжим"

yes_no_buttons = [no, yes]
keyboard_yes_no = ReplyKeyboardMarkup.from_column(yes_no_buttons, resize_keyboard=True)

ok = "До встречи!"
keyboard_ok = ReplyKeyboardMarkup.from_column([ok], resize_keyboard=True) 


loc = "Поделиться моей текущей локацией"

keyboard_location = ReplyKeyboardMarkup(
                [
                    [KeyboardButton(loc, request_location=True)],
                    [KeyboardButton(cancel_text)]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
)


keyboard_cancel = ReplyKeyboardMarkup(
                [
                    [KeyboardButton(cancel_text)]
                ],
                resize_keyboard=True
            )

async def button_info(page, num_pages):
    return InlineKeyboardButton(
                text=f'{page}/{num_pages}', 
                callback_data=f' '
                )

async def button_forward(page):
    callback_data = {
        "Method": "pagination",
        "CurrentPage": page + 1}
    return InlineKeyboardButton(
                text="Вперёд --->",
                callback_data=json.dumps(callback_data)
            ) #не могу понять, че за форматирование такое

async def button_backward(page):
    callback_data = {
        "Method": "pagination",
        "CurrentPage": page - 1
    }
    return InlineKeyboardButton(
                text="<--- Назад",
                callback_data=json.dumps(callback_data)
            )

async def button_cancel():
    callback_data = {
        'Method': 'cancel'
        }
    return InlineKeyboardButton(
        text="В другой раз",
        callback_data=json.dumps(callback_data)
    )




         