import logging
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import credentials # my API
import random
import json #dictionary with questions and answers



###! GLOBAL VARIABLES

insert_question = 0 # 0 if you cannot insert the question, 1 else
insert_answer = 0 #same but with the answer
q = "" #the question needed to be saved
answer = 0 #0 if you cannot answer 1 else

shufflelist = [] #list with the answer shuffled
###! GLOBAL VARIABLES


logging.basicConfig(

    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO

)

# set higher logging level for httpx to avoid all GET and POST requests being logged

logging.getLogger("httpx").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)



# Define a few command handlers. These usually take the two arguments update and

# context.

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Send a message when the command /start is issued."""

    user = update.effective_user

    await update.message.reply_html(

        rf"Hi {user.mention_html()}!",

        reply_markup=ForceReply(selective=True),

    )

async def test_random(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    #A shuffled array containing all the cards is created
    global shufflelist
    with open("records.json","r") as f:
        dictionary = json.load(f)

    shufflelist = ([[x,y[0]] for x,y in dictionary.items()])
    random.shuffle(shufflelist)
    await update.message.reply_text("Test started")
    await update.message.reply_text(shufflelist[-1][0])

async def new_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Funzione per ottenere l'input dall'utente
    global insert_question
    await update.message.reply_text("Insert the question")
    insert_question = 1

    #domande.cards[question[1:]] = 'ciao'
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Send a message when the command /help is issued."""

    await update.message.reply_text("Help!")



async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Echo the user message."""

    global q,insert_answer,insert_question,shufflelist


    ###! INSERTION OF CARDS
    if insert_answer:
        a = update.message.text #answer
        with open("records.json","r") as f:
            dictionary = json.load(f)
        dictionary[q] = [a,3] #there are 3 levels of priority, the higher is the level the most frequenlty it will appear
        with open("records.json","w") as f:
            json.dump(dictionary,f)
        insert_answer = 0
        await update.message.reply_text("The card has been saved")
    if insert_question:
        q = update.message.text #question
        insert_question = 0
        insert_answer = 1
        await update.message.reply_text("Insert the answer")
        
    ###! INSERTION OF CARDS

    ###! THE SHUFFLED ARRAY IS SHOWN AND THE TEST STARTS
    if len(shufflelist):
        await update.message.reply_text(f"The answer is {shufflelist[-1][1]}")
        shufflelist.pop()
        print(len(shufflelist))
        if len(shufflelist) == 0:
            await update.message.reply_text("Game ended")
        await update.message.reply_text(shufflelist[-1][0])
        if update.message.text == "END":
            shufflelist = []
            await update.message.reply_text("Game ended")
    ###! THE SHUFFLED ARRAY IS SHOWN AND THE TEST STARTS

def main() -> None:

    """Start the bot."""

    # Create the Application and pass it your bot's token.

    application = Application.builder().token(credentials.api).build()


    # on different commands - answer in Telegram

    application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("help", help_command))


    application.add_handler(CommandHandler("test_random", test_random))

    application.add_handler(CommandHandler("new_card",new_card))

    # on non command i.e message - echo the message on Telegram

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


    # Run the bot until the user presses Ctrl-C

    application.run_polling(allowed_updates=Update.ALL_TYPES)



if __name__ == "__main__":

    main()

