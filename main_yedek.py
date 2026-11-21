
import tkinter as tk
from tkinter import messagebox
import threading
import mss
from PIL import Image
import pytesseract
import argostranslate.translate

# Tesseract OCR konumu
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


class GameLingo:
    def __init__(self, root):
        self.root = root
        self.root.title("GameLingo - Ekran Çevirisi")
        self.root.geometry("800x650")
        self.root.configure(bg="#171923")

        tk.Label(
            root,
            text="GameLingo",
            font=("Segoe UI", 24, "bold"),
            fg="#7dd3fc",
            bg="#171923"
        ).pack(pady=(15, 5))

        tk.Label(
            root,
            text="Ekrandaki İngilizce yazıları Türkçeye çevir",
            font=("Segoe UI", 11),
            fg="white",
            bg="#171923"
        ).pack(pady=5)

        self.button = tk.Button(
            root,
            text="Ekranı Tara ve Çevir",
            command=self.start_scan,
            font=("Segoe UI", 12, "bold"),
            bg="#0284c7",
            fg="white",
            padx=18,
            pady=10
        )
        self.button.pack(pady=12)

        tk.Label(
            root, text="Algılanan İngilizce metin",
            fg="#93c5fd", bg="#171923"
        ).pack(anchor="w", padx=15)

        self.original = tk.Text(
            root, height=8, wrap="word",
            font=("Segoe UI", 11)
        )
        self.original.pack(fill="both", padx=15, pady=6)

        tk.Label(
            root, text="Türkçe çeviri",
            fg="#86efac", bg="#171923"
        ).pack(anchor="w", padx=15)

        self.translated = tk.Text(
            root, height=8, wrap="word",
            font=("Segoe UI", 11)
        )
        self.translated.pack(
            fill="both", expand=True, padx=15, pady=6
        )

        self.status = tk.Label(
            root, text="Hazır",
            fg="#d1d5db", bg="#171923"
        )
        self.status.pack(pady=8)

    def start_scan(self):
        self.button.config(state="disabled")
        self.status.config(text="Ekran taranıyor...")
        threading.Thread(
            target=self.scan_and_translate,
            daemon=True
        ).start()

    def update_ui(self, original, translated, status):
        def update():
            self.original.delete("1.0", tk.END)
            self.original.insert(tk.END, original)

            self.translated.delete("1.0", tk.END)
            self.translated.insert(tk.END, translated)

            self.status.config(text=status)
            self.button.config(state="normal")

        self.root.after(0, update)

    def scan_and_translate(self):
        try:
            with mss.mss() as screen:
                monitor = screen.monitors[1]
                shot = screen.grab(monitor)
                image = Image.frombytes(
                    "RGB", shot.size, shot.rgb
                )

            text = pytesseract.image_to_string(
                image, lang="eng"
            ).strip()

            if not text:
                self.update_ui(
                    "Okunabilir metin bulunamadı.",
                    "",
                    "Başka bir ekranda tekrar deneyebilirsin."
                )
                return

            translation = argostranslate.translate.translate(
                text, "en", "tr"
            )

            self.update_ui(
                text,
                translation,
                "Çeviri tamamlandı (çevrimdışı)."
            )

        except Exception as error:
            self.root.after(
                0,
                lambda: self.show_error(str(error))
            )

    def show_error(self, error):
        self.button.config(state="normal")
        self.status.config(text="Bir hata oluştu.")
        messagebox.showerror("GameLingo Hatası", error)


if __name__ == "__main__":
    root = tk.Tk()
    app = GameLingo(root)
    root.mainloop()
