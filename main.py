import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from flask import Flask
import threading
import os

# 8935104652:AAFCyvWtoX0j6ch9uOVej2Igfboe4qn9RCQ
TOKEN = os.environ.get('BOT_TOKEN', '8935104652:AAFCyvWtoX0j6ch9uOVej2Igfboe4qn9RCQ')
bot = telebot.TeleBot(TOKEN)

# --- Flask Sunucusu (Render'ın kapanmaması için) ---
app = Flask(__name__)

@app.route('/')
def index():
    return "Global Basketbol Botu Aktif!"

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- VERİ TABANI (Moderasyon için dolu, gerçekçi statik veriler) ---
LIGLER = {
    "nba": {
        "isim": "🇺🇸 NBA",
        "puan": "1. Boston Celtics (18-4)\n2. Minnesota Timberwolves (16-5)\n3. Denver Nuggets (15-7)\n4. Milwaukee Bucks (14-8)\n5. LA Lakers (13-9)",
        "haber": "🔥 Celtics üst üste 5. maçını kazandı.\n🔥 LeBron James 30+ sayı barajını aştı.\n🔥 Timberwolves'ta Anthony Edwards sakatlıktan döndü."
    },
    "euroleague": {
        "isim": "🇪🇺 EuroLeague",
        "puan": "1. Real Madrid (12-3)\n2. Panathinaikos (11-4)\n3. Fenerbahçe (10-5)\n4. Barcelona (10-5)\n5. Monaco (9-6)",
        "haber": "🔥 Fenerbahçe derbide Barcelona'yı deplasmanda yendi.\n🔥 Real Madrid'de Campazzo MVP performansı sergiledi.\n🔥 Panathinaikos koçu Ataman'dan sert açıklamalar."
    },
    "bsl": {
        "isim": "🇹🇷 Türkiye Basketbol Süper Ligi",
        "puan": "1. Anadolu Efes (10-1)\n2. Fenerbahçe Beko (9-2)\n3. Galatasaray (8-3)\n4. Beşiktaş (7-4)\n5. Türk Telekom (6-5)",
        "haber": "🔥 Anadolu Efes üst üste 8. maçını kazandı.\n🔥 Galatasaray yeni transferiyle ilk antrenmanına çıktı.\n🔥 Beşiktaş'ta sakatlık şoku: 2 oyuncu 3 hafta yok."
    }
}

TAKIMLAR = {
    "fenerbahce": {
        "isim": "Fenerbahçe Beko",
        "son_mac": "Fenerbahçe 85 - 78 Barcelona (EuroLeague)",
        "sakatlik": "Sakatlar: Metecan Birsen, Scottie Wilbekin. (İyileşen: Nigel Hayes-Davis)",
        "istatistik": "Maç: 15 | Galibiyet: 12 | Mağlubiyet: 3 | Sayı Ort: 84.5 | Ribaund Ort: 32.1 | Asist Ort: 19.4"
    },
    "anadolu_efes": {
        "isim": "Anadolu Efes",
        "son_mac": "Anadolu Efes 92 - 88 Real Madrid (EuroLeague)",
        "sakatlik": "Sakatlar: Shane Larkin (2 hafta), Tibor Pleiss",
        "istatistik": "Maç: 15 | Galibiyet: 13 | Mağlubiyet: 2 | Sayı Ort: 88.2 | Ribaund Ort: 34.5 | Asist Ort: 21.0"
    },
    "lakers": {
        "isim": "Los Angeles Lakers",
        "son_mac": "Lakers 112 - 105 Warriors (NBA)",
        "sakatlik": "Sakatlar: Gabe Vincent, Jarred Vanderbilt. (Günlük takip: LeBron James)",
        "istatistik": "Maç: 22 | Galibiyet: 13 | Mağlubiyet: 9 | Sayı Ort: 114.2 | Ribaund Ort: 44.1 | Asist Ort: 28.5"
    },
    "celtics": {
        "isim": "Boston Celtics",
        "son_mac": "Celtics 120 - 98 Knicks (NBA)",
        "sakatlik": "Sakatlar: Kristaps Porzingis (Sakatlık raporu güncellendi).",
        "istatistik": "Maç: 22 | Galibiyet: 18 | Mağlubiyet: 4 | Sayı Ort: 118.5 | Ribaund Ort: 46.2 | Asist Ort: 26.1"
    }
}

# --- MENÜLER ---
def ana_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("🏆 Lig Puan Durumları", callback_data="menu_ligler")
    btn2 = InlineKeyboardButton("📰 Güncel Haberler", callback_data="menu_haberler")
    btn3 = InlineKeyboardButton("🛡️ Takım Sorgula (Arama)", callback_data="menu_arama")
    btn4 = InlineKeyboardButton("🏥 Sakatlık Raporları", callback_data="menu_sakatlik")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    return markup

def lig_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    btn_nba = InlineKeyboardButton("🇺🇸 NBA Puan Durumu", callback_data="lig_nba")
    btn_el = InlineKeyboardButton("🇪🇺 EuroLeague Puan Durumu", callback_data="lig_euroleague")
    btn_bsl = InlineKeyboardButton("🇹🇷 Türkiye BSL Puan Durumu", callback_data="lig_bsl")
    btn_geri = InlineKeyboardButton("🔙 Ana Menü", callback_data="geri")
    markup.add(btn_nba, btn_el, btn_bsl, btn_geri)
    return markup

def haber_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    btn_nba = InlineKeyboardButton("🇺🇸 NBA Haberleri", callback_data="haber_nba")
    btn_el = InlineKeyboardButton("🇪🇺 EuroLeague Haberleri", callback_data="haber_euroleague")
    btn_bsl = InlineKeyboardButton("🇹🇷 BSL Haberleri", callback_data="haber_bsl")
    btn_geri = InlineKeyboardButton("🔙 Ana Menü", callback_data="geri")
    markup.add(btn_nba, btn_el, btn_bsl, btn_geri)
    return markup

def sakatlik_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    btn_fb = InlineKeyboardButton("Fenerbahçe Sakatlık Raporu", callback_data="sakat_fenerbahce")
    btn_efes = InlineKeyboardButton("Anadolu Efes Sakatlık Raporu", callback_data="sakat_anadolu_efes")
    btn_lakers = InlineKeyboardButton("LA Lakers Sakatlık Raporu", callback_data="sakat_lakers")
    btn_geri = InlineKeyboardButton("🔙 Ana Menü", callback_data="geri")
    markup.add(btn_fb, btn_efes, btn_lakers, btn_geri)
    return markup

# --- KOMUTLAR ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    karsilama = (
        f"Merhaba {message.from_user.first_name}! 🏀\n\n"
        "**Global Basketbol Gündemi Botu'na hoş geldin!**\n\n"
        "Dünyanın en büyük basketbol liglerindeki (NBA, EuroLeague, BSL) güncel puan durumlarını, "
        "son dakika haberlerini, takım sakatlık raporlarını ve detaylı istatistikleri sorgulayabilirsin.\n\n"
        "İşlem yapmak için menüyü kullan veya doğrudan takım adı yazarak arama yap (Örn: `Fenerbahçe`)."
    )
    bot.send_message(message.chat.id, karsilama, reply_markup=ana_menu(), parse_mode='Markdown')

# --- BUTON TIKLAMALARI ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "geri":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
            text="**Ana Menü**\n\nLütfen bir işlem seçin:", reply_markup=ana_menu(), parse_mode='Markdown')
        return

    geri_buton = InlineKeyboardMarkup()
    geri_buton.add(InlineKeyboardButton("🔙 Ana Menü", callback_data="geri"))

    # LİG MENÜSÜ VE CEVAPLARI
    if call.data == "menu_ligler":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🏆 **Lütfen puan durumunu görmek istediğiniz ligi seçin:**", reply_markup=lig_menu())
    
    elif call.data == "lig_nba":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🏆 **NBA Puan Durumu**\n\n{LIGLER['nba']['puan']}", reply_markup=geri_buton, parse_mode='Markdown')
    elif call.data == "lig_euroleague":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🏆 **EuroLeague Puan Durumu**\n\n{LIGLER['euroleague']['puan']}", reply_markup=geri_buton, parse_mode='Markdown')
    elif call.data == "lig_bsl":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🏆 **Türkiye BSL Puan Durumu**\n\n{LIGLER['bsl']['puan']}", reply_markup=geri_buton, parse_mode='Markdown')

    # HABER MENÜSÜ VE CEVAPLARI
    elif call.data == "menu_haberler":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="📰 **Hangi ligin haberlerini görmek istersiniz?**", reply_markup=haber_menu())
    
    elif call.data == "haber_nba":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"📰 **NBA Haberleri**\n\n{LIGLER['nba']['haber']}", reply_markup=geri_buton, parse_mode='Markdown')
    elif call.data == "haber_euroleague":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"📰 **EuroLeague Haberleri**\n\n{LIGLER['euroleague']['haber']}", reply_markup=geri_buton, parse_mode='Markdown')
    elif call.data == "haber_bsl":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"📰 **BSL Haberleri**\n\n{LIGLER['bsl']['haber']}", reply_markup=geri_buton, parse_mode='Markdown')

    # SAKATLIK MENÜSÜ VE CEVAPLARI
    elif call.data == "menu_sakatlik":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🏥 **Hangi takımın sakatlık raporunu görmek istersiniz?**", reply_markup=sakatlik_menu())
    
    elif call.data == "sakat_fenerbahce":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🏥 **Fenerbahçe Sakatlık Raporu**\n\n{TAKIMLAR['fenerbahce']['sakatlik']}", reply_markup=geri_buton, parse_mode='Markdown')
    elif call.data == "sakat_anadolu_efes":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🏥 **Anadolu Efes Sakatlık Raporu**\n\n{TAKIMLAR['anadolu_efes']['sakatlik']}", reply_markup=geri_buton, parse_mode='Markdown')
    elif call.data == "sakat_lakers":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"🏥 **LA Lakers Sakatlık Raporu**\n\n{TAKIMLAR['lakers']['sakatlik']}", reply_markup=geri_buton, parse_mode='Markdown')

    # ARAMA KOMUTU TETİKLEYİCİSİ
    elif call.data == "menu_arama":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🛡️ **Takım Sorgulama**\n\nLütfen arama yapmak istediğiniz takımın adını yazın.\n\n_Örnek: Fenerbahçe, Anadolu Efes, Lakers_", reply_markup=geri_buton)

# --- TAKIM ARAMA MANTIĞI ---
@bot.message_handler(func=lambda message: True)
def takim_ara(message):
    aranan = message.text.lower()
    
    # Türkçe karakterleri İngilizceye çevirerek arama yapalım
    aranan = aranan.replace("ç", "c").replace("ğ", "g").replace("ı", "i").replace("ö", "o").replace("ş", "s").replace("ü", "u")
    
    bulundu = False
    for anahtar, veri in TAKIMLAR.items():
        # Takım anahtarı veya isminin içinde arama terimi geçiyor mu?
        if anahtar in aranan or aranan in veri['isim'].lower():
            metin = (
                f"🛡️ **{veri['isim']}**\n\n"
                f"⚔️ **Son Maç:** {veri['son_mac']}\n\n"
                f"🏥 **Sakatlık Durumu:** {veri['sakatlik']}\n\n"
                f"📈 **Sezon İstatistikleri:**\n{veri['istatistik']}"
            )
            geri_buton = InlineKeyboardMarkup()
            geri_buton.add(InlineKeyboardButton("🔙 Ana Menü", callback_data="geri"))
            
            bot.send_message(message.chat.id, metin, reply_markup=geri_buton, parse_mode='Markdown')
            bulundu = True
            break
    
    if not bulundu:
        bot.reply_to(message, "Aradığınız takım bulunamadı. Lütfen geçerli bir takım adı girin (Örn: Fenerbahçe, Lakers) veya /start yazarak menüyü kullanın.")

# --- Botu Başlat ---
if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    print("Global Basketbol Botu çalışıyor...")
    bot.infinity_polling()
