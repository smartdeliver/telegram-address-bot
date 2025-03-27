import logging
import csv
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

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
    context.user_data["שם"] = update.message.text
    await update.message.reply_text("מה הכתובת?")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["כתובת"] = update.message.text
    await update.message.reply_text("מה הקומה?")
    return FLOOR

async def get_floor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["קומה"] = update.message.text
    await update.message.reply_text("מה מספר הדירה?")
    return APARTMENT

async def get_apartment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["דירה"] = update.message.text
    await update.message.reply_text("קוד בניין (לא חובה, אפשר לדלג):")
    return CODE

async def get_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["קוד"] = update.message.text
    await update.message.reply_text("הערות נוספות? (גם כן לא חובה)")
    return NOTES

async def get_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["הערות"] = update.message.text

    # שמירת הנתונים לקובץ
    file_exists = os.path.isfile("data.csv")
    with open("data.csv", mode="a", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["שם", "כתובת", "קומה", "דירה", "קוד", "הערות"])
        writer.writerow([
            context.user_data["שם"],
            context.user_data["כתובת"],
            context.user_data["קומה"],
            context.user_data["דירה"],
            context.user_data["קוד"],
            context.user_data["הערות"]
        ])

    summary = (
        f"שם: {context.user_data['שם']}\n"
        f"כתובת: {context.user_data['כתובת']}\n"
        f"קומה: {context.user_data['קומה']}\n"
        f"דירה: {context.user_data['דירה']}\n"
        f"קוד בניין: {context.user_data['קוד']}\n"
        f"הערות: {context.user_data['הערות']}"
    )
    await update.message.reply_text(f"הנתונים התקבלו ונשמרו:\n\n{summary}")
    return ConversationHandler.END

# פונקציית חיפוש
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("כתוב את הפקודה כך: /search [שם]")
        return

    name_to_search = " ".join(context.args)

    if not os.path.isfile("data.csv"):
        await update.message.reply_text("אין נתונים בקובץ.")
        return

    found = False
    with open("data.csv", mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["שם"] == name_to_search:
                summary = (
                    f"שם: {row['שם']}\n"
                    f"כתובת: {row['כתובת']}\n"
                    f"קומה: {row['קומה']}\n"
                    f"דירה: {row['דירה']}\n"
                    f"קוד: {row['קוד']}\n"
                    f"הערות: {row['הערות']}"
                )
                await update.message.reply_text(summary)
                found = True
                break

    if not found:
        await update.message.reply_text("השם לא נמצא.")

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
