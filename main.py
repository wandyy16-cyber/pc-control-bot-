import os
import sys
import time
import threading
import webbrowser
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ========== ТВОЙ ТОКЕН ==========
TOKEN = "8672220677:AAHYvjAfDvqpQuSxbQ3jwT7A34xvg8EImaU"
# =================================

# Хранилище для таймеров
active_timers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Бот для управления ПК готов!\n\n"
        "Команды:\n"
        "/shutdown - выключить ПК сейчас\n"
        "/timer X - выключить через X минут\n"
        "/cancel - отменить таймер\n"
        "/open URL - открыть сайт (например /open google.com)\n"
        "/help - показать это сообщение"
    )

async def shutdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text("⚠️ ВЫКЛЮЧАЮ КОМПЬЮТЕР...")
    
    # Отменяем таймер если был
    if user_id in active_timers:
        active_timers[user_id].cancel()
        del active_timers[user_id]
    
    # Выключаем
    os.system("shutdown /s /t 10" if sys.platform == "win32" else "shutdown -h now")
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
    await update.message.reply_text(f"⏰ Таймер установлен на {minutes} мин. Пришлю уведомление перед выключением.")
    
    def shutdown_task():
        time.sleep(seconds)
        os.system("shutdown /s /t 10" if sys.platform == "win32" else "shutdown -h now")
    
    timer = threading.Timer(seconds, shutdown_task)
    timer.daemon = True
    timer.start()
    active_timers[user_id] = timer
    
    # Поток для уведомлений за 10 секунд
    def notify_task():
        time.sleep(seconds - 10)
        import asyncio
        asyncio.run_coroutine_threadsafe(
            update.message.reply_text("⚠️ ЧЕРЕЗ 10 СЕКУНД ВЫКЛЮЧЕНИЕ! Сохраните данные!"),
            context.application.update_queue
        )
    
    notify = threading.Thread(target=notify_task, daemon=True)
    notify.start()

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in active_timers:
        active_timers[user_id].cancel()
        del active_timers[user_id]
        await update.message.reply_text("✅ Таймер отменён")
    else:
        await update.message.reply_text("❌ Активных таймеров нет")

async def open_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Укажи URL. Пример: /open google.com")
        return
    
    url = " ".join(context.args)
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        webbrowser.open(url)
        await update.message.reply_text(f"✅ Открываю: {url}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("shutdown", shutdown_command))
    app.add_handler(CommandHandler("timer", timer_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
    app.add_handler(CommandHandler("open", open_command))
    app.add_handler(CommandHandler("help", help_command))
    
    print("🤖 Бот запущен! Напиши /start в Telegram")
    app.run_polling()

if __name__ == "__main__":
    main()
