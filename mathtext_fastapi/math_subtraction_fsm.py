import random
from transitions import Machine


class MathSubtractionFSM(object):
    states = [
        'quiz_start',
        'quiz_question',
        'quiz_end'
    ]

    transitions = [
        ['ask_second_question', 'quiz_start', 'quiz_question'],
        ['ask_next_question', 'quiz_question', 'quiz_question'],
        ['exit', 'quiz_start', 'quiz_end'],
        ['exit', 'quiz_question', 'quiz_end'],
    ]

    def __init__(
        self,
        initial_state='quiz_start',
        question_nums=[4, 3],
        initial_student_answer=0,
    ):
        # Instantiate the FSM
        self.machine = Machine(
            model=self,
            states=MathSubtractionFSM.states,
            transitions=MathSubtractionFSM.transitions,
            initial=initial_state
        )

        # Instantiate variables necessary for tracking activity
        self.question_nums = question_nums
        self.correct_answer = self.question_nums[0] - self.question_nums[1]
        self.student_answer = initial_student_answer
        self.is_correct_answer = False
        self.response_text = f"What is {self.question_nums[0]} - {self.question_nums[1]}?"

        # Define functions to run on transitions
        self.machine.on_enter_quiz_question('generate_math_problem')
        self.machine.on_exit_quiz_question('validate_answer')

    def validate_answer(self):
        if self.student_answer == 'exit':
            self.machine.set_state('quiz_end')
            return ["Come back any time!"]
        elif self.correct_answer == self.student_answer:
            self.machine.set_state('quiz_question')
            self.generate_math_problem()
            return ['Great job!', self.response_text]
        else:
            return ["That's not quite right.  Try again.", self.response_text]
    
    def generate_math_problem(self):
        self.question_nums = random.sample(range(1, 100), 2)
        self.response_text = f"What is {self.question_nums[0]} - {self.question_nums[1]}"
        self.correct_answer = self.question_nums[0] - self.question_nums[1]