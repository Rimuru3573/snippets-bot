# Импорты
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from utils.db import db

# Клавиатура вренутся на главное меню 
def back_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Назад", callback_data="back"))
    return builder.as_markup()

# ФСМ стейты
class Add(StatesGroup):
    snippet = State()
    hashteg = State()

# Роутер
r = Router()

# Стартовый хендлер
def start_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Добавить сниппет", callback_data="add_new"))
    builder.row(InlineKeyboardButton(text="Все хештеги", callback_data="all_hashtegs"))
    return builder.as_markup()

@r.message(CommandStart())
async def start(message: Message):
    await message.answer(text="Бот для создание заметок и сниппетов", reply_markup=start_kb())

@r.callback_query(F.data == "back")
async def start_back(callback: CallbackQuery):
    await callback.message.answer(text="Бот для создание заметок и сниппетов", reply_markup=start_kb())


# Добавление нового сниппета
@r.callback_query(F.data == "add_new")
async def add_new_one(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="Введите текст самого сниппета")
    await state.set_state(Add.snippet)
    
@r.message(Add.snippet)
async def add_new_two(message: Message, state: FSMContext):
    await message.answer(text="Введите хештег для этого сниппета")
    await state.update_data(snippet=message.text)
    await state.set_state(Add.hashteg)

@r.message(Add.hashteg)
async def add_new_three(message: Message, state: FSMContext):
    data = await state.get_data()
    hashteg = message.text
    snippet = data.get("snippet")

    trying = await db.add_snippet(snippet, hashteg)
    if trying == True:
        state.clear()
        await message.answer(text="Успешное добавление сниппета", reply_markup=back_kb())
    else:
        state.set_state(Add.hashteg)
        await message.answer(text="Неверно введен хештег, введите другой")

# Получить все хештеги
@r.callback_query(F.data == "all_hashtegs")
async def all_hashtegs(callback: CallbackQuery):
    data = await db.get_all_hashtegs()

    builder = InlineKeyboardBuilder()
    for x in data:
        builder.row(InlineKeyboardButton(text=f"x. {x[0]}", callback_data=f"hashteg|{x}"))
    
    await callback.message.answer(text="Все хештеги:", reply_markup=builder.as_markup())

@r.callback_query(F.data.startswith("hashteg|"))
async def show_hashteg(callback: CallbackQuery):
    hashteg = callback.data.split("|")[1]
    snippet = await db.search_snippet(hashteg)
    if snippet == "":
        await callback.message.answer(text="Ошибка при поиске сниппета", reply_markup=back_kb())
    else:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="Удалить сниппет", callback_data=f"del|{hashteg}"))
        builder.row(InlineKeyboardButton(text="Назад", callback_data="back"))
        await callback.message.answer(text=snippet, reply_markup=builder.as_markup())

# Удаление сниппета
@r.callback_query(F.data.startswith("del|"))
async def remove(callback: CallbackQuery):
    hashteg = callback.data.split("|")[1]
    del_status = await db.remove_snippet(hashteg)

    if del_status == True:
        await callback.message.answer(text="Успешное удаление", reply_markup=back_kb())
    else: 
        await callback.message.answer(text="Не получилось удалить", reply_markup=back_kb())






