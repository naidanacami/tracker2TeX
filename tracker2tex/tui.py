import os
from ast import literal_eval


def clear_term():
    os.system("cls" if os.name == "nt" else "clear") 


def get_type(input_data):
    try:
        return(type(literal_eval(input_data)))
    except (ValueError, SyntaxError):
        # A string, so return str
        return(str)


def user_input(query:str, answers:list, escape_char:str=None, nullify:list=[]):
    """Gets user input

    Args:
        query (str): What to ask the user
        answers (list): The list of acceptable answers
        escape_char (str) (optional): escape squence--returns None
        nulligy (list) (optional): Answers to remove from list

    Returns:
        User's input (Item from given list). Returns None if escape char used
    """
    clear_term()
    invalid_answers = []
    while True:
        print(query)
        for index, item in enumerate(answers):
            index += 1
            if item in nullify:
                print(len(f"[{index}] - {item}")*"-")
                invalid_answers.append(index-1)
            else:
                print(f"[{index}] - {item}")

        # Gets user input
        if escape_char != None:
            user_input = input(f"Please select (1-{len(answers)}) ({escape_char} to exit): ")
        else:
            user_input = input(f"Please select (1-{len(answers)}): ")

        if user_input == escape_char:
            return(None)

        # Error handling:
        try:
            user_input = int(user_input)-1
            answers[user_input]
        except ValueError:
            clear_term()
            print("ERROR: please enter a number")
            continue
        except IndexError:
            clear_term()
            print("ERROR: outside of range")
            continue
        
        if user_input in invalid_answers:
            clear_term()
            print("ERROR: please enter a valid selection")
            continue

        return(answers[user_input])



def basic_input(prompt:str, anstype:type) -> str:
    clear_term()
    while True:
        uin = input(f"{prompt}  >")
        uin_type = get_type(uin)
        if uin_type != anstype:
            clear_term()
            print(f"Please enter answer in form: {anstype}")
            continue
        # fix later--match/case does not work
        if int == uin_type:
            return(int(uin))
        elif str == uin_type:
            return(str(uin))
        elif float == uin_type:
            return(float(uin))
        elif bool == uin_type:
            return(bool(uin))