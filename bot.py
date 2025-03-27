import logging
import csv
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

BOT_TOKEN = "8043230540:AAE4artNipeMm8ZZ3QTcn0bdtZieHRsHfX0"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# שלבים בתהליך הכנסת הנתונים
NAME, ADDRESS, FLOOR, APARTMENT, CODE, NOTES = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("מה השם?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text
    await update.message.reply_text("מה הכתובת?")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["address"] = update.message.text
    await update.message.reply_text("מה הקומה?")
    return FLOOR

async def get_floor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["floor"] = update.message.text
    await update.message.reply_text("מה מספר הדירה?")
    return APARTMENT

async def get_apartment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["apartment"] = update.message.text
    await update.message.reply_text("קוד בניין (לא חובה, אפשר לדלג):")
    return CODE

async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["code"] = update.message.text
    await update.message.reply_text("הערות נוספות? (גם כן לא חובה)")
    return NOTES

async def get_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["notes"] = update.message.text

    # שמירת הנתונים לקובץ
    file_exists = os.path.isfile("data.csv")
    with open("data.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["שם", "כתובת", "קומה", "דירה", "קוד", "הערות"])
        writer.writerow([
            context.user_data.get("name", ""),
            context.user_data.get("address", ""),
            context.user_data.get("floor", ""),
            context.user_data.get("apartment", ""),
            context.user_data.get("code", ""),
            context.user_data.get("notes", "")
        ])

    summary = (
        "שם: " + context.user_data.get("name", "") + "\n" +
        "כתובת: " + context.user_data.get("address", "") + "\n" +
        "קומה: " + context.user_data.get("floor", "") + "\n" +
        "דירה: " + context.user_data.get("apartment", "") + "\n" +
        "קוד בניין: " + context.user_data.get("code", "") + "\n" +
        "הערות: " + context.user_data.get("notes", "")
    )

    await update.message.reply_text("הנתונים התקבלו ונשמרו:\n\n" + summary)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("ביטלת את התהליך.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            FLOOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_floor)],
            APARTMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_apartment)],
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_code)],
            NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_notes)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
