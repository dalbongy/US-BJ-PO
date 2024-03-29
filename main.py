import os
import time
import random
from openai import OpenAI
from dotenv import load_dotenv
import tiktoken
from prettytable import PrettyTable


def num_tokens_from_messages(messages):
    """Return the number of tokens used by a list of messages."""
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens_per_message = 3
    tokens_per_name = 1

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def update_deck(deck, promptHistory, game):
    promptHistory = promptHistory[promptHistory.index("Game: " + str(game)) : -1]
    for card in deck:
        if card in promptHistory:
            deck.pop(deck.index(card))

    return deck


def analyse_game(message, current_game, current_round, current_deck):
    # Den Running Count vom Card Counter extrahieren
    message = message[message.index(f"Game: {current_game}"): -1]
    message = message[message.index(f"Round: {current_round}"): -1]

    card_counter_count = message[message.index("Running count:"): message.index("Running count:") + 17].replace(
        "Running Count:", "").replace(".", "").strip()

    # Den tatsächlichen Count berechnen
    full_deck = ["Ace of Hearts", "2 of Hearts", "3 of Hearts", "4 of Hearts", "5 of Hearts", "6 of Hearts",
                 "7 of Hearts", "8 of Hearts", "9 of Hearts", "10 of Hearts", "Jack of Hearts", "Queen of Hearts", "King of Hearts",
                 "Ace of Diamonds", "2 of Diamonds", "3 of Diamonds", "4 of Diamonds", "5 of Diamonds", "6 of Diamonds",
                 "7 of Diamonds", "8 of Diamonds", "9 of Diamonds", "10 of Diamonds", "Jack of Diamonds",
                 "Queen of Diamonds", "King of Diamonds",
                 "Ace of Clubs", "2 of Clubs", "3 of Clubs", "4 of Clubs", "5 of Clubs", "6 of Clubs", "7 of Clubs",
                 "8 of Clubs", "9 of Clubs", "10 of Clubs", "Jack of Clubs", "Queen of Clubs", "King of Clubs",
                 "Ace of Spades", "2 of Spades", "3 of Spades", "4 of Spades", "5 of Spades", "6 of Spades",
                 "7 of Spades", "8 of Spades", "9 of Spades", "10 of Spades", "Jack of Spades", "Queen of Spades", "King of Spades"
                 ]
    played_cards = [x for x in full_deck if x not in current_deck]
    real_count = 0

    for card in played_cards:
        if "2" in card or "3" in card or "4" in card or "5" in card or "6" in card:
            real_count += 1
        elif "7" in card or "8" in card or "9" in card:
            real_count += 0
        else:
            real_count -= 1

    counter_bet = message[message.index("€") - 3 : message.index("€") + 1].strip()

    table = PrettyTable()

    table.field_names = ["His Card Count", "Actual Card Count", "His Bet"]

    table.add_row([card_counter_count, real_count, counter_bet])

    print(f"\n{table}\n")

    return card_counter_count, real_count


load_dotenv()

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=os.getenv('OPEN_AI_KEY'),
)

total_tokens_burned = 0

players = '2'

deck_of_cards = '1'

num_rounds = 2

num_games = 3

stake = '100 €'

gpt_model = "gpt-4"
game = 1

f = open('prompt templates/system_desc.txt', "r")
system_prompt = f.read()
system_prompt = system_prompt.replace("<Players>", players)
system_prompt = system_prompt.replace("<Decks>", deck_of_cards)
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

while game <= num_games:
    print("Game: " + str(game))

    card_counter_prompt = card_counter_prompt + '\n\n' + f"Game: {str(game)}"
    house_prompt = house_prompt + '\n\n' + f"Game: {str(game)}"
    player_prompt = player_prompt + '\n\n' + f"Game: {str(game)}"
    security_prompt = security_prompt + '\n\n' + f"Game: {str(game)}"

    round = 1

    positive_deck = ["Ace of Hearts", "8 of Hearts", "9 of Hearts", "10 of Hearts", "Jack of Hearts", "Queen of Hearts",
                     "King of Hearts",
                     "Ace of Diamonds", "8 of Diamonds", "9 of Diamonds", "10 of Diamonds", "Jack of Diamonds",
                     "Queen of Diamonds", "King of Diamonds",
                     "Ace of Clubs", "8 of Clubs", "9 of Clubs", "10 of Clubs", "Jack of Clubs", "Queen of Clubs",
                     "King of Clubs",
                     "Ace of Spades", "8 of Spades", "9 of Spades", "10 of Spades", "Jack of Spades", "Queen of Spades",
                     "King of Spades"
                     ]

    negative_deck = ["2 of Hearts", "3 of Hearts", "4 of Hearts", "5 of Hearts", "6 of Hearts", "7 of Hearts",
                   "8 of Hearts", "2 of Diamonds", "3 of Diamonds", "4 of Diamonds", "5 of Diamonds",
                   "6 of Diamonds", "7 of Diamonds", "8 of Diamonds",
                   "2 of Clubs", "3 of Clubs", "4 of Clubs", "5 of Clubs", "6 of Clubs", "7 of Clubs",
                   "8 of Clubs", "2 of Spades", "3 of Spades", "4 of Spades", "5 of Spades", "6 of Spades",
                   "7 of Spades", "8 of Spades"
                   ]

    amount_of_cards_already_played = 12 * 2
    i = 1

    random_deck = ["Ace of Hearts", "2 of Hearts", "3 of Hearts", "4 of Hearts", "5 of Hearts", "6 of Hearts", "7 of Hearts",
            "8 of Hearts", "9 of Hearts", "10 of Hearts", "Jack of Hearts", "Queen of Hearts", "King of Hearts",
            "Ace of Diamonds", "2 of Diamonds", "3 of Diamonds", "4 of Diamonds", "5 of Diamonds", "6 of Diamonds",
            "7 of Diamonds", "8 of Diamonds", "9 of Diamonds", "10 of Diamonds", "Jack of Diamonds",
            "Queen of Diamonds", "King of Diamonds",
            "Ace of Clubs", "2 of Clubs", "3 of Clubs", "4 of Clubs", "5 of Clubs", "6 of Clubs", "7 of Clubs",
            "8 of Clubs", "9 of Clubs", "10 of Clubs", "Jack of Clubs", "Queen of Clubs", "King of Clubs",
            "Ace of Spades", "2 of Spades", "3 of Spades", "4 of Spades", "5 of Spades", "6 of Spades", "7 of Spades",
            "8 of Spades", "9 of Spades", "10 of Spades", "Jack of Spades", "Queen of Spades", "King of Spades"
            ]

    while i <= amount_of_cards_already_played:
        random_deck.pop(random.randint(0, len(random_deck) - 1))
        i += 1

    random.shuffle(positive_deck)
    random.shuffle(negative_deck)
    random.shuffle(random_deck)

    all_decks = [positive_deck, negative_deck, random_deck]

    while round <= num_rounds:
        card_counter_prompt = card_counter_prompt + ('\n New Round! \n'
                                                     'The following Cards are left in the deck:'
                                                     ', '.join(all_decks[game - 1]))
        house_prompt = house_prompt + ('\n New Round! \n'
                                       'The following Cards are left in the deck:'
                                       ', '.join(all_decks[game - 1]))
        player_prompt = player_prompt + ('\n New Round! \n'
                                         'The following Cards are left in the deck:'
                                         ', '.join(all_decks[game - 1]))
        security_prompt = security_prompt + ('\n New Round! \n'
                                             'The following Cards are left in the deck:'
                                             ', '.join(all_decks[game - 1]))

        print("Round: " + str(round))

        card_counter_prompt = card_counter_prompt + '\n\n' + f"Round: {str(round)}"
        house_prompt = house_prompt + '\n\n' + f"Round: {str(round)}"
        player_prompt = player_prompt + '\n\n' + f"Round: {str(round)}"
        security_prompt = security_prompt + '\n\n' + f"Round: {str(round)}"

        print("\n Player 1 [Card Counter] places his bet. \n")

        card_counter_prompt = card_counter_prompt + '\n' + "Player 1 [Card Counter] places his bet."
        house_prompt = house_prompt + '\n' + "Player 1 [Card Counter] places his bet."
        player_prompt = player_prompt + '\n' + "Player 1 [Card Counter] places his bet."
        security_prompt = security_prompt + '\n' + "Player 1 [Card Counter] places his bet."

        message = [
            {"role": "user",
             "content": card_counter_prompt + '\n You are Player 1 at the table.'
                                              'Bet your stake and play to your persona.'
                                              'Always state your stake as a number with currency.'
                                              'Give us your thought process but try to keep it short.'
                                              'Tell me the running count. In a format as the following example: "/n running count: +1 /n"'
                                              'You know which cards are still in the game.'
                                              'If you received feedback by the card counter optimizer, then implement it into your strategy.'
                                              'Only generate the next answer.'
                                              'Rounds to go before the game ends: ' + str(num_rounds)
             },
        ]

        if total_tokens_burned + num_tokens_from_messages(message) >= 10000:
            print("Too many tokens. Going to sleep!\n")
            time.sleep(60)
            total_tokens_burned = num_tokens_from_messages(message)
        else:
            total_tokens_burned += num_tokens_from_messages(message)

        res = client.chat.completions.create(
            messages=message,
            model=gpt_model,

        )

        card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
        house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
        player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
        security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

        print(res.choices[0].message.content + '\n')

        print("\n Player 2 places his bet. \n")

        """
        card_counter_prompt = card_counter_prompt + '\n' + "Player 2 places his bet."
        house_prompt = house_prompt + '\n' + "Player 2 places his bet."
        player_prompt = player_prompt + '\n' + "Player 2 places his bet."
        security_prompt = security_prompt + '\n' + "Player 2 places his bet."
        """

        message = [
            {"role": "user",
             "content": player_prompt + '\n You are Player 2 at the table.'
                                        'Bet your stake and play to your persona.'
                                        'Only generate the next answer.'
                                        'Rounds to go before the game ends: ' + str(num_rounds)
             },

        ]

        if total_tokens_burned + num_tokens_from_messages(message) >= 10000:
            print("Too many tokens. Going to sleep!")
            time.sleep(60)
            total_tokens_burned = num_tokens_from_messages(message)
        else:
            total_tokens_burned += num_tokens_from_messages(message)

        res = client.chat.completions.create(
            messages=message,
            model=gpt_model,
        )

        card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
        house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
        player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
        security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

        print(res.choices[0].message.content + '\n')

        # Bank teilt jedem eine Karte aus und deckt seine erste Karte auf
        # Bank teilt jedem seine 2. Karte aus und zieht seine 2. Karte verdeckt
        print("\n House gives every player two cards and itself one. \n")

        message = [
            {"role": "user",
             "content": house_prompt + '\n Give every player at the table a card including yourself. '
                                       'The cards are known to every player. '
                                       'Afterwards give every player a second card and give yourself a card that is '
                                       'unknown to the other players.'
                                       'Tell me every known card that has been given out to which player.'
                                       'Only generate the next answer.'
                                       'Rounds to go before the game ends: ' + str(num_rounds)
             },
        ]

        if total_tokens_burned + num_tokens_from_messages(message) >= 10000:
            print("Too many tokens. Going to sleep!")
            time.sleep(60)
            total_tokens_burned = num_tokens_from_messages(message)
        else:
            total_tokens_burned += num_tokens_from_messages(message)

        res = client.chat.completions.create(
            messages=message,
            model=gpt_model,

        )

        card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
        house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
        player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
        security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

        print(res.choices[0].message.content + '\n')

        # Card Counter zieht Karten
        """
        # Der alte Prompt
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
                                                  # Ein Beispiel einbinden
                                                  # Vielleicht draw additional cards statt hit
                                                  # Generell expliziter machen
                 },
            ],
            model=gpt_model,

        )
        """
        print("\n Player 1 [Card Counter] draws additional cards. \n")

        message = [
            {"role": "user",
             "content": card_counter_prompt + '\n You are Player 1 at the table.'
                                              'Play to your persona.'
                                              'Give us your thought process but try to keep it short.'
                                              'Decide if you want to draw a card according to your strategy.'
                                              'Before drawing a cards reevaluate the running count.'
                                              'You can draw as many cards as you want.'
                                              'Draw them yourself and don\'t wait for the house.'
                                              'Tell me every known card that you have drawn or flipped.'
                                              'If you draw an Ace you can decide whether it is a 1 or an 11.'
                                              'If you received feedback by the card counter optimizer, then implement it into your strategy.'
                                              'Here is an example: Your previous two cards were a 2 of Hearts and a 3 of Hearts. You decide to draw another card which is a 6 of Clubs. This is still low so you draw another card which is a 10. You don\'t want to draw another time and finish your turn.'
                                              'Here is another example: Your previous two cards were a 7 of Hearts and an 8 of Spades. You decide to draw another card which is a 5 of Clubs. You don\'t want to risk it and decidde to not draw another card.'
                                              'Here is another example: Your previous cards are a 10 of Hearts and a 9 of Clubs. You decide not to draw another card and finish your turn.'
                                              'Only generate the next answer.'
                                              'Rounds to go before the game ends: ' + str(num_rounds)

             # Ein Beispiel einbinden
             # Vielleicht draw additional cards statt hit
             # Generell expliziter machen
             },
        ]

        if total_tokens_burned + num_tokens_from_messages(message) >= 10000:
            print("Too many tokens. Going to sleep!")
            time.sleep(60)
            total_tokens_burned = num_tokens_from_messages(message)
        else:
            total_tokens_burned += num_tokens_from_messages(message)

        res = client.chat.completions.create(
            messages=message,
            model=gpt_model,

        )

        card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
        house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
        player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
        security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

        print(res.choices[0].message.content + '\n')

        # Alle Spieler ziehen nacheinander Karten
        print("\n Player 2 draws additional cards. \n")
        """
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
                                            'Tell me every known card that you have drawn or flipped.'

                 },

            ],
            model=gpt_model,

        )
        """

        message = [
            {"role": "user",
             "content": player_prompt + '\n You are Player 2 at the table.'
                                        'Play to your persona.'
                                        'Decide if you want to draw a card according to your strategy.'
                                        'You can draw as many cards as you want.'
                                        'Draw them yourself and don\'t wait for the house.'
                                        'Tell me every known card that you have drawn or flipped.'
                                        'If you draw an Ace you can decide whether it is a 1 or an 11.'
                                        'Here is an example: Your previous two cards were a 2 of Hearts and a 3 of Hearts. You decide to draw another card which is a 6 of Clubs. This is still low so you draw another card which is a 10. You don\'t want to draw another time and finish your turn.'
                                        'Here is another example: Your previous two cards were a 7 of Hearts and an 8 of Spades. You decide to draw another card which is a 5 of Clubs. You don\'t want to risk it and decidde to not draw another card.'
                                        'Here is another example: Your previous cards are a 10 of Hearts and a 9 of Clubs. You decide not to draw another card and finish your turn.'
                                        'Only generate the next answer.'
                                        'Rounds to go before the game ends: ' + str(num_rounds)
             },

        ]

        if total_tokens_burned + num_tokens_from_messages(message) >= 10000:
            print("Too many tokens. Going to sleep!")
            time.sleep(60)
            total_tokens_burned = num_tokens_from_messages(message)
        else:
            total_tokens_burned += num_tokens_from_messages(message)

        res = client.chat.completions.create(
            messages=message,
            model=gpt_model,

        )

        card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
        house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
        player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
        security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

        print(res.choices[0].message.content + '\n')

        # Bank deckt so lange auf bis Blackjack Regel bedient ist.
        # Gewinn wird ausgewertet
        print("\n The house draws additional cards and evaluates the outcome. \n")

        message = [
            {"role": "user",
             "content": house_prompt +
                        'Reveal your hidden card if every player decides to stay with their hand.'
                        'Draw additional cards according to the blackjack rulebook as the house. '
                        'Tell me every known card that you have drawn or flipped.'
                        'Evaluate which players have won and which haven\'t according to the blackjack rulebook.'
                        'If you have busted then all players which stayed below 21 won automatically'
                        'If a players has an ace, '
                        'the value of the ace is that what makes the hand nearest to 21.'
                        'Change their stakes accordingly.'
                        'Please give me a table of all the played cards of each player and the sum their hand'
                        'Please give me an overview of the new stakes of each player.'
                        'Don\'t give us an evaluation of the players\' behaviour.'
                        'Only generate the next answer.'
             },
        ]

        if total_tokens_burned + num_tokens_from_messages(message) >= 10000:
            print("Too many tokens. Going to sleep!")
            time.sleep(60)
            total_tokens_burned = num_tokens_from_messages(message)
        else:
            total_tokens_burned += num_tokens_from_messages(message)

        res = client.chat.completions.create(
            messages=message,
            model=gpt_model,

        )

        card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
        house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
        player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
        security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

        print(res.choices[0].message.content + '\n')

        # Habs auskommentiert um Tokens zu sparen
        # Security beobachtet das Spiel, prüft, ob er den Card Counter ausfindig machen kann
        print("\n Security checks if someone is counting cards. \n")

        message = [
            {"role": "user",
             "content": security_prompt +
                        'Your job is to catch the card counter.'
                        'Only give an observation based on what you read.'
                        'Ignore the thought processes of the players and make your decision based on the betting behavior.'
                        'If you are sure that someone is counting cards, then tell me who it is.'  # Eventuell an dieser Stelle eine Methode einführen, welche den Wert "im Spiel" ändert
                        'If you think, that nobody is counting cards then end your turn.'
                        'Only generate the next answer.'
             },
        ]

        if total_tokens_burned + num_tokens_from_messages(message) >= 10000:
            print("Too many tokens. Going to sleep!")
            time.sleep(60)
            total_tokens_burned = num_tokens_from_messages(message)
        else:
            total_tokens_burned += num_tokens_from_messages(message)

        res = client.chat.completions.create(
            messages=message,
            model=gpt_model,

        )

        card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
        house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
        player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
        security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

        print(res.choices[0].message.content + '\n')

        card_counter_count, real_count = analyse_game(card_counter_prompt, game, round, all_decks[game - 1])
        all_decks[game - 1] = update_deck(all_decks[game - 1], card_counter_prompt, game)

        # Hier den Promptopimizer machen
        if round == 2:
            print("\n Prompt optimizer gives tipps to the card counter. \n")

            message = [
                {"role": "user",
                 "content": 'You know every method of card counting.'
                            'Give the advice for the card counter and the security separately.'
                            'You look over the game and watch every action and observe every move the card counter makes.'
                            'Give the Card Counter Feedback on what to improve on with his game.'
                            'It can be everything for example his bets or general strategy'
                            'Tell the card counter his count and the real count.'
                            f'His count was {card_counter_count} while the real count was {real_count}.'
                            'Only generate the next answer.'
                 },
            ]

            if total_tokens_burned + num_tokens_from_messages(message) >= 10000:
                print("Too many tokens. Going to sleep!")
                time.sleep(60)
                total_tokens_burned = num_tokens_from_messages(message)
            else:
                total_tokens_burned += num_tokens_from_messages(message)

            res = client.chat.completions.create(
                messages=message,
                model=gpt_model,
            )

            card_counter_prompt = card_counter_prompt + '\n\n' + res.choices[0].message.content
            house_prompt = house_prompt + '\n\n' + res.choices[0].message.content
            player_prompt = player_prompt + '\n\n' + res.choices[0].message.content
            security_prompt = security_prompt + '\n\n' + res.choices[0].message.content

            print(res.choices[0].message.content + '\n')

        print("\n Next Round. \n")
        round += 1
    game += 1
