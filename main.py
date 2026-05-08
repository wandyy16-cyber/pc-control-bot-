import os
import sys
import threading
import time
import webbrowser
from tkinter import *
from tkinter import messagebox, ttk

# ========== ТВОЙ ТОКЕН ВСТАВЛЕН ==========
TELEGRAM_BOT_TOKEN = "8672220677:AAHYvjAfDvqpQuSxbQ3jwT7A34xvg8EImaU"
# =========================================

class PCControlBot:
    def __init__(self, root):
        self.root = root
        self.root.title("PC Control Bot")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.timer_running = False
        self.remaining_seconds = 0
        self.timer_thread = None
        
        self.setup_ui()
    
    def setup_ui(self):
        title = Label(self.root, text="Управление компьютером", font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Мгновенное выключение
        frame_instant = LabelFrame(self.root, text="Мгновенное выключение", padx=10, pady=10)
        frame_instant.pack(fill="x", padx=20, pady=10)
        
        btn_shutdown = Button(frame_instant, text="ВЫКЛЮЧИТЬ ПК СЕЙЧАС", bg="red", fg="white", 
                              font=("Arial", 12, "bold"), command=self.shutdown_now)
        btn_shutdown.pack(fill="x")
        
        # Таймер
        frame_timer = LabelFrame(self.root, text="Выключение по таймеру", padx=10, pady=10)
        frame_timer.pack(fill="x", padx=20, pady=10)
        
        timer_controls = Frame(frame_timer)
        timer_controls.pack(fill="x")
        
        Label(timer_controls, text="Минут:", font=("Arial", 11)).pack(side="left", padx=5)
        
        self.timer_entry = Entry(timer_controls, width=10, font=("Arial", 11))
        self.timer_entry.pack(side="left", padx=5)
        self.timer_entry.insert(0, "5")
        
        self.start_timer_btn = Button(timer_controls, text="Запустить таймер", bg="orange", 
                                       command=self.start_timer, font=("Arial", 10))
        self.start_timer_btn.pack(side="left", padx=10)
        
        self.cancel_timer_btn = Button(timer_controls, text="Отменить", bg="gray", fg="white", 
                                        command=self.cancel_timer, font=("Arial", 10), state="disabled")
        self.cancel_timer_btn.pack(side="left")
        
        self.timer_label = Label(frame_timer, text="⏳ Таймер не активен", fg="blue", font=("Arial", 10))
        self.timer_label.pack(pady=10)
        
        # Открытие страниц
        frame_browser = LabelFrame(self.root, text="Открыть страницу в браузере", padx=10, pady=10)
        frame_browser.pack(fill="x", padx=20, pady=10)
        
        url_controls = Frame(frame_browser)
        url_controls.pack(fill="x")
        
        Label(url_controls, text="URL:", font=("Arial", 11)).pack(side="left", padx=5)
        
        self.url_entry = Entry(url_controls, width=30, font=("Arial", 11))
        self.url_entry.pack(side="left", padx=5)
        self.url_entry.insert(0, "https://www.google.com")
        
        btn_open = Button(url_controls, text="🔥 Открыть", bg="green", fg="white", 
                          command=self.open_url, font=("Arial", 10))
        btn_open.pack(side="left", padx=5)
        
        btn_exit = Button(self.root, text="Закрыть бота", bg="gray", fg="white", 
                          command=self.exit_app, font=("Arial", 10))
        btn_exit.pack(pady=10)
    
    def shutdown_now(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите выключить компьютер СЕЙЧАС?\nВсе несохранённые данные будут потеряны!"):
            self.cancel_timer()
            messagebox.showinfo("Выключение", "Компьютер выключается...")
            self._shutdown_system()
    
    def start_timer(self):
        if self.timer_running:
            messagebox.showwarning("Таймер уже запущен", "Сначала отмените текущий таймер")
            return
        
        try:
            minutes = int(self.timer_entry.get())
            if minutes <= 0:
                messagebox.showerror("Ошибка", "Введите положительное число минут")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите число минут")
            return
        
        if messagebox.askyesno("Подтверждение", f"Выключить компьютер через {minutes} минут?"):
            self.remaining_seconds = minutes * 60
            self.timer_running = True
            self.start_timer_btn.config(state="disabled")
            self.cancel_timer_btn.config(state="normal")
            self.timer_entry.config(state="disabled")
            
            self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
            self.timer_thread.start()
    
    def _timer_loop(self):
        while self.timer_running and self.remaining_seconds > 0:
            mins = self.remaining_seconds // 60
            secs = self.remaining_seconds % 60
            self.timer_label.config(text=f"⏰ Выключение через: {mins:02d}:{secs:02d}")
            time.sleep(1)
            self.remaining_seconds -= 1
        
        if self.timer_running and self.remaining_seconds == 0:
            self.timer_label.config(text="💀 ВЫКЛЮЧЕНИЕ...")
            self._shutdown_system()
    
    def cancel_timer(self):
        if self.timer_running:
            self.timer_running = False
            if self.timer_thread and self.timer_thread.is_alive():
                self.timer_thread.join(timeout=1)
            self.timer_label.config(text="⏳ Таймер отменён")
            self.start_timer_btn.config(state="normal")
            self.cancel_timer_btn.config(state="disabled")
            self.timer_entry.config(state="normal")
            messagebox.showinfo("Таймер отменён", "Выключение по таймеру отменено")
    
    def open_url(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Ошибка", "Введите URL")
            return
        
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        try:
            webbrowser.open(url)
            messagebox.showinfo("Успех", f"Страница открывается:\n{url}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть браузер:\n{str(e)}")
    
    def _shutdown_system(self):
        try:
            if sys.platform == "win32":
                os.system("shutdown /s /t 1")
            elif sys.platform == "darwin":
                os.system("sudo shutdown -h now")
            else:
                os.system("shutdown now")
        except:
            messagebox.showerror("Ошибка", "Не удалось выполнить команду выключения")
        finally:
            self.root.quit()
    
    def exit_app(self):
        if self.timer_running:
            if messagebox.askyesno("Таймер активен", "Закрыть программу и отменить таймер?"):
                self.cancel_timer()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = Tk()
    app = PCControlBot(root)
    root.mainloop()
