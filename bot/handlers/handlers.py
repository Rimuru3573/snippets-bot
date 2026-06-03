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
    builder.row(InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main"))
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
    builder.row(InlineKeyboardButton(text="➕ Добавить сниппет", callback_data="add_new"))
    builder.row(InlineKeyboardButton(text="  🏷 Все хештеги", callback_data="all_hashtegs"))
    return builder.as_markup()

@r.message(CommandStart())
async def start(message: Message):
    await message.answer(
    text=(
        "📦 *Snippets Bot* — Твоя карманная база знаний\n\n"
        "Привет! Это пространство для удобного хранения кода, заметок и быстрых мыслей. "
        "Все сниппеты индексируются по хештегам, чтобы ты мог найти нужный фрагмент в один клик.\n\n"
        "💻 *Выбери действие в меню ниже:* "
    ),
    reply_markup=start_kb(),
    parse_mode="Markdown"
)

@r.callback_query(F.data == "back_to_main")
async def process_back_to_main(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.clear()

    await callback.message.edit_text(
        text=(
            "📦 *Snippets Bot* — Твоя карманная база знаний\n\n"
            "Привет! Это пространство для удобного хранения кода, заметок и быстрых мыслей. "
            "Все сниппеты индексируются по хештегам, чтобы ты мог найти нужный фрагмент в один клик.\n\n"
            "💻 *Выбери действие в меню ниже:*"
        ),
        reply_markup=start_kb(),
        parse_mode="Markdown"
    )


# Добавление нового сниппета
@r.callback_query(F.data == "add_new")
async def add_new_one(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Add.snippet)
    
    await callback.message.edit_text(
        text=(
            "📝 *Шаг 1 из 2: Добавление сниппета*\n\n"
            "Отправьте следующим сообщением код, команду или текст, который вы хотите сохранить.\n\n"
            "💡 _Подсказка: форматирование кода (моноширинный шрифт) тоже поддерживается!_"
        ),
        reply=back_kb(),
        parse_mode="Markdown"
    )
    
@r.message(Add.snippet)
async def add_new_two(message: Message, state: FSMContext):
    await state.update_data(snippet=message.text)
    await state.set_state(Add.hashteg)

    await message.answer(
        text=(
            "🏷 *Шаг 2 из 2: Привязка хештега*\n\n"
            "Отлично, текст сниппета зафиксирован!\n"
            "Теперь отправьте хештег для этой заметки (например: `#python`, `#deploy` или `#todo`)."
        ),
        reply_markup=back_kb(),
        parse_mode="Markdown"
    )

@r.message(Add.hashteg)
async def add_new_three(message: Message, state: FSMContext):
    data = await state.get_data()
    hashteg = message.text
    snippet = data.get("snippet")

    trying = await db.add_snippet(snippet, hashteg)
    if trying == True:
        await state.clear()
        await message.answer(
            text=(
                "✅ *Успех! Сниппет сохранен*\n\n"
                "Запись успешно добавлена в базу данных и проиндексирована. "
                "Теперь вы можете найти её через меню всех хештегов."
            ),
            reply_markup=back_kb(),
            parse_mode="Markdown"
        )
    else:
        state.set_state(Add.hashteg)
        await message.answer(
            text=(
                "⚠️ *Ошибка добавления*\n\n"
                "Похоже, хештег введен некорректно или нарушает правила форматирования.\n"
                "Пожалуйста, попробуйте отправить другой вариант (например: `#notes`):"
            ),
            reply_markup=back_kb(state),
            parse_mode="Markdown"
        )

# Получить все хештеги
@r.callback_query(F.data == "all_hashtegs")
async def all_hashtegs(callback: CallbackQuery):
    await callback.answer()
    data = await db.get_all_hashtegs()

    if not data:
        await callback.message.edit_text(
            text=(
                "🏷 *Ваша база хештегов пуста*\n\n"
                "Вы еще не сохранили ни одного сниппета. Самое время добавить первый!"
            ),
            reply_markup=back_kb(),
            parse_mode="Markdown"
        )
        return

    builder = InlineKeyboardBuilder()
    for tag_name in data:
        builder.row(InlineKeyboardButton(text=f"▪️ {tag_name[0]}", callback_data=f"hashteg|{tag_name[0]}"))
    builder.row(InlineKeyboardButton(text="⬅️ Главное меню", callback_data="back_to_main"))

    await callback.message.edit_text(
        text=(
            "🏷 *Ваша база хештегов*\n\n"
            "Выберите нужный тег из списка ниже, чтобы просмотреть сохраненный фрагмент или удалить его:"
        ),
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@r.callback_query(F.data.startswith("hashteg|"))
async def show_hashteg(callback: CallbackQuery):
    await callback.answer()
    hashteg = callback.data.split("|")[1]
    snippet = await db.search_snippet(hashteg)

    if snippet == "" or snippet is None:
        await callback.message.edit_text(
            text=(
                "⚠️ *Ошибка при поиске сниппета*\n\n"
                f"Не удалось найти данные по тегу `{hashteg}`. Возможно, запись была удалена."
            ),
            reply_markup=back_kb(),
            parse_mode="Markdown"
        )
    else:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🗑 Удалить сниппет", callback_data=f"del|{hashteg}"))
        builder.row(InlineKeyboardButton(text="⬅️ Главное меню", callback_data="back_to_main"))
        await callback.message.edit_text(
            text=(
                f"🏷 *Тег:* `{hashteg}`\n"
                f"───────────────────\n"
                f"📝 *Содержимое сниппета:*\n\n"
                f"```\n{snippet}\n```" # Оборачиваем в моноширинный блок для копирования в один клик
            ),
            reply_markup=builder.as_markup(),
            parse_mode="Markdown"
        )

# Удаление сниппета
@r.callback_query(F.data.startswith("del|"))
async def remove(callback: CallbackQuery):
    await callback.answer()

    hashteg = callback.data.split("|")[1]
    del_status = await db.remove_snippet(hashteg)

    if del_status:
        await callback.message.edit_text(
            text=(
                f"🗑 *Сниппет успешно удален*\n\n"
                f"Запись с хештегом `{hashteg}` была безвозвратно стерта из базы данных."
            ),
            reply_markup=back_kb(),
            parse_mode="Markdown"
        )
    else: 
        await callback.message.edit_text(
            text=(
                f"⚠️ *Ошибка удаления*\n\n"
                f"Что-то пошло не так при попытке удалить сниппет `{hashteg}`. "
                f"Возможно, запись уже была удалена ранее."
            ),
            reply_markup=back_kb(),
            parse_mode="Markdown"
        )






