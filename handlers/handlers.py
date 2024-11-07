from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.filters import Command, CommandStart
from aiogram.client.session.aiohttp import AiohttpSession

from config import config
from keyboards import keyboards as kb
from filters.filters import EntityFilter

router = Router()
state_router = Router()
router_storage = MemoryStorage()
session = AiohttpSession()
bot = Bot(token=config.BOT_TOKEN.get_secret_value(), 
          session=session)

class SendMessageState(StatesGroup):
    send_message = State()
    send_contact = State()
    contact = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Hi')
    print (type(SendMessageState.send_message))

@router.message(Command('send'))
async def cmd_send(message: Message, state: FSMContext):
    await state.set_state(SendMessageState.send_message)
    # print(await state.get_state())
    await message.answer('Введите сообщение, которое вы хотите отправить')

@state_router.message(Command('stop'), SendMessageState())
async def cmd_stop(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Stopped')


@state_router.message( SendMessageState.send_message)
async def send_message(message: Message, state: FSMContext):
    await state.update_data(message=message.text)
    await message.answer(text='Отлично!\nТеперь, чтобы на ваше сообщение ответили, отправьте нам свой номер или email по кнопкам ниже.', 
                         reply_markup=kb.contacts)
    await state.set_state(SendMessageState.send_contact)
   
@state_router.callback_query(F.data.startswith('sendcont_'), SendMessageState.send_contact)
async def cb_sendcontact(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'sendcont_email':
        await callback.answer('Вы выбрали отправить email')
        await state.set_state(SendMessageState.contact)
        await callback.message.answer('Введите свой email')
    elif callback.data == 'sendcont_phone':
        await callback.answer('Вы выбрали отправить номер')
        await state.set_state(SendMessageState.contact)
        await callback.message.answer(text='Для отправки номера нажмите кнопку ниже', 
                                         reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отправить номер телефона', 
                                                                                                    request_contact=True)]],
                                                                          resize_keyboard=True,
                                                                          input_field_placeholder='Отправить номер...'))
@state_router.callback_query(F.data.startswith('sendcont_'))
async def no_cb_sendcont(callback: CallbackQuery):
    await callback.answer('Сообщение истекло...')

@state_router.message(F.text, SendMessageState.contact, EntityFilter(['email']))
async def receive_email(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await sending(message=message, state=state)
@state_router.message(F.contact.phone_number, SendMessageState.contact)
async def receive_phone_number(message: Message, state: FSMContext):
    await state.update_data(contact=message.contact.phone_number)
    await sending(message=message, state=state)
@state_router.message(SendMessageState.contact)
async def uncorrect_receive_phone_number(message: Message):
    await message.answer('Неверный формат. Попробуйте еще раз.')


async def sending(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await bot.send_message(chat_id=1748203595, text=f'Получено новое сообщение\n\n{data["message"]}\n\n{data["contact"]}')
    await session.close()
    await message.answer('Сообщение успешно отправлено', reply_markup=ReplyKeyboardRemove())








    

    
