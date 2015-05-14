import random

class Card(object):
    """A card in Hanabi has two attributes, color and number.

    Attributes:
        color: A string representing the "suit" of the card. Must be one of the
            following values: Red, Yellow, Green, Blue, White, or Rainbow.
        number: An integer representing the "value" of the card. Must be 1
            through 5.
    """
    colors = ["Red", "Yellow", "Green", "Blue", "White", "Rainbow"]

    def __init__(self, color, number):
        self.color = color
        self.number = number

    def __str__(self):
        return "%s %s" % (self.color, self.number)

    def __repr__(self):
        return "<Card color:%s number:%s>" % (self.color, self.number)

class Deck(object):
    def __init__(self, variation):
        self.deck = []
        self.variation = variation
        numbers = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]
        for c in Card.colors:
            if variation == 0:
                if c == "Rainbow":
                    break
            elif variation == 1:
                if c == "Rainbow":
                    numbers = [1,2,3,4,5]

            for n in numbers:
                self.deck.append(Card(c,n))

        self.count = len(self.deck)

    def shuffle(self):
        random.shuffle(self.deck)

    def draw(self):
        if self.count == 0:
            return -1

        c = self.deck.pop()
        self.count = len(self.deck)
        return c

    def __repr__(self):
        return "<Deck variation:%s count:%s>" % (self.variation, self.count)

class Player(object):
    choices = """Discard (0). \nPlay (1). \nGive Information (2).\n"""

    def __init__(self):
        self.hand = []
        self.knowns = [[], [], [], [], []]

    def print_hand(self):
        cards = []
        for card in self.hand:
            cards.append(str(card))

        return cards

    def discard(self, index):
        card = self.hand.pop(index)
        self.knowns.pop(index)

    def play(self, index):
        self.knowns.pop(index)
        return self.hand.pop(index)

    def give_information(self, information):
        pass

    def recv_information(self, information):
        reorder = []
        if isinstance(information, str):
            for i, card in enumerate(self.hand):
                if card.color == information:
                    if information not in self.knowns[i]:
                        self.knowns[i].insert(0, information)
                        reorder.append(i)
        else:
            for i in range(len(self.hand)):
                if self.hand[i].number == information:
                    if information not in self.knowns[i]:
                        self.knowns[i].append(information)
                        reorder.append(i)
        self.reorder(reorder)

    def reorder(self, reorder):
        for index in reorder:
            card = self.hand[index]
            known = self.knowns[index]
            self.hand.pop(index)
            self.knowns.pop(index)
            inserted = 0
            for i in range(len(self.knowns)):
                if self.knowns[i] == []:
                    self.hand.insert(i, card)
                    self.knowns.insert(i, known)
                    inserted = 1
                    break
            if inserted != 1:
                self.hand.append(card)
                self.knowns.append(known)

    def __repr__(self):
        return "<Player knowns:%s hand:%s>" % (self.knowns, self.hand)

    def __str__(self):
        cards = []

        for h in self.hand:
            cards.append(str(h))

        return str({"hand": cards, "knowns": self.knowns})


class Board(object):
    def __init__(self, players):
        self.players = []
        self.player_turn = 0
        self.bombs = 3
        self.time = 8
        self.deck = Deck(0)
        self.board = {"Red":[], "Yellow":[], "Green":[],
                      "Blue":[], "White":[], "Rainbow":[]}

        self.deck.shuffle()

        #for p in range(players):
        #    self.players.append(Player())
        #    if players < 4:
        #        for i in range(5):
        #            self.players[p].hand.append(self.deck.draw())
        self.players.append(Player())
        for i in range(5):
            self.players[0].hand.append(self.deck.draw())

        self.players.append(AI())
        for i in range(5):
            self.players[1].hand.append(self.deck.draw())

    def add_to_board(self, card):
        if card.number == 1:
            if self.board[card.color] == []:
                self.board[card.color].append(card)
            else:
                self.bombs -= 1
        else:
            cards = self.board[card.color]
            if cards != []:
                stack = cards[-1]
                if card.number - stack.number == 1:
                    self.board[card.color].append(card)
                    if card.number == 5 and self.time < 8:
                        self.time += 1
            else:
                self.bombs -= 1

    def __repr__(self):
        return "<Board players:%s bombs:%s time:%s>" % (len(self.players),
                                                        self.bombs,
                                                        self.time)

class Game(object):
    def __init__(self):
        self.board = Board(2)
        for i in range(len(self.board.players)):
            player = self.board.players[i]
            print "Player %s" % (i)
            print player.print_hand()

    def play(self):
        while self.board.bombs > 0:
            self.print_board(self.board.player_turn)
            player = self.board.players[self.board.player_turn]
            partner = self.board.players[(self.board.player_turn + 1) % 2]

            ai = isinstance(player, AI)
            decision = ()
            if ai:
                player.time = self.board.time
                player.bombs = self.board.bombs
                player.partner_hand = self.board.players[0].hand
                player.partner_known = self.board.players[0].knowns
                player.board = self.board.board
                player.calculate_next_playable()
                decision = player.turn()
                choice = str(decision[0])
            else:
                choice = raw_input(Player.choices)

            if choice == '0': # discard
                if ai:
                    index = decision[1]
                    print "AI == Discard"
                else:
                    index = int(raw_input("Card index: ") or "-1")

                player.discard(index)

                self.draw_card(player)

                if self.board.time < 8:
                    self.board.time += 1
                #player.print_hand()

            elif choice == '1': # play card
                if ai:
                    index = decision[1]
                    print "AI == Play Card"
                else:
                    index = int(raw_input("Card index: "))
                card = player.play(index)
                self.board.add_to_board(card)

                self.draw_card(player)

                #player.print_hand()

            elif choice == '2': # give information
                if self.board.time == 0:
                    return
                if ai:
                    index = decision[1]
                    info = decision[2]
                    print "AI == Give Info"
                else:
                    index = int(raw_input("Card index: "))
                    info = raw_input("Color(0) or Number(1)")

                card = partner.hand[index]
                self.board.time -= 1
                if info == '0':
                    info = card.color
                elif info == '1':
                    info = card.number
                partner.recv_information(info)
            else:
                return

            self.board.player_turn = (self.board.player_turn + 1) % 2


    def draw_card(self, player):
        inserted = 0
        for i in range(len(player.knowns)):
            if player.knowns[i] == []:
                player.hand.insert(i, self.board.deck.draw())
                player.knowns.insert(i, [])
                inserted = 1
                break;

        if inserted == 0:
            player.hand.append(self.board.deck.draw())
            player.knowns.append([])


    def print_board(self, player_number):
        b = self.board.board
        cards = []
        for key in b:
            if b[key] != []:
                cards.append(str(b[key][-1]))

        print "\n"
        print "Time: %s" % (self.board.time)
        print "Bombs: %s" % (self.board.bombs)
        print "Board: %s" % (cards)
        print "\n"
        print "Player %s's turn" % (player_number)
        print "Partner's cards: %s" % (self.board.players[
            (player_number + 1) % 2].print_hand())
        print "Partner's Knowns: %s\n" % (self.board.players[
            (player_number + 1) % 2].knowns)
        print "Knowns %s" % (self.board.players[player_number].knowns)
        print "\n"


    def __repr__(self):
        return "<Game players:%s>" % (len(self.board.players))

class AI(Player):
    def __init__(self):
        self.DISCARD = 0
        self.PLAY = 1
        self.GIVE_INFORMATION = 2
        self.COLOR = '0'
        self.NUMBER = '1'
        self.time = 8
        self.bombs = 3
        self.next_playable = []
        self.partner_hand = []
        self.partner_known = []
        self.board = {"Red":[], "Yellow":[], "Green":[],
                      "Blue":[], "White":[], "Rainbow":[]}
        super(AI, self).__init__()

    def turn(self):
        # check for playable card and play if found
        for index, n_playable in enumerate(self.next_playable):
            if n_playable in self.knowns:
                return (self.PLAY, index)
            # check if card is already played
            if self.board[n_playable[0]] != []:
                if n_playable[1] == self.board[n_playable[0]][-1].number:
                    return (self.DISCARD, index)

        # find if we can give information.
        if self.time > 0:
            lowest = 0
            give_info = 0
            for i in range(len(self.partner_hand)):
                card = self.partner_hand[i]
                if len(self.partner_known[i]) < 2:
                    give_info = 1
                    if card.number < self.partner_hand[lowest].number:
                        lowest = i
            if give_info > 0:
                print "DEBUG == lowest: %s" % (lowest)
                print "DEBUG == self.partner_known: %s" % (self.partner_known)
                if self.partner_known[lowest] != []:
                    if isinstance(self.partner_known[lowest][0], str):
                        print "Number: %s" % (self.partner_hand[lowest].number)
                        return (self.GIVE_INFORMATION, lowest, self.NUMBER)
                    else:
                        print "Color: %s" % (self.partner_hand[lowest].color)
                        return (self.GIVE_INFORMATION, lowest, self.COLOR)      
                else:
                    return (self.GIVE_INFORMATION, lowest, self.NUMBER)

        # if none of the above, discard card farthest to the right.
        return (self.DISCARD, -1)

    def calculate_next_playable(self):
        self.next_playable = []
        for color in Card.colors:
            if self.board[color] == []:
                self.next_playable.append([color, 1])
            elif self.board[color][-1].number < 5:
                self.next_playable.append([color,
                                           self.board[color][-1].number + 1])

