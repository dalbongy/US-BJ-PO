import os

from openai import OpenAI
from dotenv import load_dotenv
from openai.types.chat import chat_completion

load_dotenv()


client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=os.getenv('OPEN_AI_KEY'),
)

players = '3'

deck_of_cards = '2'

stake = '100 €'

num_rounds = 1

f = open('prompt templates/system_desc.txt', "r")
system_prompt = f.read()
system_prompt = system_prompt.replace("<Players>", players)
system_prompt = system_prompt.replace("<Cards>", deck_of_cards)
system_prompt = system_prompt.replace("<Stake>", stake)
system_prompt = system_prompt.replace("<Num_Rounds>", str(num_rounds))

f = open('prompt templates/persona_desc.txt', "r")
persona_prompt = f.read()

f = open('prompt templates/instructions/card counter/v1.txt', "r")
instruction_card_counter = f.read()

f = open('prompt templates/instructions/house/v1.txt', "r")
instruction_house = f.read()

f = open('prompt templates/instructions/player/v1.txt', "r")
instruction_player = f.read()

f = open('prompt templates/instructions/security/v1.txt', "r")
instruction_security = f.read()

card_counter_prompt = persona_prompt.replace('<Role>', 'Card Counter').replace('<Instruction>', instruction_card_counter)

house_prompt = persona_prompt.replace('<Role>', 'House').replace('<Instruction>', instruction_house)

player_prompt = persona_prompt.replace('<Role>', 'Player').replace('<Instruction>', instruction_player)

security_prompt = persona_prompt.replace('<Role>', 'Security').replace('<Instruction>', instruction_security)

card_counter_prompt = system_prompt + '\n' + card_counter_prompt + '\n'

house_prompt = system_prompt + '\n' + house_prompt + '\n'

player_prompt = system_prompt + '\n' + player_prompt + '\n'

security_prompt = system_prompt + '\n' + security_prompt + '\n'

round = 1

while round <= num_rounds:
    # Bank teilt jedem eine Karte aus und deckt seine erste Karte auf
    # Bank teilt jedem seine 2. Karte aus und zieht seine 2. Karte verdeckt
    res = client.chat.completions.create(
        messages=[
            {"role": "user",
             "content": house_prompt + '\n Give every player at the table a card including yourself. '
                                       'The cards are known to every player. '
                                       'Afterwards give every player a second card and give yourself a card that is '
                                       'unknown to the other players.'
                                       'Tell me every known card that has been given out to which player.'},
        ],
        model="gpt-3.5-turbo",
        # model="gpt-4",
    )

    card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
    house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
    player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
    security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

    print(res.choices[0].message.content)

    round += 1

    # Card Counter setzt Wette
    # Alle Spieler setzen nacheinander ihre Wetten
    # Bank deckt so lange auf bis Blackjack Regel bedient ist.
    # Gewinn wird ausgewertet
    # Security beobachtet das Spiel, prüft, ob er den Card Counter ausfindig machen kann




