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

# שלבי השיחה
NAME, ADDRESS, FLOOR, APARTMENT, CODE, NOTES = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("מה השם?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("מה הכתובת?")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    await update.message.reply_text("מה הקומה?")
    return FLOOR

async def get_floor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["floor"] = update.message.text
    await update.message.reply_text("מה מספר הדירה?")
    return APARTMENT

async def get_apartment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["apartment"] = update.message.text
    await update.message.reply_text("קוד בניין (לא חובה, אפשר לדלג):")
    return CODE

async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["code"] = update.message.text
    await update.message.reply_text("הערות נוספות? (גם כן לא חובה)")
    return NOTES

async def get_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["notes"] = update.message.text

    # שמירה לקובץ
    file_exists = os.path.isfile("data.csv")
    with open("data.csv", mode="a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["שם", "כתובת", "קומה", "דירה", "קוד", "הערות"])
        writer.writerow([
            context.user_data["name"],
            context.user_data["address"],
            context.user_data["floor"],
            context.user_data["apartment"],
            context.user_data["code"],
            context.user_data["notes"]
        ])

    summary = (
        f"שם: {context.user_data['name']}\n"
        f"כתובת: {context.user_data['address']}\n"
        f"קומה: {context.user_data['floor']}\n"
        f"דירה: {context.user_data['apartment']}\n"
        f"קוד: {context.user_data['code']}\n"
        f"הערות: {context.user_data['notes']}"
    )
    await update.message.reply_text("הנתונים התקבלו ונשמרו:\n\n" + summary)
    return ConversationHandler.END

# חיפוש לפי שם
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("כתוב את הפקודה כך: /search [שם]")
        return

    name_to_search = " ".join(context.args).strip()
    if not os.path.exists("data.csv"):
        await update.message.reply_text("אין עדיין נתונים.")
        return

    with open("data.csv", newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["שם"] == name_to_search:
                response = (
                    f"שם: {row['שם']}\n"
                    f"כתובת: {row['כתובת']}\n"
                    f"קומה: {row['קומה']}\n"
                    f"דירה: {row['דירה']}\n"
                    f"קוד: {row['קוד']}\n"
                    f"הערות: {row['הערות']}"
                )
                await update.message.reply_text(response)
                return

    await update.message.reply_text("לא נמצא שם כזה.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            FLOOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_floor)],
            APARTMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_apartment)],
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_code)],
            NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_notes)],
        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("search", search))

    app.run_polling()
