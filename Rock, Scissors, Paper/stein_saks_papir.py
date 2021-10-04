from random import randint
import operator
import matplotlib.pyplot as plt

action_values = {"Rock": 0, "Scissors": 1, "Paper": 2}
action_names = {val: name for name, val in action_values.items()}


class Action:
    """
    Help class to make moves easier
    """
    action_values = {"Rock": 0, "Scissors": 1, "Paper": 2}
    action_names = {val: name for name, val in action_values.items()}

    def __init__(self, value):
        if isinstance(value, str):
            value = self.action_values[value]
        assert isinstance(value, int) & (value >= 0) & (value < 3)
        self.value = value

    def __eq__(self, other):
        return self.value == other.value

    def __gt__(self, other):
        return (self.value + 1) % 3 == other.value

    def __str__(self):
        return self.action_names[self.value]

    def who_beats_me(self):
        return (self.value + 2) % 3


class Player:
    """
    Base class for Rock Scissors Paper Player
    """

    def __init__(self):
        self.count = {"Rock": 0, "Scissors": 0, "Paper": 0}
        self.value = 0
        self.move = ""
        self.name = "Player"

    def receive_result(self, other_move):
        self.count[other_move] += 1


class Random(Player):
    """
    Sublass of Player-class
    Chooses its move randomly
    """

    def select_action(self):
        self.value = randint(0, 2)
        self.move = Action(self.value).__str__()

    def enter_name(self):
        self.name = "Random"


class Sequence(Player):
    """
    Sublass of Player-class
    Chooses its move based on a given sequence
    """

    def __init__(self, sequence):
        """
        sequence (list): The given sequence of moves
        """
        Player.__init__(self)
        self.sequence = sequence
        self.pointer = 0

    def select_action(self):
        self.value = self.sequence[self.pointer]
        self.move = Action(self.value).__str__()
        self.pointer = (self.pointer + 1) % len(self.sequence)

    def enter_name(self):
        self.name = "Sequence"


class MostCommon(Player):
    """
    Sublass of Player-class
    Chooses its move based on opponents most common move
    """

    def __init__(self):
        Player.__init__(self)
        self.other_player_most_common_move = 0

    def select_action(self):
        self.other_player_most_common_move = max(
            self.count.items(), key=operator.itemgetter(1))[0]
        self.value = Action(self.other_player_most_common_move).who_beats_me()
        self.move = Action(self.value).__str__()

    def enter_name(self):
        self.name = "MostCommon"


class Historian(Player):
    """
    Sublass of Player-class
    Chooses its move based on pattern recognition of opponents earlier moves
    """

    def __init__(self, remember):
        Player.__init__(self)
        self.remember = remember
        self.last_moves = [None] * (self.remember + 1)
        self.pointer = 0

    def select_action(self):
        """
        Looks at n last moves and what is most commonly played after n moves based on history
        """
        if None not in self.last_moves:
            pattern = tuple()
            for i in range(self.remember):
                move = (self.last_moves[(self.pointer - i) %
                                        (self.remember + 1)], )
                pattern += move
            num_used = 0
            most_used_value = None
            for i in range(3):
                if pattern + (action_names[i], ) in self.count:
                    if num_used < self.count[pattern + (action_names[i], )]:
                        num_used = self.count[pattern + (action_names[i], )]
                        most_used_value = i
            if most_used_value is None:
                self.play_random()
            else:
                self.value = Action(most_used_value).who_beats_me()
                self.move = action_names[self.value]
        else:
            self.play_random()

    def play_random(self):
        self.value = randint(0, 2)
        self.move = Action(self.value).__str__()

    def receive_result(self, other_move):
        self.count[other_move] += 1
        self.last_moves[self.pointer] = other_move
        self.pointer = (self.pointer + 1) % (self.remember + 1)
        pattern = tuple()
        if None not in self.last_moves:
            for i in range(self.remember + 1):
                move = (self.last_moves[(self.pointer + i) %
                                        (self.remember + 1)], )
                pattern += move
            if pattern in self.count:
                self.count[pattern] += 1
            else:
                self.count[pattern] = 1

    def enter_name(self):
        self.name = "Historian (" + str(self.remember) + ")"


class SingleGame:
    """
    Initializes a single games and performs the game
    """

    def __init__(self, player_1, player_2, should_print):
        """
        Args:
            player_1 (Player): Player 1
            player_2 (Player): Player 2
            should_print (boolean): Print the games
        """
        self.player_1 = player_1
        self.player_2 = player_2
        self.player_1.enter_name()
        self.player_2.enter_name()
        self.should_print = should_print

    def perform_game(self):
        self.player_1.select_action()
        self.player_2.select_action()
        self.player_1.receive_result(self.player_2.move)
        self.player_2.receive_result(self.player_1.move)

    def show_result(self):
        if self.player_1.value == self.player_2.value:
            result = "Draw!"
            winner = "d"
        elif self.player_1.value == (self.player_2.value + 1) % 3:
            result = self.player_2.name + " wins!"
            winner = self.player_2
        else:
            result = self.player_1.name + " wins!"
            winner = self.player_1
        if self.should_print:
            print(self.player_1.name, "chose", self.player_1.move, "\n" +
                  self.player_2.name, "chose", self.player_2.move, "\n" + result + "\n")
        return winner


class Tournament:
    """
    Initializes a tournament between two players and plots the average points of player 2
    """

    def __init__(self, player_1, player_2, number_of_games, should_print):
        """
        Args:
            player_1 (Player): Player 1
            player_2 (Player): Player 2
            number_of_games (int): Number of games to be played
            should_print (boolean): Print the games
        """
        self.player_1 = player_1
        self.player_2 = player_2
        self.player_1_points = 0
        self.player_2_points = 0
        self.player_1_avg = 0
        self.player_2_avg = 0
        self.player_1_avgs = []
        self.player_2_avgs = []
        self.num_games = number_of_games
        self.should_print = should_print

    def arrange_singlegame(self):
        single_game = SingleGame(
            self.player_1, self.player_2, self.should_print)
        single_game.perform_game()
        winner = single_game.show_result()
        if winner == "d":
            self.player_1_points += 0.5
            self.player_2_points += 0.5
        elif winner == self.player_1:
            self.player_1_points += 1
        else:
            self.player_2_points += 1

    def arrange_tournament(self):
        for game in range(self.num_games):
            self.arrange_singlegame()
            self.player_1_avg = self.player_1_points/(game+1)
            self.player_2_avg = self.player_2_points/(game+1)
            self.player_1_avgs.append(self.player_1_avg)
            self.player_2_avgs.append(self.player_2_avg)
        print("Result after", self.num_games, "games:\n" + self.player_1.name +
              ":", self.player_1_points, "\n" + self.player_2.name + ":", self.player_2_points)
        plt.plot(self.player_2_avgs)
        plt.title("Average points of " + self.player_2.name)
        plt.xlabel("Games")
        plt.axis([1, self.num_games, 0, 1])
        plt.show()


def choose_player_type(player_num):
    player = input("Player " + str(player_num) + ": (mos, his, ran, seq) ")
    if player == "mos":
        return MostCommon()
    if player == "his":
        moves = int(
            input("How many moves should Historian remember? (1, 2, 3...) "))
        return Historian(moves)
    if player == "ran":
        return Random()
    if player == "seq":
        sequence = input(
            'What sequence should Sequence play? (0 = Rock, 1 = Scissors, 2 = Paper, seperated by comma (",")) ')
        sequence = sequence.split(",")
        moves = []
        for num in sequence:
            moves.append(int(num))
        return Sequence(moves)
    return None


def main():
    """
    Main function
    """
    player_1 = choose_player_type(1)
    player_2 = choose_player_type(2)
    num_games = int(input("How many games should be played? "))
    tournament = Tournament(player_1, player_2, num_games, False)
    tournament.arrange_tournament()


main()
