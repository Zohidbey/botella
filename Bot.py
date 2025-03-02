from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
import os

# Bot Token
TOKEN = "YOUR_BOT_TOKEN"

# Tasdiqlovchi shaxslarning ID ro‘yxati
ADMIN_IDS = [732255152]  # Tasdiqlovchilar ro‘yxati

# Kanal IDsi (Videolar yuklanadigan kanal)
CHANNEL_ID = "https://t.me/+Ed4_OYF5gI8zZDFi"

# Ma'lumotlar saqlash uchun dict
user_data = {}
video_submissions = {}

# Start komandasi
def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    if user_id not in user_data:
        user_data[user_id] = {"videos": 0, "approved": 0, "rejected": 0, "balance": 0}
    update.message.reply_text("Salom! Video yuklash uchun /yangi_video buyrug‘ini bosing.")

# Video yuklash funksiyasi
def upload_video(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    if update.message.video:
        video = update.message.video.file_id
        caption = f"🆕 Yangi video yuklandi!\n\nYuboruvchi: {update.message.chat.username or 'Noma’lum'}"
        
        keyboard = [[InlineKeyboardButton("👍 Tasdiqlash", callback_data=f"approve_{video}"),
                     InlineKeyboardButton("👎 Rad etish", callback_data=f"reject_{video}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Videoni kanalda e’lon qilish
        message = context.bot.send_video(chat_id=CHANNEL_ID, video=video, caption=caption, reply_markup=reply_markup)
        video_submissions[video] = {"user_id": user_id, "status": "pending", "message_id": message.message_id}
        
        update.message.reply_text("Videongiz kanalga joylandi va tasdiqlash jarayoniga yuborildi!")
    else:
        update.message.reply_text("Iltimos, faqat video yuboring.")

# Video tasdiqlash yoki rad etish funksiyasi
def review_video(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    
    if user_id not in ADMIN_IDS:
        query.answer("Sizda bu amalni bajarish huquqi yo‘q!", show_alert=True)
        return
    
    action, video_id = query.data.split("_")
    if video_id not in video_submissions:
        query.answer("Video topilmadi!")
        return
    
    editor_id = video_submissions[video_id]["user_id"]
    message_id = video_submissions[video_id]["message_id"]
    
    if action == "approve":
        user_data[editor_id]["approved"] += 1
        user_data[editor_id]["balance"] += 100000
        context.bot.send_message(chat_id=editor_id, text="🎉 Videongiz tasdiqlandi va balansingizga 100,000 so‘m qo‘shildi!")
        context.bot.edit_message_caption(chat_id=CHANNEL_ID, message_id=message_id, caption="✅ Video tasdiqlandi!")
    elif action == "reject":
        user_data[editor_id]["rejected"] += 1
        context.bot.send_message(chat_id=editor_id, text="❌ Videongiz rad etildi. Iltimos, xatolarni to‘g‘rilab, qayta yuklang.")
        context.bot.edit_message_caption(chat_id=CHANNEL_ID, message_id=message_id, caption="❌ Video rad etildi.")
    
    query.answer("Jarayon bajarildi.")

# Balansni ko‘rish
def check_balance(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    if user_id in user_data:
        balance = user_data[user_id]["balance"]
        update.message.reply_text(f"💰 Sizning balansingiz: {balance} so‘m")
    else:
        update.message.reply_text("Sizning hisobingiz topilmadi.")

# Komandalar qo‘shish
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("yangi_video", upload_video))
    dp.add_handler(CommandHandler("balans", check_balance))
    dp.add_handler(MessageHandler(Filters.video, upload_video))
    dp.add_handler(CallbackQueryHandler(review_video))
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
