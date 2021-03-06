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
    """A deck of cards.

    There are many variations of Hanabi, the most notable
    are whether or not to include the rainbow cards in the deck.

    Attributes:
    """

    def __init__(self, variation):
        self.deck = []
        self.variation = variation
        numbers = [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]
        for color in Card.colors:
            if variation == 0:
                if color == "Rainbow":
                    break
            elif variation == 1:
                if color == "Rainbow":
                    numbers = [1, 2, 3, 4, 5]

            for number in numbers:
                self.deck.append(Card(color, number))

        self.count = len(self.deck)

    def shuffle(self):
        """Shuffle the deck of Hanabi cards.
        """

        random.shuffle(self.deck)

    def draw(self):
        """Draw a card from the deck.
        """

        if self.count == 0:
            return -1

        card = self.deck.pop()
        self.count = len(self.deck)
        return card

    def __repr__(self):
        return "<Deck variation:%s count:%s>" % (self.variation, self.count)

class Player(object):
    """Player of Hanabi.

    The player class keeps track of the player's hand as well as known cards.

    Attributes:

    """
    choices = """Discard (0). \nPlay (1). \nGive Information (2).\n"""

    def __init__(self):
        self.hand = []
        self.knowns = [[], [], [], [], []]

    def print_hand(self):
        """Print hand in a human readable way.
        """
        cards = []
        for card in self.hand:
            cards.append(str(card))

        return cards

    def discard(self, index):
        """Discard selected card from hand.

        Args:
            index: index of card to be discarded.
        """
        self.hand.pop(index)
        self.knowns.pop(index)

    def play(self, index):
        """Play a card to the board.

        Args:
            index: index of card to play.

        Returns:
            The card that is to be played.
        """
        self.knowns.pop(index)
        return self.hand.pop(index)

    def recv_information(self, information):
        """Receive information about hand from another player. All cards
        with the same color or number are identified.

        Args:
            information: either color or number of a card.
        """

        if isinstance(information, str):
            for i, card in enumerate(self.hand):
                if card.color == information:
                    if information not in self.knowns[i]:
                        self.knowns[i].insert(0, information)
        else:
            for i in range(len(self.hand)):
                if self.hand[i].number == information:
                    if information not in self.knowns[i]:
                        self.knowns[i].append(information)
        self.reorder()

    def reorder(self):
        """Reorder cards in hand after receiving information. Place like colors
        next to each, highest number on the left.
        """
        list_color = []
        list_number = []
        order = []
        # find which cards have known information
        for i, known in enumerate(self.knowns):
            if known != []:
                if known[0] in Card.colors:
                    list_color.append(i)
                else:
                    list_number.append(i)

        # sort by color
        if list_color != []:
            order = self.__color_sort(list_color)

        place = 0
        for index in order:
            card = self.hand.pop(index)
            known = self.knowns.pop(index)

            self.hand.insert(place, card)
            self.knowns.insert(place, known)

            place += 1
            #inserted = 0
            #for i, knowns in enumerate(self.knowns)):
            #    if knowns == []:
            #        self.hand.insert(i, card)
            #        self.knowns.insert(i, known)
            #        inserted = 1
            #        break
            #if inserted != 1:
            #    self.hand.append(card)
            #    self.knowns.append(known)

    def __color_sort(self, lst):
        """Merge sort a list of knowns in order of Card.colors.

        Args:
            lst: a list of indecies for the cards in hand to be sorted.

        Return:
            a list in the order of Card.colors
        """
        if len(lst) == 1:
            return lst

        left = self.__color_sort(lst[:len(lst)/2])
        right = self.__color_sort(lst[len(lst)/2:])
        order = []
        while (len(left) > 0) and (len(right) > 0):
            color_left = Card.colors.index(self.knowns[left[0]][0])
            color_right = Card.colors.index(self.knowns[right[0]][0])

            if color_left <= color_right:
                order.append(left.pop(0))
            else:
                order.append(right.pop(0))

        while len(left) > 0:
            order.append(left.pop(0))
        while len(right) > 0:
            order.append(right.pop(0))

        return order

    def __repr__(self):
        return "<Player knowns:%s hand:%s>" % (self.knowns, self.hand)

    def __str__(self):
        cards = []

        for card in self.hand:
            cards.append(str(card))

        return str({"hand": cards, "knowns": self.knowns})


class Board(object):
    """Board to keep track of Hanabi.

    Board keeps track of players, player's turn, bombs, time, deck, and
    what has been played.

    Attributes:
    """

    def __init__(self, players):
        self.players = []
        self.player_turn = 0
        self.bombs = 3
        self.time = 8
        self.deck = Deck(0)
        self.board = {"Red":[], "Yellow":[], "Green":[],
                      "Blue":[], "White":[], "Rainbow":[]}

        self.deck.shuffle()

        self.players.append(Player())
        self.players.append(AI())
        for i in range(5):
            self.players[0].hand.append(self.deck.draw())
            self.players[1].hand.append(self.deck.draw())

    def add_to_board(self, card):
        """Add a card to the board.

        Args:
            card: Card to be added.
        """
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
    """Game contains methods to play the game.

    Game handles the game play.  Keeping track of whose turn it is, and
    figuring out when the game is over.

    Attributes:
    """

    def __init__(self):
        self.board = Board(2)
        for i in range(len(self.board.players)):
            player = self.board.players[i]
            print "Player %s" % (i)
            print player.print_hand()

    def play(self):
        """Start the game.
        """

        while self.board.bombs > 0:
            self.print_board(self.board.player_turn)
            player = self.board.players[self.board.player_turn]
            partner = self.board.players[(self.board.player_turn + 1) % 2]

            ai_player = isinstance(player, AI)
            decision = ()
            if ai_player:
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
                if ai_player:
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
                if ai_player:
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
                if ai_player:
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
        """Draw a card from the deck.

        Args:
            player: person receiving the card.
        """

        inserted = 0
        for i in range(len(player.knowns)):
            if player.knowns[i] == []:
                player.hand.insert(i, self.board.deck.draw())
                player.knowns.insert(i, [])
                inserted = 1
                break

        if inserted == 0:
            player.hand.append(self.board.deck.draw())
            player.knowns.append([])


    def print_board(self, player_number):
        """Print the board from a player's perspective.

        Args:
            player_number: print from this player's perspective.
        """

        board = self.board.board
        cards = []
        for key in board:
            if board[key] != []:
                cards.append(str(board[key][-1]))

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
    """Artificial Intelligence for Hanabi.

    AI allows the python to simulate a player.

    Attributes:
    """

    DISCARD = 0
    PLAY = 1
    GIVE_INFORMATION = 2
    COLOR = '0'
    NUMBER = '1'

    def __init__(self):
        self.time = 8
        self.bombs = 3
        self.next_playable = []
        self.partner_hand = []
        self.partner_known = []
        self.board = {"Red":[], "Yellow":[], "Green":[],
                      "Blue":[], "White":[], "Rainbow":[]}
        super(AI, self).__init__()

    def turn(self):
        """Signal AI to play.  All of the logic for AI to figure out
        what to do.
        """

        # check for playable card and play if found
        for index, n_playable in enumerate(self.next_playable):
            if n_playable in self.knowns:
                return (AI.PLAY, index)
            # check if card is already played
            if self.board[n_playable[0]] != []:
                if n_playable[1] == self.board[n_playable[0]][-1].number:
                    return (AI.DISCARD, index)

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
                        return (AI.GIVE_INFORMATION, lowest, AI.NUMBER)
                    else:
                        print "Color: %s" % (self.partner_hand[lowest].color)
                        return (AI.GIVE_INFORMATION, lowest, AI.COLOR)
                else:
                    return (AI.GIVE_INFORMATION, lowest, AI.NUMBER)

        # if none of the above, discard card farthest to the right.
        return (AI.DISCARD, -1)

    def calculate_next_playable(self):
        """Calculate the next card that the AI will be able to play.
        """

        self.next_playable = []
        for color in Card.colors:
            if self.board[color] == []:
                self.next_playable.append([color, 1])
            elif self.board[color][-1].number < 5:
                self.next_playable.append([color,
                                           self.board[color][-1].number + 1])

