import os
import sys
import time
import threading
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== ТВОЙ ТОКЕН ==========
TOKEN = "8672220677:AAHYvjAfDvqpQuSxbQ3jwT7A34xvg8EImaU"
# =================================

# Хранилище таймеров
active_timers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Бот для управления ПК запущен!\n\n"
        "Команды:\n"
        "/shutdown - выключить компьютер сейчас\n"
        "/timer X - выключить через X минут\n"
        "/cancel - отменить таймер\n"
        "/open URL - открыть сайт (пример: /open google.com)\n"
        "/ping - проверить что бот работает"
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Бот работает!")

async def shutdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Отменяем таймер если есть
    if user_id in active_timers:
        active_timers[user_id].cancel()
        del active_timers[user_id]
    
    await update.message.reply_text("⚠️ ВЫКЛЮЧЕНИЕ КОМПЬЮТЕРА ЧЕРЕЗ 10 СЕКУНД!")
    
    # Команда выключения для разных ОС
    if sys.platform == "win32":
        os.system("shutdown /s /t 10")
    else:
        os.system("shutdown -h +0.1")
    
    await update.message.reply_text("💀 Команда выполнена")

async def timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("❌ Укажи время в минутах. Пример: /timer 5")
        return
    
    try:
        minutes = int(context.args[0])
        if minutes <= 0:
            raise ValueError
    except:
        await update.message.reply_text("❌ Введи положительное число минут")
        return
    
    # Отменяем старый таймер
    if user_id in active_timers:
        active_timers[user_id].cancel()
    
    seconds = minutes * 60
    await update.message.reply_text(f"⏰ Таймер установлен на {minutes} мин. Компьютер выключится через {minutes} минут.")
    
    def shutdown_task():
        time.sleep(seconds)
        if sys.platform == "win32":
            os.system("shutdown /s /t 10")
        else:
            os.system("shutdown -h +0.1")
    
    timer = threading.Timer(seconds, shutdown_task)
    timer.daemon = True
    timer.start()
    active_timers[user_id] = timer
    
    # Уведомление за 10 секунд до выключения
    if seconds > 10:
        def notify():
            time.sleep(seconds - 10)
            # Отправляем уведомление через бота (упрощённо)
            print(f"Уведомление: через 10 секунд выключение для {user_id}")
        
        notify_thread = threading.Thread(target=notify, daemon=True)
        notify_thread.start()

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in active_timers:
        active_timers[user_id].cancel()
        del active_timers[user_id]
        await update.message.reply_text("✅ Таймер выключения отменён")
    else:
        await update.message.reply_text("❌ Нет активных таймеров")

async def open_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажи URL. Пример: /open google.com")
        return
    
    url = " ".join(context.args)
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    await update.message.reply_text(f"🌐 Открываю в браузере: {url}")
    
    # Для разных ОС
    if sys.platform == "win32":
        os.system(f'start {url}')
    elif sys.platform == "darwin":
        os.system(f'open {url}')
    else:
        os.system(f'xdg-open {url}')

def main():
    """Запуск бота"""
    app = Application.builder().token(TOKEN).build()
    
    # Регистрируем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("shutdown", shutdown_command))
    app.add_handler(CommandHandler("timer", timer_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(CommandHandler("open", open_command))
    app.add_handler(CommandHandler("ping", ping))
    
    print("🤖 Бот запущен! Жду команды...")
    app.run_polling()

if __name__ == "__main__":
    main()
