import os, telebot, logging, sys#, cv2
from pyzbar.pyzbar import decode
from dotenv import load_dotenv
from PIL import Image

# Carga las variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# logger.setLevel(logging.INFO)

# Crea el handler para logs en archivo
file_handler = logging.FileHandler('code-scanner.log')
file_handler.setLevel(logging.DEBUG)

# Crea el handler para logs en terminal
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# Añade formato a ambos handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # "%(asctime)s - %(levelname)s - %(message)s"
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Añade los handlers al logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Inicia el bot
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))

# Stickers
HI = "CAACAgIAAxkBAAEw6mhnidEJLQfBuGjc-i6Pyji7leWkOAACQhAAAjPFKUmQDtQRpypKgjYE"
CODES = "CAACAgIAAxkBAAEwo3xnfh0dgWfPOjBubK4DIm8awlWQlwACvAwAAocoMEntN5GZWCFoBDYE"
NO_CODES = "CAACAgIAAxkBAAEw6mZnidEHCNz0VYfwr-rfLgso2J7HbQACWBEAAr4RKEkctAGRFeQMEDYE"


# Mensaje por defecto
@bot.message_handler()
def start(message):
    logger.debug(f'"{message.from_user.username} ({message.chat.id})" inició el bot')
    text = 'Hola, envía una foto y te responderé con los datos de los códigos de barras o códigos QRs encontrados en la foto.'
    bot.send_sticker(chat_id=message.chat.id, sticker=HI)
    bot.send_message(chat_id=message.chat.id, text=text)

# Sí el mensaje es una imagen, envía los datos de cada código encontrado
@bot.message_handler(content_types=['photo'])
def scan_code(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('image.png', 'wb') as new_file:
        new_file.write(downloaded_file)
    image = Image.open('image.png')
    #image = cv2.imread('image.png')
    decoded_objects = decode(image)
    if not decoded_objects:
        logger.debug('No se encontró ningún código válido en la imagen.')
        bot.send_sticker(chat_id=message.chat.id, sticker=NO_CODES)
        bot.reply_to(message, 'No se encontró ningún código válido en la imagen.')
    else:
        logger.debug('Se encontraron códigos válidos en la imagen.')
        bot.send_sticker(chat_id=message.chat.id, sticker=CODES)
        for obj in decoded_objects:
            text = f"Se encontró un código:\n<b>Tipo</b>: {obj.type}\n<b>Dato</b>: <code>{obj.data.decode('utf-8')}</code>"
            bot.reply_to(message=message, text=text, parse_mode='HTML')


if __name__ == '__main__':
    try:
        logger.info('El bot está encendido')
        bot.infinity_polling()
        logger.info('El bot está apagado')
    except Exception as e:
        logger.error(f'Ha ocurrido un error: {e}')