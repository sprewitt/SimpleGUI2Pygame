# 20 Questions - Pygame version

import ui
from state import State
from filehelper import FileHelper

#The default question tree
question_tree = ["human", None]


class GameStart(State):
    #The location of the question tree file
    question_file = "questions.txt"

    def __init__(self):
        State.__init__(self)
        self.nextState = lambda: Playing(question_tree)
        self.next_state_type = None
        self.message = "Load previous question tree?"

    def yes(self):
        global question_tree
        question_tree = FileHelper(GameStart.question_file).load()
        self.transition()

    def no(self):
        self.transition()

    def setup(self, screen):
        self.ui.add_button(screen, "Yes", lambda btn: self.yes(), (10, self.ui.font + 15))
        self.ui.add_button(screen, "No", lambda btn: self.no(), (120, self.ui.font + 15))
    def update(self, screen):
        self.ui.draw_text(screen, self.message)


class Playing(State):
    def __init__(self, tree):
        State.__init__(self)
        self.next_state = self.get_next_state
        self.next_state_type = None
        self.tree = tree

    def yes(self):
        self.next_state_type = lambda: GameOver("I win!")
        if self.tree[1] <> None:
            self.next_state_type = lambda: Playing(self.tree[1][True])
        self.transition()

    def no(self):
        self.next_state_type = lambda: Learning(self.tree, 0)
        if self.tree[1] <> None:
            self.next_state_type = lambda: Playing(self.tree[1][False])
        self.transition()

    def setup(self, screen):
        self.ui.add_button(screen, "Yes", lambda btn: self.yes(),
                           (10, self.ui.font + 15))
        self.ui.add_button(screen, "No", lambda btn: self.no(),
                           (120, self.ui.font + 15))

    def update(self, screen):
        self.ui.draw_text(screen, self.get_question())

    def get_question(self):
        return "Is it " + self.tree[0] + "?"

    def get_next_state(self):
        return self.next_state_type

class Learning(State):
    NAME_TEXT = "What is the name of the new animal?"
    DESCRIPTION_TEXT = "Enter an adjective that descibes the animal"

    messages = [NAME_TEXT,
                DESCRIPTION_TEXT]

    def __init__(self, tree, index, answers=None):
        State.__init__(self)
        self.tree = tree
        self.index = index
        if answers == None:
            answers = []
        self.answers = answers

    def learn_next(self):
        if self.index < len(Learning.messages) - 1:
            self.nextState = lambda: Learning(self.tree, self.index + 1, self.answers)
        else:
            self.build_tree()
            self.nextState = lambda: GameOver("You win!")
        self.transition()

    def build_tree(self):
        new_name = self.answers[0]
        descriptor = self.answers[1]
        false_branch = self.tree[0]
        self.tree[0] = descriptor
        self.tree[1] = {True:[new_name, None]}
        self.tree[1][False] = [false_branch, None]
        FileHelper(GameStart.question_file).save(question_tree)

    def input_text(self, text):
        self.answers.append(text)
        self.learn_next()

    def setup(self, screen):
        self.ui.add_input(screen,
                          Learning.messages[self.index],
                          lambda text: self.input_text(text),
                          (10, self.ui.font + 15),
                          (400, 25),
                          )

    def update(self, screen):
        left = 300
        top = self.ui.font
        width = 200
        height = 50
        self.ui.draw_text(screen, Learning.messages[self.index])
        self.ui.add_label(screen,
                          "(Remember to press enter after typing your answer)",
                          location=(10, 2 * self.ui.font + 20))

class GameOver(State):
    def __init__(self, message):
        State.__init__(self)
        self.nextState = lambda: Playing(question_tree)
        self.next_state_type = None
        self.message = message

    def yes(self):
        self.transition()

    def no(self):
        self.ui.quit()

    def setup(self, screen):
        self.ui.add_button(screen, "Yes", lambda btn: self.yes(),
                           (10, 2 * self.ui.font + 15))
        self.ui.add_button(screen, "No", lambda btn: self.no(),
                           (120, 2 * self.ui.font + 15))

    def update(self, screen):
        self.ui.draw_text(screen, self.message)
        self.ui.draw_text(screen, "Play again?", (10, self.ui.font + 15))

question_tree = ["human", None]
new_game = GameStart()
new_game.start()
