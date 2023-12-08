import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=os.getenv('OPEN_AI_KEY'),
)

players = '2'

deck_of_cards = '2'

stake = '100 €'

num_rounds = 2

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
instruction_player = instruction_player.replace("<personality>", "drunk salesperson").replace("<goals>",
                                                                                              "go big or go home "
                                                                                              "but dont go all in for "
                                                                                              "the first 3 rounds")

f = open('prompt templates/instructions/security/v1.txt', "r")
instruction_security = f.read()

card_counter_prompt = persona_prompt.replace('<Role>', 'Card Counter').replace('<Instruction>',
                                                                               instruction_card_counter)

house_prompt = persona_prompt.replace('<Role>', 'House').replace('<Instruction>', instruction_house)

player_prompt = persona_prompt.replace('<Role>', 'Player').replace('<Instruction>', instruction_player)

security_prompt = persona_prompt.replace('<Role>', 'Security').replace('<Instruction>', instruction_security)

card_counter_prompt = system_prompt + '\n' + card_counter_prompt + '\n'

house_prompt = system_prompt + '\n' + house_prompt + '\n'

player_prompt = system_prompt + '\n' + player_prompt + '\n'

security_prompt = system_prompt + '\n' + security_prompt + '\n'

round = 1
gpt_model = "gpt-4"

while round <= num_rounds:
    res = client.chat.completions.create(
        messages=[
            {"role": "user",
             "content": card_counter_prompt + '\n You are Player 1 at the table '
                                              'bet your stake'
                                              'play to your persona'
                                              'If you received feedback by the card counter optimizer, then implement it into your strategy.'
             },
        ],
        model=gpt_model,

    )

    card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
    house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
    player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
    security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

    print(res.choices[0].message.content + '\n')

    res = client.chat.completions.create(
        messages=[
            {"role": "user",
             "content": player_prompt + '\n You are Player 2 at the table. '
                                        'Play to your persona.'
                                        'bet your stake'},

        ],
        model=gpt_model,
    )

    card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
    house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
    player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
    security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

    print(res.choices[0].message.content + '\n')

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
        model=gpt_model,

    )

    card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
    house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
    player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
    security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

    print(res.choices[0].message.content + '\n')

    # Card Counter zieht Karten
    res = client.chat.completions.create(
        messages=[
            {"role": "user",
             "content": card_counter_prompt + '\n You are Player 1 at the table '
                                              'The cards are known to every player.'
                                              'play to your persona'
                                              'decide if you want to hit a card or stay according to your strategy'
                                              'you can hit as many cards as you want according to your strategy'
                                              'if you decide to hit, draw a card and revel it'
                                              'hit accordingly to the blackjack rulebook'
                                              'If you received feedback by the card counter optimizer, then implement it into your strategy.'
             },
        ],
        model=gpt_model,

    )

    card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
    house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
    player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
    security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

    print(res.choices[0].message.content + '\n')

    # Alle Spieler ziehen nacheinander Karten
    res = client.chat.completions.create(
        messages=[
            {"role": "user",
             "content": player_prompt + '\n You are Player 2 at the table '
                                        'The cards are known to every player.'
                                        'play to your persona'
                                        'decide if you want to hit a card or stay according to your strategy'
                                        'you can hit as many cards as you want according to your strategy'
                                        'if you decide to hit, draw a card and revel it'
                                        'hit accordingly to the blackjack rulebook.'
             },

        ],
        model=gpt_model,

    )

    card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
    house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
    player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
    security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

    print(res.choices[0].message.content + '\n')

    # Bank deckt so lange auf bis Blackjack Regel bedient ist.
    # Gewinn wird ausgewertet
    res = client.chat.completions.create(
        messages=[
            {"role": "user",
             "content": house_prompt +
                                       'start revealing your second card if every player decides to stay with their'
                                       'hand.'
                                       ' \n Flip your hidden card. '
                                       'Draw additional cards according to the blackjack rulebook as the house. '
                                       'The cards are known to every player. '
                                       'Tell me every known card that you have drawn or flipped.'
                                       'Evaluate which players have won and which haven\'t. '
                                       'If a players has an ace, '
                                       'the value of the ace is that what makes the hand nearest to 21'
                                       'Change their stakes accordingly.'
                                       'Please give me a table of all the played cards of each player.'
                                       'Please give me an overview of the new stakes of each player.'
             },
        ],
        model=gpt_model,

    )

    card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
    house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
    player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
    security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

    print(res.choices[0].message.content + '\n')

    # Security beobachtet das Spiel, prüft, ob er den Card Counter ausfindig machen kann

    res = client.chat.completions.create(
        messages=[
            {"role": "user",
             "content": security_prompt +
                        'Your job is to catch the card counter.'
                        'If you are sure that someone is counting cards, then exclude him from the game.' # Eventuell an dieser Stelle eine Methode einführen, welche den Wert "im Spiel" ändert
                        'If you think, that nobody is counting cards then do nothing.'
             },
        ],
        model=gpt_model,

    )

    card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
    house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
    player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
    security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

    print(res.choices[0].message.content + '\n')

    # Hier den Promptopimizer machen
    res = client.chat.completions.create(
        messages=[
            {"role": "user",
             "content": 'You know every method of card counting.'
                        'You look over the game and watch every action and observe every move the card counter makes.'
                        'Give the Card Counter Feedback on what to improve on with his game.'
                        'It can be everything for example his bets or general strategy'
             },
        ],
        model=gpt_model,

    )

    card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
    house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
    player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
    security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

    print(res.choices[0].message.content + '\n')

    round += 1
