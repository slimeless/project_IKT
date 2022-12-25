
from aiogram import Bot, Dispatcher, executor, types
from os import getenv
from sys import exit
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.dispatcher.filters.state import StatesGroup, State
import re

from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import aiogram.utils.markdown as fmt
import pandas as pd
from string import Template

foo = pd.read_csv("data/45.csv")["Продукт"].tolist()
food = pd.read_csv("data/45.csv")

foo = [i.lower() for i in foo]
food["Продукт"] = foo

def sortSearch(a):
    inputData = []
    a = str(a).lower().split()
    a = list(map(lambda x: re.sub(r"[\W]", "", x), a))
    for i in range(len(a)):
        if len(a[i]) != 2:
            inputData.append(a[i])

    return inputData


def search(b):
    asd = food
    for i in b:
        asd = asd[[i in c for c in list(asd['Продукт'])]]
    return asd


def endSearch(c):
    end = []
    for i in list(c.index):
        end.append(c.loc[i,].values.tolist())
    return end


def retypeSearch(d):
    for i in range(len(d)):
        for j in range(len(d[0])):
            if j != 0:
                d[i][j] = re.sub(r"[,]", ".", d[i][j])
                d[i][j] = float(re.sub(r"[^0-9.]", "", d[i][j]))

    return d


def DCI(a):
    for i in range(3):

        a[i] = re.sub(r"[,]", ".", str(a[i]))
        a[i] = float(re.sub(r"[^0-9.]", "", a[i]))
    if a[3] == "м":
        a[3] = 5
    elif a[3] == "ж":
        a[3] = -165
    else:
        a[3] = 5
    a[4] = str(a[4])

    if a[4] == "1":
        a[4] = 1.2
    elif a[4] == "2":
        a[4] = 1.38
    elif a[4] == "3":
        a[4] = 1.46
    elif a[4] == "4":
        a[4] = 1.55
    elif a[4] == "5":
        a[4] = 1.64
    elif a[4] == "6":
        a[4] = 1.73
    elif a[4] == "7":
        a[4] = 1.9
    DCI_COMPILLER = int(((a[0] * 10) + (a[1] * 6.25) - (a[2] * 5) + a[3] ) *a[4])
    return DCI_COMPILLER

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit("Error: no token provided")

bot = Bot(token=bot_token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
DCI_Product = []
calo = {}
dci = {}
photo = open('1584210764_12-scaled.jpg', 'rb')

SA = Template(fmt.text(f"""
вес: {fmt.hbold("$ma кг")}
рост:  {fmt.hbold("$sm см")}
возраст: {fmt.hbold("$yo лет")}
пол: {fmt.hbold("$mg")}
ко-оф активности: {fmt.hbold("$kf")}
{fmt.hbold("Всё верно? если да нажми кнопку save")}
"""))

FA = Template(fmt.text(f"""
еда: {fmt.hbold("$food_name ")}
вес: {fmt.hbold("$food_massa грамм ")}
{fmt.hbold("Калорийность твоего приема пищи: $food_cal, всё успешно занесено в список!")}
"""))
FOOD_product = []
class Test(StatesGroup):
    Q1 = State()  # вес
    Q2 = State()  # рост
    Q3 = State()  # возраст
    Q4 = State()  # пол
    Q5 = State()  # коофицент активности


class Food(StatesGroup):
    P1 = State()
    P2 = State()
    P3 = State()


@dp.message_handler(commands='start')
async def start_hendler(message: types.Message):
    await message.reply(
        f"Привет,{fmt.text(fmt.hbold(message.from_user.first_name))}\n напиши /help чтобы узнать список команд")
    dci[message.from_user.id] = 0
    calo[message.from_user.id] = 0




@dp.message_handler(commands='help')
async def help_handler(message: types.Message):
    mrcp = ReplyKeyboardMarkup(resize_keyboard=True)
    mrcp.add("/start", "/test" ,"/calories" ,"/food" ,"/callback")
    await message.reply("Список команд: ", reply_markup=mrcp)
    if message.from_user.id == ADM_ID:
        await message.answer("Добавлены admin-функции",reply_markup=mrcp.add("/admin"))


@dp.message_handler(commands="calories")
async def callories_handler(message: types.Message):
    await message.answer(f"Твоя норма каллорий: {fmt.hbold(str(dci[message.from_user.id]))}\nЗа сегодня ты уже употребил в пищу: {fmt.hbold(str(calo[message.from_user.id]))}")
    if calo[message.from_user.id] > dci[message.from_user.id]:
        await message.answer("лимит на еду превышен, если не хочешь набрать вес лучше не ешь!")
    

ADM_ID = 1104876158


# ------------------------------------------------------------------------------------state----------------------------------------------------------------------------------------------

@dp.message_handler(commands="callback")
async def callback_from_people_handler(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Напиши свой отзыв, буду рад")
    await Food.P3.set()
@dp.message_handler(state=Food.P3)
async def P3_handler(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(answercallback=answer)
    data = await state.get_data()
    answer = data.get("answercallback")
    await message.answer("Очень признателен за отзыв!")
    await bot.send_message(ADM_ID, f"""
У вас новый отзыв/сообщение от 
{fmt.hbold(message.from_user.full_name)}({fmt.hbold(message.from_user.id)})
{fmt.hbold("Текст сообщения:")}
{answer}""")
    await state.finish()




@dp.message_handler(commands=['test'], state=None)
async def test_handler(message: types.Message):
    mrcp = ReplyKeyboardMarkup(resize_keyboard=True)
    await message.answer("Привет, этот тест предназначен для того чтобы узнать твою норму каллорий, поехали!")
    await message.answer("какой у вас вес?" ,reply_markup=mrcp)
    await message.delete()
    await Test.Q1.set()
    DCI_Product.clear()




@dp.message_handler(state=Test.Q1)
async def answerq1(message: types.Message, state: FSMContext):
    mrcp = ReplyKeyboardMarkup(resize_keyboard=True)
    answer = message.text
    await state.update_data(answer1=answer)
    await message.answer("Какой у вас рост?(см)" ,reply_markup=mrcp)

    await Test.Q2.set()



@dp.message_handler(state=Test.Q2)
async def answerq2(message: types.Message, state: FSMContext):
    mrcp = ReplyKeyboardMarkup(resize_keyboard=True)
    answer = message.text
    await state.update_data(answer2=answer)
    await message.answer("Какой у вас возраст?(в годах)" ,reply_markup=mrcp)
    await Test.Q3.set()



@dp.message_handler(state=Test.Q3)
async def answerq3(message: types.Message, state: FSMContext):
    mrcp = ReplyKeyboardMarkup(resize_keyboard=True)

    mrcp.add("м" ,"ж" ,"Другое")
    answer = message.text
    await state.update_data(answer3=answer)
    await message.answer("Какой у вас пол?(м\ж)" ,reply_markup=mrcp)
    await Test.Q4.set()



@dp.message_handler(state=Test.Q4)
async def answerq4(message: types.Message, state: FSMContext):
    mrcp = ReplyKeyboardMarkup(resize_keyboard=True)
    answer = message.text
    await state.update_data(answer4=answer)
    await message.answer(f"""Какой у тебя коофицент активности?
{fmt.hbold("1.20")} - Физическая нагрузка минимальная
{fmt.hbold("1.38")} - Тренировки средней тяжести 3 раза в неделю
{fmt.hbold("1.46")} - Тренировки средней тяжести 5 раза в неделю
{fmt.hbold("1.55")} - Интенсивные тренировки 5 раза в неделю
{fmt.hbold("1.64")} - Тренировки каждый день
{fmt.hbold("1.73")} - Интенсивные тренировки каждый день или по 2 раза в день
{fmt.hbold("1.90")} - Ежедневная физическая нагрузка + физическая работа
""" ,reply_markup=mrcp.add("1.2" ,"1.38" ,"1.46" ,"1.55" ,"1.64" ,"1.73" ,"1.9"))
    await Test.Q5.set()

@dp.message_handler(state=Test.Q5)
async def answerq4(message: types.Message, state: FSMContext):
    mrcp = ReplyKeyboardMarkup(resize_keyboard=True)

    answer = message.text
    await state.update_data(answer5=answer)
    data = await state.get_data()
    DCI_Product.append(data.get("answer1"))
    DCI_Product.append(data.get("answer2"))
    DCI_Product.append(data.get("answer3"))
    DCI_Product.append(data.get("answer4"))
    DCI_Product.append(data.get("answer5"))
    print(DCI_Product)
    await message.answer \
        (SA.substitute(ma=DCI_Product[0], sm=DCI_Product[1], yo=DCI_Product[2], mg=DCI_Product[3], kf=DCI_Product[4]), reply_markup=mrcp.add("/save" ,"/test"))

    await state.finish()


@dp.message_handler(commands="save")
async def save_handler(message: types.Message):
    mrcp = ReplyKeyboardMarkup(resize_keyboard=True)
    if DCI_Product[3] == "м":
        DCI_Product[3] = 5
    elif DCI_Product[3] == "ж":
        DCI_Product[3] = -165
    else:
        DCI_Product[3] = 5
    DCI_INT = int(((float(DCI_Product[0]) * 10) + (float(DCI_Product[1]) * 6.25) - (float(DCI_Product[2]) * 5) + float
        (DCI_Product[3]) ) *float(DCI_Product[4]))
    await message.answer(
        f"{fmt.hbold('Отлично!')}\nтеперь посмотрим какая у вас норма калорий...\n\n\nбиб-буп-бииб-буп!\nНаконец-то!\nВаша норма калорий: {fmt.hbold(str(DCI_INT))}",
        reply_markup=mrcp.add("/help"))
    print(DCI_Product)
    dci[message.from_user.id] = DCI_INT





@dp.message_handler(commands="food" ,state=None)
async def food_handler(message: types.Message ,state: FSMContext):

    await message.answer("Привет! Расскажи что ты съел.")
    if not dci[message.from_user.id]:
        await state.finish()
        await message.answer(fmt.text
            (f"{fmt.hbold(message.from_user.first_name)}, я еще не знаю твою норму калорий!\n\nПожалуйста пройди тест и узнай свою калорийность, а потом обязательно возвращайся.(/test)"))
    else:

        await Food.P1.set()



@dp.message_handler(state=Food.P1)
async def P1_handler(message: types.Message, state: FSMContext):
    mrcp = ReplyKeyboardMarkup(resize_keyboard=True)
    answer = retypeSearch(endSearch(search(sortSearch(message.text))))
    if not answer:
        await message.answer("Упс! такого продукта у нас пока что нет, нажми /food и попробуй еще раз!")
        await state.finish()

    else:
        await state.update_data(answerp1=answer[0])

        await message.answer \
            ("За один прием пищи человек должен съедать от 300 до 350 грамм, по твоим ощущениям сколько ты съел в граммах? ")
        await Food.P2.set()
@dp.message_handler(state=Food.P2)
async def P1_handler(message: types.Message, state: FSMContext):

    await state.update_data(answerp2=message.text)
    data = await state.get_data()
    FOOD_product.append(data.get("answerp1"))
    FOOD_product.append(data.get("answerp2"))
    print(FOOD_product)
    callories = int((int(FOOD_product[1] )//100) * FOOD_product[0][1])
    await message.answer(FA.substitute(food_name=FOOD_product[0][0] ,food_massa=FOOD_product[1] ,food_cal=callories))
    FOOD_product.clear()
    await state.finish()

    calo[message.from_user.id] += callories
    print(calo)


# --------------------------------------------------------------admincosole-----------------------------------------------------------------------------------------------

@dp.message_handler(commands="admin")
async def ADM_console_handler_settings(message:types.Message):
    mrcp = ReplyKeyboardMarkup(resize_keyboard=True)
    await message.answer("функции админ консоли:",reply_markup=mrcp.add("block_user"))



@dp.message_handler()
async def something_handler(message: types.Message):
    mrcp = ReplyKeyboardMarkup()
    await message.answer (fmt.text(f"{fmt.hbold(message.from_user.first_name)}, напиши /help чтобы узнать список комманд")
        ,reply_markup=mrcp.add("/help"))







if __name__ == '__main__':
    executor.start_polling(dispatcher=dp)

