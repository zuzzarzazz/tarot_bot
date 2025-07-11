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
            "00": {"name": "Шут", "meaning": "новое начинание, доверие миру, интуитивный путь, неожиданный помощник, внутренняя чистота, начало пути, ученичество, импульс, рождение веры.", "reversed": "страх перемен, уход от ответственности, забвение дара, отказ от себя настоящего, сомнения, чрезмерное планирование, потеря связи с интуицией"},
            "01": {"name": "Маг", "meaning": "Настоящее знание, проверенное временем, Опыт и умение применять силу точно и спокойно. Мастерство без показного величия. Магия, вплетённая в повседневность, Контроль через мудрость, а не через силу. Талант находить нестандартные решения. Тандем, в котором даже тьма учится быть светом. Удачный союз логики и интуиции", "reversed": "Манипуляции под маской знания. Желание контролировать — из страха. Использование силы ради выгоды, а не истины. Отказ от перемен, когда они назрели. Привычка зарываться в рутину вместо действия. Ложное чувство «всё под контролем». Страх перед собственным даром."},
            "02": {"name": "Верховная Жрица", "meaning": "Молчаливое знание. Интуиция, пришедшая из глубины веков. Возможность прикоснуться к запретному, не нарушив баланса. Союз с потусторонним — без страха, но с уважением. Женская сила, не требующая доказательств. Появление старого друга, скрытого союзника или Тени, что помогает", "reversed": "Псевдомудрость и духовный пафос. Манипуляция знаниями ради власти. Изоляция от мира и людей. Сокрытие правды, которая должна быть озвучена. Опасная тяга к запретному без должного уважения."},
            "03": {"name": "Императрица", "meaning": "власть, обретённая через уверенность в себе и природные ресурсы. Женская энергия, способная нести как созидание, так и разрушение. Появление могущественного союзника. Умение принимать и направлять. Плодородие идей. Искушение как инструмент, а не слабость.", "reversed": "злоупотребление властью. Соблазн использовать ресурсы в эгоистичных целях. Иллюзия контроля. Пренебрежение пределами дозволенного"},
            "04": {"name": "Император", "meaning": "Власть, харизма, лидерство. Контроль, манипуляции. Успех, но за счёт других. Маг силы, но не добра", "reversed": "Обман, деспотизм. Зависимость от внешней силы. Крах амбиций. Бунт против авторитетов. Капкан гордыни."},
            "05": {"name": "Иерофант", "meaning": "Глубокая духовность без догмы. Подлинная вера, живущая в действиях, а не в словах. Служение — добровольное и искреннее. Помощь тем, кто не может сам себя защитить. Призвание, за которым не стоит тщеславие. Ангельская защита — явная или невидимая. Возможность исцеления через сострадание и любовь. Встреча с Человеком Света — тихим, но судьбоносным.", "reversed": "Подмена веры — ритуалом, формы — содержанием. Жесткость там, где требуется мягкость. Принятие на себя «божественной роли» без внутренней зрелости. Нежелание слышать или быть услышанным. Подавление внутреннего света под давлением чужих норм"},
            "06": {"name": "Влюбленные", "meaning": "Любовь, союз, выбор, принятие, откровенность, взаимность, духовная и/или физическая близость, доверие, искренность, осознанность, соединение противоположностей, верность себе и другому", "reversed": "Сомнение, страх близости, избегание ответственности, ложный выбор, самообман, зависимость, разделение, испытание чувств, моральная дилемма, разрушительные связи, уход от любви"},
            "07": {"name": "Колесница", "meaning": "Победа над собой. Воля как единственный транспорт. Доверие пути. Признание Небес. Смелость быть первым, кто уходит.", "reversed": "Бегство вместо пути. Попытка управлять стихиями, не зная их. Страх замаскированный под решимость. Преследуемое прошлое."},
            "08": {"name": "Сила", "meaning": "Внутренняя сила, выдержка, стойкость. Умение преодолевать трудности без насилия. Лидерство, основанное на уважении. Способность погасить конфликт", "reversed": "Подавление, а не убеждение. Слабость, маскируемая агрессией. Потеря контроля. Страх перед необходимостью действовать"},
            "09": {"name": "Отшельник", "meaning": "Путь знания. Отстранение от суеты ради истины. Глубокое понимание процессов. Необходимость одиночества для принятия верных решений. Внутренний свет и дисциплина", "reversed": "Изоляция, ставшая самоцелью. Страх выйти за пределы известного. Эмоциональное отстранение. Бегство в теорию, отказ от действия. Слепота к тому, что рядом"},
            "10": {"name": "Колесо Фортуны", "meaning": "Удача, неожиданные благоприятные события, возможность изменить жизнь к лучшему, поворот судьбы, дар свыше. Появление в раскладе говорит о моменте, когда пространство само открывает дверь — но пройти через неё предстоит вам", "reversed": "НЗамкнутый круг, утрата шанса, самосаботаж, цикличные ошибки, отказ от ответственности, слепота к возможностям"},
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
        
        #application.run_polling()

if __name__ == '__main__':
    TOKEN = os.environ.get('BOT_TOKEN')
    CARDS_FOLDER = "cards"
    
    if not os.path.exists(CARDS_FOLDER):
        logger.error(f"Папка с картами не найдена: {os.path.abspath(CARDS_FOLDER)}")
        exit(1)
    
    bot = TarotBot(TOKEN, CARDS_FOLDER)
    bot.run()
