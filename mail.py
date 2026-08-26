import telebot
import json
import os
from datetime import datetime
import random
import time
import re
from collections import Counter
import threading
import shutil

TOKEN = "8759519021:AAHasUoViUffO7qyjtntnxFMK52za_rcW8E"
bot = telebot.TeleBot(TOKEN)

DATA_FILE = "users_data.json"
ADMINS_FILE = "admins.json"
SHOP_FILE = "shop_items.json"
TICKETS_FILE = "tickets.json"
PROMO_FILE = "promocodes.json"
LOSE_IMAGE_PATH = "roulette_lose.jpg"
WIN_IMAGE_PATH = "roulette_win.jpg"
MENU_IMAGE_PATH = "menu_image.jpg"
DATA_BACKUP_FILE = "users_data_backup.json"
FROG_LOSE_IMAGE_PATH = "frog_lose.jpg"
FROG_WIN_IMAGE_PATH = "frog_win.jpg"
POCKET_IMAGE_PATH = "pocket_image.jpg"  # ДОБАВЛЕНО

# ========== УЛУЧШЕННАЯ ЗАГРУЗКА ДАННЫХ С РЕЗЕРВИРОВАНИЕМ ==========
def load_data():
    """Загружает данные, при ошибке пытается восстановить из резервной копии."""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data:
                    with open(DATA_BACKUP_FILE, 'w', encoding='utf-8') as bf:
                        json.dump(data, bf, indent=4, ensure_ascii=False)
                return data
    except Exception as e:
        print(f"Ошибка загрузки основного файла: {e}")
        try:
            if os.path.exists(DATA_BACKUP_FILE):
                with open(DATA_BACKUP_FILE, 'r', encoding='utf-8') as bf:
                    data = json.load(bf)
                    print("Данные восстановлены из резервной копии.")
                    return data
        except Exception as be:
            print(f"Не удалось загрузить резервную копию: {be}")
    return {}

def save_data(data):
    """Сохраняет данные, предварительно создавая резервную копию."""
    try:
        if os.path.exists(DATA_FILE):
            shutil.copy2(DATA_FILE, DATA_BACKUP_FILE)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Ошибка сохранения данных: {e}")
        if os.path.exists(DATA_BACKUP_FILE):
            shutil.copy2(DATA_BACKUP_FILE, DATA_FILE)
            print("Восстановлены данные из резервной копии.")
        return False

# ========== РАБОТА С ПРОМОКОДАМИ ==========
def load_promocodes():
    try:
        if os.path.exists(PROMO_FILE):
            with open(PROMO_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки промокодов: {e}")
    return {}

def save_promocodes(promos):
    try:
        with open(PROMO_FILE, 'w', encoding='utf-8') as f:
            json.dump(promos, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Ошибка сохранения промокодов: {e}")
    return False

def init_promocode():
    promos = load_promocodes()
    if "zo34435" not in promos:
        promos["zo34435"] = {
            "reward": 100_000_000_000,
            "max_uses": 10,
            "used": 0,
            "users": []
        }
        save_promocodes(promos)

init_promocode()

# ========== ФУНКЦИЯ ЭКРАНИРОВАНИЯ ДЛЯ MARKDOWN ==========
def escape_markdown(text):
    if text is None:
        return ""
    chars = ['_', '*', '`', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for ch in chars:
        text = text.replace(ch, f'\\{ch}')
    return text

# ========== РАБОТА С АДМИНАМИ ==========
def load_admins():
    try:
        if os.path.exists(ADMINS_FILE):
            with open(ADMINS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки админов: {e}")
    return []

def save_admins(admins):
    try:
        with open(ADMINS_FILE, 'w', encoding='utf-8') as f:
            json.dump(admins, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Ошибка сохранения админов: {e}")
    return False

def is_admin(user_id):
    admins = load_admins()
    return str(user_id) in admins

def add_admin(user_id):
    admins = load_admins()
    if str(user_id) not in admins:
        admins.append(str(user_id))
        save_admins(admins)
        return True
    return False

# ========== ОСНОВНЫЕ ФУНКЦИИ ==========
def get_user_data(user_id):
    data = load_data()
    user_id_str = str(user_id)
    if user_id_str not in data:
        data[user_id_str] = {
            'balance': 0,
            'pocket': 0,
            'clicks': 0,
            'last_click': None,
            'referrals': 0,
            'referred_by': None,
            'username': None,
            'first_name': None,
            'referral_earned': 0,
            'work_transport': 'пешком',
            'work_orders': 0,
            'work_earned': 0,
            'roulette_bet': 0,
            'last_order_time': time.time(),
            'next_work_delay': random.choice([15, 30, 60]),
            'last_manual_order_time': 0,
            'manual_cooldown': 0,
            'transfer_history': [],
            'temp_receiver': None,
            'banned': False,
            'referral_level1': [],
            'referral_level2': [],
            'referral_clicks_bonus': 0,
            'referral_clicks_count': 0,
            'roulette_always_win': False,
            'daily_bonus_time': 0,
            'treasure_hunts': 0,
            'treasure_found': 0,
            'treasure_earned': 0,
            'last_treasure_time': 0,
            'postal_hunts': 0,
            'postal_found': 0,
            'postal_earned': 0,
            'last_postal_time': 0,
            'inventory': [],
            'equipped_item': None,
            'trade_state': None,
            'trade_partner': None,
            'trade_offer': None,
            'trade_created_at': 0,
            'activated_promos': []
        }
        save_data(data)
    else:
        user = data[user_id_str]
        if 'pocket' not in user:
            user['pocket'] = 0
        if 'transfer_history' not in user:
            user['transfer_history'] = []
        if 'temp_receiver' not in user:
            user['temp_receiver'] = None
        if 'banned' not in user:
            user['banned'] = False
        if 'referral_level1' not in user:
            user['referral_level1'] = []
        if 'referral_level2' not in user:
            user['referral_level2'] = []
        if 'referral_clicks_bonus' not in user:
            user['referral_clicks_bonus'] = 0
        if 'referral_clicks_count' not in user:
            user['referral_clicks_count'] = 0
        if 'roulette_always_win' not in user:
            user['roulette_always_win'] = False
        if 'daily_bonus_time' not in user:
            user['daily_bonus_time'] = 0
        if 'treasure_hunts' not in user:
            user['treasure_hunts'] = 0
        if 'treasure_found' not in user:
            user['treasure_found'] = 0
        if 'treasure_earned' not in user:
            user['treasure_earned'] = 0
        if 'last_treasure_time' not in user:
            user['last_treasure_time'] = 0
        if 'postal_hunts' not in user:
            user['postal_hunts'] = 0
        if 'postal_found' not in user:
            user['postal_found'] = 0
        if 'postal_earned' not in user:
            user['postal_earned'] = 0
        if 'last_postal_time' not in user:
            user['last_postal_time'] = 0
        if 'first_name' not in user:
            user['first_name'] = None
        if 'inventory' not in user:
            user['inventory'] = []
        if 'equipped_item' not in user:
            user['equipped_item'] = None
        if 'trade_state' not in user:
            user['trade_state'] = None
        if 'trade_partner' not in user:
            user['trade_partner'] = None
        if 'trade_offer' not in user:
            user['trade_offer'] = None
        if 'trade_created_at' not in user:
            user['trade_created_at'] = 0
        if 'activated_promos' not in user:
            user['activated_promos'] = []
        save_data(data)
    return data[user_id_str]

def update_user_data(user_id, new_data):
    data = load_data()
    data[str(user_id)] = new_data
    save_data(data)

def is_banned(user_id):
    user_data = get_user_data(user_id)
    return user_data.get('banned', False)

# ========== ФУНКЦИИ ДЛЯ МАГАЗИНА ==========
def load_shop_items():
    try:
        if os.path.exists(SHOP_FILE):
            with open(SHOP_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки товаров: {e}")
    return []

def save_shop_items(items):
    try:
        with open(SHOP_FILE, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Ошибка сохранения товаров: {e}")
    return False

def get_next_item_id():
    items = load_shop_items()
    if not items:
        return 1
    max_id = max(item.get('id', 0) for item in items)
    return max_id + 1

# ========== ФУНКЦИИ ДЛЯ ЖАЛОБ (ПОДДЕРЖКИ) ==========
def load_tickets():
    try:
        if os.path.exists(TICKETS_FILE):
            with open(TICKETS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки жалоб: {e}")
    return []

def save_tickets(tickets):
    try:
        with open(TICKETS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tickets, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Ошибка сохранения жалоб: {e}")
    return False

def send_support_notification_to_admins(user_id, user_name, text):
    admins = load_admins()
    for admin_id in admins:
        try:
            bot.send_message(
                admin_id,
                f"📩 НОВОЕ ОБРАЩЕНИЕ В ПОДДЕРЖКУ\n"
                f"От: ID {user_id} ({escape_markdown(user_name)})\n"
                f"Текст:\n{escape_markdown(text)}",
                parse_mode='Markdown'
            )
        except:
            pass

# ========== ФУНКЦИЯ ОТПРАВКИ СООБЩЕНИЯ С ФОТО ==========
def send_custom_photo(chat_id, photo_path, caption, reply_markup=None):
    try:
        if photo_path and os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
            with open(photo_path, 'rb') as photo:
                bot.send_photo(
                    chat_id,
                    photo,
                    caption=caption,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
        else:
            bot.send_message(chat_id, caption, parse_mode='Markdown', reply_markup=reply_markup)
    except Exception as e:
        print(f"Ошибка отправки фото: {e}")
        try:
            bot.send_message(chat_id, caption, parse_mode=None, reply_markup=reply_markup)
        except:
            pass

def send_menu_message(chat_id, text, reply_markup=None, photo_path=None):
    if photo_path and os.path.exists(photo_path) and os.path.getsize(photo_path) > 0:
        send_custom_photo(chat_id, photo_path, text, reply_markup)
    else:
        if os.path.exists(MENU_IMAGE_PATH) and os.path.getsize(MENU_IMAGE_PATH) > 0:
            send_custom_photo(chat_id, MENU_IMAGE_PATH, text, reply_markup)
        else:
            bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=reply_markup)

# ========== ФУНКЦИЯ ПОКАЗА ГЛАВНОГО МЕНЮ ==========
def show_main_menu(user_id, chat_id):
    try:
        if is_banned(user_id):
            bot.send_message(chat_id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        user_data = get_user_data(user_id)
        user_name = user_data.get('first_name') or "Игрок"
        user_name_escaped = escape_markdown(user_name)
        greeting = get_greeting()
        balance = user_data.get('balance', 0)
        pocket = user_data.get('pocket', 0)
        balance_str = f"{balance:,}".replace(',', ' ')
        pocket_str = f"{pocket:,}".replace(',', ' ')

        equipped_item_id = user_data.get('equipped_item')
        item_photo_path = None
        if equipped_item_id is not None:
            items = load_shop_items()
            for item in items:
                if item.get('id') == equipped_item_id:
                    if 'image' in item and item['image'] and os.path.exists(item['image']):
                        item_photo_path = item['image']
                    break

        welcome_text = f"""
{greeting}, {user_name_escaped}! 👋

Ты попал в главное меню.

💰 Твой баланс: {balance_str} монет
👖 В кармане: {pocket_str} монет

🆔 Игровой ID: {user_id}
"""
        send_menu_message(chat_id, welcome_text, main_keyboard(), photo_path=item_photo_path)
    except Exception as e:
        print(f"Критическая ошибка в show_main_menu: {e}")
        bot.send_message(chat_id, f"❌ Ошибка при открытии меню: {e}\nПожалуйста, сообщите админу.")

# ========== ПЕРЕВОД ДЕНЕГ ==========
def transfer_money(sender_id, receiver_id, amount):
    if sender_id == receiver_id:
        return False, "❌ Нельзя перевести самому себе!"
    if amount < 1000:
        return False, "❌ Минимальная сумма – 1,000 монет!"

    data = load_data()
    if str(receiver_id) not in data:
        return False, "❌ Получатель не найден!"

    sender = get_user_data(sender_id)
    if sender['balance'] < amount:
        return False, f"❌ Недостаточно средств! Баланс: {sender['balance']:,} монет."

    receiver = get_user_data(receiver_id)
    sender['balance'] -= amount
    receiver['balance'] += amount
    now = datetime.now().strftime("%d.%m %H:%M")
    sender['transfer_history'].append(f"➡️ -{amount:,} → ID:{receiver_id} ({now})")
    receiver['transfer_history'].append(f"⬅️ +{amount:,} от ID:{sender_id} ({now})")
    if len(sender['transfer_history']) > 10:
        sender['transfer_history'] = sender['transfer_history'][-10:]
    if len(receiver['transfer_history']) > 10:
        receiver['transfer_history'] = receiver['transfer_history'][-10:]
    update_user_data(sender_id, sender)
    update_user_data(receiver_id, receiver)

    try:
        bot.send_message(
            receiver_id,
            f"💰 Вам зачислено {amount:,} монет!\n"
            f"👤 Отправитель: ID {sender_id}\n"
            f"💎 Ваш новый баланс: {receiver['balance']:,} монет",
            parse_mode='Markdown'
        )
    except Exception:
        pass

    return True, f"✅ Перевод выполнен!\n💰 Ваш новый баланс: {sender['balance']:,} монет"

# ========== АВТОМАТИЧЕСКОЕ НАЧИСЛЕНИЕ ЗАКАЗОВ ==========
def process_work_orders(user_id):
    try:
        user_data = get_user_data(user_id)
        last_time = user_data.get('last_order_time', time.time())
        delay = user_data.get('next_work_delay', random.choice([15, 30, 60]))
        now = time.time()
        elapsed = now - last_time
        orders_added = 0

        while elapsed >= delay:
            transport = user_data.get('work_transport', 'пешком')
            multiplier = get_transport_multiplier(transport)
            base_reward = 5000
            reward = int(base_reward * multiplier)

            user_data['balance'] = user_data.get('balance', 0) + reward
            user_data['work_orders'] = user_data.get('work_orders', 0) + 1
            user_data['work_earned'] = user_data.get('work_earned', 0) + reward

            orders_added += 1
            last_time += delay
            delay = random.choice([15, 30, 60])
            elapsed = now - last_time

        user_data['last_order_time'] = last_time
        user_data['next_work_delay'] = delay
        update_user_data(user_id, user_data)

        if orders_added > 0:
            balance_str = f"{user_data['balance']:,}".replace(',', ' ')
            bot.send_message(
                user_id,
                f"🚚 Автоматически выполнено заказов: {orders_added}\n"
                f"💰 Новый баланс: {balance_str} монет",
                parse_mode='Markdown'
            )
        return orders_added

    except Exception as e:
        print(f"Ошибка process_work_orders: {e}")
        return 0

# ========== ПРОВЕРКА КУЛДАУНА РУЧНОГО ЗАКАЗА ==========
def can_take_manual_order(user_id):
    user_data = get_user_data(user_id)
    last = user_data.get('last_manual_order_time', 0)
    cooldown = user_data.get('manual_cooldown', 0)
    if cooldown == 0:
        return True, 0
    elapsed = time.time() - last
    if elapsed >= cooldown:
        return True, 0
    else:
        return False, cooldown - elapsed

# ========== КЛАВИАТУРЫ ==========
# ========== МНОГОПОЛЬЗОВАТЕЛЬСКАЯ ИГРА В КОСТИ ДЛЯ ЧАТОВ ==========

# Хранилище активных игр в чатах
chat_dice_games = {}

def chat_dice_clear_game(chat_id):
    """Очищает игру в чате."""
    if chat_id in chat_dice_games:
        del chat_dice_games[chat_id]

def chat_dice_create_game(chat_id, creator_id, bet):
    """Создает новую игру в чате."""
    chat_dice_games[chat_id] = {
        'creator': creator_id,
        'creator_name': None,
        'creator_dice': None,
        'creator_sum': 0,
        'opponent': None,
        'opponent_name': None,
        'opponent_dice': None,
        'opponent_sum': 0,
        'bet': bet,
        'status': 'waiting',  # waiting, playing, finished
        'created_at': time.time(),
        'winner': None,
        'result_text': '',
        'message_id': None  # ID сообщения с игрой
    }
    return chat_id

@bot.message_handler(func=lambda message: message.text == '🎲 Кости (Чат)')
def chat_dice_start(message):
    """Начинает создание игры в чате."""
    try:
        # Проверяем, что это чат
        if message.chat.type not in ['group', 'supergroup']:
            bot.send_message(
                message.chat.id,
                "❌ Эта команда доступна только в групповых чатах!\n"
                "Используйте '🎲 Кости (PvP)' для личных игр.",
                reply_markup=main_keyboard()
            )
            return

        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        chat_id = message.chat.id
        process_work_orders(user_id)
        user_data = get_user_data(user_id)
        balance = user_data.get('balance', 0)

        # Проверяем, есть ли уже активная игра в этом чате
        if chat_id in chat_dice_games:
            game = chat_dice_games[chat_id]
            if game['status'] == 'waiting':
                bot.send_message(
                    message.chat.id,
                    f"❌ В этом чате уже есть активная игра!\n"
                    f"💰 Ставка: {game['bet']:,} монет\n"
                    f"👤 Создатель: {game['creator_name']}\n"
                    f"Чтобы присоединиться, нажмите кнопку '✅ Принять игру'",
                    parse_mode='Markdown'
                )
                return

        bot.send_message(
            message.chat.id,
            f"🎲 МНОГОПОЛЬЗОВАТЕЛЬСКИЕ КОСТИ ДЛЯ ЧАТА 🎲\n\n"
            f"💰 Твой баланс: {balance:,} монет\n"
            f"📝 Правила:\n"
            f"• Минимальная ставка: 1,000 монет\n"
            f"• Выигрыш: x2 от ставки\n"
            f"• За дубль (две одинаковые цифры): x3\n"
            f"• ДЖЕКПОТ (6-6): x5!\n"
            f"• Любой участник чата может присоединиться\n\n"
            f"💰 Введите сумму ставки (можно с суффиксами к, кк, ккк):",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(message, chat_dice_process_bet)
    except Exception as e:
        print(f"Ошибка в chat_dice_start: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.", reply_markup=main_keyboard())

def chat_dice_process_bet(message):
    """Обрабатывает ставку и создает игру в чате."""
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        chat_id = message.chat.id
        user_data = get_user_data(user_id)
        balance = user_data.get('balance', 0)

        bet = parse_amount(message.text.strip())
        if bet is None or bet <= 0:
            bot.send_message(
                message.chat.id,
                "❌ Неверная сумма. Используйте число или суффиксы к, кк, ккк.\n"
                "Примеры: 1000, 500к, 2кк, 1ккк",
                parse_mode='Markdown'
            )
            return

        if bet < 1000:
            bot.send_message(
                message.chat.id,
                "❌ Минимальная ставка 1,000 монет!",
                parse_mode='Markdown'
            )
            return

        if bet > balance:
            bot.send_message(
                message.chat.id,
                f"❌ Недостаточно монет!\n💰 Ваш баланс: {balance:,} монет",
                parse_mode='Markdown'
            )
            return

        # Создаем игру в чате
        chat_dice_create_game(chat_id, user_id, bet)
        game = chat_dice_games[chat_id]
        
        # Сохраняем имя создателя
        creator_name = message.from_user.first_name or "Игрок"
        if message.from_user.username:
            creator_name = "@" + message.from_user.username
        game['creator_name'] = creator_name

        # Блокируем ставку (списываем деньги временно)
        user_data['balance'] -= bet
        update_user_data(user_id, user_data)

        # Создаем клавиатуру для игры
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn_join = telebot.types.InlineKeyboardButton(
            "✅ Принять игру",
            callback_data=f"chat_dice_join_{chat_id}"
        )
        btn_cancel = telebot.types.InlineKeyboardButton(
            "❌ Отменить игру",
            callback_data=f"chat_dice_cancel_{chat_id}"
        )
        keyboard.add(btn_join)
        keyboard.add(btn_cancel)

        # Отправляем сообщение с игрой
        msg = bot.send_message(
            message.chat.id,
            f"🎲 НОВАЯ ИГРА В КОСТИ!\n\n"
            f"💰 Ставка: {bet:,} монет\n"
            f"👤 Создатель: {creator_name}\n"
            f"⏳ Ожидание противника...\n\n"
            f"Нажмите '✅ Принять игру', чтобы присоединиться!",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
        
        game['message_id'] = msg.message_id

        # Запускаем таймер на отмену игры через 2 минуты
        threading.Thread(target=chat_dice_timer, args=(chat_id,), daemon=True).start()

    except Exception as e:
        print(f"Ошибка в chat_dice_process_bet: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.", reply_markup=main_keyboard())

def chat_dice_timer(chat_id):
    """Таймер для автоматической отмены игры в чате."""
    time.sleep(120)  # 2 минуты
    if chat_id in chat_dice_games:
        game = chat_dice_games[chat_id]
        if game['status'] == 'waiting':
            # Возвращаем деньги создателю
            creator_id = game['creator']
            user_data = get_user_data(creator_id)
            user_data['balance'] += game['bet']
            update_user_data(creator_id, user_data)
            
            # Уведомляем в чате
            try:
                bot.edit_message_text(
                    f"⏰ Игра в кости отменена (время ожидания истекло).\n"
                    f"💰 Ставка {game['bet']:,} монет возвращена создателю.",
                    chat_id,
                    game['message_id'],
                    parse_mode='Markdown'
                )
            except:
                pass
            
            chat_dice_clear_game(chat_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('chat_dice_join_'))
def chat_dice_join(call):
    """Присоединение к игре в чате."""
    try:
        user_id = call.from_user.id
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "🚫 Вы забанены!", show_alert=True)
            return

        chat_id = int(call.data.split('_')[3])
        game = chat_dice_games.get(chat_id)
        
        if not game:
            bot.answer_callback_query(call.id, "❌ Игра уже завершена!", show_alert=True)
            return

        if game['status'] != 'waiting':
            bot.answer_callback_query(call.id, "❌ Игра уже началась!", show_alert=True)
            return

        if game['creator'] == user_id:
            bot.answer_callback_query(call.id, "❌ Вы не можете присоединиться к своей игре!", show_alert=True)
            return

        # Проверяем баланс
        user_data = get_user_data(user_id)
        if user_data['balance'] < game['bet']:
            bot.answer_callback_query(
                call.id,
                f"❌ Недостаточно монет! Нужно: {game['bet']:,}, у вас: {user_data['balance']:,}",
                show_alert=True
            )
            return

        # Списываем ставку у присоединившегося
        user_data['balance'] -= game['bet']
        update_user_data(user_id, user_data)
        
        # Сохраняем информацию о противнике
        opponent_name = call.from_user.first_name or "Игрок"
        if call.from_user.username:
            opponent_name = "@" + call.from_user.username
        
        game['opponent'] = user_id
        game['opponent_name'] = opponent_name
        game['status'] = 'playing'

        bot.answer_callback_query(call.id, "✅ Вы присоединились к игре!", show_alert=False)

        # Запускаем игру
        chat_dice_play(chat_id)

    except Exception as e:
        print(f"Ошибка в chat_dice_join: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('chat_dice_cancel_'))
def chat_dice_cancel(call):
    """Отменяет игру в чате."""
    try:
        user_id = call.from_user.id
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "🚫 Вы забанены!", show_alert=True)
            return

        chat_id = int(call.data.split('_')[3])
        game = chat_dice_games.get(chat_id)
        
        if not game:
            bot.answer_callback_query(call.id, "❌ Игра уже завершена!", show_alert=True)
            return

        if game['creator'] != user_id:
            bot.answer_callback_query(call.id, "❌ Только создатель может отменить игру!", show_alert=True)
            return

        if game['status'] != 'waiting':
            bot.answer_callback_query(call.id, "❌ Игра уже началась, её нельзя отменить!", show_alert=True)
            return

        # Возвращаем деньги создателю
        user_data = get_user_data(user_id)
        user_data['balance'] += game['bet']
        update_user_data(user_id, user_data)

        bot.answer_callback_query(call.id, "❌ Игра отменена!", show_alert=False)
        
        try:
            bot.edit_message_text(
                f"❌ ИГРА ОТМЕНЕНА\n\n"
                f"💰 Ставка {game['bet']:,} монет возвращена создателю.",
                chat_id,
                game['message_id'],
                parse_mode='Markdown'
            )
        except:
            pass

        chat_dice_clear_game(chat_id)

    except Exception as e:
        print(f"Ошибка в chat_dice_cancel: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)

def chat_dice_play(chat_id):
    """Запускает игру в чате."""
    try:
        game = chat_dice_games.get(chat_id)
        if not game or game['status'] != 'playing':
            return

        creator_id = game['creator']
        opponent_id = game['opponent']
        bet = game['bet']

        # Бросаем кости для обоих игроков
        creator_dice1 = random.randint(1, 6)
        creator_dice2 = random.randint(1, 6)
        opponent_dice1 = random.randint(1, 6)
        opponent_dice2 = random.randint(1, 6)

        creator_sum = creator_dice1 + creator_dice2
        opponent_sum = opponent_dice1 + opponent_dice2

        creator_double = creator_dice1 == creator_dice2
        opponent_double = opponent_dice1 == opponent_dice2

        creator_jackpot = creator_double and creator_dice1 == 6
        opponent_jackpot = opponent_double and opponent_dice1 == 6

        # Определяем победителя
        winner_id = None
        multiplier = 1
        result_text = ""

        # Джекпот у создателя
        if creator_jackpot:
            winner_id = creator_id
            multiplier = 5
            result_text = "🎉 ДЖЕКПОТ! 6-6! ВЫИГРЫШ! 🎉"
        # Джекпот у оппонента
        elif opponent_jackpot:
            winner_id = opponent_id
            multiplier = 5
            result_text = "🎉 ДЖЕКПОТ! 6-6! ВЫИГРЫШ! 🎉"
        # Обычная игра
        else:
            if creator_sum > opponent_sum:
                winner_id = creator_id
                multiplier = 3 if creator_double else 2
                result_text = f"🎉 ВЫИГРЫШ! ({creator_sum} > {opponent_sum})"
            elif creator_sum < opponent_sum:
                winner_id = opponent_id
                multiplier = 3 if opponent_double else 2
                result_text = f"🎉 ВЫИГРЫШ! ({opponent_sum} > {creator_sum})"
            else:
                winner_id = None
                multiplier = 1
                result_text = "🤝 НИЧЬЯ!"

            if winner_id == creator_id and creator_double and not creator_jackpot:
                result_text += " (ДУБЛЬ! x3)"
            elif winner_id == opponent_id and opponent_double and not opponent_jackpot:
                result_text += " (ДУБЛЬ! x3)"

        # Рассчитываем выигрыш
        win_amount = 0
        
        if winner_id:
            win_amount = int(bet * multiplier)
            # Начисляем выигрыш победителю
            winner_data = get_user_data(winner_id)
            winner_data['balance'] += win_amount
            update_user_data(winner_id, winner_data)
        else:
            # Ничья - возвращаем деньги обоим
            creator_data = get_user_data(creator_id)
            creator_data['balance'] += bet
            update_user_data(creator_id, creator_data)
            
            opponent_data = get_user_data(opponent_id)
            opponent_data['balance'] += bet
            update_user_data(opponent_id, opponent_data)
            win_amount = bet

        # Сохраняем результаты
        game['creator_dice'] = (creator_dice1, creator_dice2)
        game['creator_sum'] = creator_sum
        game['opponent_dice'] = (opponent_dice1, opponent_dice2)
        game['opponent_sum'] = opponent_sum
        game['winner'] = winner_id
        game['status'] = 'finished'

        dice_emojis = {1: '⚀', 2: '⚁', 3: '⚂', 4: '⚃', 5: '⚄', 6: '⚅'}

        # Формируем результат
        result_message = f"🎲 РЕЗУЛЬТАТ ИГРЫ В КОСТИ 🎲\n\n"
        result_message += f"👤 {game['creator_name']}: {dice_emojis[creator_dice1]} {dice_emojis[creator_dice2]} (сумма: {creator_sum})\n"
        result_message += f"👤 {game['opponent_name']}: {dice_emojis[opponent_dice1]} {dice_emojis[opponent_dice2]} (сумма: {opponent_sum})\n\n"
        result_message += f"{result_text}\n"
        
        if winner_id:
            winner_name = game['creator_name'] if winner_id == creator_id else game['opponent_name']
            result_message += f"🏆 ПОБЕДИТЕЛЬ: {winner_name}\n"
            result_message += f"💰 Выигрыш: {win_amount:,} монет (x{multiplier})"
        else:
            result_message += f"💰 Ставка возвращена обоим игрокам"

        # Редактируем сообщение с результатом
        try:
            bot.edit_message_text(
                result_message,
                chat_id,
                game['message_id'],
                parse_mode='Markdown'
            )
        except:
            bot.send_message(chat_id, result_message, parse_mode='Markdown')

        # Отправляем личные уведомления игрокам
        try:
            bot.send_message(
                creator_id,
                f"🎲 Результат игры в чате:\n\n{result_message}",
                parse_mode='Markdown'
            )
        except:
            pass

        try:
            bot.send_message(
                opponent_id,
                f"🎲 Результат игры в чате:\n\n{result_message}",
                parse_mode='Markdown'
            )
        except:
            pass

        # Удаляем игру из хранилища
        chat_dice_clear_game(chat_id)

    except Exception as e:
        print(f"Ошибка в chat_dice_play: {e}")
        try:
            bot.send_message(chat_id, "❌ Ошибка во время игры. Попробуйте позже.", reply_markup=main_keyboard())
        except:
            pass
        if chat_id in chat_dice_games:
            chat_dice_clear_game(chat_id)

# Команда для создания игры в чате
@bot.message_handler(commands=['dicechat'])
def chat_dice_command(message):
    """Команда /dicechat - создание игры в чате."""
    chat_dice_start(message)

# Команда для отмены игры в чате
@bot.message_handler(commands=['cancelchatgame'])
def chat_dice_cancel_command(message):
    """Команда /cancelchatgame - отмена игры в чате."""
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        chat_id = message.chat.id
        game = chat_dice_games.get(chat_id)
        
        if not game:
            bot.send_message(message.chat.id, "❌ В этом чате нет активной игры!", reply_markup=main_keyboard())
            return

        if game['creator'] != user_id:
            bot.send_message(message.chat.id, "❌ Только создатель может отменить игру!", reply_markup=main_keyboard())
            return

        if game['status'] != 'waiting':
            bot.send_message(message.chat.id, "❌ Игра уже началась, её нельзя отменить!", reply_markup=main_keyboard())
            return

        # Возвращаем деньги
        user_data = get_user_data(user_id)
        user_data['balance'] += game['bet']
        update_user_data(user_id, user_data)

        try:
            bot.edit_message_text(
                f"❌ ИГРА ОТМЕНЕНА\n\n"
                f"💰 Ставка {game['bet']:,} монет возвращена создателю.",
                chat_id,
                game['message_id'],
                parse_mode='Markdown'
            )
        except:
            pass

        bot.send_message(
            message.chat.id,
            f"❌ Игра отменена! Ставка {game['bet']:,} монет возвращена.",
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )

        chat_dice_clear_game(chat_id)

    except Exception as e:
        print(f"Ошибка в chat_dice_cancel_command: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.", reply_markup=main_keyboard())

# Добавляем кнопку в главное меню
def main_keyboard():
    """Обновленная клавиатура с кнопкой смены имени."""
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('💰 Клик!')
    btn2 = telebot.types.KeyboardButton('📊 Статистика')
    btn3 = telebot.types.KeyboardButton('🏆 Топ игроков')
    btn4 = telebot.types.KeyboardButton('👥 Рефералы')
    btn5 = telebot.types.KeyboardButton('🎰 Рулетка')
    btn6 = telebot.types.KeyboardButton('🃏 Блэкджек')
    btn7 = telebot.types.KeyboardButton('🚚 Работа')
    btn8 = telebot.types.KeyboardButton('💸 Перевести')
    btn13 = telebot.types.KeyboardButton('🔄 Обмен')
    btn14 = telebot.types.KeyboardButton('📞 Поддержка')
    btn9 = telebot.types.KeyboardButton('🏪 Магазин')
    btn10 = telebot.types.KeyboardButton('🎒 Инвентарь')
    btn11 = telebot.types.KeyboardButton('🔙 Назад')
    btn12 = telebot.types.KeyboardButton('🎁 Ежедневный бонус')
    btn_promo = telebot.types.KeyboardButton('🎫 Промокод')
    btn_pocket = telebot.types.KeyboardButton('👖 Карман')
    btn_frog = telebot.types.KeyboardButton('🐸 Лягушка')
    btn_dice_pvp = telebot.types.KeyboardButton('🎲 Кости (PvP)')
    btn_dice_chat = telebot.types.KeyboardButton('🎲 Кости (Чат)')
    btn_change_name = telebot.types.KeyboardButton('📝 Сменить имя')  # НОВАЯ КНОПКА
    keyboard.add(btn1, btn2)
    keyboard.add(btn3, btn4)
    keyboard.add(btn5, btn6)
    keyboard.add(btn7, btn8)
    keyboard.add(btn13, btn9)
    keyboard.add(btn14, btn10)
    keyboard.add(btn11, btn12)
    keyboard.add(btn_promo, btn_pocket)
    keyboard.add(btn_frog, btn_dice_pvp)
    keyboard.add(btn_dice_chat)
    keyboard.add(btn_change_name)  # Добавляем в отдельный ряд
    return keyboard
    """Обновленная клавиатура с кнопкой '🎲 Кости (Чат)'."""
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('💰 Клик!')
    btn2 = telebot.types.KeyboardButton('📊 Статистика')
    btn3 = telebot.types.KeyboardButton('🏆 Топ игроков')
    btn4 = telebot.types.KeyboardButton('👥 Рефералы')
    btn5 = telebot.types.KeyboardButton('🎰 Рулетка')
    btn6 = telebot.types.KeyboardButton('🃏 Блэкджек')
    btn7 = telebot.types.KeyboardButton('🚚 Работа')
    btn8 = telebot.types.KeyboardButton('💸 Перевести')
    btn13 = telebot.types.KeyboardButton('🔄 Обмен')
    btn14 = telebot.types.KeyboardButton('📞 Поддержка')
    btn9 = telebot.types.KeyboardButton('🏪 Магазин')
    btn10 = telebot.types.KeyboardButton('🎒 Инвентарь')
    btn11 = telebot.types.KeyboardButton('🔙 Назад')
    btn12 = telebot.types.KeyboardButton('🎁 Ежедневный бонус')
    btn_promo = telebot.types.KeyboardButton('🎫 Промокод')
    btn_pocket = telebot.types.KeyboardButton('👖 Карман')
    btn_frog = telebot.types.KeyboardButton('🐸 Лягушка')
    btn_dice_pvp = telebot.types.KeyboardButton('🎲 Кости (PvP)')
    btn_dice_chat = telebot.types.KeyboardButton('🎲 Кости (Чат)')  # НОВАЯ КНОПКА
    keyboard.add(btn1, btn2)
    keyboard.add(btn3, btn4)
    keyboard.add(btn5, btn6)
    keyboard.add(btn7, btn8)
    keyboard.add(btn13, btn9)
    keyboard.add(btn14, btn10)
    keyboard.add(btn11, btn12)
    keyboard.add(btn_promo, btn_pocket)
    keyboard.add(btn_frog, btn_dice_pvp)
    keyboard.add(btn_dice_chat)  # Добавляем в отдельный ряд для удобства
    return keyboard

    

def admin_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_addmoney = telebot.types.KeyboardButton('💰 Выдать деньги')
    btn_ban = telebot.types.KeyboardButton('🚫 Забанить игрока')
    btn_unban = telebot.types.KeyboardButton('✅ Разбанить игрока')
    btn_always_win = telebot.types.KeyboardButton('🎰 Всегда выигрывать')
    btn_list = telebot.types.KeyboardButton('📋 Список игроков')
    btn_set_lose_image = telebot.types.KeyboardButton('🖼 Фото проигрыша')
    btn_set_win_image = telebot.types.KeyboardButton('🏆 Фото выигрыша')
    btn_set_menu_image = telebot.types.KeyboardButton('🖼 Фото меню')
    btn_set_pocket_image = telebot.types.KeyboardButton('👖 Фото кармана')
    btn_shop_manage = telebot.types.KeyboardButton('🏪 Управление магазином')
    btn_tickets = telebot.types.KeyboardButton('📋 Жалобы')
    btn_promo_manage = telebot.types.KeyboardButton('🎫 Управление промокодами')
    btn_exit = telebot.types.KeyboardButton('🔙 Выйти из админки')
    keyboard.add(btn_addmoney, btn_ban)
    keyboard.add(btn_unban, btn_always_win)
    keyboard.add(btn_list, btn_set_lose_image)
    keyboard.add(btn_set_win_image, btn_set_menu_image)
    keyboard.add(btn_set_pocket_image, btn_shop_manage)
    keyboard.add(btn_tickets, btn_promo_manage)
    keyboard.add(btn_exit)
    return keyboard
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_addmoney = telebot.types.KeyboardButton('💰 Выдать деньги')
    btn_ban = telebot.types.KeyboardButton('🚫 Забанить игрока')
    btn_unban = telebot.types.KeyboardButton('✅ Разбанить игрока')
    btn_always_win = telebot.types.KeyboardButton('🎰 Всегда выигрывать')
    btn_list = telebot.types.KeyboardButton('📋 Список игроков')
    btn_set_lose_image = telebot.types.KeyboardButton('🖼 Фото проигрыша')
    btn_set_win_image = telebot.types.KeyboardButton('🏆 Фото выигрыша')
    btn_set_menu_image = telebot.types.KeyboardButton('🖼 Фото меню')
    btn_set_pocket_image = telebot.types.KeyboardButton('👖 Фото кармана')
    btn_shop_manage = telebot.types.KeyboardButton('🏪 Управление магазином')
    btn_tickets = telebot.types.KeyboardButton('📋 Жалобы')
    btn_exit = telebot.types.KeyboardButton('🔙 Выйти из админки')
    keyboard.add(btn_addmoney, btn_ban)
    keyboard.add(btn_unban, btn_always_win)
    keyboard.add(btn_list, btn_set_lose_image)
    keyboard.add(btn_set_win_image, btn_set_menu_image)
    keyboard.add(btn_set_pocket_image, btn_shop_manage)
    keyboard.add(btn_tickets, btn_exit)
    return keyboard

def work_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_order = telebot.types.KeyboardButton('📦 Взять заказ')
    btn_transport = telebot.types.KeyboardButton('🚲 Транспорт')
    btn_stats = telebot.types.KeyboardButton('📊 Статистика работы')
    btn_treasure = telebot.types.KeyboardButton('⛏️ Кладоискатель')
    btn_postal = telebot.types.KeyboardButton('📮 Почтальон')
    btn_back = telebot.types.KeyboardButton('🔙 Назад')
    keyboard.add(btn_order, btn_transport)
    keyboard.add(btn_stats)
    keyboard.add(btn_treasure, btn_postal)
    keyboard.add(btn_back)
    return keyboard

def transport_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_foot = telebot.types.KeyboardButton('🚶 Пешком (x1)')
    btn_bike = telebot.types.KeyboardButton('🚲 Велосипед (x1.2)')
    btn_car = telebot.types.KeyboardButton('🚗 Машина (x1.5)')
    btn_plane = telebot.types.KeyboardButton('✈️ Самолёт (x2)')
    btn_back = telebot.types.KeyboardButton('🔙 Назад')
    keyboard.add(btn_foot, btn_bike)
    keyboard.add(btn_car, btn_plane)
    keyboard.add(btn_back)
    return keyboard

def pocket_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_put = telebot.types.KeyboardButton('📥 Положить в карман')
    btn_take = telebot.types.KeyboardButton('📤 Снять с кармана')
    btn_back = telebot.types.KeyboardButton('🔙 Назад')
    keyboard.add(btn_put, btn_take)
    keyboard.add(btn_back)
    return keyboard

def get_transport_multiplier(transport):
    multipliers = {
        'пешком': 1.0,
        'велосипед': 1.2,
        'машина': 1.5,
        'самолёт': 2.0
    }
    return multipliers.get(transport, 1.0)

def get_greeting():
    greetings = [
        "👋 Привет", "🌞 Здравствуй", "🎉 С возвращением",
        "✨ Приветствую", "🤗 Рад тебя видеть", "🎊 О, это ты",
        "👋 Хей", "🌟 Салам", "🎈 Приветик", "💫 Здорово"
    ]
    return random.choice(greetings)

def generate_referral_link(bot_info, user_id):
    return f"https://t.me/{bot_info.username}?start={user_id}"

# ========== ПАРСИНГ СУММЫ (к, кк, ккк) ==========
def parse_amount(amount_str):
    amount_str = amount_str.lower().strip()
    if amount_str.endswith('ккк'):
        try:
            num = float(amount_str[:-3].replace(',', '.'))
            return int(num * 1_000_000_000)
        except:
            return None
    elif amount_str.endswith('кк'):
        try:
            num = float(amount_str[:-2].replace(',', '.'))
            return int(num * 1_000_000)
        except:
            return None
    elif amount_str.endswith('к'):
        try:
            num = float(amount_str[:-1].replace(',', '.'))
            return int(num * 1_000)
        except:
            return None
    else:
        try:
            return int(amount_str.replace(',', '').replace(' ', ''))
        except:
            return None

# ========== НОВЫЙ РАЗДЕЛ: КАРМАН (POCKET) ==========
@bot.message_handler(func=lambda message: message.text == '👖 Карман')
def pocket_menu(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        user_data = get_user_data(user_id)
        balance = user_data.get('balance', 0)
        pocket = user_data.get('pocket', 0)

        text = f"""
👖 КАРМАН

💰 Основной баланс: {balance:,} монет
👖 В кармане: {pocket:,} монет

Выберите действие:
• Положить — перевести деньги с основного баланса в карман
• Снять — перевести деньги из кармана на основной баланс
"""
        send_custom_photo(message.chat.id, POCKET_IMAGE_PATH, text, pocket_keyboard())
    except Exception as e:
        print(f"Ошибка в pocket_menu: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при открытии кармана.", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == '📥 Положить в карман')
def pocket_put_start(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        user_data = get_user_data(user_id)
        balance = user_data.get('balance', 0)
        bot.send_message(
            message.chat.id,
            f"📥 ПОЛОЖИТЬ В КАРМАН\n\n"
            f"💰 У вас на балансе: {balance:,} монет\n"
            f"Введите сумму для перевода в карман (можно с суффиксами к, кк, ккк):\n"
            f"Примеры: 1000, 500к, 2кк, 1ккк",
            parse_mode='Markdown',
            reply_markup=telebot.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, pocket_put_amount)
    except Exception as e:
        print(f"Ошибка в pocket_put_start: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка.", reply_markup=main_keyboard())

def pocket_put_amount(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        amount = parse_amount(message.text.strip())
        if amount is None or amount <= 0:
            bot.send_message(
                message.chat.id,
                "❌ Неверная сумма. Используйте число или суффиксы к, кк, ккк.\n"
                "Примеры: 1000, 500к, 2кк, 1ккк",
                parse_mode='Markdown',
                reply_markup=pocket_keyboard()
            )
            return

        user_data = get_user_data(user_id)
        balance = user_data.get('balance', 0)
        if amount > balance:
            bot.send_message(
                message.chat.id,
                f"❌ Недостаточно монет на балансе!\n"
                f"💰 У вас: {balance:,} монет",
                parse_mode='Markdown',
                reply_markup=pocket_keyboard()
            )
            return

        user_data['balance'] -= amount
        user_data['pocket'] = user_data.get('pocket', 0) + amount
        update_user_data(user_id, user_data)

        bot.send_message(
            message.chat.id,
            f"✅ В карман положено {amount:,} монет!\n\n"
            f"💰 Баланс: {user_data['balance']:,} монет\n"
            f"👖 В кармане: {user_data['pocket']:,} монет",
            parse_mode='Markdown',
            reply_markup=pocket_keyboard()
        )
    except Exception as e:
        print(f"Ошибка в pocket_put_amount: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка.", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == '📤 Снять с кармана')
def pocket_take_start(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        user_data = get_user_data(user_id)
        pocket = user_data.get('pocket', 0)
        bot.send_message(
            message.chat.id,
            f"📤 СНЯТЬ С КАРМАНА\n\n"
            f"👖 В кармане: {pocket:,} монет\n"
            f"Введите сумму для перевода на основной баланс (можно с суффиксами к, кк, ккк):\n"
            f"Примеры: 1000, 500к, 2кк, 1ккк",
            parse_mode='Markdown',
            reply_markup=telebot.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, pocket_take_amount)
    except Exception as e:
        print(f"Ошибка в pocket_take_start: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка.", reply_markup=main_keyboard())

def pocket_take_amount(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        amount = parse_amount(message.text.strip())
        if amount is None or amount <= 0:
            bot.send_message(
                message.chat.id,
                "❌ Неверная сумма. Используйте число или суффиксы к, кк, ккк.\n"
                "Примеры: 1000, 500к, 2кк, 1ккк",
                parse_mode='Markdown',
                reply_markup=pocket_keyboard()
            )
            return

        user_data = get_user_data(user_id)
        pocket = user_data.get('pocket', 0)
        if amount > pocket:
            bot.send_message(
                message.chat.id,
                f"❌ Недостаточно монет в кармане!\n"
                f"👖 В кармане: {pocket:,} монет",
                parse_mode='Markdown',
                reply_markup=pocket_keyboard()
            )
            return

        user_data['pocket'] -= amount
        user_data['balance'] = user_data.get('balance', 0) + amount
        update_user_data(user_id, user_data)

        bot.send_message(
            message.chat.id,
            f"✅ С кармана снято {amount:,} монет!\n\n"
            f"💰 Баланс: {user_data['balance']:,} монет\n"
            f"👖 В кармане: {user_data['pocket']:,} монет",
            parse_mode='Markdown',
            reply_markup=pocket_keyboard()
        )
    except Exception as e:
        print(f"Ошибка в pocket_take_amount: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка.", reply_markup=main_keyboard())

# ========== КОМАНДЫ: карман, положить, снять (текстовые команды) ==========
@bot.message_handler(commands=['pocket', 'карман'])
def pocket_command(message):
    pocket_menu(message)

@bot.message_handler(commands=['put', 'положить'])
def pocket_put_command(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        args = message.text.split()
        if len(args) < 2:
            bot.send_message(
                message.chat.id,
                "❌ Используйте: /положить <сумма>\nПримеры: /положить 1000, /положить 500к, /положить 2кк",
                parse_mode='Markdown'
            )
            return

        amount = parse_amount(args[1])
        if amount is None or amount <= 0:
            bot.send_message(
                message.chat.id,
                "❌ Неверная сумма. Используйте число или суффиксы к, кк, ккк.",
                parse_mode='Markdown'
            )
            return

        user_data = get_user_data(user_id)
        balance = user_data.get('balance', 0)
        if amount > balance:
            bot.send_message(
                message.chat.id,
                f"❌ Недостаточно монет на балансе!\n💰 У вас: {balance:,} монет",
                parse_mode='Markdown'
            )
            return

        user_data['balance'] -= amount
        user_data['pocket'] = user_data.get('pocket', 0) + amount
        update_user_data(user_id, user_data)

        bot.send_message(
            message.chat.id,
            f"✅ В карман положено {amount:,} монет!\n\n"
            f"💰 Баланс: {user_data['balance']:,} монет\n"
            f"👖 В кармане: {user_data['pocket']:,} монет",
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )
    except Exception as e:
        print(f"Ошибка в pocket_put_command: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка.", reply_markup=main_keyboard())

@bot.message_handler(commands=['take', 'снять'])
def pocket_take_command(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        args = message.text.split()
        if len(args) < 2:
            bot.send_message(
                message.chat.id,
                "❌ Используйте: /снять <сумма>\nПримеры: /снять 1000, /снять 500к, /снять 2кк",
                parse_mode='Markdown'
            )
            return

        amount = parse_amount(args[1])
        if amount is None or amount <= 0:
            bot.send_message(
                message.chat.id,
                "❌ Неверная сумма. Используйте число или суффиксы к, кк, ккк.",
                parse_mode='Markdown'
            )
            return

        user_data = get_user_data(user_id)
        pocket = user_data.get('pocket', 0)
        if amount > pocket:
            bot.send_message(
                message.chat.id,
                f"❌ Недостаточно монет в кармане!\n👖 В кармане: {pocket:,} монет",
                parse_mode='Markdown'
            )
            return

        user_data['pocket'] -= amount
        user_data['balance'] = user_data.get('balance', 0) + amount
        update_user_data(user_id, user_data)

        bot.send_message(
            message.chat.id,
            f"✅ С кармана снято {amount:,} монет!\n\n"
            f"💰 Баланс: {user_data['balance']:,} монет\n"
            f"👖 В кармане: {user_data['pocket']:,} монет",
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )
    except Exception as e:
        print(f"Ошибка в pocket_take_command: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка.", reply_markup=main_keyboard())

# ========== ОСТАЛЬНЫЕ ФУНКЦИИ БОТА ==========
@bot.message_handler(commands=['start'])
def start(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        user_data = get_user_data(user_id)
        user_name = message.from_user.first_name or "Игрок"
        user_data['first_name'] = user_name

        if message.from_user.username:
            user_data['username'] = message.from_user.username

        args = message.text.split()
        referrer_bonus = 100000000
        new_user_bonus = 50000000

        if len(args) > 1:
            try:
                referrer_id = int(args[1])
                if str(referrer_id) != str(user_id) and user_data.get('referred_by') is None:
                    referrer_data = get_user_data(referrer_id)
                    if referrer_data:
                        referrer_data['balance'] = referrer_data.get('balance', 0) + referrer_bonus
                        referrer_data['referrals'] = referrer_data.get('referrals', 0) + 1
                        referrer_data['referral_earned'] = referrer_data.get('referral_earned', 0) + referrer_bonus
                        if str(user_id) not in referrer_data['referral_level1']:
                            referrer_data['referral_level1'].append(str(user_id))
                        update_user_data(referrer_id, referrer_data)

                        user_data['balance'] = user_data.get('balance', 0) + new_user_bonus
                        user_data['referred_by'] = referrer_id
                        update_user_data(user_id, user_data)

                        if referrer_data.get('referred_by'):
                            try:
                                referrer2_id = int(referrer_data['referred_by'])
                                referrer2_data = get_user_data(referrer2_id)
                                if str(user_id) not in referrer2_data.get('referral_level2', []):
                                    referrer2_data['referral_level2'].append(str(user_id))
                                update_user_data(referrer2_id, referrer2_data)
                            except:
                                pass

                        try:
                            bot.send_message(
                                referrer_id,
                                f"🎉 *{escape_markdown(user_name)}* перешел по вашей реферальной ссылке!\n"
                                f"💰 Вам начислено *{referrer_bonus:,} монет!*\n"
                                f"👥 Всего рефералов: {referrer_data['referrals']}\n"
                                f"💎 Всего заработано: {referrer_data['referral_earned']:,} монет",
                                parse_mode='Markdown'
                            )
                        except:
                            pass
                        bot.send_message(
                            message.chat.id,
                            f"🎉 *Вы получили бонус за регистрацию!*\n"
                            f"💰 Вам начислено *{new_user_bonus:,} монет!*\n"
                            f"🤝 Вас пригласил: @{escape_markdown(referrer_data.get('username', 'Игрок') or 'Игрок')}",
                            parse_mode='Markdown'
                        )
            except:
                pass

        show_main_menu(user_id, message.chat.id)
    except Exception as e:
        print(f"Ошибка в start: {e}")
        bot.send_message(message.chat.id, "❌ Произошла ошибка. Попробуйте позже.")

@bot.message_handler(commands=['menu'])
# ========== ФУНКЦИЯ ПОКАЗА ГЛАВНОГО МЕНЮ ==========
def show_main_menu(user_id, chat_id):
    try:
        if is_banned(user_id):
            bot.send_message(chat_id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        user_data = get_user_data(user_id)
        # Берем имя из базы данных, а не из Telegram
        user_name = user_data.get('first_name') or "Игрок"
        user_name_escaped = escape_markdown(user_name)
        greeting = get_greeting()
        balance = user_data.get('balance', 0)
        pocket = user_data.get('pocket', 0)
        balance_str = f"{balance:,}".replace(',', ' ')
        pocket_str = f"{pocket:,}".replace(',', ' ')

        equipped_item_id = user_data.get('equipped_item')
        item_photo_path = None
        if equipped_item_id is not None:
            items = load_shop_items()
            for item in items:
                if item.get('id') == equipped_item_id:
                    if 'image' in item and item['image'] and os.path.exists(item['image']):
                        item_photo_path = item['image']
                    break

        welcome_text = f"""
{greeting}, {user_name_escaped}! 👋

Ты попал в главное меню.

💰 Твой баланс: {balance_str} монет
👖 В кармане: {pocket_str} монет

🆔 Игровой ID: {user_id}
"""
        send_menu_message(chat_id, welcome_text, main_keyboard(), photo_path=item_photo_path)
    except Exception as e:
        print(f"Критическая ошибка в show_main_menu: {e}")
        bot.send_message(chat_id, f"❌ Ошибка при открытии меню: {e}\nПожалуйста, сообщите админу.")

# ========== ОБРАБОТЧИКИ КОМАНД /start, /menu и "я" ==========
@bot.message_handler(commands=['start'])
def start(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        user_data = get_user_data(user_id)
        user_name = message.from_user.first_name or "Игрок"
        # ВАЖНО: Не перезаписываем имя, если оно уже есть!
        if not user_data.get('first_name'):
            user_data['first_name'] = user_name

        if message.from_user.username:
            user_data['username'] = message.from_user.username

        args = message.text.split()
        referrer_bonus = 100000000
        new_user_bonus = 50000000

        if len(args) > 1:
            try:
                referrer_id = int(args[1])
                if str(referrer_id) != str(user_id) and user_data.get('referred_by') is None:
                    referrer_data = get_user_data(referrer_id)
                    if referrer_data:
                        referrer_data['balance'] = referrer_data.get('balance', 0) + referrer_bonus
                        referrer_data['referrals'] = referrer_data.get('referrals', 0) + 1
                        referrer_data['referral_earned'] = referrer_data.get('referral_earned', 0) + referrer_bonus
                        if str(user_id) not in referrer_data['referral_level1']:
                            referrer_data['referral_level1'].append(str(user_id))
                        update_user_data(referrer_id, referrer_data)

                        user_data['balance'] = user_data.get('balance', 0) + new_user_bonus
                        user_data['referred_by'] = referrer_id
                        update_user_data(user_id, user_data)

                        if referrer_data.get('referred_by'):
                            try:
                                referrer2_id = int(referrer_data['referred_by'])
                                referrer2_data = get_user_data(referrer2_id)
                                if str(user_id) not in referrer2_data.get('referral_level2', []):
                                    referrer2_data['referral_level2'].append(str(user_id))
                                update_user_data(referrer2_id, referrer2_data)
                            except:
                                pass

                        try:
                            bot.send_message(
                                referrer_id,
                                f"🎉 *{escape_markdown(user_name)}* перешел по вашей реферальной ссылке!\n"
                                f"💰 Вам начислено *{referrer_bonus:,} монет!*\n"
                                f"👥 Всего рефералов: {referrer_data['referrals']}\n"
                                f"💎 Всего заработано: {referrer_data['referral_earned']:,} монет",
                                parse_mode='Markdown'
                            )
                        except:
                            pass
                        bot.send_message(
                            message.chat.id,
                            f"🎉 *Вы получили бонус за регистрацию!*\n"
                            f"💰 Вам начислено *{new_user_bonus:,} монет!*\n"
                            f"🤝 Вас пригласил: @{escape_markdown(referrer_data.get('username', 'Игрок') or 'Игрок')}",
                            parse_mode='Markdown'
                        )
            except:
                pass

        show_main_menu(user_id, message.chat.id)
    except Exception as e:
        print(f"Ошибка в start: {e}")
        bot.send_message(message.chat.id, "❌ Произошла ошибка. Попробуйте позже.")

@bot.message_handler(commands=['menu'])
def menu_command(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return
        user_data = get_user_data(user_id)
        # Не перезаписываем имя!
        show_main_menu(user_id, message.chat.id)
    except Exception as e:
        print(f"Ошибка в menu_command: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}\nПопробуйте позже.")

@bot.message_handler(func=lambda message: message.text.lower() == 'я')
def menu_by_ya(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return
        user_data = get_user_data(user_id)
        # Не перезаписываем имя!
        show_main_menu(user_id, message.chat.id)
    except Exception as e:
        print(f"Ошибка в menu_by_ya: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}\nПопробуйте позже.")

@bot.message_handler(func=lambda message: message.text.lower() == 'я')
def menu_by_ya(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return
        user_data = get_user_data(user_id)
        user_data['first_name'] = message.from_user.first_name
        update_user_data(user_id, user_data)
        show_main_menu(user_id, message.chat.id)
    except Exception as e:
        print(f"Ошибка в menu_by_ya: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}\nПопробуйте позже.")

# ========== ОБРАБОТЧИК ЕЖЕДНЕВНОГО БОНУСА ==========
@bot.message_handler(func=lambda message: message.text == '🎁 Ежедневный бонус')
def daily_bonus(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        user_data = get_user_data(user_id)

        last_time = user_data.get('daily_bonus_time', 0)
        now = time.time()

        if now - last_time >= 86400:
            bonus_amount = 100000000
            user_data['balance'] = user_data.get('balance', 0) + bonus_amount
            user_data['daily_bonus_time'] = now
            update_user_data(user_id, user_data)

            formatted_balance = f"{user_data['balance']:,}".replace(',', ' ')
            bot.send_message(
                message.chat.id,
                f"🎁 ВЫ ПОЛУЧИЛИ ЕЖЕДНЕВНЫЙ БОНУС!\n\n"
                f"💰 +{bonus_amount:,} монет!\n"
                f"📊 Ваш новый баланс: {formatted_balance} монет\n\n"
                f"⏳ Следующий бонус будет доступен через 24 часа.",
                parse_mode='Markdown'
            )
        else:
            time_left = int(86400 - (now - last_time))
            hours = time_left // 3600
            minutes = (time_left % 3600) // 60
            bot.send_message(
                message.chat.id,
                f"⏳ Ежедневный бонус уже получен!\n\n"
                f"📅 До следующего бонуса осталось: {hours}ч {minutes}м.\n"
                f"⏰ Возвращайтесь завтра!",
                parse_mode='Markdown'
            )
    except Exception as e:
        print(f"Ошибка в daily_bonus: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при получении бонуса. Попробуйте позже.", reply_markup=main_keyboard())

# ========== НОВЫЕ АКТИВНОСТИ В МЕНЮ РАБОТЫ ==========
@bot.message_handler(func=lambda message: message.text == '⛏️ Кладоискатель')
def treasure_hunt(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        user_data = get_user_data(user_id)

        last_time = user_data.get('last_treasure_time', 0)
        now = time.time()
        cooldown = 30
        if now - last_time < cooldown:
            remaining = int(cooldown - (now - last_time))
            bot.send_message(
                message.chat.id,
                f"⏳ Подождите {remaining} секунд перед следующим поиском клада!",
                parse_mode='Markdown',
                reply_markup=work_keyboard()
            )
            return

        if random.random() < 0.9:
            reward = 1
            rarity = "обычный"
        else:
            reward = 10
            rarity = "редкий"

        user_data['balance'] = user_data.get('balance', 0) + reward
        user_data['treasure_hunts'] = user_data.get('treasure_hunts', 0) + 1
        user_data['treasure_found'] = user_data.get('treasure_found', 0) + 1
        user_data['treasure_earned'] = user_data.get('treasure_earned', 0) + reward
        user_data['last_treasure_time'] = now
        update_user_data(user_id, user_data)

        balance_str = f"{user_data['balance']:,}".replace(',', ' ')
        text = (
            f"⛏️ ВЫ НАШЛИ КЛАД!\n\n"
            f"💰 +{reward} монет ({rarity} находка)\n"
            f"📊 Новый баланс: {balance_str} монет\n\n"
            f"📈 Статистика кладоискателя:\n"
            f"• Всего поисков: {user_data['treasure_hunts']}\n"
            f"• Найдено кладов: {user_data['treasure_found']}\n"
            f"• Всего заработано: {user_data['treasure_earned']} монет"
        )
        bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=work_keyboard())

    except Exception as e:
        print(f"Ошибка в treasure_hunt: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при поиске клада. Попробуйте позже.", reply_markup=work_keyboard())

@bot.message_handler(func=lambda message: message.text == '📮 Почтальон')
def postal_delivery(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        user_data = get_user_data(user_id)

        last_time = user_data.get('last_postal_time', 0)
        now = time.time()
        cooldown = 30
        if now - last_time < cooldown:
            remaining = int(cooldown - (now - last_time))
            bot.send_message(
                message.chat.id,
                f"⏳ Подождите {remaining} секунд перед следующей доставкой писем!",
                parse_mode='Markdown',
                reply_markup=work_keyboard()
            )
            return

        if random.random() < 0.9:
            reward = 1
            rarity = "обычное"
        else:
            reward = 5
            rarity = "редкое"

        user_data['balance'] = user_data.get('balance', 0) + reward
        user_data['postal_hunts'] = user_data.get('postal_hunts', 0) + 1
        user_data['postal_found'] = user_data.get('postal_found', 0) + 1
        user_data['postal_earned'] = user_data.get('postal_earned', 0) + reward
        user_data['last_postal_time'] = now
        update_user_data(user_id, user_data)

        balance_str = f"{user_data['balance']:,}".replace(',', ' ')
        text = (
            f"📮 ВЫ ДОСТАВИЛИ ПИСЬМО!\n\n"
            f"💰 +{reward} монет ({rarity} письмо)\n"
            f"📊 Новый баланс: {balance_str} монет\n\n"
            f"📈 Статистика почтальона:\n"
            f"• Всего доставок: {user_data['postal_hunts']}\n"
            f"• Успешных доставок: {user_data['postal_found']}\n"
            f"• Всего заработано: {user_data['postal_earned']} монет"
        )
        bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=work_keyboard())

    except Exception as e:
        print(f"Ошибка в postal_delivery: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при доставке писем. Попробуйте позже.", reply_markup=work_keyboard())

# ========== ОСТАЛЬНЫЕ ФУНКЦИИ БОТА ==========
@bot.message_handler(func=lambda message: message.text == '💰 Клик!')
def click(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        user_data = get_user_data(user_id)

        reward = 1000000
        user_data['balance'] = user_data.get('balance', 0) + reward
        user_data['clicks'] = user_data.get('clicks', 0) + 1
        user_data['last_click'] = datetime.now().isoformat()

        if user_data.get('referred_by'):
            try:
                referrer_id = int(user_data['referred_by'])
                referrer_data = get_user_data(referrer_id)
                bonus1 = int(reward * 0.1)
                referrer_data['balance'] = referrer_data.get('balance', 0) + bonus1
                referrer_data['referral_clicks_bonus'] = referrer_data.get('referral_clicks_bonus', 0) + bonus1
                referrer_data['referral_clicks_count'] = referrer_data.get('referral_clicks_count', 0) + 1
                update_user_data(referrer_id, referrer_data)
            except:
                pass

            try:
                referrer_data = get_user_data(int(user_data['referred_by']))
                if referrer_data.get('referred_by'):
                    referrer2_id = int(referrer_data['referred_by'])
                    referrer2_data = get_user_data(referrer2_id)
                    bonus2 = int(reward * 0.05)
                    referrer2_data['balance'] = referrer2_data.get('balance', 0) + bonus2
                    referrer2_data['referral_clicks_bonus'] = referrer2_data.get('referral_clicks_bonus', 0) + bonus2
                    referrer2_data['referral_clicks_count'] = referrer2_data.get('referral_clicks_count', 0) + 1
                    update_user_data(referrer2_id, referrer2_data)
            except:
                pass

        update_user_data(user_id, user_data)

        formatted_balance = f"{user_data['balance']:,}".replace(',', ' ')
        effects = ['💥', '⚡', '🔥', '💫', '✨']

        bot.send_message(
            message.chat.id,
            f"{random.choice(effects)} +1,000,000 монет!\n\n💰 Баланс: {formatted_balance} монет\n🖱 Кликов: {user_data['clicks']}",
            parse_mode='Markdown'
        )

    except Exception as e:
        print(f"Ошибка в click: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при клике. Попробуйте еще раз.")

@bot.message_handler(func=lambda message: message.text == '📊 Статистика')
def stats(message):
    try:
        user_id = message.from_user.id  # Сначала получаем user_id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        user_data = get_user_data(user_id) # Потом получаем user_data
        user_name = user_data.get('first_name') or "Игрок" # Берем имя из базы, а не из Telegram

        formatted_balance = f"{user_data.get('balance', 0):,}".replace(',', ' ')
        pocket = user_data.get('pocket', 0)
        formatted_pocket = f"{pocket:,}".replace(',', ' ')
        clicks = user_data.get('clicks', 0)

        if clicks == 0:
            progress_bar = "⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0%"
        else:
            progress = min(clicks / 100 * 100, 100)
            filled = int(progress / 10)
            empty = 10 - filled
            progress_bar = "🟩" * filled + "⬜" * empty + f" {int(progress)}%"

        if clicks >= 100:
            status = '🏆 Лидер'
        elif clicks >= 50:
            status = '⭐ Игрок'
        else:
            status = '🌱 Новичок'

        referred_info = ""
        if user_data.get('referred_by'):
            try:
                referrer = bot.get_chat(int(user_data['referred_by']))
                referred_info = f"\n👤 Пригласил: {escape_markdown(referrer.first_name or 'Игрок')}"
            except:
                referred_info = "\n👤 Пригласил: Неизвестно"

        inventory_list = user_data.get('inventory', [])
        inv_text = ", ".join(inventory_list) if inventory_list else "пусто"

        stats_text = f"""
📊 ТВОЯ СТАТИСТИКА

👤 Игрок: {escape_markdown(user_name)}
🆔 ID: {user_id}

💰 Баланс: {formatted_balance} монет
👖 В кармане: {formatted_pocket} монет
🖱 Всего кликов: {clicks}
👥 Рефералов: {user_data.get('referrals', 0)}
💎 Заработано с рефералов: {user_data.get('referral_earned', 0):,} монет
💸 Бонусов за клики рефералов: {user_data.get('referral_clicks_bonus', 0):,} монет{referred_info}

📈 Прогресс:
{progress_bar}

🎒 Инвентарь: {inv_text}

📊 Детали:
• 1 клик = 1,000,000 монет
• Бонус за приглашение = 100,000,000 монет
• Бонус за переход = 50,000,000 монет
• Всего заработано: {formatted_balance} монет

💪 Статус: {status}
"""
        bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')
    except Exception as e:
        print(f"Ошибка в stats: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при получении статистики.")
        inventory_list = user_data.get('inventory', [])
        inv_text = ", ".join(inventory_list) if inventory_list else "пусто"

        stats_text = f"""
📊 ТВОЯ СТАТИСТИКА

👤 Игрок: {escape_markdown(user_name)}
🆔 ID: {user_id}

💰 Баланс: {formatted_balance} монет
👖 В кармане: {formatted_pocket} монет
🖱 Всего кликов: {clicks}
👥 Рефералов: {user_data.get('referrals', 0)}
💎 Заработано с рефералов: {user_data.get('referral_earned', 0):,} монет
💸 Бонусов за клики рефералов: {user_data.get('referral_clicks_bonus', 0):,} монет{referred_info}

📈 Прогресс:
{progress_bar}

🎒 Инвентарь: {inv_text}

📊 Детали:
• 1 клик = 1,000,000 монет
• Бонус за приглашение = 100,000,000 монет
• Бонус за переход = 50,000,000 монет
• Всего заработано: {formatted_balance} монет

💪 Статус: {status}
"""
        bot.send_message(message.chat.id, stats_text, parse_mode='Markdown')
    except Exception as e:
        print(f"Ошибка в stats: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при получении статистики.")

@bot.message_handler(func=lambda message: message.text == '🏆 Топ игроков')
def top_players(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        data = load_data()
        if not data:
            bot.send_message(message.chat.id, "📭 Пока нет игроков!\nБудь первым! 🏆", parse_mode='Markdown')
            return

        sorted_players = sorted(data.items(), key=lambda x: x[1].get('balance', 0), reverse=True)
        top_10 = sorted_players[:10]

        top_text = "🏆 ТОП 10 ИГРОКОВ 🏆\n"
        top_text += "═" * 25 + "\n\n"

        for i, (user_id, user_data) in enumerate(top_10, 1):
            try:
                user = bot.get_chat(int(user_id))
                name = escape_markdown(user.first_name or f"User_{user_id[:6]}")
            except:
                name = f"User_{user_id[:6]}"

            balance = user_data.get('balance', 0)
            clicks = user_data.get('clicks', 0)
            referrals = user_data.get('referrals', 0)
            formatted_balance = f"{balance:,}".replace(',', ' ')
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            elif i == 3:
                medal = "🥉"
            else:
                medal = f"{i}."
            top_text += f"{medal} *{name[:20]}*\n"
            top_text += f" 💰 {formatted_balance} монет\n"
            top_text += f" 🖱 {clicks} кликов\n"
            top_text += f" 👥 {referrals} рефералов\n\n"

        user_id = message.from_user.id
        user_data = get_user_data(user_id)
        user_balance = f"{user_data.get('balance', 0):,}".replace(',', ' ')

        position = 0
        for i, (uid, data) in enumerate(sorted_players, 1):
            if str(uid) == str(user_id):
                position = i
                break

        top_text += "═" * 25 + "\n"
        if position > 0:
            top_text += f"👤 Твой рейтинг: #{position} из {len(sorted_players)}\n"
        else:
            top_text += f"👤 Твой рейтинг: Не в топе\n"
        top_text += f"💰 Твой баланс: {user_balance} монет"

        bot.send_message(message.chat.id, top_text, parse_mode='Markdown')

    except Exception as e:
        print(f"Ошибка в top_players: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при получении топа игроков.")

@bot.message_handler(func=lambda message: message.text == '👥 Рефералы')
def referrals(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        user_data = get_user_data(user_id)
        bot_info = bot.get_me()

        referral_link = generate_referral_link(bot_info, user_id)
        referral_link_escaped = escape_markdown(referral_link)

        data = load_data()
        level1_users = []
        level2_users = []
        for uid, udata in data.items():
            if udata.get('referred_by') == user_id:
                try:
                    user = bot.get_chat(int(uid))
                    name = escape_markdown(user.first_name or f"User_{uid[:6]}")
                    level1_users.append(f"• {name} (кликов: {udata.get('clicks', 0)})")
                except:
                    level1_users.append(f"• User_{uid[:6]} (кликов: {udata.get('clicks', 0)})")
            if str(user_id) in udata.get('referral_level2', []):
                try:
                    user = bot.get_chat(int(uid))
                    name = escape_markdown(user.first_name or f"User_{uid[:6]}")
                    level2_users.append(f"• {name} (кликов: {udata.get('clicks', 0)})")
                except:
                    level2_users.append(f"• User_{uid[:6]} (кликов: {udata.get('clicks', 0)})")

        referrals_text = f"""
👥 РЕФЕРАЛЬНАЯ СИСТЕМА

🔗 Твоя реферальная ссылка:
{referral_link_escaped}

💰 Бонусы:
• За приглашение друга - 100,000,000 монет (вам)
• За переход по ссылке - 50,000,000 монет (другу)
• 10% от каждого клика реферала 1-го уровня (100,000)
• 5% от каждого клика реферала 2-го уровня (50,000)

📊 Твоя статистика:
• Всего рефералов (1-й уровень): {user_data.get('referrals', 0)}
• Рефералов 2-го уровня: {len(user_data.get('referral_level2', []))}
• Заработано с рефералов (за регистрацию): {user_data.get('referral_earned', 0):,} монет
• Бонусов за клики рефералов: {user_data.get('referral_clicks_bonus', 0):,} монет
• Всего кликов рефералов: {user_data.get('referral_clicks_count', 0)}

📋 Как это работает:

Отправь ссылку другу

Друг переходит и регистрируется

Вы оба получаете бонусы!
"""

        if level1_users:
            referrals_text += f"\n👥 Рефералы 1-го уровня:\n" + "\n".join(level1_users[:10])
            if len(level1_users) > 10:
                referrals_text += f"\n... и еще {len(level1_users) - 10} человек"
        else:
            referrals_text += "\n📭 У вас пока нет рефералов 1-го уровня"

        if level2_users:
            referrals_text += f"\n\n👥 Рефералы 2-го уровня:\n" + "\n".join(level2_users[:10])
            if len(level2_users) > 10:
                referrals_text += f"\n... и еще {len(level2_users) - 10} человек"
        else:
            referrals_text += "\n📭 У вас пока нет рефералов 2-го уровня"

        keyboard = telebot.types.InlineKeyboardMarkup()
        copy_btn = telebot.types.InlineKeyboardButton("📋 Копировать ссылку", callback_data=f"copy_{user_id}")
        share_btn = telebot.types.InlineKeyboardButton("📤 Поделиться", callback_data=f"share_{user_id}")
        keyboard.add(copy_btn)
        keyboard.add(share_btn)

        bot.send_message(
            message.chat.id,
            referrals_text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )

    except Exception as e:
        print(f"Ошибка в referrals: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при получении реферальной информации.")

# ========== РУЛЕТКА ==========
@bot.message_handler(func=lambda message: message.text == '🎰 Рулетка')
def roulette(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        user_data = get_user_data(user_id)

        bot.send_message(
            message.chat.id,
            f"🎰 РУЛЕТКА КАЗИНО\n\n"
            f"💰 Твой баланс: {user_data.get('balance', 0):,} монет\n\n"
            f"🔴 Красное - выигрыш x2\n"
            f"⚫ Черное - выигрыш x2\n"
            f"🟢 Зеленое - выигрыш x14\n"
            f"🔽 Мал (1-18) - выигрыш x2\n"
            f"🔼 Бол (19-36) - выигрыш x2\n\n"
            f"📝 Введите сумму ставки:\n"
            f"Минимальная ставка: 1,000 монет\n"
            f"Максимальная: {user_data.get('balance', 0):,} монет",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(message, process_roulette_bet)
    except Exception as e:
        print(f"Ошибка в roulette: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.")

def process_roulette_bet(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        user_data = get_user_data(user_id)
        balance = user_data.get('balance', 0)

        try:
            bet = int(message.text.strip())
        except:
            bot.send_message(
                message.chat.id,
                "❌ Введите число!\nПопробуйте снова /start",
                parse_mode='Markdown'
            )
            return

        if bet < 1000:
            bot.send_message(
                message.chat.id,
                "❌ Минимальная ставка 1,000 монет!",
                parse_mode='Markdown'
            )
            return

        if bet > balance:
            bot.send_message(
                message.chat.id,
                f"❌ Недостаточно монет!\n"
                f"💰 Ваш баланс: {balance:,} монет",
                parse_mode='Markdown'
            )
            return

        user_data['roulette_bet'] = bet
        update_user_data(user_id, user_data)

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn_red = telebot.types.InlineKeyboardButton("🔴 Красное (x2)", callback_data=f"roulette_red_{user_id}")
        btn_black = telebot.types.InlineKeyboardButton("⚫ Черное (x2)", callback_data=f"roulette_black_{user_id}")
        btn_low = telebot.types.InlineKeyboardButton("🔽 Мал (1-18) (x2)", callback_data=f"roulette_low_{user_id}")
        btn_high = telebot.types.InlineKeyboardButton("🔼 Бол (19-36) (x2)", callback_data=f"roulette_high_{user_id}")
        btn_green = telebot.types.InlineKeyboardButton("🟢 Зеленое (x14)", callback_data=f"roulette_green_{user_id}")
        btn_cancel = telebot.types.InlineKeyboardButton("❌ Отмена", callback_data=f"roulette_cancel_{user_id}")
        keyboard.add(btn_red, btn_black)
        keyboard.add(btn_low, btn_high)
        keyboard.add(btn_green, btn_cancel)

        bot.send_message(
            message.chat.id,
            f"🎰 РУЛЕТКА КАЗИНО\n\n"
            f"💰 Ставка: {bet:,} монет\n"
            f"📊 Твой баланс: {balance:,} монет\n\n"
            f"🔴 Красное - выигрыш x2\n"
            f"⚫ Черное - выигрыш x2\n"
            f"🟢 Зеленое - выигрыш x14\n"
            f"🔽 Мал (1-18) - выигрыш x2\n"
            f"🔼 Бол (19-36) - выигрыш x2\n\n"
            f"Выбери ставку! 🍀",
            parse_mode='Markdown',
            reply_markup=keyboard
        )

    except Exception as e:
        print(f"Ошибка в process_roulette_bet: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('roulette_'))
def roulette_callback(call):
    try:
        user_id = call.from_user.id
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "🚫 Вы забанены!", show_alert=True)
            return

        data_parts = call.data.split('_')
        action = data_parts[1]
        user_id_from_data = int(data_parts[2])

        if user_id != user_id_from_data:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return

        if action == "cancel":
            bot.answer_callback_query(call.id, "❌ Игра отменена")
            bot.edit_message_text(
                "❌ Игра отменена\n\nНажми /start чтобы вернуться в меню",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
            return

        user_data = get_user_data(user_id)
        balance = user_data.get('balance', 0)
        bet = user_data.get('roulette_bet', 1000000)

        if balance < bet:
            bot.answer_callback_query(call.id, "❌ Недостаточно монет!", show_alert=True)
            bot.edit_message_text(
                "❌ Недостаточно монет для игры!\n\nНажми /start чтобы вернуться в меню",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown'
            )
            return

        always_win = user_data.get('roulette_always_win', False)
        if always_win:
            win = True
            multiplier = 2
            roulette_number = random.randint(0, 36)
            if roulette_number == 0:
                result_color = "green"
            elif roulette_number % 2 == 0:
                result_color = "red"
            else:
                result_color = "black"
        else:
            roulette_number = random.randint(0, 36)
            if roulette_number == 0:
                result_color = "green"
            elif roulette_number % 2 == 0:
                result_color = "red"
            else:
                result_color = "black"

            win = False
            multiplier = 0

            if action == "red" and result_color == "red":
                win = True
                multiplier = 2
            elif action == "black" and result_color == "black":
                win = True
                multiplier = 2
            elif action == "green" and result_color == "green":
                win = True
                multiplier = 14
            elif action == "low" and 1 <= roulette_number <= 18:
                win = True
                multiplier = 2
            elif action == "high" and 19 <= roulette_number <= 36:
                win = True
                multiplier = 2

        color_names = {
            "red": "🔴 Красное",
            "black": "⚫ Черное",
            "green": "🟢 Зеленое"
        }

        action_names = {
            "red": "🔴 Красное",
            "black": "⚫ Черное",
            "green": "🟢 Зеленое",
            "low": "🔽 Мал (1-18)",
            "high": "🔼 Бол (19-36)"
        }

        if win:
            winnings = bet * multiplier
            user_data['balance'] = balance + winnings
            update_user_data(user_id, user_data)
            result_text = f"🎉 ВЫ ВЫИГРАЛИ!\n\n"
            result_text += f"💰 Выигрыш: {winnings:,} монет\n"
            result_text += f"📊 Новый баланс: {user_data['balance']:,} монет"
            result_text += f"\n\n🎯 Результаты:\n"
            result_text += f"• Число: {roulette_number}\n"
            result_text += f"• Цвет: {color_names[result_color]}\n"
            result_text += f"• Ваша ставка: {action_names[action]}\n"
            result_text += f"• Сумма ставки: {bet:,} монет"
            if always_win:
                result_text += "\n\n✨ *Режим «Всегда выигрывать» активен!*"
            emojis = ['🍀', '✨', '🌟', '💫', '🎊']
            result_text = f"{random.choice(emojis)} " + result_text

            bot.answer_callback_query(call.id, "✅ Игра завершена!")

            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass

            if os.path.exists(WIN_IMAGE_PATH) and os.path.getsize(WIN_IMAGE_PATH) > 0:
                with open(WIN_IMAGE_PATH, 'rb') as photo:
                    bot.send_photo(
                        call.message.chat.id,
                        photo,
                        caption=result_text,
                        parse_mode='Markdown'
                    )
            else:
                bot.send_message(
                    call.message.chat.id,
                    result_text,
                    parse_mode='Markdown'
                )

            if winnings >= 10000000:
                bot.send_message(
                    call.message.chat.id,
                    f"🔥 КРУПНЫЙ ВЫИГРЫШ!\n"
                    f"Игрок выиграл {winnings:,} монет в рулетку!\n"
                    f"🎉 Поздравляем!",
                    parse_mode='Markdown'
                )

        else:
            user_data['balance'] = balance - bet
            update_user_data(user_id, user_data)

            caption = f"😢 ВЫ ПРОИГРАЛИ\n\n" \
                      f"💰 Проиграно: {bet:,} монет\n" \
                      f"📊 Новый баланс: {user_data['balance']:,} монет\n\n" \
                      f"🎯 Результаты:\n" \
                      f"• Число: {roulette_number}\n" \
                      f"• Цвет: {color_names[result_color]}\n" \
                      f"• Ваша ставка: {action_names[action]}\n" \
                      f"• Сумма ставки: {bet:,} монет"

            try:
                if os.path.exists(LOSE_IMAGE_PATH) and os.path.getsize(LOSE_IMAGE_PATH) > 0:
                    with open(LOSE_IMAGE_PATH, 'rb') as photo:
                        bot.send_photo(
                            call.message.chat.id,
                            photo,
                            caption=caption,
                            parse_mode='Markdown'
                        )
                else:
                    bot.send_message(
                        call.message.chat.id,
                        caption + "\n\n(Изображение не найдено. Админ может загрузить фото через /setloseimage)",
                        parse_mode='Markdown'
                    )
            except Exception as e:
                print(f"Ошибка отправки фото: {e}")
                bot.send_message(
                    call.message.chat.id,
                    caption + "\n\n(Ошибка загрузки изображения)",
                    parse_mode='Markdown'
                )

            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                print(f"Не удалось удалить сообщение: {e}")

            bot.answer_callback_query(call.id, "❌ Вы проиграли!")

        user_data['roulette_bet'] = 0
        update_user_data(user_id, user_data)

    except Exception as e:
        print(f"Ошибка в roulette_callback: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)

# ===================== БЛЭКДЖЕК =====================
def create_deck():
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [{'rank': r, 'suit': s} for s in suits for r in ranks]
    random.shuffle(deck)
    return deck

def card_value(card):
    rank = card['rank']
    if rank in ['J', 'Q', 'K']:
        return 10
    elif rank == 'A':
        return 11
    else:
        return int(rank)

def hand_value(hand):
    total = sum(card_value(c) for c in hand)
    aces = sum(1 for c in hand if c['rank'] == 'A')
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

def hand_string(hand):
    return ' '.join([f"{c['rank']}{c['suit']}" for c in hand])

def is_blackjack(hand):
    return len(hand) == 2 and hand_value(hand) == 21

@bot.message_handler(func=lambda message: message.text == '🃏 Блэкджек')
def blackjack_start(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        user_data = get_user_data(user_id)

        bot.send_message(
            message.chat.id,
            f"🃏 БЛЭКДЖЕК\n\n"
            f"💰 Твой баланс: {user_data.get('balance', 0):,} монет\n\n"
            f"📝 Введите сумму ставки (минимум 1,000 монет):",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(message, process_blackjack_bet)
    except Exception as e:
        print(f"Ошибка в blackjack_start: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.")

def process_blackjack_bet(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        user_data = get_user_data(user_id)
        balance = user_data.get('balance', 0)

        try:
            bet = int(message.text.strip())
        except:
            bot.send_message(
                message.chat.id,
                "❌ Введите число!\nПопробуйте снова /start",
                parse_mode='Markdown'
            )
            return

        if bet < 1000:
            bot.send_message(
                message.chat.id,
                "❌ Минимальная ставка 1,000 монет!",
                parse_mode='Markdown'
            )
            return

        if bet > balance:
            bot.send_message(
                message.chat.id,
                f"❌ Недостаточно монет!\n"
                f"💰 Ваш баланс: {balance:,} монет",
                parse_mode='Markdown'
            )
            return

        deck = create_deck()
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]

        user_data['bj_bet'] = bet
        user_data['bj_deck'] = deck
        user_data['bj_player_hand'] = player_hand
        user_data['bj_dealer_hand'] = dealer_hand
        user_data['bj_doubled'] = False
        update_user_data(user_id, user_data)

        show_blackjack_game(message, user_id, initial=True)

    except Exception as e:
        print(f"Ошибка в process_blackjack_bet: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.")

def show_blackjack_game(message, user_id, initial=False):
    user_data = get_user_data(user_id)
    bet = user_data['bj_bet']
    player_hand = user_data['bj_player_hand']
    dealer_hand = user_data['bj_dealer_hand']
    player_value = hand_value(player_hand)
    dealer_value = hand_value(dealer_hand)
    deck = user_data['bj_deck']

    player_bj = is_blackjack(player_hand)
    dealer_bj = is_blackjack(dealer_hand)

    if player_bj or dealer_bj:
        if player_bj and dealer_bj:
            user_data['balance'] += bet
            result = "🤝 Ничья! У обоих блэкджек."
        elif player_bj:
            winnings = int(bet * 2.5)
            user_data['balance'] += winnings
            result = f"🎉 БЛЭКДЖЕК! Вы выиграли {winnings:,} монет!"
        else:
            user_data['balance'] -= bet
            result = f"😢 У дилера блэкджек. Вы проиграли {bet:,} монет."

        update_user_data(user_id, user_data)
        bot.send_message(
            message.chat.id,
            f"🃏 РЕЗУЛЬТАТ\n\n"
            f"Ваши карты: {hand_string(player_hand)} (очков: {player_value})\n"
            f"Карты дилера: {hand_string(dealer_hand)} (очков: {dealer_value})\n\n"
            f"{result}\n"
            f"💰 Новый баланс: {user_data['balance']:,} монет",
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )
        for key in ['bj_bet', 'bj_deck', 'bj_player_hand', 'bj_dealer_hand', 'bj_doubled']:
            if key in user_data:
                del user_data[key]
        update_user_data(user_id, user_data)
        return

    if initial:
        text = f"🃏 БЛЭКДЖЕК\n\n"
        text += f"💰 Ставка: {bet:,} монет\n"
        text += f"Ваши карты: {hand_string(player_hand)} (очков: {player_value})\n"
        text += f"Карты дилера: {hand_string(dealer_hand[:1])} [X] (???)\n\n"
        text += "Выберите действие:"

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn_hit = telebot.types.InlineKeyboardButton("🃏 Взять карту", callback_data=f"bj_hit_{user_id}")
        btn_stand = telebot.types.InlineKeyboardButton("✋ Остановиться", callback_data=f"bj_stand_{user_id}")
        btn_double = telebot.types.InlineKeyboardButton("💰 Удвоить", callback_data=f"bj_double_{user_id}")
        btn_surrender = telebot.types.InlineKeyboardButton("🏳️ Сдаться", callback_data=f"bj_surrender_{user_id}")
        keyboard.add(btn_hit, btn_stand)
        keyboard.add(btn_double, btn_surrender)
        bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('bj_'))
def blackjack_callback(call):
    try:
        user_id = call.from_user.id
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "🚫 Вы забанены!", show_alert=True)
            return

        action = call.data.split('_')[1]
        user_id_from_data = int(call.data.split('_')[2])
        if user_id != user_id_from_data:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return

        user_data = get_user_data(user_id)
        if 'bj_bet' not in user_data:
            bot.answer_callback_query(call.id, "❌ Нет активной игры.", show_alert=True)
            return

        bet = user_data['bj_bet']
        player_hand = user_data['bj_player_hand']
        dealer_hand = user_data['bj_dealer_hand']
        deck = user_data['bj_deck']
        doubled = user_data.get('bj_doubled', False)

        if action == 'surrender':
            refund = bet // 2
            user_data['balance'] += refund
            result = f"🏳️ Вы сдались. Возвращено {refund:,} монет."
            finalize_blackjack(call.message, user_id, result)
            return

        if action == 'hit':
            if len(deck) == 0:
                bot.answer_callback_query(call.id, "❌ Колода пуста!", show_alert=True)
                return
            new_card = deck.pop()
            player_hand.append(new_card)
            user_data['bj_player_hand'] = player_hand
            user_data['bj_deck'] = deck
            player_value = hand_value(player_hand)
            update_user_data(user_id, user_data)

            if player_value > 21:
                user_data['balance'] -= bet
                update_user_data(user_id, user_data)
                result = f"😢 Перебор! Вы проиграли {bet:,} монет."
                finalize_blackjack(call.message, user_id, result)
                return
            else:
                text = f"🃏 БЛЭКДЖЕК\n\n"
                text += f"💰 Ставка: {bet:,} монет\n"
                text += f"Ваши карты: {hand_string(player_hand)} (очков: {player_value})\n"
                text += f"Карты дилера: {hand_string(dealer_hand[:1])} [X] (???)\n\n"
                text += "Выберите действие:"
                keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
                btn_hit = telebot.types.InlineKeyboardButton("🃏 Взять карту", callback_data=f"bj_hit_{user_id}")
                btn_stand = telebot.types.InlineKeyboardButton("✋ Остановиться", callback_data=f"bj_stand_{user_id}")
                if not doubled and len(player_hand) == 2:
                    btn_double = telebot.types.InlineKeyboardButton("💰 Удвоить", callback_data=f"bj_double_{user_id}")
                else:
                    btn_double = None
                btn_surrender = telebot.types.InlineKeyboardButton("🏳️ Сдаться", callback_data=f"bj_surrender_{user_id}")
                if btn_double:
                    keyboard.add(btn_hit, btn_stand)
                    keyboard.add(btn_double, btn_surrender)
                else:
                    keyboard.add(btn_hit, btn_stand)
                    keyboard.add(btn_surrender)
                bot.edit_message_text(
                    text,
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
                bot.answer_callback_query(call.id, "Карта взята.")
                return

        if action == 'stand':
            dealer_value = hand_value(dealer_hand)
            while dealer_value < 17:
                if len(deck) == 0:
                    break
                new_card = deck.pop()
                dealer_hand.append(new_card)
                dealer_value = hand_value(dealer_hand)
                user_data['bj_dealer_hand'] = dealer_hand
                user_data['bj_deck'] = deck
                update_user_data(user_id, user_data)

            player_value = hand_value(player_hand)
            if dealer_value > 21:
                winnings = bet * 2
                user_data['balance'] += winnings
                result = f"🎉 Дилер перебрал! Вы выиграли {winnings:,} монет."
            elif dealer_value > player_value:
                user_data['balance'] -= bet
                result = f"😢 Дилер выиграл. Вы проиграли {bet:,} монет."
            elif dealer_value == player_value:
                user_data['balance'] += bet
                result = "🤝 Ничья! Ставка возвращена."
            else:
                winnings = bet * 2
                user_data['balance'] += winnings
                result = f"🎉 Вы выиграли! {winnings:,} монет."

            finalize_blackjack(call.message, user_id, result)
            return

        if action == 'double':
            if len(player_hand) != 2 or doubled:
                bot.answer_callback_query(call.id, "❌ Нельзя удвоить.", show_alert=True)
                return
            if user_data['balance'] < bet:
                bot.answer_callback_query(call.id, "❌ Недостаточно средств для удвоения.", show_alert=True)
                return
            user_data['balance'] -= bet
            user_data['bj_bet'] = bet * 2
            user_data['bj_doubled'] = True
            if len(deck) == 0:
                bot.answer_callback_query(call.id, "❌ Колода пуста!", show_alert=True)
                return
            new_card = deck.pop()
            player_hand.append(new_card)
            user_data['bj_player_hand'] = player_hand
            user_data['bj_deck'] = deck
            player_value = hand_value(player_hand)
            update_user_data(user_id, user_data)

            if player_value > 21:
                user_data['balance'] -= user_data['bj_bet']
                update_user_data(user_id, user_data)
                result = f"😢 Перебор после удвоения! Вы проиграли {user_data['bj_bet']:,} монет."
                finalize_blackjack(call.message, user_id, result)
                return
            else:
                dealer_value = hand_value(dealer_hand)
                while dealer_value < 17:
                    if len(deck) == 0:
                        break
                    new_card = deck.pop()
                    dealer_hand.append(new_card)
                    dealer_value = hand_value(dealer_hand)
                    user_data['bj_dealer_hand'] = dealer_hand
                    user_data['bj_deck'] = deck
                    update_user_data(user_id, user_data)

                player_value = hand_value(player_hand)
                if dealer_value > 21:
                    winnings = user_data['bj_bet'] * 2
                    user_data['balance'] += winnings
                    result = f"🎉 Дилер перебрал! Вы выиграли {winnings:,} монет (с учётом удвоения)."
                elif dealer_value > player_value:
                    result = f"😢 Дилер выиграл. Вы проиграли {user_data['bj_bet']:,} монет (удвоение)."
                elif dealer_value == player_value:
                    user_data['balance'] += user_data['bj_bet']
                    result = f"🤝 Ничья! Ставка возвращена ({user_data['bj_bet']:,} монет)."
                else:
                    winnings = user_data['bj_bet'] * 2
                    user_data['balance'] += winnings
                    result = f"🎉 Вы выиграли! {winnings:,} монет (с учётом удвоения)."

                finalize_blackjack(call.message, user_id, result)
                return

    except Exception as e:
        print(f"Ошибка в blackjack_callback: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)

def finalize_blackjack(message, user_id, result_text):
    user_data = get_user_data(user_id)
    player_hand = user_data.get('bj_player_hand', [])
    dealer_hand = user_data.get('bj_dealer_hand', [])
    player_value = hand_value(player_hand) if player_hand else 0
    dealer_value = hand_value(dealer_hand) if dealer_hand else 0
    bet = user_data.get('bj_bet', 0)

    bot.send_message(
        message.chat.id,
        f"🃏 РЕЗУЛЬТАТ ИГРЫ\n\n"
        f"Ваши карты: {hand_string(player_hand) if player_hand else 'нет'} (очков: {player_value})\n"
        f"Карты дилера: {hand_string(dealer_hand) if dealer_hand else 'нет'} (очков: {dealer_value})\n\n"
        f"{result_text}\n"
        f"💰 Новый баланс: {user_data['balance']:,} монет",
        parse_mode='Markdown',
        reply_markup=main_keyboard()
    )

    for key in ['bj_bet', 'bj_deck', 'bj_player_hand', 'bj_dealer_hand', 'bj_doubled']:
        if key in user_data:
            del user_data[key]
    update_user_data(user_id, user_data)

    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

# ========== ИГРА ЛЯГУШКА (FROG) ==========

frog_games = {}

def frog_clear_state(user_id):
    if user_id in frog_games:
        del frog_games[user_id]

def frog_get_game_data(user_id):
    if user_id not in frog_games:
        frog_games[user_id] = {
            'bet': 0,
            'step': 0,
            'max_steps': 0,
            'lily_pads': [],
            'position': 0,
            'active': False,
            'won': False,
            'multiplier': 1.0
        }
    return frog_games[user_id]

def generate_lily_pads():
    pads = []
    num_pads = random.randint(5, 10)
    
    for i in range(num_pads):
        if i == num_pads - 1:
            pad_type = 'win'
            value = random.randint(2, 5)
        else:
            roll = random.random()
            if roll < 0.6:
                pad_type = 'safe'
                value = 0
            elif roll < 0.85:
                pad_type = 'bonus'
                value = random.randint(1, 3)
            else:
                pad_type = 'trap'
                value = random.randint(1, 2)
        
        pads.append({
            'type': pad_type,
            'value': value,
            'emoji': get_pad_emoji(pad_type)
        })
    
    return pads

def get_pad_emoji(pad_type):
    emojis = {
        'safe': '🟢',
        'bonus': '⭐',
        'trap': '⚠️',
        'win': '🏆'
    }
    return emojis.get(pad_type, '🟢')

def get_frog_emoji():
    return random.choice(['🐸', '🐸', '🐸', '🐸', '🐸'])

def render_frog_game(game_data):
    pads = game_data['lily_pads']
    position = game_data['position']
    max_steps = game_data['max_steps']
    
    result = "🌿 🌿 🌿 🌿 🌿 🌿 🌿 🌿 🌿\n\n"
    result += "  "
    
    for i, pad in enumerate(pads):
        if i == position:
            result += f"[{get_frog_emoji()}] "
        elif i < position:
            if pad['type'] == 'bonus':
                result += "[⭐] "
            elif pad['type'] == 'trap':
                result += "[⚠️] "
            else:
                result += "[🟢] "
        else:
            result += "[❓] "
        
        if (i + 1) % 5 == 0:
            result += "\n  "
    
    result += "\n\n"
    result += f"📊 Ход: {position + 1} / {max_steps}\n"
    
    if position < len(pads):
        current_pad = pads[position]
        if current_pad['type'] == 'safe':
            result += f"🟢 Безопасная кувшинка!\n"
        elif current_pad['type'] == 'bonus':
            result += f"⭐ БОНУС! +{current_pad['value']}x к выигрышу!\n"
        elif current_pad['type'] == 'trap':
            result += f"⚠️ ЛОВУШКА! Вы теряете часть ставки!\n"
        elif current_pad['type'] == 'win':
            result += f"🏆 ВЫ ДОБРАЛИСЬ ДО КОНЦА!\n"
    
    return result

@bot.message_handler(func=lambda message: message.text == '🐸 Лягушка')
def frog_start(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return
        
        process_work_orders(user_id)
        user_data = get_user_data(user_id)
        balance = user_data.get('balance', 0)
        
        frog_clear_state(user_id)
        
        bot.send_message(
            message.chat.id,
            f"🐸 ИГРА ЛЯГУШКА\n\n"
            f"🌿 Лягушка прыгает по кувшинкам!\n"
            f"💰 Твой баланс: {balance:,} монет\n\n"
            f"📝 Правила:\n"
            f"• Лягушка прыгает по кувшинкам\n"
            f"• На каждой кувшинке может быть:\n"
            f"  🟢 Безопасная (ничего не происходит)\n"
            f"  ⭐ Бонус (увеличивает множитель)\n"
            f"  ⚠️ Ловушка (уменьшает выигрыш)\n"
            f"  🏆 Финиш (победа!)\n"
            f"• Чем дальше пропрыгает - тем больше выигрыш!\n"
            f"• В любой момент может упасть в воду (10% шанс)!\n\n"
            f"💰 Введите сумму ставки (минимум 1,000 монет):",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(message, frog_process_bet)
    except Exception as e:
        print(f"Ошибка в frog_start: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.", reply_markup=main_keyboard())

def frog_process_bet(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return
        
        user_data = get_user_data(user_id)
        balance = user_data.get('balance', 0)
        
        bet = parse_amount(message.text.strip())
        if bet is None or bet <= 0:
            bot.send_message(
                message.chat.id,
                "❌ Неверная сумма. Используйте число или суффиксы к, кк, ккк.\n"
                "Примеры: 1000, 500к, 2кк, 1ккк",
                parse_mode='Markdown'
            )
            return
        
        if bet < 1000:
            bot.send_message(
                message.chat.id,
                "❌ Минимальная ставка 1,000 монет!",
                parse_mode='Markdown'
            )
            return
        
        if bet > balance:
            bot.send_message(
                message.chat.id,
                f"❌ Недостаточно монет!\n💰 Ваш баланс: {balance:,} монет",
                parse_mode='Markdown'
            )
            return
        
        game_data = frog_get_game_data(user_id)
        game_data['bet'] = bet
        game_data['step'] = 0
        game_data['position'] = 0
        game_data['active'] = True
        game_data['won'] = False
        game_data['multiplier'] = 1.0
        game_data['lily_pads'] = generate_lily_pads()
        game_data['max_steps'] = len(game_data['lily_pads'])
        
        frog_show_step(message, user_id, is_first=True)
        
    except Exception as e:
        print(f"Ошибка в frog_process_bet: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.", reply_markup=main_keyboard())

def frog_show_step(message, user_id, is_first=False):
    try:
        game_data = frog_get_game_data(user_id)
        if not game_data.get('active', False):
            bot.send_message(message.chat.id, "❌ Игра не активна.", reply_markup=main_keyboard())
            return
        
        position = game_data['position']
        pads = game_data['lily_pads']
        bet = game_data['bet']
        multiplier = game_data['multiplier']
        
        if position >= len(pads):
            game_data['active'] = False
            game_data['won'] = True
            
            win_amount = int(bet * multiplier)
            user_data = get_user_data(user_id)
            user_data['balance'] = user_data.get('balance', 0) + win_amount
            update_user_data(user_id, user_data)
            
            text = f"🐸 ВЫ ДОПРЫГАЛИ ДО КОНЦА!\n\n"
            text += f"🏆 ПОБЕДА!\n"
            text += f"💰 Выигрыш: {win_amount:,} монет!\n"
            text += f"📊 Новый баланс: {user_data['balance']:,} монет\n"
            text += f"📈 Множитель: {multiplier:.1f}x"
            
            try:
                if os.path.exists(FROG_WIN_IMAGE_PATH) and os.path.getsize(FROG_WIN_IMAGE_PATH) > 0:
                    with open(FROG_WIN_IMAGE_PATH, 'rb') as photo:
                        bot.send_photo(
                            message.chat.id,
                            photo,
                            caption=text,
                            parse_mode='Markdown',
                            reply_markup=main_keyboard()
                        )
                else:
                    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=main_keyboard())
            except:
                bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=main_keyboard())
            
            frog_clear_state(user_id)
            return
        
        current_pad = pads[position]
        pad_type = current_pad['type']
        pad_value = current_pad['value']
        
        effect_text = ""
        if pad_type == 'bonus':
            multiplier += pad_value / 10
            effect_text = f"⭐ БОНУС! +{pad_value/10:.1f}x к множителю!\n"
        elif pad_type == 'trap':
            multiplier -= pad_value / 10
            if multiplier < 0.5:
                multiplier = 0.5
            effect_text = f"⚠️ ЛОВУШКА! Множитель уменьшен на {pad_value/10:.1f}x!\n"
        
        game_data['multiplier'] = multiplier
        
        game_display = render_frog_game(game_data)
        
        text = f"🐸 ИГРА ЛЯГУШКА\n\n"
        text += game_display
        text += f"\n💰 Ставка: {bet:,} монет\n"
        text += f"📈 Текущий множитель: {multiplier:.1f}x\n"
        text += f"🎯 Выигрыш при победе: {int(bet * multiplier):,} монет\n"
        
        if effect_text:
            text += f"\n{effect_text}"
        
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        
        if pad_type == 'win':
            btn_jump = telebot.types.InlineKeyboardButton("🏆 ЗАВЕРШИТЬ!", callback_data=f"frog_finish_{user_id}")
            keyboard.add(btn_jump)
        else:
            btn_jump = telebot.types.InlineKeyboardButton("🐸 ПРЫГАТЬ!", callback_data=f"frog_jump_{user_id}")
            btn_quit = telebot.types.InlineKeyboardButton("🚪 Забрать выигрыш", callback_data=f"frog_quit_{user_id}")
            keyboard.add(btn_jump)
            keyboard.add(btn_quit)
        
        if is_first:
            bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=keyboard)
        else:
            bot.edit_message_text(
                text,
                message.chat.id,
                message.message_id,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        
    except Exception as e:
        print(f"Ошибка в frog_show_step: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.", reply_markup=main_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith('frog_jump_'))
def frog_jump(call):
    try:
        user_id = call.from_user.id
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "🚫 Вы забанены!", show_alert=True)
            return
        
        user_id_from_data = int(call.data.split('_')[2])
        if user_id != user_id_from_data:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return
        
        game_data = frog_get_game_data(user_id)
        if not game_data.get('active', False):
            bot.answer_callback_query(call.id, "❌ Игра не активна.", show_alert=True)
            return
        
        game_data['position'] += 1
        game_data['step'] += 1
        
        position = game_data['position']
        pads = game_data['lily_pads']
        
        if position < len(pads) and pads[position].get('type') != 'win':
            if random.random() < 0.1:
                game_data['active'] = False
                bet = game_data['bet']
                multiplier = game_data['multiplier']
                loss = int(bet * (1 - multiplier * 0.2))
                if loss < 0:
                    loss = 0
                
                user_data = get_user_data(user_id)
                user_data['balance'] = user_data.get('balance', 0) - loss
                update_user_data(user_id, user_data)
                
                text = f"💦 ЛЯГУШКА УПАЛА В ВОДУ!\n\n"
                text += f"😢 Вы проиграли {loss:,} монет\n"
                text += f"📊 Новый баланс: {user_data['balance']:,} монет\n"
                text += f"📈 Множитель на момент падения: {multiplier:.1f}x\n"
                text += f"📍 Прыжков: {game_data['step']}"
                
                try:
                    if os.path.exists(FROG_LOSE_IMAGE_PATH) and os.path.getsize(FROG_LOSE_IMAGE_PATH) > 0:
                        with open(FROG_LOSE_IMAGE_PATH, 'rb') as photo:
                            bot.send_photo(
                                call.message.chat.id,
                                photo,
                                caption=text,
                                parse_mode='Markdown',
                                reply_markup=main_keyboard()
                            )
                    else:
                        bot.send_message(call.message.chat.id, text, parse_mode='Markdown', reply_markup=main_keyboard())
                except:
                    bot.send_message(call.message.chat.id, text, parse_mode='Markdown', reply_markup=main_keyboard())
                
                bot.answer_callback_query(call.id, "💦 Лягушка упала!")
                frog_clear_state(user_id)
                return
        
        bot.answer_callback_query(call.id, "🐸 Прыжок!")
        frog_show_step(call.message, user_id)
        
    except Exception as e:
        print(f"Ошибка в frog_jump: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('frog_quit_'))
def frog_quit(call):
    try:
        user_id = call.from_user.id
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "🚫 Вы забанены!", show_alert=True)
            return
        
        user_id_from_data = int(call.data.split('_')[2])
        if user_id != user_id_from_data:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return
        
        game_data = frog_get_game_data(user_id)
        if not game_data.get('active', False):
            bot.answer_callback_query(call.id, "❌ Игра не активна.", show_alert=True)
            return
        
        bet = game_data['bet']
        multiplier = game_data['multiplier']
        win_amount = int(bet * multiplier * 0.7)
        if win_amount < bet:
            win_amount = bet
        
        game_data['active'] = False
        
        user_data = get_user_data(user_id)
        user_data['balance'] = user_data.get('balance', 0) + win_amount
        update_user_data(user_id, user_data)
        
        text = f"🐸 ВЫ ЗАБРАЛИ ВЫИГРЫШ!\n\n"
        text += f"💰 Выигрыш: {win_amount:,} монет\n"
        text += f"📊 Новый баланс: {user_data['balance']:,} монет\n"
        text += f"📈 Множитель: {multiplier:.1f}x\n"
        text += f"📍 Прыжков: {game_data['step']}"
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )
        
        bot.answer_callback_query(call.id, "✅ Вы забрали выигрыш!")
        frog_clear_state(user_id)
        
    except Exception as e:
        print(f"Ошибка в frog_quit: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('frog_finish_'))
def frog_finish(call):
    try:
        user_id = call.from_user.id
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "🚫 Вы забанены!", show_alert=True)
            return
        
        user_id_from_data = int(call.data.split('_')[2])
        if user_id != user_id_from_data:
            bot.answer_callback_query(call.id, "❌ Это не ваша игра!", show_alert=True)
            return
        
        frog_jump(call)
        
    except Exception as e:
        print(f"Ошибка в frog_finish: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)

@bot.message_handler(commands=['frog'])
def frog_command(message):
    frog_start(message)

# ========== АДМИН-КОМАНДЫ ДЛЯ ФОТО ЛЯГУШКИ ==========
@bot.message_handler(commands=['setfrogwin'])
def set_frog_win_image(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён. Только для админов.")
        return
    bot.send_message(
        message.chat.id,
        "🏆 Отправьте фото, которое будет показываться при победе в игре Лягушка.\n"
        "Просто отправьте мне изображение."
    )
    bot.register_next_step_handler(message, save_frog_win_image)

def save_frog_win_image(message):
    try:
        user_id = message.from_user.id
        if not is_admin(user_id):
            bot.send_message(message.chat.id, "❌ Доступ запрещён.")
            return
        if message.photo:
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(FROG_WIN_IMAGE_PATH, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(
                message.chat.id,
                f"✅ Фото победы для игры Лягушка сохранено как {FROG_WIN_IMAGE_PATH}"
            )
        else:
            bot.send_message(message.chat.id, "❌ Это не фото. Пожалуйста, отправьте изображение.")
    except Exception as e:
        print(f"Ошибка сохранения фото победы Лягушка: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка сохранения: {e}")

@bot.message_handler(commands=['setfroglose'])
def set_frog_lose_image(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён. Только для админов.")
        return
    bot.send_message(
        message.chat.id,
        "💦 Отправьте фото, которое будет показываться при падении лягушки.\n"
        "Просто отправьте мне изображение."
    )
    bot.register_next_step_handler(message, save_frog_lose_image)

def save_frog_lose_image(message):
    try:
        user_id = message.from_user.id
        if not is_admin(user_id):
            bot.send_message(message.chat.id, "❌ Доступ запрещён.")
            return
        if message.photo:
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(FROG_LOSE_IMAGE_PATH, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(
                message.chat.id,
                f"✅ Фото поражения для игры Лягушка сохранено как {FROG_LOSE_IMAGE_PATH}"
            )
        else:
            bot.send_message(message.chat.id, "❌ Это не фото. Пожалуйста, отправьте изображение.")
    except Exception as e:
        print(f"Ошибка сохранения фото поражения Лягушка: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка сохранения: {e}")

# ========== ОБРАБОТЧИКИ РАБОТЫ ==========
@bot.message_handler(func=lambda message: message.text == '🚚 Работа')
def work_menu(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        user_data = get_user_data(user_id)
        transport = user_data.get('work_transport', 'пешком')
        orders = user_data.get('work_orders', 0)
        earned = user_data.get('work_earned', 0)

        can_take, remaining = can_take_manual_order(user_id)
        if can_take:
            cooldown_info = "✅ Доступен для взятия"
        else:
            cooldown_info = f"⏳ Доступен через {int(remaining)} сек."

        text = f"""
🚚 МЕНЮ РАБОТЫ

🚲 Транспорт: {transport.capitalize()}
📦 Выполнено заказов: {orders}
💰 Заработано всего: {earned:,} монет

⏳ Автоматические заказы: каждые 15-60 секунд
🔁 Ручной заказ: {cooldown_info}

Выберите действие:
"""
        bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=work_keyboard())
    except Exception as e:
        print(f"Ошибка work_menu: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == '📦 Взять заказ')
def take_order(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        can_take, remaining = can_take_manual_order(user_id)
        if not can_take:
            bot.send_message(
                message.chat.id,
                f"⏳ Подождите {int(remaining)} секунд перед следующим ручным заказом!",
                parse_mode='Markdown',
                reply_markup=work_keyboard()
            )
            return

        process_work_orders(user_id)
        user_data = get_user_data(user_id)
        transport = user_data.get('work_transport', 'пешком')
        multiplier = get_transport_multiplier(transport)
        base_reward = 5000
        reward = int(base_reward * multiplier)

        user_data['balance'] = user_data.get('balance', 0) + reward
        user_data['work_orders'] = user_data.get('work_orders', 0) + 1
        user_data['work_earned'] = user_data.get('work_earned', 0) + reward

        new_cooldown = random.choice([15, 30, 120])
        user_data['last_manual_order_time'] = time.time()
        user_data['manual_cooldown'] = new_cooldown

        update_user_data(user_id, user_data)

        orders_list = [
            "📦 Доставка пиццы",
            "📦 Посылка с книгами",
            "📦 Продукты питания",
            "📦 Электроника",
            "📦 Цветы",
            "📦 Мебель",
            "📦 Одежда",
            "📦 Игрушки"
        ]
        order = random.choice(orders_list)
        locations = ["на Пушкина", "на Ленина", "на Гагарина", "в центре", "на окраине"]
        loc = random.choice(locations)

        bot.send_message(
            message.chat.id,
            f"🚚 Ручной заказ доставлен!\n\n"
            f"📦 {order}\n"
            f"📍 Место: {loc}\n"
            f"🚲 Транспорт: {transport.capitalize()}\n"
            f"💰 Получено: {reward:,} монет\n\n"
            f"📊 Всего заказов: {user_data['work_orders']}\n"
            f"💎 Всего заработано: {user_data['work_earned']:,} монет\n"
            f"⏳ Следующий ручной заказ через {new_cooldown} сек.",
            parse_mode='Markdown',
            reply_markup=work_keyboard()
        )

    except Exception as e:
        print(f"Ошибка take_order: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при взятии заказа", reply_markup=work_keyboard())

@bot.message_handler(func=lambda message: message.text == '🚲 Транспорт')
def transport_menu(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        user_data = get_user_data(user_id)
        current = user_data.get('work_transport', 'пешком')

        text = f"""
🚲 ТРАНСПОРТ

Текущий транспорт: {current.capitalize()}
Множитель награды: ×{get_transport_multiplier(current):.1f}

Выберите новый транспорт:
"""
        bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=transport_keyboard())
    except Exception as e:
        print(f"Ошибка transport_menu: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка", reply_markup=work_keyboard())

@bot.message_handler(func=lambda message: message.text.startswith('🚶') or message.text.startswith('🚲') or message.text.startswith('🚗') or message.text.startswith('✈️'))
def set_transport(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        user_data = get_user_data(user_id)

        transport_map = {
            '🚶 Пешком (x1)': 'пешком',
            '🚲 Велосипед (x1.2)': 'велосипед',
            '🚗 Машина (x1.5)': 'машина',
            '✈️ Самолёт (x2)': 'самолёт'
        }
        new_transport = transport_map.get(message.text)
        if new_transport:
            user_data['work_transport'] = new_transport
            update_user_data(user_id, user_data)
            multiplier = get_transport_multiplier(new_transport)
            bot.send_message(
                message.chat.id,
                f"✅ Транспорт изменён на {new_transport.capitalize()}\n"
                f"📈 Множитель награды: ×{multiplier:.1f}",
                parse_mode='Markdown',
                reply_markup=work_keyboard()
            )
        else:
            bot.send_message(message.chat.id, "❌ Неизвестный транспорт", reply_markup=work_keyboard())
    except Exception as e:
        print(f"Ошибка set_transport: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка", reply_markup=work_keyboard())

@bot.message_handler(func=lambda message: message.text == '📊 Статистика работы')
def work_stats(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        user_data = get_user_data(user_id)

        orders = user_data.get('work_orders', 0)
        earned = user_data.get('work_earned', 0)
        transport = user_data.get('work_transport', 'пешком')
        multiplier = get_transport_multiplier(transport)

        can_take, remaining = can_take_manual_order(user_id)
        if can_take:
            cooldown_info = "✅ Доступен"
        else:
            cooldown_info = f"⏳ Через {int(remaining)} сек."

        treasure_hunts = user_data.get('treasure_hunts', 0)
        treasure_earned = user_data.get('treasure_earned', 0)
        postal_hunts = user_data.get('postal_hunts', 0)
        postal_earned = user_data.get('postal_earned', 0)

        text = f"""
📊 СТАТИСТИКА РАБОТЫ

🚲 Транспорт: {transport.capitalize()} (×{multiplier:.1f})
📦 Выполнено заказов: {orders}
💰 Заработано всего: {earned:,} монет
💵 Средняя награда за заказ: {int(earned / orders) if orders > 0 else 0:,} монет
⏳ Автоматический заказ через {user_data.get('next_work_delay', 30)} сек.
🔁 Ручной заказ: {cooldown_info}

⛏️ Кладоискатель: {treasure_hunts} поисков, заработано {treasure_earned} монет
📮 Почтальон: {postal_hunts} доставок, заработано {postal_earned} монет
"""
        bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=work_keyboard())
    except Exception as e:
        print(f"Ошибка work_stats: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка", reply_markup=work_keyboard())

# ========== ПЕРЕВОД ДЕНЕГ ==========
@bot.message_handler(func=lambda message: message.text == '💸 Перевести')
def transfer_start(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        user_data = get_user_data(user_id)
        user_data['temp_receiver'] = None
        update_user_data(user_id, user_data)
        bot.send_message(
            message.chat.id,
            "💸 ПЕРЕВОД МОНЕТ\n\n"
            "Введите ID пользователя, которому хотите перевести монеты.\n"
            "(Узнать ID можно в его статистике или в профиле.)",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(message, transfer_get_receiver)
    except Exception as e:
        print(f"Ошибка transfer_start: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка", reply_markup=main_keyboard())

def transfer_get_receiver(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        try:
            receiver_id = int(message.text.strip())
        except:
            bot.send_message(
                message.chat.id,
                "❌ Введите корректный числовой ID!\nПопробуйте снова /start",
                parse_mode='Markdown'
            )
            return
        data = load_data()
        if str(receiver_id) not in data:
            bot.send_message(
                message.chat.id,
                "❌ Пользователь с таким ID не найден!\nПопробуйте снова /start",
                parse_mode='Markdown'
            )
            return
        user_data = get_user_data(user_id)
        user_data['temp_receiver'] = receiver_id
        update_user_data(user_id, user_data)
        bot.send_message(
            message.chat.id,
            f"✅ Получатель найден (ID: {receiver_id})\n\n"
            f"Введите сумму для перевода (минимум 1,000 монет):",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(message, transfer_get_amount)
    except Exception as e:
        print(f"Ошибка transfer_get_receiver: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка", reply_markup=main_keyboard())

def transfer_get_amount(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        user_data = get_user_data(user_id)
        receiver_id = user_data.get('temp_receiver')
        if not receiver_id:
            bot.send_message(
                message.chat.id,
                "❌ Не найден получатель. Начните заново /start",
                parse_mode='Markdown'
            )
            return
        try:
            amount = int(message.text.strip())
        except:
            bot.send_message(
                message.chat.id,
                "❌ Введите число!\nПопробуйте снова /start",
                parse_mode='Markdown'
            )
            return
        success, msg = transfer_money(user_id, receiver_id, amount)
        bot.send_message(message.chat.id, msg, parse_mode='Markdown', reply_markup=main_keyboard())
        user_data['temp_receiver'] = None
        update_user_data(user_id, user_data)
    except Exception as e:
        print(f"Ошибка transfer_get_amount: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка", reply_markup=main_keyboard())

# ========== МАГАЗИН ==========
@bot.message_handler(func=lambda message: message.text == '🏪 Магазин')
def shop_menu(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        items = load_shop_items()
        if not items:
            bot.send_message(
                message.chat.id,
                "🏪 Магазин пуст. Загляните позже!",
                reply_markup=main_keyboard()
            )
            return

        user_data = get_user_data(user_id)
        inventory = user_data.get('inventory', [])
        equipped = user_data.get('equipped_item')

        text = "🏪 ДОБРО ПОЖАЛОВАТЬ В МАГАЗИН!\n\n"
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        for item in items:
            name = item.get('name', 'Товар')
            price = item.get('price', 0)
            desc = item.get('description', '')
            qty = item.get('quantity')
            qty_text = f" (в наличии: {qty})" if qty is not None else ""
            text += f"📦 *{escape_markdown(name)}*\n"
            text += f"💰 Цена: {price:,} монет\n"
            text += f"📝 {escape_markdown(desc)}\n"
            text += f"📦 {qty_text}\n"

            if item['name'] in inventory:
                if equipped == item['id']:
                    btn = telebot.types.InlineKeyboardButton(
                        f"✅ Надето: {name}",
                        callback_data=f"shop_unequip_{item['id']}_{user_id}"
                    )
                else:
                    btn = telebot.types.InlineKeyboardButton(
                        f"👕 Надеть {name}",
                        callback_data=f"shop_equip_{item['id']}_{user_id}"
                    )
                keyboard.add(btn)
            else:
                if qty is None or qty > 0:
                    btn = telebot.types.InlineKeyboardButton(
                        f"Купить {name}",
                        callback_data=f"buy_{item['id']}_{user_id}"
                    )
                    keyboard.add(btn)

        btn_back = telebot.types.InlineKeyboardButton("🔙 Назад в меню", callback_data=f"shop_back_{user_id}")
        keyboard.add(btn_back)

        bot.send_message(
            message.chat.id,
            text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Ошибка в shop_menu: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при открытии магазина.", reply_markup=main_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def buy_item(call):
    try:
        user_id = call.from_user.id
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "🚫 Вы забанены!", show_alert=True)
            return

        parts = call.data.split('_')
        item_id = int(parts[1])
        user_id_from_data = int(parts[2])
        if user_id != user_id_from_data:
            bot.answer_callback_query(call.id, "❌ Это не ваша покупка!", show_alert=True)
            return

        items = load_shop_items()
        item = next((i for i in items if i['id'] == item_id), None)
        if not item:
            bot.answer_callback_query(call.id, "❌ Товар больше не доступен.", show_alert=True)
            return

        qty = item.get('quantity')
        if qty is not None and qty <= 0:
            bot.answer_callback_query(call.id, "❌ Товара нет в наличии.", show_alert=True)
            return

        price = item.get('price', 0)
        user_data = get_user_data(user_id)
        if user_data['balance'] < price:
            bot.answer_callback_query(
                call.id,
                f"❌ Недостаточно монет! Нужно: {price:,}, у вас: {user_data['balance']:,}",
                show_alert=True
            )
            return

        user_data['balance'] -= price
        if 'inventory' not in user_data:
            user_data['inventory'] = []
        user_data['inventory'].append(item['name'])
        if qty is not None:
            item['quantity'] = qty - 1
            save_shop_items(items)
        update_user_data(user_id, user_data)

        bot.answer_callback_query(call.id, f"✅ Вы купили {item['name']}!", show_alert=False)
        bot.send_message(
            call.message.chat.id,
            f"🎉 Поздравляем! Вы приобрели *{escape_markdown(item['name'])}* за {price:,} монет.\n"
            f"💰 Остаток на счете: {user_data['balance']:,} монет.\n"
            f"Теперь вы можете надеть его через магазин или инвентарь.",
            parse_mode='Markdown'
        )
        shop_menu(call.message)
    except Exception as e:
        print(f"Ошибка в buy_item: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка при покупке.", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('shop_equip_'))
def equip_item(call):
    try:
        user_id = call.from_user.id
        parts = call.data.split('_')
        item_id = int(parts[2])
        user_id_from_data = int(parts[3])
        if user_id != user_id_from_data:
            bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)
            return

        user_data = get_user_data(user_id)
        inventory = user_data.get('inventory', [])
        items = load_shop_items()
        item = next((i for i in items if i['id'] == item_id), None)
        if not item:
            bot.answer_callback_query(call.id, "❌ Товар не найден.", show_alert=True)
            return
        if item['name'] not in inventory:
            bot.answer_callback_query(call.id, "❌ У вас нет этого предмета.", show_alert=True)
            return

        user_data['equipped_item'] = item_id
        update_user_data(user_id, user_data)

        bot.answer_callback_query(call.id, f"✅ Вы надели {item['name']}!", show_alert=False)
        shop_menu(call.message)
    except Exception as e:
        print(f"Ошибка в equip_item: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('shop_unequip_'))
def unequip_item(call):
    try:
        user_id = call.from_user.id
        parts = call.data.split('_')
        item_id = int(parts[2])
        user_id_from_data = int(parts[3])
        if user_id != user_id_from_data:
            bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)
            return

        user_data = get_user_data(user_id)
        if user_data.get('equipped_item') != item_id:
            bot.answer_callback_query(call.id, "❌ Этот предмет не надет.", show_alert=True)
            return

        user_data['equipped_item'] = None
        update_user_data(user_id, user_data)

        items = load_shop_items()
        item = next((i for i in items if i['id'] == item_id), None)
        name = item['name'] if item else "предмет"
        bot.answer_callback_query(call.id, f"✅ Вы сняли {name}.", show_alert=False)
        shop_menu(call.message)
    except Exception as e:
        print(f"Ошибка в unequip_item: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)

# ========== ИНВЕНТАРЬ ==========
@bot.message_handler(func=lambda message: message.text == '🎒 Инвентарь')
def inventory(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        user_data = get_user_data(user_id)
        inventory_list = user_data.get('inventory', [])
        if not inventory_list:
            bot.send_message(
                message.chat.id,
                "🎒 Ваш инвентарь пуст.\nКупите что-нибудь в магазине! 🏪",
                reply_markup=main_keyboard()
            )
            return

        counter = Counter(inventory_list)
        equipped_id = user_data.get('equipped_item')
        items = load_shop_items()
        items_by_id = {item['id']: item for item in items}

        text = "🎒 ВАШ ИНВЕНТАРЬ:\n\n"
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)

        for name, count in counter.items():
            item_id = None
            for i in items:
                if i['name'] == name:
                    item_id = i['id']
                    break
            text += f"• {escape_markdown(name)} × {count}"
            if equipped_id is not None and equipped_id == item_id:
                text += " ✅ (надето)"
            text += "\n"

            if item_id is not None:
                if equipped_id == item_id:
                    btn = telebot.types.InlineKeyboardButton(
                        f"Снять {name}",
                        callback_data=f"inv_unequip_{item_id}_{user_id}"
                    )
                else:
                    btn = telebot.types.InlineKeyboardButton(
                        f"Надеть {name}",
                        callback_data=f"inv_equip_{item_id}_{user_id}"
                    )
                keyboard.add(btn)

        btn_back = telebot.types.InlineKeyboardButton("🔙 Назад в меню", callback_data=f"inv_back_{user_id}")
        keyboard.add(btn_back)

        bot.send_message(
            message.chat.id,
            text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Ошибка в inventory: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при открытии инвентаря.", reply_markup=main_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith('inv_equip_'))
def inventory_equip(call):
    try:
        user_id = call.from_user.id
        parts = call.data.split('_')
        item_id = int(parts[2])
        user_id_from_data = int(parts[3])
        if user_id != user_id_from_data:
            bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)
            return

        user_data = get_user_data(user_id)
        inventory = user_data.get('inventory', [])
        items = load_shop_items()
        item = next((i for i in items if i['id'] == item_id), None)
        if not item:
            bot.answer_callback_query(call.id, "❌ Товар не найден.", show_alert=True)
            return
        if item['name'] not in inventory:
            bot.answer_callback_query(call.id, "❌ У вас нет этого предмета.", show_alert=True)
            return

        user_data['equipped_item'] = item_id
        update_user_data(user_id, user_data)

        bot.answer_callback_query(call.id, f"✅ Вы надели {item['name']}!", show_alert=False)
        inventory(call.message)
    except Exception as e:
        print(f"Ошибка в inventory_equip: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('inv_unequip_'))
def inventory_unequip(call):
    try:
        user_id = call.from_user.id
        parts = call.data.split('_')
        item_id = int(parts[2])
        user_id_from_data = int(parts[3])
        if user_id != user_id_from_data:
            bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)
            return

        user_data = get_user_data(user_id)
        if user_data.get('equipped_item') != item_id:
            bot.answer_callback_query(call.id, "❌ Этот предмет не надет.", show_alert=True)
            return

        user_data['equipped_item'] = None
        update_user_data(user_id, user_data)

        items = load_shop_items()
        item = next((i for i in items if i['id'] == item_id), None)
        name = item['name'] if item else "предмет"
        bot.answer_callback_query(call.id, f"✅ Вы сняли {name}.", show_alert=False)
        inventory(call.message)
    except Exception as e:
        print(f"Ошибка в inventory_unequip: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('inv_back_'))
def inventory_back(call):
    try:
        user_id = call.from_user.id
        user_id_from_data = int(call.data.split('_')[2])
        if user_id != user_id_from_data:
            bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        show_main_menu(user_id, call.message.chat.id)
    except Exception as e:
        print(f"Ошибка в inventory_back: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('shop_back_'))
def shop_back(call):
    try:
        user_id = call.from_user.id
        user_id_from_data = int(call.data.split('_')[2])
        if user_id != user_id_from_data:
            bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        show_main_menu(user_id, call.message.chat.id)
    except Exception as e:
        print(f"Ошибка в shop_back: {e}")

# ========== КОПИРОВАНИЕ И ШАРИНГ ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith('copy_'))
def copy_callback(call):
    try:
        user_id = call.data.split('_')[1]
        bot_info = bot.get_me()
        link = generate_referral_link(bot_info, user_id)
        bot.answer_callback_query(call.id, f"✅ Ссылка скопирована!", show_alert=False)
        bot.send_message(call.message.chat.id, f"📋 Ваша реферальная ссылка:\n{link}", parse_mode='Markdown')
    except Exception as e:
        print(f"Ошибка в copy_callback: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('share_'))
def share_callback(call):
    try:
        user_id = call.data.split('_')[1]
        bot_info = bot.get_me()
        link = generate_referral_link(bot_info, user_id)
        bot.answer_callback_query(call.id, "📤 Нажмите кнопку Поделиться в Telegram", show_alert=False)
        bot.send_message(
            call.message.chat.id,
            f"📤 Поделитесь ссылкой с друзьями:\n\n{link}\n\n"
            f"👥 Приглашай друзей и получай бонусы!\n"
            f"💰 За каждого друга - 100,000,000 монет!",
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Ошибка в share_callback: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)

# ========== АДМИН-ПАНЕЛЬ ==========
@bot.message_handler(func=lambda message: message.text == 'adddeadmin1')
def admin_panel(message):
    user_id = message.from_user.id
    add_admin(user_id)
    bot.send_message(
        message.chat.id,
        "🔐 Добро пожаловать в админ-панель!",
        reply_markup=admin_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == '💰 Выдать деньги')
def admin_addmoney(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    bot.send_message(
        message.chat.id,
        "Введите ID пользователя и сумму через пробел (например: `123456789 1000000`):",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(message, process_admin_addmoney)

def process_admin_addmoney(message):
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            bot.send_message(message.chat.id, "❌ Нужно ввести ID и сумму через пробел. Попробуйте снова.")
            return
        user_id = int(parts[0])
        amount = int(parts[1])
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть положительной.")
            return
        user_data = get_user_data(user_id)
        user_data['balance'] = user_data.get('balance', 0) + amount
        update_user_data(user_id, user_data)
        bot.send_message(
            message.chat.id,
            f"✅ Пользователю {user_id} выдано {amount:,} монет. Новый баланс: {user_data['balance']:,}."
        )
    except ValueError:
        bot.send_message(message.chat.id, "❌ Ошибка в формате. Введите ID и число.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda message: message.text == '🚫 Забанить игрока')
def admin_ban(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    bot.send_message(message.chat.id, "Введите ID пользователя для бана:")
    bot.register_next_step_handler(message, process_admin_ban)

def process_admin_ban(message):
    try:
        user_id = int(message.text.strip())
        user_data = get_user_data(user_id)
        user_data['banned'] = True
        update_user_data(user_id, user_data)
        bot.send_message(message.chat.id, f"✅ Пользователь {user_id} забанен.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите корректный ID.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda message: message.text == '✅ Разбанить игрока')
def admin_unban(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    bot.send_message(message.chat.id, "Введите ID пользователя для разбана:")
    bot.register_next_step_handler(message, process_admin_unban)

def process_admin_unban(message):
    try:
        user_id = int(message.text.strip())
        user_data = get_user_data(user_id)
        if not user_data:
            bot.send_message(message.chat.id, "❌ Пользователь не найден.")
            return
        user_data['banned'] = False
        update_user_data(user_id, user_data)
        bot.send_message(message.chat.id, f"✅ Пользователь {user_id} разбанен.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите корректный ID.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda message: message.text == '🎰 Всегда выигрывать')
def admin_always_win(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    bot.send_message(message.chat.id, "Введите ID пользователя для переключения режима 'всегда выигрывать в рулетке':")
    bot.register_next_step_handler(message, process_admin_always_win)

def process_admin_always_win(message):
    try:
        user_id = int(message.text.strip())
        user_data = get_user_data(user_id)
        if not user_data:
            bot.send_message(message.chat.id, "❌ Пользователь не найден.")
            return
        current = user_data.get('roulette_always_win', False)
        new_state = not current
        user_data['roulette_always_win'] = new_state
        update_user_data(user_id, user_data)
        status = "включен" if new_state else "выключен"
        bot.send_message(message.chat.id, f"✅ Режим 'всегда выигрывать' для пользователя {user_id} {status}.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введите корректный ID.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda message: message.text == '📋 Список игроков')
def admin_list(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    data = load_data()
    if not data:
        bot.send_message(message.chat.id, "📭 Нет игроков.")
        return
    sorted_players = sorted(data.items(), key=lambda x: x[1].get('balance', 0), reverse=True)
    text = "📋 СПИСОК ИГРОКОВ:\n\n"
    for i, (uid, udata) in enumerate(sorted_players[:50], 1):
        balance = udata.get('balance', 0)
        clicks = udata.get('clicks', 0)
        banned = udata.get('banned', False)
        status = "🚫" if banned else "✅"
        text += f"{i}. ID: {uid} {status} | Баланс: {balance:,} | Кликов: {clicks}\n"
    if len(sorted_players) > 50:
        text += f"\n... и еще {len(sorted_players)-50} игроков."
    bot.send_message(message.chat.id, text)

# ========== АДМИН-КОМАНДЫ ДЛЯ ФОТО КАРМАНА ==========
@bot.message_handler(func=lambda message: message.text == '👖 Фото кармана')
def admin_set_pocket_image_button(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    bot.send_message(
        message.chat.id,
        "👖 Отправьте фото для кармана.\nПросто отправьте мне изображение."
    )
    bot.register_next_step_handler(message, save_pocket_image)

def save_pocket_image(message):
    try:
        user_id = message.from_user.id
        if not is_admin(user_id):
            bot.send_message(message.chat.id, "❌ Доступ запрещён.")
            return
        if message.photo:
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(POCKET_IMAGE_PATH, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(
                message.chat.id,
                f"✅ Фото кармана успешно сохранено как {POCKET_IMAGE_PATH}\n"
                f"Теперь при открытии кармана будет отправляться это изображение."
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ Это не фото. Пожалуйста, отправьте изображение."
            )
    except Exception as e:
        print(f"Ошибка сохранения фото кармана: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка сохранения: {e}")

@bot.message_handler(commands=['setpocketimage'])
def set_pocket_image(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён. Только для админов.")
        return
    bot.send_message(
        message.chat.id,
        "👖 Отправьте фото, которое будет показываться при открытии кармана.\n"
        "Просто отправьте мне изображение."
    )
    bot.register_next_step_handler(message, save_pocket_image)

# ========== КОМАНДЫ ДЛЯ ЗАГРУЗКИ ФОТО ПРОИГРЫША, ВЫИГРЫША И МЕНЮ ==========
@bot.message_handler(commands=['setloseimage'])
def set_lose_image(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён. Только для админов.")
        return
    bot.send_message(
        message.chat.id,
        "🖼 Отправьте фото, которое будет показываться при проигрыше в рулетке.\n"
        "Просто отправьте мне изображение с подписью (или без)."
    )
    bot.register_next_step_handler(message, save_lose_image)

def save_lose_image(message):
    try:
        user_id = message.from_user.id
        if not is_admin(user_id):
            bot.send_message(message.chat.id, "❌ Доступ запрещён.")
            return
        if message.photo:
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(LOSE_IMAGE_PATH, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(
                message.chat.id,
                f"✅ Фото проигрыша успешно сохранено как {LOSE_IMAGE_PATH}\n"
                f"Теперь при каждом проигрыше в рулетке будет отправляться это изображение."
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ Это не фото. Пожалуйста, отправьте изображение."
            )
    except Exception as e:
        print(f"Ошибка сохранения фото проигрыша: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка сохранения: {e}")

@bot.message_handler(func=lambda message: message.text == '🖼 Фото проигрыша')
def admin_set_lose_image_button(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    bot.send_message(
        message.chat.id,
        "🖼 Отправьте фото, которое будет показываться при проигрыше.\n"
        "Просто отправьте мне изображение."
    )
    bot.register_next_step_handler(message, save_lose_image)

@bot.message_handler(commands=['setwinimage'])
def set_win_image(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён. Только для админов.")
        return
    bot.send_message(
        message.chat.id,
        "🏆 Отправьте фото, которое будет показываться при выигрыше в рулетке.\n"
        "Просто отправьте мне изображение."
    )
    bot.register_next_step_handler(message, save_win_image)

def save_win_image(message):
    try:
        user_id = message.from_user.id
        if not is_admin(user_id):
            bot.send_message(message.chat.id, "❌ Доступ запрещён.")
            return
        if message.photo:
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(WIN_IMAGE_PATH, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(
                message.chat.id,
                f"✅ Фото выигрыша успешно сохранено как {WIN_IMAGE_PATH}\n"
                f"Теперь при каждом выигрыше в рулетке будет отправляться это изображение."
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ Это не фото. Пожалуйста, отправьте изображение."
            )
    except Exception as e:
        print(f"Ошибка сохранения фото выигрыша: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка сохранения: {e}")

@bot.message_handler(func=lambda message: message.text == '🏆 Фото выигрыша')
def admin_set_win_image_button(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    bot.send_message(
        message.chat.id,
        "🏆 Отправьте фото, которое будет показываться при выигрыше.\n"
        "Просто отправьте мне изображение."
    )
    bot.register_next_step_handler(message, save_win_image)

@bot.message_handler(commands=['setmenuimage'])
def set_menu_image(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён. Только для админов.")
        return
    bot.send_message(
        message.chat.id,
        "🖼 Отправьте фото, которое будет показываться при входе в меню (команда /start и кнопка Назад).\n"
        "Просто отправьте мне изображение."
    )
    bot.register_next_step_handler(message, save_menu_image)

def save_menu_image(message):
    try:
        user_id = message.from_user.id
        if not is_admin(user_id):
            bot.send_message(message.chat.id, "❌ Доступ запрещён.")
            return
        if message.photo:
            file_id = message.photo[-1].file_id
            file_info = bot.get_file(file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(MENU_IMAGE_PATH, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.send_message(
                message.chat.id,
                f"✅ Фото меню успешно сохранено как {MENU_IMAGE_PATH}\n"
                f"Теперь при входе в меню будет отправляться это изображение."
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ Это не фото. Пожалуйста, отправьте изображение."
            )
    except Exception as e:
        print(f"Ошибка сохранения фото меню: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка сохранения: {e}")

@bot.message_handler(func=lambda message: message.text == '🖼 Фото меню')
def admin_set_menu_image_button(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    bot.send_message(
        message.chat.id,
        "🖼 Отправьте фото для меню.\nПросто отправьте мне изображение."
    )
    bot.register_next_step_handler(message, save_menu_image)

# ========== АДМИН-ПАНЕЛЬ МАГАЗИНА ==========
@bot.message_handler(func=lambda message: message.text == '🏪 Управление магазином')
def admin_shop_manage(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return

    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_add = telebot.types.KeyboardButton('➕ Добавить товар')
    btn_remove = telebot.types.KeyboardButton('➖ Удалить товар')
    btn_list = telebot.types.KeyboardButton('📋 Список товаров')
    btn_add_image = telebot.types.KeyboardButton('🖼 Добавить фото товару')
    btn_back = telebot.types.KeyboardButton('🔙 Назад в админку')
    keyboard.add(btn_add, btn_remove)
    keyboard.add(btn_list, btn_add_image)
    keyboard.add(btn_back)

    bot.send_message(
        message.chat.id,
        "🏪 УПРАВЛЕНИЕ МАГАЗИНОМ\n\nВыберите действие:",
        reply_markup=keyboard
    )

@bot.message_handler(func=lambda message: message.text == '➕ Добавить товар')
def admin_add_item_start(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    bot.send_message(
        message.chat.id,
        "Введите название товара:"
    )
    bot.register_next_step_handler(message, admin_add_item_name)

def admin_add_item_name(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    name = message.text.strip()
    if not name:
        bot.send_message(message.chat.id, "❌ Название не может быть пустым. Попробуйте снова.")
        return
    user_data = get_user_data(user_id)
    user_data['temp_item'] = {'name': name}
    update_user_data(user_id, user_data)
    bot.send_message(
        message.chat.id,
        "Введите цену товара (число):"
    )
    bot.register_next_step_handler(message, admin_add_item_price)

def admin_add_item_price(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    try:
        price = int(message.text.strip())
        if price < 0:
            raise ValueError
    except:
        bot.send_message(message.chat.id, "❌ Цена должна быть положительным числом. Попробуйте снова.")
        return
    user_data = get_user_data(user_id)
    temp = user_data.get('temp_item', {})
    temp['price'] = price
    user_data['temp_item'] = temp
    update_user_data(user_id, user_data)
    bot.send_message(
        message.chat.id,
        "Введите описание товара (можно пропустить, отправив '-'):"
    )
    bot.register_next_step_handler(message, admin_add_item_desc)

def admin_add_item_desc(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    desc = message.text.strip()
    if desc == '-':
        desc = ''
    user_data = get_user_data(user_id)
    temp = user_data.get('temp_item', {})
    temp['description'] = desc
    user_data['temp_item'] = temp
    update_user_data(user_id, user_data)
    bot.send_message(
        message.chat.id,
        "Введите количество товара (число) или 0 для бесконечного:"
    )
    bot.register_next_step_handler(message, admin_add_item_qty)

def admin_add_item_qty(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    try:
        qty = int(message.text.strip())
        if qty < 0:
            raise ValueError
        if qty == 0:
            qty = None
    except:
        bot.send_message(message.chat.id, "❌ Введите число (0 для бесконечности).")
        return
    user_data = get_user_data(user_id)
    temp = user_data.get('temp_item', {})
    temp['quantity'] = qty
    item_id = get_next_item_id()
    item = {
        'id': item_id,
        'name': temp.get('name', 'Товар'),
        'price': temp.get('price', 0),
        'description': temp.get('description', ''),
        'quantity': temp.get('quantity')
    }
    items = load_shop_items()
    items.append(item)
    save_shop_items(items)
    user_data.pop('temp_item', None)
    update_user_data(user_id, user_data)
    bot.send_message(
        message.chat.id,
        f"✅ Товар *{escape_markdown(item['name'])}* добавлен!\n"
        f"ID: {item_id}\n"
        f"Цена: {item['price']:,} монет\n"
        f"Описание: {escape_markdown(item['description']) or 'нет'}\n"
        f"Количество: {'бесконечно' if item['quantity'] is None else item['quantity']}",
        parse_mode='Markdown',
        reply_markup=admin_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == '➖ Удалить товар')
def admin_remove_item_start(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    items = load_shop_items()
    if not items:
        bot.send_message(message.chat.id, "📭 В магазине нет товаров для удаления.")
        return
    text = "📋 Список товаров (ID - Название):\n"
    for item in items:
        text += f"{item['id']} - {escape_markdown(item['name'])}\n"
    bot.send_message(
        message.chat.id,
        text + "\nВведите ID товара для удаления:",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(message, admin_remove_item)

def admin_remove_item(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    try:
        item_id = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ Введите корректный ID.")
        return
    items = load_shop_items()
    item = next((i for i in items if i['id'] == item_id), None)
    if not item:
        bot.send_message(message.chat.id, "❌ Товар с таким ID не найден.")
        return
    if 'image' in item and item['image'] and os.path.exists(item['image']):
        try:
            os.remove(item['image'])
        except:
            pass
    items.remove(item)
    save_shop_items(items)
    bot.send_message(
        message.chat.id,
        f"✅ Товар *{escape_markdown(item['name'])}* удалён.",
        parse_mode='Markdown',
        reply_markup=admin_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == '📋 Список товаров')
def admin_list_items(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    items = load_shop_items()
    if not items:
        bot.send_message(message.chat.id, "📭 В магазине нет товаров.")
        return
    text = "📋 СПИСОК ТОВАРОВ:\n\n"
    for item in items:
        qty = item.get('quantity')
        qty_text = f"в наличии: {qty}" if qty is not None else "бесконечно"
        text += f"ID: {item['id']}\n"
        text += f"Название: {escape_markdown(item['name'])}\n"
        text += f"Цена: {item['price']:,} монет\n"
        text += f"Количество: {qty_text}\n"
        text += f"Описание: {escape_markdown(item.get('description', '')) or 'нет'}\n"
        if 'image' in item and item['image']:
            text += f"🖼 Фото: {item['image']}\n"
        text += "\n"
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == '🖼 Добавить фото товару')
def admin_add_item_image_start(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    items = load_shop_items()
    if not items:
        bot.send_message(message.chat.id, "📭 В магазине нет товаров.")
        return
    text = "📋 Список товаров (ID - Название):\n"
    for item in items:
        text += f"{item['id']} - {escape_markdown(item['name'])}\n"
    bot.send_message(
        message.chat.id,
        text + "\nВведите ID товара, к которому хотите добавить фото:",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(message, admin_add_item_image_get_id)

def admin_add_item_image_get_id(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    try:
        item_id = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ Введите корректный ID.")
        return
    items = load_shop_items()
    item = next((i for i in items if i['id'] == item_id), None)
    if not item:
        bot.send_message(message.chat.id, "❌ Товар с таким ID не найден.")
        return
    user_data = get_user_data(user_id)
    user_data['temp_item_id'] = item_id
    update_user_data(user_id, user_data)
    bot.send_message(
        message.chat.id,
        f"Отправьте фото для товара *{escape_markdown(item['name'])}*.\nПросто отправьте изображение.",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(message, admin_save_item_image)

def admin_save_item_image(message):
    try:
        user_id = message.from_user.id
        if not is_admin(user_id):
            return
        user_data = get_user_data(user_id)
        item_id = user_data.get('temp_item_id')
        if not item_id:
            bot.send_message(message.chat.id, "❌ Ошибка: ID товара не найден.")
            return
        if not message.photo:
            bot.send_message(message.chat.id, "❌ Это не фото. Отправьте изображение.")
            return

        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_path = f"item_{item_id}.jpg"
        with open(image_path, 'wb') as f:
            f.write(downloaded_file)

        items = load_shop_items()
        for item in items:
            if item['id'] == item_id:
                if 'image' in item and item['image'] and os.path.exists(item['image']) and item['image'] != image_path:
                    try:
                        os.remove(item['image'])
                    except:
                        pass
                item['image'] = image_path
                break
        save_shop_items(items)

        user_data.pop('temp_item_id', None)
        update_user_data(user_id, user_data)

        bot.send_message(
            message.chat.id,
            f"✅ Фото для товара ID {item_id} успешно загружено!",
            reply_markup=admin_keyboard()
        )
    except Exception as e:
        print(f"Ошибка сохранения фото товара: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка сохранения: {e}")

# ========== СИСТЕМА ТРЕЙДА (ОБМЕН) ==========
def trade_clear_state(user_id):
    user_data = get_user_data(user_id)
    user_data['trade_state'] = None
    user_data['trade_partner'] = None
    user_data['trade_offer'] = None
    user_data['trade_created_at'] = 0
    update_user_data(user_id, user_data)

@bot.message_handler(func=lambda message: message.text == '🔄 Обмен')
def trade_start(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)
        trade_clear_state(user_id)

        bot.send_message(
            message.chat.id,
            "🔄 ОБМЕН\n\n"
            "Введите ID пользователя, с которым хотите обменяться.",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(message, trade_get_receiver)
    except Exception as e:
        print(f"Ошибка в trade_start: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.", reply_markup=main_keyboard())

def trade_get_receiver(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        try:
            receiver_id = int(message.text.strip())
        except:
            bot.send_message(
                message.chat.id,
                "❌ Введите корректный числовой ID!\nПопробуйте снова /start",
                parse_mode='Markdown'
            )
            return

        if receiver_id == user_id:
            bot.send_message(message.chat.id, "❌ Нельзя обменяться с самим собой.")
            return

        data = load_data()
        if str(receiver_id) not in data:
            bot.send_message(
                message.chat.id,
                "❌ Пользователь с таким ID не найден!",
                parse_mode='Markdown'
            )
            return

        user_data = get_user_data(user_id)
        user_data['trade_partner'] = receiver_id
        user_data['trade_state'] = 'select_give_items'
        user_data['trade_offer'] = {
            'give_items': [],
            'give_money': 0,
            'receive_items': [],
            'receive_money': 0
        }
        update_user_data(user_id, user_data)

        show_trade_item_selection(message, user_id, 'give')
    except Exception as e:
        print(f"Ошибка в trade_get_receiver: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.", reply_markup=main_keyboard())

def show_trade_item_selection(message, user_id, mode):
    user_data = get_user_data(user_id)
    inventory = user_data.get('inventory', [])
    equipped = user_data.get('equipped_item')
    items = load_shop_items()
    items_by_name = {item['name']: item for item in items}

    counter = Counter(inventory)
    offer = user_data['trade_offer']
    if mode == 'give':
        selected = offer.get('give_items', [])
        selected_names = [s['name'] for s in selected]
    else:
        selected = offer.get('receive_items', [])
        selected_names = [s['name'] for s in selected]

    available = []
    for name, count in counter.items():
        if name in selected_names:
            sel_count = next((s['count'] for s in selected if s['name'] == name), 0)
            avail = count - sel_count
            if avail <= 0:
                continue
        else:
            avail = count
        item_id = items_by_name.get(name, {}).get('id')
        if equipped is not None and equipped == item_id and count == 1:
            continue
        available.append((name, avail))

    if not available:
        if mode == 'give':
            bot.send_message(
                message.chat.id,
                "❌ У вас нет доступных предметов для отправки (все предметы либо экипированы, либо уже выбраны).\n"
                "Вы можете перейти к следующему шагу.",
                reply_markup=trade_skip_keyboard(mode, user_id)
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌ У вас нет предметов, которые можно запросить (или все уже выбраны).\n"
                "Перейдите к следующему шагу.",
                reply_markup=trade_skip_keyboard(mode, user_id)
            )
        return

    text = f"🔄 Выберите предметы для {'отправки' if mode=='give' else 'получения'}:\n\n"
    for name, count in available:
        text += f"• {name} (×{count})\n"

    text += "\nВведите название предмета и количество через пробел (например: 'Меч 2').\n"
    text += "После выбора всех предметов нажмите кнопку '✅ Готово'."

    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_skip = telebot.types.KeyboardButton("⏭ Пропустить" if available else "✅ Готово")
    btn_cancel = telebot.types.KeyboardButton("❌ Отменить обмен")
    keyboard.add(btn_skip, btn_cancel)

    bot.send_message(
        message.chat.id,
        text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    bot.register_next_step_handler(message, trade_add_item, mode)

def trade_skip_keyboard(mode, user_id):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_skip = telebot.types.KeyboardButton("✅ Готово")
    btn_cancel = telebot.types.KeyboardButton("❌ Отменить обмен")
    keyboard.add(btn_skip, btn_cancel)
    return keyboard

def trade_add_item(message, mode):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        text = message.text.strip()
        if text == "❌ Отменить обмен":
            trade_clear_state(user_id)
            bot.send_message(message.chat.id, "❌ Обмен отменён.", reply_markup=main_keyboard())
            return

        if text == "✅ Готово" or text == "⏭ Пропустить":
            if mode == 'give':
                bot.send_message(
                    message.chat.id,
                    "💰 Теперь введите сумму монет, которую вы готовы отдать (можно 0):",
                    parse_mode='Markdown',
                    reply_markup=telebot.types.ReplyKeyboardRemove()
                )
                user_data = get_user_data(user_id)
                user_data['trade_state'] = 'enter_give_money'
                update_user_data(user_id, user_data)
                bot.register_next_step_handler(message, trade_set_money_offer, 'give')
            else:
                bot.send_message(
                    message.chat.id,
                    "💰 Теперь введите сумму монет, которую вы хотите получить (можно 0):",
                    parse_mode='Markdown',
                    reply_markup=telebot.types.ReplyKeyboardRemove()
                )
                user_data = get_user_data(user_id)
                user_data['trade_state'] = 'enter_receive_money'
                update_user_data(user_id, user_data)
                bot.register_next_step_handler(message, trade_set_money_offer, 'receive')
            return

        parts = text.split()
        if len(parts) < 1 or len(parts) > 2:
            bot.send_message(
                message.chat.id,
                "❌ Неверный формат. Введите название предмета и количество через пробел.\n"
                "Пример: Меч 2",
                parse_mode='Markdown'
            )
            show_trade_item_selection(message, user_id, mode)
            return

        name = ' '.join(parts[:-1]) if len(parts) == 2 else parts[0]
        count = int(parts[-1]) if len(parts) == 2 else 1
        if count <= 0:
            raise ValueError

        user_data = get_user_data(user_id)
        inventory = user_data.get('inventory', [])
        counter = Counter(inventory)
        offer = user_data['trade_offer']

        if mode == 'give':
            selected = offer.get('give_items', [])
            if name not in counter:
                bot.send_message(
                    message.chat.id,
                    f"❌ У вас нет предмета '{name}'.",
                    parse_mode='Markdown'
                )
                show_trade_item_selection(message, user_id, mode)
                return
            already = sum(s['count'] for s in selected if s['name'] == name)
            if already + count > counter[name]:
                bot.send_message(
                    message.chat.id,
                    f"❌ У вас только {counter[name]} шт. предмета '{name}'. Вы уже выбрали {already}.",
                    parse_mode='Markdown'
                )
                show_trade_item_selection(message, user_id, mode)
                return
            if already == 0:
                selected.append({'name': name, 'count': count})
            else:
                for s in selected:
                    if s['name'] == name:
                        s['count'] += count
                        break
            offer['give_items'] = selected
            user_data['trade_offer'] = offer
            update_user_data(user_id, user_data)
            bot.send_message(
                message.chat.id,
                f"✅ Добавлено: {name} × {count} для отправки.",
                parse_mode='Markdown'
            )
            show_trade_item_selection(message, user_id, mode)
        else:
            selected = offer.get('receive_items', [])
            partner_id = user_data.get('trade_partner')
            partner_data = get_user_data(partner_id) if partner_id else None
            if not partner_data:
                bot.send_message(message.chat.id, "❌ Ошибка: партнёр не найден.")
                trade_clear_state(user_id)
                return
            partner_inv = partner_data.get('inventory', [])
            partner_counter = Counter(partner_inv)
            if name not in partner_counter:
                bot.send_message(
                    message.chat.id,
                    f"❌ У вашего партнёра нет предмета '{name}'.",
                    parse_mode='Markdown'
                )
                show_trade_item_selection(message, user_id, mode)
                return
            already = sum(s['count'] for s in selected if s['name'] == name)
            if already + count > partner_counter[name]:
                bot.send_message(
                    message.chat.id,
                    f"❌ У партнёра только {partner_counter[name]} шт. предмета '{name}'. Вы уже запросили {already}.",
                    parse_mode='Markdown'
                )
                show_trade_item_selection(message, user_id, mode)
                return
            if already == 0:
                selected.append({'name': name, 'count': count})
            else:
                for s in selected:
                    if s['name'] == name:
                        s['count'] += count
                        break
            offer['receive_items'] = selected
            user_data['trade_offer'] = offer
            update_user_data(user_id, user_data)
            bot.send_message(
                message.chat.id,
                f"✅ Запрошено: {name} × {count} для получения.",
                parse_mode='Markdown'
            )
            show_trade_item_selection(message, user_id, mode)
    except ValueError:
        bot.send_message(
            message.chat.id,
            "❌ Количество должно быть положительным числом.",
            parse_mode='Markdown'
        )
        show_trade_item_selection(message, user_id, mode)
    except Exception as e:
        print(f"Ошибка в trade_add_item: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.", reply_markup=main_keyboard())

def trade_set_money_offer(message, mode):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        text = message.text.strip()
        if text == "❌ Отменить обмен":
            trade_clear_state(user_id)
            bot.send_message(message.chat.id, "❌ Обмен отменён.", reply_markup=main_keyboard())
            return

        try:
            amount = int(text)
            if amount < 0:
                raise ValueError
        except:
            bot.send_message(
                message.chat.id,
                "❌ Введите неотрицательное целое число.",
                parse_mode='Markdown'
            )
            if mode == 'give':
                bot.register_next_step_handler(message, trade_set_money_offer, 'give')
            else:
                bot.register_next_step_handler(message, trade_set_money_offer, 'receive')
            return

        user_data = get_user_data(user_id)
        offer = user_data['trade_offer']
        if mode == 'give':
            if amount > user_data.get('balance', 0):
                bot.send_message(
                    message.chat.id,
                    f"❌ У вас недостаточно монет. Доступно: {user_data['balance']:,}",
                    parse_mode='Markdown'
                )
                bot.register_next_step_handler(message, trade_set_money_offer, 'give')
                return
            offer['give_money'] = amount
            user_data['trade_offer'] = offer
            user_data['trade_state'] = 'select_receive_items'
            update_user_data(user_id, user_data)
            bot.send_message(
                message.chat.id,
                f"✅ Вы отдадите {amount:,} монет.",
                parse_mode='Markdown'
            )
            show_trade_item_selection(message, user_id, 'receive')
        else:
            offer['receive_money'] = amount
            user_data['trade_offer'] = offer
            user_data['trade_state'] = 'finish'
            update_user_data(user_id, user_data)
            bot.send_message(
                message.chat.id,
                f"✅ Вы запросите {amount:,} монет.\n\n"
                "Теперь предложение сформировано. Отправить его партнёру?",
                parse_mode='Markdown',
                reply_markup=trade_finish_keyboard(user_id)
            )
            bot.register_next_step_handler(message, trade_finish_offer)
    except Exception as e:
        print(f"Ошибка в trade_set_money_offer: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.", reply_markup=main_keyboard())

def trade_finish_keyboard(user_id):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_send = telebot.types.KeyboardButton("📤 Отправить предложение")
    btn_cancel = telebot.types.KeyboardButton("❌ Отменить обмен")
    keyboard.add(btn_send, btn_cancel)
    return keyboard

def trade_finish_offer(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        text = message.text.strip()
        if text == "❌ Отменить обмен":
            trade_clear_state(user_id)
            bot.send_message(message.chat.id, "❌ Обмен отменён.", reply_markup=main_keyboard())
            return

        if text != "📤 Отправить предложение":
            bot.send_message(
                message.chat.id,
                "Нажмите '📤 Отправить предложение' или '❌ Отменить обмен'.",
                reply_markup=trade_finish_keyboard(user_id)
            )
            bot.register_next_step_handler(message, trade_finish_offer)
            return

        user_data = get_user_data(user_id)
        partner_id = user_data.get('trade_partner')
        offer = user_data.get('trade_offer', {})
        if not partner_id or not offer:
            bot.send_message(message.chat.id, "❌ Ошибка: данные обмена не найдены.")
            trade_clear_state(user_id)
            return

        user_data['trade_created_at'] = time.time()
        update_user_data(user_id, user_data)

        text_offer = f"🔄 ПРЕДЛОЖЕНИЕ ОБМЕНА от ID {user_id}\n\n"
        text_offer += "📦 Вы отдаёте:\n"
        if offer.get('give_items'):
            for item in offer['give_items']:
                text_offer += f"• {item['name']} × {item['count']}\n"
        else:
            text_offer += "• (ничего)\n"
        text_offer += f"💰 Монет: {offer.get('give_money', 0):,}\n\n"
        text_offer += "📦 Вы получаете:\n"
        if offer.get('receive_items'):
            for item in offer['receive_items']:
                text_offer += f"• {item['name']} × {item['count']}\n"
        else:
            text_offer += "• (ничего)\n"
        text_offer += f"💰 Монет: {offer.get('receive_money', 0):,}\n\n"
        text_offer += "Предложение действительно 5 минут."

        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        btn_accept = telebot.types.InlineKeyboardButton("✅ Принять", callback_data=f"trade_accept_{user_id}")
        btn_decline = telebot.types.InlineKeyboardButton("❌ Отклонить", callback_data=f"trade_decline_{user_id}")
        keyboard.add(btn_accept, btn_decline)

        try:
            bot.send_message(
                partner_id,
                text_offer,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            bot.send_message(
                message.chat.id,
                "✅ Предложение отправлено партнёру. Ожидайте ответа.",
                reply_markup=main_keyboard()
            )
        except Exception as e:
            bot.send_message(
                message.chat.id,
                f"❌ Не удалось отправить предложение партнёру. Возможно, он заблокировал бота.\nОшибка: {e}",
                reply_markup=main_keyboard()
            )
        trade_clear_state(user_id)
    except Exception as e:
        print(f"Ошибка в trade_finish_offer: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.", reply_markup=main_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith('trade_accept_') or call.data.startswith('trade_decline_'))
def trade_response(call):
    try:
        user_id = call.from_user.id
        if is_banned(user_id):
            bot.answer_callback_query(call.id, "🚫 Вы забанены!", show_alert=True)
            return

        parts = call.data.split('_')
        action = parts[1]
        sender_id = int(parts[2])

        if action == 'decline':
            bot.answer_callback_query(call.id, "❌ Вы отклонили предложение.")
            bot.edit_message_text(
                "❌ Предложение отклонено.",
                call.message.chat.id,
                call.message.message_id
            )
            try:
                bot.send_message(sender_id, f"❌ Пользователь {user_id} отклонил ваше предложение обмена.")
            except:
                pass
            return

        sender_data = get_user_data(sender_id)
        created_at = sender_data.get('trade_created_at', 0)
        if time.time() - created_at > 300:
            bot.answer_callback_query(call.id, "⏳ Предложение истекло.", show_alert=True)
            bot.edit_message_text(
                "⏳ Предложение истекло (5 минут).",
                call.message.chat.id,
                call.message.message_id
            )
            returm

        offer = sender_data.get('trade_offer', {})
        if not offer:
            bot.answer_callback_query(call.id, "❌ Предложение не найдено.", show_alert=True)
            return

        sender_data = get_user_data(sender_id)
        receiver_data = get_user_data(user_id)

        if sender_data.get('balance', 0) < offer.get('give_money', 0):
            bot.answer_callback_query(call.id, "❌ У отправителя недостаточно монет.", show_alert=True)
            return
        sender_inv = sender_data.get('inventory', [])
        sender_counter = Counter(sender_inv)
        for item in offer.get('give_items', []):
            if sender_counter.get(item['name'], 0) < item['count']:
                bot.answer_callback_query(call.id, f"❌ У отправителя не хватает предмета {item['name']}.", show_alert=True)
                return

        if receiver_data.get('balance', 0) < offer.get('receive_money', 0):
            bot.answer_callback_query(call.id, "❌ У вас недостаточно монет для этого обмена.", show_alert=True)
            return
        receiver_inv = receiver_data.get('inventory', [])
        receiver_counter = Counter(receiver_inv)
        for item in offer.get('receive_items', []):
            if receiver_counter.get(item['name'], 0) < item['count']:
                bot.answer_callback_query(call.id, f"❌ У вас не хватает предмета {item['name']}.", show_alert=True)
                return

        sender_data['balance'] -= offer.get('give_money', 0)
        receiver_data['balance'] += offer.get('give_money', 0)
        receiver_data['balance'] -= offer.get('receive_money', 0)
        sender_data['balance'] += offer.get('receive_money', 0)

        for item in offer.get('give_items', []):
            for _ in range(item['count']):
                sender_data['inventory'].remove(item['name'])
                receiver_data['inventory'].append(item['name'])

        for item in offer.get('receive_items', []):
            for _ in range(item['count']):
                receiver_data['inventory'].remove(item['name'])
                sender_data['inventory'].append(item['name'])

        update_user_data(sender_id, sender_data)
        update_user_data(user_id, receiver_data)

        sender_data['trade_offer'] = None
        sender_data['trade_created_at'] = 0
        update_user_data(sender_id, sender_data)

        bot.answer_callback_query(call.id, "✅ Обмен выполнен успешно!", show_alert=True)
        bot.edit_message_text(
            "✅ Обмен выполнен!",
            call.message.chat.id,
            call.message.message_id
        )

        try:
            bot.send_message(
                sender_id,
                f"✅ Пользователь {user_id} принял ваш обмен. Все предметы и монеты переданы."
            )
        except:
            pass
        try:
            bot.send_message(
                user_id,
                "✅ Вы приняли обмен. Предметы и монеты переданы."
            )
        except:
            pass

    except Exception as e:
        print(f"Ошибка в trade_response: {e}")
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)

# ========== СИСТЕМА ПОДДЕРЖКИ (ЖАЛОБЫ) ==========
@bot.message_handler(func=lambda message: message.text == '📞 Поддержка')
def support_start(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        bot.send_message(
            message.chat.id,
            "📞 Поддержка\n\nНапишите ваше сообщение (жалобу, вопрос, предложение).\n"
            "Администраторы получат его и свяжутся с вами.",
            parse_mode='Markdown',
            reply_markup=telebot.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, process_support_message)
    except Exception as e:
        print(f"Ошибка в support_start: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.", reply_markup=main_keyboard())

def process_support_message(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        text = message.text.strip()
        if not text:
            bot.send_message(message.chat.id, "❌ Сообщение не может быть пустым. Попробуйте снова.", reply_markup=main_keyboard())
            return

        user_data = get_user_data(user_id)
        user_name = user_data.get('first_name') or "Игрок"

        tickets = load_tickets()
        ticket_id = len(tickets) + 1
        tickets.append({
            'id': ticket_id,
            'user_id': user_id,
            'user_name': user_name,
            'text': text,
            'timestamp': time.time()
        })
        save_tickets(tickets)

        send_support_notification_to_admins(user_id, user_name, text)

        bot.send_message(
            message.chat.id,
            f"✅ Ваше обращение отправлено администраторам.\n"
            "Ожидайте ответа в личные сообщения.",
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )

    except Exception as e:
        print(f"Ошибка в process_support_message: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.", reply_markup=main_keyboard())

@bot.message_handler(commands=['support'])
def support_command(message):
    support_start(message)

@bot.message_handler(func=lambda message: message.text == '📋 Жалобы')
def admin_tickets(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return

    tickets = load_tickets()
    if not tickets:
        bot.send_message(message.chat.id, "📭 Нет активных жалоб.", reply_markup=admin_keyboard())
        return

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    for ticket in tickets:
        ticket_id = ticket['id']
        user_id_str = ticket['user_id']
        user_name = ticket.get('user_name', 'Игрок')
        text_preview = ticket['text'][:30] + "..." if len(ticket['text']) > 30 else ticket['text']
        btn = telebot.types.InlineKeyboardButton(
            f"#{ticket_id} от {user_name} ({user_id_str}) - {text_preview}",
            callback_data=f"admin_ticket_close_{ticket_id}_{user_id}"
        )
        keyboard.add(btn)

    btn_back = telebot.types.InlineKeyboardButton("🔙 Назад в админку", callback_data="admin_tickets_back")
    keyboard.add(btn_back)

    bot.send_message(
        message.chat.id,
        f"📋 АКТИВНЫЕ ЖАЛОБЫ (всего: {len(tickets)})",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_ticket_close_'))
def admin_ticket_close(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "❌ Доступ запрещён.", show_alert=True)
        return

    parts = call.data.split('_')
    ticket_id = int(parts[3])
    ticket_user_id = int(parts[4])

    tickets = load_tickets()
    ticket = next((t for t in tickets if t['id'] == ticket_id), None)
    if not ticket:
        bot.answer_callback_query(call.id, "❌ Жалоба уже закрыта.", show_alert=True)
        return

    tickets.remove(ticket)
    save_tickets(tickets)

    bot.answer_callback_query(call.id, "✅ Жалоба закрыта.", show_alert=False)
    bot.edit_message_text(
        f"✅ Жалоба #{ticket_id} от пользователя {ticket_user_id} закрыта.",
        call.message.chat.id,
        call.message.message_id
    )

    admin_tickets(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'admin_tickets_back')
def admin_tickets_back(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "❌ Доступ запрещён.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "🔙 Возврат в админ-панель.", reply_markup=admin_keyboard())

# ========== ВЫХОД ИЗ АДМИНКИ ==========
@bot.message_handler(func=lambda message: message.text == '🔙 Выйти из админки')
def admin_exit(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    bot.send_message(message.chat.id, "🔙 Выход из админ-панели.", reply_markup=main_keyboard())

@bot.message_handler(func=lambda message: message.text == '🔙 Назад в админку')
def back_to_admin(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    admin_panel(message)

@bot.message_handler(func=lambda message: message.text == '🔙 Назад')
def back(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return
        show_main_menu(user_id, message.chat.id)
    except Exception as e:
        print(f"Ошибка в back: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка", reply_markup=main_keyboard())

@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
        return

    process_work_orders(user_id)
    help_text = """
📖 Помощь по боту

🎮 Команды:
/start - Начать игру
/menu - Открыть главное меню
/я   - Открыть главное меню (по слову "я")
/help - Эта справка
/stats - Моя статистика
/top - Топ игроков
/support - Отправить обращение в поддержку
/pocket или /карман - Показать карман
/put <сумма> или /положить <сумма> - Положить деньги в карман
/take <сумма> или /снять <сумма> - Снять деньги из кармана

🔘 Кнопки:
💰 Клик! - Получить 1,000,000 монет
📊 Статистика - Проверить свой прогресс
🏆 Топ игроков - Рейтинг лучших
👥 Рефералы - Реферальная система
🎰 Рулетка - Игра в казино
🃏 Блэкджек - Классическая карточная игра
🚚 Работа - Заработок заказов
💸 Перевести - Перевести монеты другому игроку
🔄 Обмен - Обмен предметами и монетами с другим игроком
📞 Поддержка - Отправить жалобу или вопрос администраторам
🏪 Магазин - Купить товары, добавленные админом
🎒 Инвентарь - Посмотреть купленные товары и надеть их
🎁 Ежедневный бонус - Забрать 100,000,000 монет каждые 24 часа
🎫 Промокод - Активировать специальный код
👖 Карман - Управление карманом (положить/снять деньги)
🐸 Лягушка - Игра, где лягушка прыгает по кувшинкам!
🔙 Назад - Вернуться в главное меню

👖 Карман:
• Позволяет хранить часть денег отдельно от основного баланса
• Можно положить деньги в карман (с основного баланса)
• Можно снять деньги из кармана (на основной баланс)
• Суммы поддерживают суффиксы: к (тысяча), кк (миллион), ккк (миллиард)
• Примеры: 1000, 500к, 2кк, 1ккк

🐸 Лягушка:
• Лягушка прыгает по кувшинкам
• На каждой кувшинке может быть бонус или ловушка
• В любой момент может упасть в воду (10% шанс)
• Чем дальше пропрыгаешь - тем больше выигрыш!

🏪 Магазин и инвентарь:
• Админ добавляет товары через "Управление магазином" в админ-панели
• Товар имеет название, цену, описание, количество (или бесконечно) и фото
• Покупая товар, вы получаете его в инвентарь
• В магазине или инвентаре можно надеть предмет – тогда при входе в главное меню будет показываться его фото вместо стандартного
• Если предмет снят или не имеет фото – показывается стандартное фото меню

🔄 Обмен:
• Вы можете обменять предметы и монеты с другим игроком
• Предметы, которые надеты, нельзя обменять (снимите их)
• Предложение действительно 5 минут

📞 Поддержка:
• Напишите сообщение, и оно будет отправлено всем администраторам
• Администраторы свяжутся с вами в личных сообщениях

🎫 Промокод:
• Введите код через кнопку "🎫 Промокод" или командой /promo <код>
• Промокод можно активировать только один раз
• Количество активаций ограничено

💡 Советы:
• Кликай чаще для большего баланса
• Приглашай друзей для бонусов
• Играй в рулетку и блэкджек, но осторожно!

📱 Версия: 18.0 (добавлен карман и игра Лягушка)
"""
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown', reply_markup=main_keyboard())

@bot.message_handler(commands=['stats'])
def stats_command(message):
    stats(message)

@bot.message_handler(commands=['top'])
def top_command(message):
    top_players(message)

# ========== НОВЫЙ ОБРАБОТЧИК КОМАНД РУЛЕТКИ В ЧАТЕ ==========
@bot.message_handler(func=lambda message: message.text.lower().startswith('рул '))
def roulette_command(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        process_work_orders(user_id)

        parts = message.text.strip().split()
        if len(parts) < 3:
            bot.send_message(message.chat.id, "❌ Формат команды: Рул <тип> <сумма>\nПример: Рул мал 1кк", parse_mode='Markdown')
            return

        bet_type_str = parts[1].lower()
        amount_str = ' '.join(parts[2:])

        type_map = {
            'мал': 'low',
            'бол': 'high',
            'чет': 'even',
            'нечет': 'odd',
            'кра': 'red',
            'чер': 'black',
            'ряд1': 'dozen1',
            'ряд2': 'dozen2',
            'ряд3': 'dozen3'
        }
        if bet_type_str not in type_map:
            bot.send_message(
                message.chat.id,
                f"❌ Неизвестный тип ставки. Доступные: мал, бол, чет, нечет, кра, чер, ряд1, ряд2, ряд3.",
                parse_mode='Markdown'
            )
            return

        action = type_map[bet_type_str]
        amount = parse_amount(amount_str)
        if amount is None or amount <= 0:
            bot.send_message(message.chat.id, "❌ Неверный формат суммы. Используйте число или суффиксы к, кк, ккк.\nПример: 1000, 500к, 2кк, 1ккк", parse_mode='Markdown')
            return

        if amount < 1000:
            bot.send_message(message.chat.id, "❌ Минимальная ставка 1,000 монет!", parse_mode='Markdown')
            return

        user_data = get_user_data(user_id)
        balance = user_data.get('balance', 0)
        if amount > balance:
            bot.send_message(
                message.chat.id,
                f"❌ Недостаточно монет!\n💰 Ваш баланс: {balance:,} монет",
                parse_mode='Markdown'
            )
            return

        always_win = user_data.get('roulette_always_win', False)
        roulette_number = random.randint(0, 36)
        if roulette_number == 0:
            result_color = 'green'
        elif roulette_number % 2 == 0:
            result_color = 'red'
        else:
            result_color = 'black'

        win = False
        multiplier = 0

        if always_win:
            win = True
            multiplier = 2
        else:
            if action == 'red' and result_color == 'red':
                win = True
                multiplier = 2
            elif action == 'black' and result_color == 'black':
                win = True
                multiplier = 2
            elif action == 'low' and 1 <= roulette_number <= 18:
                win = True
                multiplier = 2
            elif action == 'high' and 19 <= roulette_number <= 36:
                win = True
                multiplier = 2
            elif action == 'even' and roulette_number != 0 and roulette_number % 2 == 0:
                win = True
                multiplier = 2
            elif action == 'odd' and roulette_number != 0 and roulette_number % 2 != 0:
                win = True
                multiplier = 2
            elif action == 'dozen1' and 1 <= roulette_number <= 12:
                win = True
                multiplier = 3
            elif action == 'dozen2' and 13 <= roulette_number <= 24:
                win = True
                multiplier = 3
            elif action == 'dozen3' and 25 <= roulette_number <= 36:
                win = True
                multiplier = 3

        action_names = {
            'мал': '🔽 Мал (1-18)',
            'бол': '🔼 Бол (19-36)',
            'чет': 'Чет',
            'нечет': 'Нечет',
            'кра': '🔴 Красное',
            'чер': '⚫ Черное',
            'ряд1': '🔢 Ряд 1 (1-12)',
            'ряд2': '🔢 Ряд 2 (13-24)',
            'ряд3': '🔢 Ряд 3 (25-36)'
        }

        if win:
            winnings = amount * multiplier
            user_data['balance'] = balance + winnings
            update_user_data(user_id, user_data)
            result_text = (
                f"🎉 ВЫ ВЫИГРАЛИ!\n\n"
                f"💰 Выигрыш: {winnings:,} монет\n"
                f"📊 Новый баланс: {user_data['balance']:,} монет\n\n"
                f"🎯 Результаты:\n"
                f"• Число: {roulette_number}\n"
                f"• Цвет: {'🔴 Красное' if result_color=='red' else '⚫ Черное' if result_color=='black' else '🟢 Зеленое'}\n"
                f"• Ваша ставка: {action_names.get(action, 'Неизвестно')}\n"
                f"• Сумма ставки: {amount:,} монет"
            )
            if always_win:
                result_text += "\n\n✨ *Режим «Всегда выигрывать» активен!*"

            if os.path.exists(WIN_IMAGE_PATH) and os.path.getsize(WIN_IMAGE_PATH) > 0:
                with open(WIN_IMAGE_PATH, 'rb') as photo:
                    bot.send_photo(
                        message.chat.id,
                        photo,
                        caption=result_text,
                        parse_mode='Markdown'
                    )
            else:
                bot.send_message(message.chat.id, result_text, parse_mode='Markdown')

        else:
            user_data['balance'] = balance - amount
            update_user_data(user_id, user_data)
            caption = (
                f"😢 ВЫ ПРОИГРАЛИ\n\n"
                f"💰 Проиграно: {amount:,} монет\n"
                f"📊 Новый баланс: {user_data['balance']:,} монет\n\n"
                f"🎯 Результаты:\n"
                f"• Число: {roulette_number}\n"
                f"• Цвет: {'🔴 Красное' if result_color=='red' else '⚫ Черное' if result_color=='black' else '🟢 Зеленое'}\n"
                f"• Ваша ставка: {action_names.get(action, 'Неизвестно')}\n"
                f"• Сумма ставки: {amount:,} монет"
            )
            try:
                if os.path.exists(LOSE_IMAGE_PATH) and os.path.getsize(LOSE_IMAGE_PATH) > 0:
                    with open(LOSE_IMAGE_PATH, 'rb') as photo:
                        bot.send_photo(
                            message.chat.id,
                            photo,
                            caption=caption,
                            parse_mode='Markdown'
                        )
                else:
                    bot.send_message(
                        message.chat.id,
                        caption + "\n\n(Изображение не найдено. Админ может загрузить фото через /setloseimage)",
                        parse_mode='Markdown'
                    )
            except Exception as e:
                print(f"Ошибка отправки фото: {e}")
                bot.send_message(
                    message.chat.id,
                    caption + "\n\n(Ошибка загрузки изображения)",
                    parse_mode='Markdown'
                )

    except Exception as e:
        print(f"Ошибка в roulette_command: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при выполнении команды. Попробуйте позже.")
        bot.send_message(message.chat.id, "❌ Ошибка при выполнении команды. Попробуйте позже.")

# ========== ОБРАБОТЧИК ПРОМОКОДОВ ==========
@bot.message_handler(func=lambda message: message.text == '🎫 Промокод')
def promo_button(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
        return
    bot.send_message(
        message.chat.id,
        "🎫 ВВЕДИТЕ ПРОМОКОД\n\n"
        "Введите код в сообщении (регистр не важен):",
        parse_mode='Markdown',
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(message, process_promo_code)

@bot.message_handler(commands=['promo'])
def promo_command(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.send_message(
            message.chat.id,
            "❌ Используйте: /promo <код>\nПример: /promo zo34435",
            parse_mode='Markdown'
        )
        return
    promo_code = args[1].strip().lower()
    process_promo_code_activation(message, promo_code)

def process_promo_code(message):
    user_id = message.from_user.id
    code = message.text.strip().lower()
    process_promo_code_activation(message, code)

def process_promo_code_activation(message, code):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    promos = load_promocodes()

    if code not in promos:
        bot.send_message(
            message.chat.id,
            "❌ Неверный промокод. Попробуйте снова или обратитесь к администратору.",
            reply_markup=main_keyboard()
        )
        return

    promo = promos[code]
    if promo['used'] >= promo['max_uses']:
        bot.send_message(
            message.chat.id,
            "❌ Данный промокод уже исчерпан (все активации использованы).",
            reply_markup=main_keyboard()
        )
        return

    if str(user_id) in promo['users']:
        bot.send_message(
            message.chat.id,
            "❌ Вы уже активировали этот промокод.",
            reply_markup=main_keyboard()
        )
        return

    reward = promo['reward']
    user_data['balance'] = user_data.get('balance', 0) + reward
    if 'activated_promos' not in user_data:
        user_data['activated_promos'] = []
    user_data['activated_promos'].append(code)
    update_user_data(user_id, user_data)

    promo['used'] += 1
    promo['users'].append(str(user_id))
    save_promocodes(promos)

    bot.send_message(
        message.chat.id,
        f"✅ ПРОМОКОД АКТИВИРОВАН!\n\n"
        f"💰 Вы получили {reward:,} монет!\n"
        f"📊 Ваш новый баланс: {user_data['balance']:,} монет\n"
        f"🎫 Осталось активаций: {promo['max_uses'] - promo['used']}",
        parse_mode='Markdown',
        reply_markup=main_keyboard()
    )
# ========== УПРАВЛЕНИЕ ПРОМОКОДАМИ В АДМИН-ПАНЕЛИ ==========
@bot.message_handler(func=lambda message: message.text == '🎫 Управление промокодами')
def admin_promo_manage(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_add = telebot.types.KeyboardButton('➕ Создать промокод')
    btn_list = telebot.types.KeyboardButton('📋 Список промокодов')
    btn_delete = telebot.types.KeyboardButton('❌ Удалить промокод')
    btn_back = telebot.types.KeyboardButton('🔙 Назад в админку')
    keyboard.add(btn_add, btn_list)
    keyboard.add(btn_delete)
    keyboard.add(btn_back)
    
    bot.send_message(
        message.chat.id,
        "🎫 УПРАВЛЕНИЕ ПРОМОКОДАМИ\n\n"
        "Выберите действие:",
        reply_markup=keyboard
    )

# ========== СОЗДАНИЕ ПРОМОКОДА ==========
@bot.message_handler(func=lambda message: message.text == '➕ Создать промокод')
def admin_promo_create_start(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    
    bot.send_message(
        message.chat.id,
        "🎫 СОЗДАНИЕ ПРОМОКОДА\n\n"
        "Введите название промокода (латиница, цифры):\n"
        "Пример: SUMMER2024",
        parse_mode='Markdown',
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(message, admin_promo_create_code)

def admin_promo_create_code(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    code = message.text.strip().lower()
    if not code or len(code) < 3:
        bot.send_message(
            message.chat.id,
            "❌ Промокод должен содержать минимум 3 символа. Попробуйте снова.",
            reply_markup=admin_keyboard()
        )
        return
    
    promos = load_promocodes()
    if code in promos:
        bot.send_message(
            message.chat.id,
            f"❌ Промокод '{code}' уже существует. Введите другой код.",
            reply_markup=admin_keyboard()
        )
        return
    
    user_data = get_user_data(user_id)
    user_data['temp_promo'] = {'code': code}
    update_user_data(user_id, user_data)
    
    bot.send_message(
        message.chat.id,
        f"✅ Промокод *{code}* принят.\n\n"
        "Введите сумму награды за активацию (можно с суффиксами к, кк, ккк):\n"
        "Примеры: 1000000, 500к, 2кк, 1ккк",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(message, admin_promo_create_reward)

def admin_promo_create_reward(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    reward = parse_amount(message.text.strip())
    if reward is None or reward <= 0:
        bot.send_message(
            message.chat.id,
            "❌ Неверная сумма. Используйте число или суффиксы к, кк, ккк.\n"
            "Примеры: 1000, 500к, 2кк, 1ккк",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(message, admin_promo_create_reward)
        return
    
    user_data = get_user_data(user_id)
    temp = user_data.get('temp_promo', {})
    temp['reward'] = reward
    user_data['temp_promo'] = temp
    update_user_data(user_id, user_data)
    
    bot.send_message(
        message.chat.id,
        f"✅ Награда: *{reward:,} монет*\n\n"
        "Введите максимальное количество активаций (число):\n"
        "Пример: 10 (или 0 для бесконечного)",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(message, admin_promo_create_max_uses)

def admin_promo_create_max_uses(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    try:
        max_uses = int(message.text.strip())
        if max_uses < 0:
            raise ValueError
    except:
        bot.send_message(
            message.chat.id,
            "❌ Введите положительное число (0 для бесконечного).",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(message, admin_promo_create_max_uses)
        return
    
    user_data = get_user_data(user_id)
    temp = user_data.get('temp_promo', {})
    temp['max_uses'] = max_uses
    user_data['temp_promo'] = temp
    update_user_data(user_id, user_data)
    
    code = temp.get('code', '')
    reward = temp.get('reward', 0)
    
    text = f"📋 ПРОВЕРЬТЕ ДАННЫЕ ПРОМОКОДА:\n\n"
    text += f"🔑 Код: *{code}*\n"
    text += f"💰 Награда: *{reward:,} монет*\n"
    text += f"📊 Макс. активаций: *{'Бесконечно' if max_uses == 0 else max_uses}*\n\n"
    text += "Подтвердите создание:"
    
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_confirm = telebot.types.InlineKeyboardButton("✅ Создать", callback_data=f"promo_confirm_{user_id}")
    btn_cancel = telebot.types.InlineKeyboardButton("❌ Отмена", callback_data=f"promo_cancel_{user_id}")
    keyboard.add(btn_confirm, btn_cancel)
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('promo_confirm_'))
def promo_confirm(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "❌ Доступ запрещён.", show_alert=True)
        return
    
    user_id_from_data = int(call.data.split('_')[2])
    if user_id != user_id_from_data:
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)
        return
    
    user_data = get_user_data(user_id)
    temp = user_data.get('temp_promo', {})
    
    if not temp or 'code' not in temp:
        bot.answer_callback_query(call.id, "❌ Данные промокода не найдены.", show_alert=True)
        return
    
    promos = load_promocodes()
    code = temp['code']
    
    promos[code] = {
        'reward': temp.get('reward', 0),
        'max_uses': temp.get('max_uses', 10),
        'used': 0,
        'users': []
    }
    save_promocodes(promos)
    
    user_data.pop('temp_promo', None)
    update_user_data(user_id, user_data)
    
    bot.answer_callback_query(call.id, "✅ Промокод создан!", show_alert=False)
    bot.edit_message_text(
        f"✅ ПРОМОКОД СОЗДАН!\n\n"
        f"🔑 Код: *{code}*\n"
        f"💰 Награда: *{promos[code]['reward']:,} монет*\n"
        f"📊 Макс. активаций: *{'Бесконечно' if promos[code]['max_uses'] == 0 else promos[code]['max_uses']}*",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=admin_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('promo_cancel_'))
def promo_cancel(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "❌ Доступ запрещён.", show_alert=True)
        return
    
    user_id_from_data = int(call.data.split('_')[2])
    if user_id != user_id_from_data:
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)
        return
    
    user_data = get_user_data(user_id)
    user_data.pop('temp_promo', None)
    update_user_data(user_id, user_data)
    
    bot.answer_callback_query(call.id, "❌ Создание отменено.", show_alert=False)
    bot.edit_message_text(
        "❌ Создание промокода отменено.",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_keyboard()
    )

# ========== СПИСОК ПРОМОКОДОВ ==========
@bot.message_handler(func=lambda message: message.text == '📋 Список промокодов')
def admin_promo_list(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    
    promos = load_promocodes()
    if not promos:
        bot.send_message(
            message.chat.id,
            "📭 Нет созданных промокодов.\nСоздайте новый через '➕ Создать промокод'.",
            reply_markup=admin_keyboard()
        )
        return
    
    text = "📋 СПИСОК ПРОМОКОДОВ:\n\n"
    for code, data in promos.items():
        reward = data.get('reward', 0)
        max_uses = data.get('max_uses', 0)
        used = data.get('used', 0)
        max_text = "∞" if max_uses == 0 else max_uses
        remaining = "∞" if max_uses == 0 else max_uses - used
        
        text += f"🔑 Код: *{code}*\n"
        text += f"💰 Награда: {reward:,} монет\n"
        text += f"📊 Активаций: {used} / {max_text}\n"
        text += f"🟢 Осталось: {remaining}\n"
        text += f"👥 Активировали: {len(data.get('users', []))} чел.\n"
        text += "─" * 20 + "\n"
    
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    btn_back = telebot.types.InlineKeyboardButton("🔙 Назад в админку", callback_data="promo_list_back")
    keyboard.add(btn_back)
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == 'promo_list_back')
def promo_list_back(call):
    user_id = call.from_user.id
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "❌ Доступ запрещён.", show_alert=True)
        return
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "🔙 Возврат в админ-панель.", reply_markup=admin_keyboard())

# ========== УДАЛЕНИЕ ПРОМОКОДА ==========
@bot.message_handler(func=lambda message: message.text == '❌ Удалить промокод')
def admin_promo_delete_start(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    
    promos = load_promocodes()
    if not promos:
        bot.send_message(
            message.chat.id,
            "📭 Нет промокодов для удаления.",
            reply_markup=admin_keyboard()
        )
        return
    
    text = "📋 ВЫБЕРИТЕ ПРОМОКОД ДЛЯ УДАЛЕНИЯ:\n\n"
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    for code in promos.keys():
        btn = telebot.types.InlineKeyboardButton(
            f"❌ {code}",
            callback_data=f"promo_delete_{code}_{user_id}"
        )
        keyboard.add(btn)
    
    btn_back = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data=f"promo_delete_back_{user_id}")
    keyboard.add(btn_back)
    
    bot.send_message(
        message.chat.id,
        text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('promo_delete_'))
def promo_delete_confirm(call):
    user_id = call.from_user.id
    parts = call.data.split('_')
    
    if parts[1] == 'back':
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Доступ запрещён.", show_alert=True)
            return
        user_id_from_data = int(parts[2])
        if user_id != user_id_from_data:
            bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        admin_promo_manage(call.message)
        return
    
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "❌ Доступ запрещён.", show_alert=True)
        return
    
    code = parts[1]
    user_id_from_data = int(parts[2])
    if user_id != user_id_from_data:
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)
        return
    
    promos = load_promocodes()
    if code not in promos:
        bot.answer_callback_query(call.id, "❌ Промокод не найден.", show_alert=True)
        return
    
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn_confirm = telebot.types.InlineKeyboardButton(
        "✅ Да, удалить",
        callback_data=f"promo_delete_yes_{code}_{user_id}"
    )
    btn_cancel = telebot.types.InlineKeyboardButton(
        "❌ Отмена",
        callback_data=f"promo_delete_no_{code}_{user_id}"
    )
    keyboard.add(btn_confirm, btn_cancel)
    
    bot.edit_message_text(
        f"⚠️ ВЫ УВЕРЕНЫ?\n\n"
        f"Вы хотите удалить промокод *{code}*?\n"
        f"Было активаций: {promos[code].get('used', 0)}",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('promo_delete_yes_'))
def promo_delete_yes(call):
    user_id = call.from_user.id
    parts = call.data.split('_')
    code = parts[3]
    user_id_from_data = int(parts[4])
    
    if user_id != user_id_from_data:
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)
        return
    
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "❌ Доступ запрещён.", show_alert=True)
        return
    
    promos = load_promocodes()
    if code not in promos:
        bot.answer_callback_query(call.id, "❌ Промокод не найден.", show_alert=True)
        return
    
    del promos[code]
    save_promocodes(promos)
    
    bot.answer_callback_query(call.id, f"✅ Промокод {code} удалён!", show_alert=False)
    bot.edit_message_text(
        f"✅ Промокод *{code}* успешно удалён!",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=admin_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('promo_delete_no_'))
def promo_delete_no(call):
    user_id = call.from_user.id
    parts = call.data.split('_')
    code = parts[3]
    user_id_from_data = int(parts[4])
    
    if user_id != user_id_from_data:
        bot.answer_callback_query(call.id, "❌ Ошибка", show_alert=True)
        return
    
    if not is_admin(user_id):
        bot.answer_callback_query(call.id, "❌ Доступ запрещён.", show_alert=True)
        return
    
    bot.answer_callback_query(call.id, "❌ Удаление отменено.", show_alert=False)
    
    promos = load_promocodes()
    text = "📋 ВЫБЕРИТЕ ПРОМОКОД ДЛЯ УДАЛЕНИЯ:\n\n"
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    
    for promo_code in promos.keys():
        btn = telebot.types.InlineKeyboardButton(
            f"❌ {promo_code}",
            callback_data=f"promo_delete_{promo_code}_{user_id}"
        )
        keyboard.add(btn)
    
    btn_back = telebot.types.InlineKeyboardButton("🔙 Назад", callback_data=f"promo_delete_back_{user_id}")
    keyboard.add(btn_back)
    
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

# ========== КОМАНДЫ ДЛЯ АДМИНОВ ==========
@bot.message_handler(commands=['promolist'])
def admin_promo_list_command(message):
    """Команда /promolist - показать все промокоды (только для админов)."""
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    admin_promo_list(message)

@bot.message_handler(commands=['createpromo'])
def admin_create_promo_command(message):
    """Команда /createpromo <код> <награда> <макс_использований>"""
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Доступ запрещён.")
        return
    
    args = message.text.split()
    if len(args) < 4:
        bot.send_message(
            message.chat.id,
            "❌ Используйте: /createpromo <код> <награда> <макс_использований>\n"
            "Пример: /createpromo TEST 1000000 10\n"
            "Для бесконечного использования: /createpromo TEST 1000000 0",
            parse_mode='Markdown'
        )
        return
    
    code = args[1].strip().lower()
    reward = parse_amount(args[2])
    if reward is None or reward <= 0:
        bot.send_message(message.chat.id, "❌ Неверная сумма награды.")
        return
    
    try:
        max_uses = int(args[3])
        if max_uses < 0:
            raise ValueError
    except:
        bot.send_message(message.chat.id, "❌ Максимальное использование должно быть числом >= 0.")
        return
    
    promos = load_promocodes()
    if code in promos:
        bot.send_message(message.chat.id, f"❌ Промокод '{code}' уже существует.")
        return
    
    promos[code] = {
        'reward': reward,
        'max_uses': max_uses,
        'used': 0,
        'users': []
    }
    save_promocodes(promos)
    
    bot.send_message(
        message.chat.id,
        f"✅ ПРОМОКОД СОЗДАН!\n\n"
        f"🔑 Код: *{code}*\n"
        f"💰 Награда: *{reward:,} монет*\n"
        f"📊 Макс. активаций: *{'Бесконечно' if max_uses == 0 else max_uses}*",
        parse_mode='Markdown'
    )
# ========== FALLBACK ==========
# ========== FALLBACK ==========
@bot.message_handler(func=lambda message: message.text == '📝 Сменить имя')
def change_name_start(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        user_data = get_user_data(user_id)
        current_name = user_data.get('first_name') or "Игрок"

        bot.send_message(
            message.chat.id,
            f"📝 СМЕНА ИМЕНИ\n\n"
            f"Ваше текущее имя: *{escape_markdown(current_name)}*\n\n"
            f"Введите новое имя (минимум 2 символа, максимум 30):\n"
            f"Имя будет отображаться в статистике и приветствиях.",
            parse_mode='Markdown',
            reply_markup=telebot.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(message, process_change_name)
    except Exception as e:
        print(f"Ошибка в change_name_start: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте позже.", reply_markup=main_keyboard())

def process_change_name(message):
    try:
        user_id = message.from_user.id
        if is_banned(user_id):
            bot.send_message(message.chat.id, "🚫 Вы забанены и не можете использовать бота.")
            return

        new_name = message.text.strip()

        # Проверки
        if not new_name:
            bot.send_message(
                message.chat.id,
                "❌ Имя не может быть пустым. Попробуйте снова.",
                reply_markup=main_keyboard()
            )
            return

        if len(new_name) < 2:
            bot.send_message(
                message.chat.id,
                "❌ Имя слишком короткое. Минимум 2 символа.",
                reply_markup=main_keyboard()
            )
            return

        if len(new_name) > 30:
            bot.send_message(
                message.chat.id,
                "❌ Имя слишком длинное. Максимум 30 символов.",
                reply_markup=main_keyboard()
            )
            return

        # Запрещённые символы
        forbidden = ['@', '#', '$', '%', '^', '&', '*', '(', ')', '=', '+', 
                     '[', ']', '{', '}', '|', ';', ':', '"', "'", '<', '>', 
                     ',', '.', '/', '?']
        if any(char in new_name for char in forbidden):
            bot.send_message(
                message.chat.id,
                "❌ Имя содержит недопустимые символы. Используйте буквы, цифры и пробелы.",
                reply_markup=main_keyboard()
            )
            return

        # Сохраняем новое имя
        user_data = get_user_data(user_id)
        old_name = user_data.get('first_name') or "Игрок"
        user_data['first_name'] = new_name
        update_user_data(user_id, user_data)

        bot.send_message(
            message.chat.id,
            f"✅ Имя успешно изменено!\n\n"
            f"Было: *{escape_markdown(old_name)}*\n"
            f"Стало: *{escape_markdown(new_name)}*\n\n"
            f"Теперь вас будут называть *{escape_markdown(new_name)}* в приветствиях и статистике.",
            parse_mode='Markdown',
            reply_markup=main_keyboard()
        )
    except Exception as e:
        print(f"Ошибка в process_change_name: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при смене имени. Попробуйте позже.", reply_markup=main_keyboard())

if __name__ == "__main__":
    print("🤖 Бот запущен и готов к работе!")
    print("👆 Нажми /start в Telegram")
    print("=" * 50)
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except KeyboardInterrupt:
            print("\n👋 Бот остановлен")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print("🔄 Перезапуск через 5 секунд...")
            time.sleep(5)