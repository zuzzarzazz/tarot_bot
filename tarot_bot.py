import os
import random
import logging
from PIL import Image
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Словарь значений карт
TAROT_MEANINGS = {
            "00": {"name": "Шут", "meaning": "Невинность, новое начало, спонтанность", "reversed": "Безрассудство, риск, незрелость"},
            "01": {"name": "Маг", "meaning": "Сила воли, мастерство, концентрация", "reversed": "Манипуляции, обман, нерешительность"},
            "02": {"name": "Верховная Жрица", "meaning": "Интуиция, тайное знание, мудрость", "reversed": "Скрытые мотивы, игнорирование интуиции"},
            "03": {"name": "Императрица", "meaning": "Плодородие, изобилие, природа", "reversed": "Зависимость, подавление, бесплодие"},
            "04": {"name": "Император", "meaning": "Авторитет, структура, контроль", "reversed": "Тирания, жесткость, злоупотребление властью"},
            "05": {"name": "Иерофант", "meaning": "Традиция, духовность, обучение", "reversed": "Догматизм, лицемерие, ограниченность"},
            "06": {"name": "Влюбленные", "meaning": "Любовь, гармония, отношения", "reversed": "Дисбаланс, конфликты, неверность"},
            "07": {"name": "Колесница", "meaning": "Победа, воля, движение вперед", "reversed": "Потеря контроля, задержки, поражение"},
            "08": {"name": "Сила", "meaning": "Мужество, сострадание, внутренняя сила", "reversed": "Слабость, неуверенность, злоупотребление силой"},
            "09": {"name": "Отшельник", "meaning": "Созерцание, поиск истины, уединение", "reversed": "Одиночество, изоляция, отказ от помощи"},
            "10": {"name": "Колесо Фортуны", "meaning": "Судьба, удача, цикличность", "reversed": "Неудача, сопротивление переменам"},
            "11": {"name": "Справедливость", "meaning": "Баланс, справедливость, правда", "reversed": "Несправедливость, предвзятость, безответственность"},
            "12": {"name": "Повешенный", "meaning": "Жертва, сдача, новый взгляд", "reversed": "Бесполезные жертвы, застой, эгоизм"},
            "13": {"name": "Смерть", "meaning": "Конец, трансформация, новое начало", "reversed": "Сопротивление изменениям, страх, застой"},
            "14": {"name": "Умеренность", "meaning": "Гармония, терпение, баланс", "reversed": "Дисбаланс, крайности, нетерпение"},
            "15": {"name": "Дьявол", "meaning": "Иллюзия, зависимость, материализм", "reversed": "Освобождение, преодоление ограничений"},
            "16": {"name": "Башня", "meaning": "Крах, откровение, внезапные изменения", "reversed": "Избегание правды, сопротивление изменениям"},
            "17": {"name": "Звезда", "meaning": "Надежда, вера, духовное просветление", "reversed": "Отчаяние, пессимизм, потеря веры"},
            "18": {"name": "Луна", "meaning": "Иллюзия, страх, подсознание", "reversed": "Ясность, преодоление страхов"},
            "19": {"name": "Солнце", "meaning": "Радость, успех, жизненная сила", "reversed": "Временные трудности, задержки"},
            "20": {"name": "Суд", "meaning": "Возрождение, призыв, прощение", "reversed": "Сомнения, страх перемен, самообвинение"},
            "21": {"name": "Мир", "meaning": "Завершение, единство, достижение", "reversed": "Незавершенность, задержки, разочарование"}
           }


class TarotBot:
    def __init__(self, token: str, cards_folder: str):
        self.token = token
        self.cards_folder = cards_folder

    async def start(self, update: Update, context: CallbackContext) -> None:
        """Обработчик команды /start"""
        keyboard = [["🔮 Вытянуть карту"]]
        reply_markup = {"keyboard": keyboard, "resize_keyboard": True}
        
        await update.message.reply_text(
            "✨ *Таро-бот: Гадание на одной карте*\n\n"
            "Нажмите кнопку ниже или отправьте /card",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    async def send_card(self, update: Update, context: CallbackContext) -> None:
        """Отправляет одну случайную карту"""
        try:
            card_file = random.choice(os.listdir(self.cards_folder))
            is_reversed = random.choice([True, False])
            card_path = os.path.join(self.cards_folder, card_file)
            
            with Image.open(card_path) as img:
                if is_reversed:
                    img = img.rotate(180)
                
                temp_path = "temp_card.jpg"
                img.save(temp_path, "JPEG")
                
                card_num = card_file.split('_')[0]
                card_info = TAROT_MEANINGS.get(card_num, {
                    "name": "Неизвестная карта",
                    "meaning": "Значение неизвестно",
                    "reversed": "Перевернутое значение неизвестно"
                })
                
                caption = (
                    f"*{card_info['name']}* {'(перевернута)' if is_reversed else ''}\n\n"
                    f"🔮 *Значение:*\n"
                    f"{card_info['reversed' if is_reversed else 'meaning']}\n\n"
                    f"Нажмите /card для новой карты"
                )
                
                with open(temp_path, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=caption,
                        parse_mode="Markdown"
                    )
            
            os.remove(temp_path)
            
        except Exception as e:
            logger.error(f"Ошибка: {str(e)}", exc_info=True)
            await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте снова.")

    def run(self):
        """Запускает бота"""
        application = Application.builder().token(self.token).build()
        
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("card", self.send_card))
        application.add_handler(MessageHandler(filters.Regex(r'^🔮 Вытянуть карту$'), self.send_card))
        
        application.run_polling()

if __name__ == '__main__':
    TOKEN = "8006477688:AAEe4Nlrb_i79VGQMgXrH7yJ4pTTa2fAIE0"
    CARDS_FOLDER = "cards"
    
    if not os.path.exists(CARDS_FOLDER):
        logger.error(f"Папка с картами не найдена: {os.path.abspath(CARDS_FOLDER)}")
        exit(1)
    
    bot = TarotBot(TOKEN, CARDS_FOLDER)
    bot.run()
