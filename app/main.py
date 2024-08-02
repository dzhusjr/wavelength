import json
from random import randint,choice
from utils import progressbar
from telebot import TeleBot
from telebot import types

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access environment variables
TOKEN = os.getenv('TOKEN')


bot = TeleBot(TOKEN)

#work with multiple users
with open('data.json', 'r') as f:
    data = json.load(f)

def save_data():
    global data
    with open('data.json', 'w') as f:
        json.dump(data, f,indent=4)
    with open('data.json', 'r') as f:
        data = json.load(f)

#keyboards
def keyboard_main():
    return types.ReplyKeyboardMarkup(True, False).add(
    types.KeyboardButton(text="Create Room 🏠"),
    types.KeyboardButton(text="Join Room 🔑"),)

def keyboard_back():
    return types.ReplyKeyboardMarkup(True, False).add(types.KeyboardButton(text = "Back 🔙"))

def join_room(message):
    global data
    if message.text == "Back 🔙":
        bot.send_message(message.chat.id,'Choose one of the options below:',reply_markup=keyboard_main())
        return
    elif message.text.isdigit():
        if message.text in data["rooms"]:
            room_code = message.text
            data["rooms"][room_code]["players"].append(message.chat.id)
            data["rooms"][room_code]["cards"] = [choice(data["cards"]) for _ in range(7)]
            data["rooms"][room_code]["score"] = 0
            data["rooms"][room_code]["value"] = randint(-10,10)
            save_data()
            bot.send_message(message.chat.id,'Room joined! Wait for the other player to start the game.',reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(data["rooms"][room_code]["players"][0],f'{message.from_user.first_name} has joined the room.',reply_markup=types.ReplyKeyboardRemove())
            round(room_code, data["rooms"][room_code]["players"][0])
        else:
            bot.send_message(message.chat.id,'Such room does not exist! Choose one of the options below:',reply_markup=keyboard_main())
            return
    else:
        bot.send_message(message.chat.id,'Wrong input! Choose one of the options below:',reply_markup=keyboard_main())
        return
    
def round(room_code, chat_id):
    global data
    data["rooms"][room_code]["value"] = randint(-10,10)
    card = data["rooms"][room_code]["cards"][0]
    data["rooms"][room_code]["cards"].pop(0)
    save_data()
    # teammate = data["rooms"][room_code]["players"]
    # teammate = teammate.remove(chat_id)[0]
    # bot.send_message(chat_id,f'{card[0] + " - " + card[1] + "\n" +progressbar(data["rooms"][room_code]["value"])}')
    bot.send_message(chat_id,f'{card[0] + " - " + card[1] + "\nValue: " + data["rooms"][room_code]["value"]}', parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(chat_id,'Please give your clue:',reply_markup=types.ReplyKeyboardRemove())
    x = data["rooms"][room_code]["players"][:]
    x.remove(chat_id)
    bot.register_next_step_handler_by_chat_id(chat_id, ask_guess, x[0], room_code,card)

def get_score(message, room_code, chat_id):
    global data
    if message.text in ["Back 🔙", "Create Room 🏠", "Join Room 🔑"]: 
        bot.send_message(message.chat.id,"You are already in a game! Please continue playing. Try again:",reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler_by_chat_id(message.chat,id, get_score, room_code, chat_id)
    if not message.text.replace('-','').isdigit():
        bot.send_message(message.chat.id,'Wrong input! Try again (from -10 to 10):',reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler_by_chat_id(message.chat,id, get_score, room_code, chat_id)
        return
    guess = int(message.text)
    value = data["rooms"][room_code]["value"]
    diff = abs(guess - value)
    score = 0 if diff > 3 else 3 - diff
    if score == 3: data["rooms"][room_code]["cards"].append(choice(data["cards"])) #bonus card
    data["rooms"][room_code]["score"] += score
    x = data["rooms"][room_code]["players"][:]
    x.remove(chat_id)
    bot.send_message(chat_id,f'You scored: *{score}* points!\nCorrect answer: *{value}*\nTotal score: *{data["rooms"][room_code]["score"]}*', parse_mode='Markdown',reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(x[0],f"Your teammate scored: *{score}* points!\nTeammate's guess: *{guess}*\nCorrect answer: *{value}*.Cards remaining: *{len(data['rooms'][room_code]['cards'])}*\nTotal score: *{data["rooms"][room_code]["score"]}*", parse_mode='Markdown',reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(x[0],"Now it's your turn to guess. Please wait for the clue.",reply_markup=types.ReplyKeyboardRemove())
    if len(data["rooms"][room_code]["cards"]) > 0:
        round(room_code, chat_id)
    else:
        bot.send_message(data["rooms"][room_code]["players"][0],f'The end! Your score: {data["rooms"][room_code]["score"]}\nYou {"won" if data["rooms"][room_code]["score"] >= 16 else "lost"}!',reply_markup=keyboard_back())
        bot.send_message(data["rooms"][room_code]["players"][1],f'The end! Your score: {data["rooms"][room_code]["score"]}',reply_markup=keyboard_back())
        data["rooms"].pop(room_code)
    save_data()

def ask_guess(message, chat_id, room_code, card):
    if message.text in ["Back 🔙", "Create Room 🏠", "Join Room 🔑"]: 
        bot.send_message(message.chat.id,"You are already in a game! Please continue playing. Try again:",reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler_by_chat_id(message.chat.id, ask_guess, chat_id, room_code,card)
    bot.send_message(message.chat.id,"Thanks! Please, wait for your teammate's guess.",reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(chat_id,f'Your teammate gave a clue for *{card[0]} - {card[1]}*: "{message.text}"\nPlease guess the value from -10 to 10:', parse_mode='Markdown', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler_by_chat_id(chat_id, get_score, room_code, chat_id)

#handlers
@bot.message_handler(commands=["start"])
def func(message):
    bot.send_message(message.chat.id,"Hello! Welcome to Wavelength game (/rules)!\nChoose one of the options below:", reply_markup = keyboard_main())
    bot.register_next_step_handler(message, func)

@bot.message_handler(commands=["rules"])
def func(message):
    bot.send_message(message.chat.id,"""
*Wavelength (Cooperative Mode) Rules*

*Goal:*
- Work together to score points by guessing as close as possible to the hidden value on a spectrum from *-10 to 10*.

*Setup:*
- One player (the *"Psychic"*) knows the target value on the spectrum.

*Play:*
1. *Psychic Clue*: Gives a clue related to the spectrum (e.g., "Hot-Cold").
2. *Teammates' Guess*: Based on the clue, teammates decide where to place the marker on the spectrum.

*Scoring:*
- *Perfect Guess* (exact value): *3 points* and a bonus card.
- *1 away from correct value*: *1 point*.
- *2 away from correct value*: *1 point*.
- *3 or more away from correct value*: *0 points*.

*Win Condition:*
- Accumulate *more than 16 points* before the game ends.
- *Deck of Cards*: Start with 7 random cards. The game ends when the deck runs out.

*Bonus Card:*
- Guessing exactly right gives a *bonus card*, adding an extra round to the game.
                     
*Clue Example:* 
- If the Psychic gives the clue "Coffee" and the target value is 5, teammates should guess around 5 on the spectrum, since coffee is warmer than middle but not the hottest.

*Summary:* 
Guess close to the hidden value. Score points based on how close your guess is. Use bonus cards wisely to extend gameplay. Aim for over 16 points to win.
""", reply_markup = keyboard_main(), parse_mode="Markdown")
    bot.register_next_step_handler(message, func)

@bot.message_handler(commands=["get_invite_link"])
def func(message):
    bot.send_message(message.chat.id,"You can invite friends, sending them this link: https://t.me/wavelength_game_bot", reply_markup = keyboard_main())


#main handler
@bot.message_handler(func=lambda msg: True)
def func(message):
    global data
    if message.text == "Back 🔙":
        bot.send_message(message.chat.id,'Choose one of the options below:',reply_markup=keyboard_main())
        return
    elif message.text == "Create Room 🏠":
        room_code = randint(100000, 999999)
        while room_code in data["rooms"]:
            room_code = randint(100000, 999999)
        data["rooms"][str(room_code)] = {}
        data["rooms"][str(room_code)]["players"] = [message.chat.id]
        save_data()
        bot.send_message(message.chat.id,f"Your room code: `{room_code}`. Copy it and send it to your friend.",reply_markup=types.ReplyKeyboardRemove(), parse_mode="Markdown")
        return

    elif message.text == "Join Room 🔑":
        bot.send_message(message.chat.id,"Enter the room code:",reply_markup=keyboard_back())
        bot.register_next_step_handler(message, join_room)

    
    else:
        bot.send_message(message.chat.id,"Choose one of the options below:",reply_markup=keyboard_main())
        return

bot.infinity_polling()
