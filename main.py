###################################################################
# Author:
# Adrian Negrea
#
#
# 20 Questions Game
# This program is a game which aims to guess the animal that someone
# is thinking about using a series of 20 yes or no questions.
#
# A database is used to store the questions in a table, with a
# separate table holding the values which each animal has for each
# question.
#
# On program start:
# - user given 3 options:
#   Start a new game
#   Add an animal
#   Exit
#
# On animal addition:
# - all the questions in the questions table are asked in order
# - the answers are stored in a dictionary in order to preserve
#   correct order
# - a new row is added to the animals table with the name of the
#   animal and the answers that have just been supplied
#
# On game start:
# - a dictionary is initialized which holds the value of each
#   animal, which is incremented by 1 each time the answer given
#   by the player matches up with the value of that animal for that
#   question
#   animals_values = {'ANIMAL NAME': VALUE}
# - a variable is initialized in order to hold the highest value
#   (currently 0)
#   max_value = 0
# - a variable is initialized in order to hold the name of the
#   animal with the highest value
#   max_animal = ""
# - the same is also done for the second highest value animal
#
# During the game:
# - a random question is asked and then that question is kept track
#   of so that it will not be asked again
# - when the user supplies an answer to the random question the
#   animals table is checked for the animals which fit the
#   description and their values in the animals_values is increased
#   by 1
# - if the value of an animal exceeds that of max_value after it is
#   incremented, the value of this animal will become the new
#   value for max_value and max_animal will hold its name and likewise
#   for the second highest valued animal
# - the best and second best guesses are used to determine which
#   questions will be asked next
#
# End of game:
# - the game supplies max_animal as a guess to the player
# - the player answers if the guess was in fact the animal they
#   were thinking of
# - if the guess is not correct then the player is asked for
#   what they were actually thinking of and then that is
#   added to the database as a new animal
# - user returned to the main_menu
###################################################################

import sqlite3, random, os
from decimal import *

# Get the current working directory
cwd = os.getcwd()
# Name of the database that is used for the program
database = cwd + "\\animals.db"
# Number of columns in animals table before the question values
nonq = 3


# Template for easier connection to the database
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


# Keeps asking for input until a valid y/n answer is given.
# Returns answer as 1 or 0.
def game_answer():
    ans = input("y/n:")

    if ans == "y":
        return 1
    elif ans == "n":
        return 0
    else:
        print("Invalid answer")
        return game_answer()


# Main game logic
def new_game():
    conn = create_connection(database)
    c = conn.cursor()
    c.execute("SELECT * FROM questions")
    questions_data = c.fetchall()

    # List of all questions that still haven't been asked
    questions_left = []
    # List of actual text of all the questions
    questions_text = []

    # Population of questions_left and questions_text
    for question in questions_data:
        questions_left.append(question[0])
        questions_text.append(question[1])

    # Initialize dictionary that will store scores for all animals.
    # Will be used to select winner.
    c.execute("SELECT * FROM animals")
    animals_data = c.fetchall()

    # Dictionary which holds values of each animal.
    # Value is incremented.
    animals_values = dict()
    for row in animals_data:
        animals_values.update({row[1]:0})

    # Prompt user for weather they are ready to begin.
    print("THINK OF AN ANIMAL!")
    print("Do you have an animal in mind?")
    # If anything other than y, prompt again.
    if (input("y/n:") != "y"):
        new_game()
        return 0

    # Initialize variables that will be used to hold best guess.
    max_value = Decimal(0)
    max_animal = ""

    second_value = Decimal(0)
    second_animal = ""

    # Dictionary that stores the questions asked along with the
    # answer which the player gives for each question.
    answers = dict()
    
    # For loop so that 20 questions will be asked before a guess is made.
    for i in range(0, 20):
        question_number = 0
        # Select random question for first question.
        if i < 2:
            rand = random.random()
            rand = rand * len(questions_left)
            rand = int(rand)
            question_number = questions_left[rand]
        # Select question to differentiate between top 2 guesses.
        else:
            # Get data of the best guess from animals table.
            sql = 'SELECT * FROM animals WHERE animal = ?'
            c.execute(sql, (max_animal,))
            best_values = c.fetchall()

            # Get data of second best guess from animals table.
            c.execute(sql, (second_animal,))
            second_values = c.fetchall()

            best_question = questions_left[0]
            best_question_difference = 0
            for j in questions_left:
                dif = abs(best_values[0][j + nonq - 1] - second_values[0][j + nonq - 1])
                if dif > 0:
                    best_question = j
                    best_question_difference = dif

            question_number = best_question

        # Print question and prompt for answer.
        question = questions_text[int(question_number) - 1]
        print(question)
        answer = game_answer()

        answers.update({question_number: answer})
        
        # Add 1 to value of all animals that match answer.
        for row in animals_data:
            # if row[question_number + nonq - 1] == answer:
            if answer == 0:
                val = animals_values.get(str(row[1]))
                val = Decimal(val)
                val += Decimal(1) - Decimal(row[question_number + nonq - 1])

                # Update best guess if needed.
                if val > max_value:
                    # Change second best if new best.
                    if max_animal != row[1]:
                        # Previous best becomes second.
                        second_value = max_value
                        second_animal = max_animal


                    # New best animal guess.
                    max_value = val
                    max_animal = row[1]

                # Update second best guess if needed.
                elif val > second_value:
                    # Don't make second best equal to best animal guess.
                    if row[1] != max_animal:
                        # Previous second best guess is replaced.
                        second_value = val
                        second_animal = row[1]
                
                animals_values.update({row[1]:val})

            elif answer == 1:
                val = animals_values.get(str(row[1]))
                val = Decimal(val)
                val += Decimal(row[question_number + nonq - 1])

                # Update best guess if needed.
                if val > max_value:
                    # change second best if new best
                    if max_animal != row[1]:
                        # Previous best becomes second.
                        second_value = max_value
                        second_animal = max_animal

                    # New best animal guess.
                    max_value = val
                    max_animal = row[1]

                # Update second best guess if needed.
                elif val > second_value:
                    # Don't make second best equal to best animal guess.
                    if row[1] != max_animal:
                        # Previous second best guess is replaced.
                        second_value = val
                        second_animal = row[1]

                animals_values.update({row[1]:val})
        print("best " + max_animal)
        print("second " + second_animal)

        # Remove question asked from questions_left so that it.
        # Does not get asked again.
        print("removed question " + str(question_number))
        q_index = questions_left.index(question_number)
        questions_left.remove(questions_left[q_index])
        print("questions_left: " + str(questions_left))

    # Provide best guess.
    guess = max_animal
    post_game_actions(guess, answers)
    
    main_menu()


# This is where all the after-game logic occurs.
# Updates animals table based on the results of the game.
def post_game_actions(guess, answers):
    print("\nWhere you thinking of " + guess + "?")
    feedback = game_answer()
    # Create connection to database.
    conn = create_connection(database)
    c = conn.cursor()
    
    questions_asked = ""

    # Analyze player response.
    # Update existing animal if the answer was correct.
    if feedback == 1:
        animal = guess
        update_animal(animal, answers)
                      
    # If guess is wrong player is prompted for what they were
    # actually thinking about.
    elif feedback == 0:
        # Ask user for the animal they had in mind,
        print("\nWhat was the animal you were thinking about?")
        animal = str(input())

        # Check if that animal already has an entry in the animals table.
        sql = 'SELECT 1 FROM animals WHERE animal = ?'
        c.execute(sql, (animal,))
        exists = c.fetchall()

        # If the animal already has an entry in the table.
        if exists:
            # Update the existing entry.
            update_animal(animal, answers)
            
        # Animal not in the table.
        # New entry will be created.
        else:
            # Create new entry in the animals table with just animal
            # and frequency defined.
            sql = 'INSERT INTO animals (animal, frequency) VALUES (?, ?);'
            c.execute(sql, (animal, 1))

            # Add all the data of the animal to the animals table.
            for key, value in answers.items():
                sql = 'UPDATE animals SET q' + str(key) + ' = q' + str(key) + ' + ' + str(value) + ' WHERE animal = ?;'
                c.execute(sql, (animal,))
            conn.commit()

    else:
        print("Error")


# Update the animal question values.
def update_animal(animal, answers):
    # Create connection to database.
    conn = create_connection(database)
    c = conn.cursor()
    
    # Fetch the existing animal data.
    sql = 'SELECT * FROM animals WHERE animal = ?'
    c.execute(sql, (animal,))
    animal_data = c.fetchall()
    prev_frequency = animal_data[0][2]

    # Update animal with the new average value for each question
    # frequency is used to not give earlier or later answers unfair
    # representation in the data.
    for key, value in answers.items():
        old_val = Decimal(animal_data[0][int(key) + nonq - 1]) * Decimal(prev_frequency)
        new_val = Decimal(Decimal(old_val + int(value)) / Decimal(prev_frequency + 1))
        q_name = 'q' + str(key)
        sql = 'UPDATE animals SET ' + q_name + ' = ' + str(new_val) + ' WHERE animal = ?;'
        c.execute(sql, (animal,))
        
    # Increase frequency of the animal that was updated by 1.
    sql = 'UPDATE animals SET frequency = ? WHERE animal = ?'
    new_frequency = prev_frequency + 1
    c.execute(sql, (new_frequency, animal))
    conn.commit()


# Ask questions during game.
# Formats the question so that it contains the animal name.
def animal_question_yn(question, animal):
    # Replaces "it" from all the questions with the animal name.
    question = question.replace("it", "a/an {}".format(animal))
    print(question)
    answer = input("y/n: ")

    # Test for valid answer.
    if answer != "y" and answer != "n":
        print("Please enter a valid answer!")
        return animal_question_yn(question, animal)
    else:
        if answer == "y":
            return 1
        else:
            return 0


# Add an animal to the animals table in animals.db.
# Parameters are connection to database and a tuple
# of size 1, with an animal name as its only element.
def create_animal(conn, animal):
    sql = 'SELECT animal FROM animals WHERE animal=?'
    c = conn.cursor()
    # Attempts to get row from animals table where animal column
    # is equal to the animal that will be added.
    c.execute(sql, animal)
    exists = c.fetchall()
    # If there already is an entry for given animal,
    # exit create_animal by returning 0.
    if exists:
        print("Animal already exists.")
        return 0

    # If there is no entry for animal supplied, create
    # a new row with the animal name as the value of the animal
    # column in the newly created row.
    sql = 'INSERT INTO animals(animal) VALUES(?)'
    c.execute(sql, animal)

    # Select animal name as string from the animal tuple.
    animal = animal[0]

    # Create a dictionary with question id as key and question
    # text as value.
    questions = {}
    c.execute('SELECT * FROM questions')
    data = c.fetchall()
    for question in data:
        questions.update({question[0]:question[1]})

    # Goes through every question and asks them.
    # Answers stored in dictionary, with key of the question used
    # as key, and answer stored as value.
    answers = {}
    for key, value in questions.items():
        answer = animal_question_yn(value, animal)
        answers.update({key:answer})

    # Will hold sqlite command.
    questions_string = ""
    # Holds values for each question for the animal.
    values_list = []
    # Create sqlite command.
    for key, value in answers.items():
        questions_string = questions_string + "q" + str(key) + " = ?,"
        values_list.append(value)

    values_list.append(str(animal))
    
    values_t = tuple(values_list)
    #print("values_t = ")
    #print(values_t)

    questions_string = questions_string[:-1]
    #question_marks = question_marks[:-1]

    sql = 'UPDATE animals SET '
    sql += str(questions_string)
    sql += ' WHERE animal = ?'
    #sql += str(animal)
    sql = str(sql)

    #print("sql = " + sql)
    c.execute(sql, values_t)
    
    return c.lastrowid


# Adds new animal to animals table.
def new_animal():
    new_animal = input("New animal: ")

    # Connect to the database.
    conn = create_connection(database)
    with conn:
        # Turn animal name into tuple.
        animal = (new_animal,)
        # Passes animal tuple to the create_animal function
        # and returns what is returned by it.
        return create_animal(conn, animal)


# Adds a question to the questions table.
# Returns id of the row once it is added to the table.
def create_question(conn, question):
    sql = 'INSERT INTO questions(question) VALUES(?)'
    # Create connection to the database.
    c = conn.cursor()
    c.execute(sql, question)
    ret = c.lastrowid

    # Will be used to add column to the animals table.
    #NOT YET IMPLEMENTED
    new_q = "q" + str(ret)
    sql = 'ALTER TABLE animals ADD ' + new_q + ' INTEGER'
    #col_name = tuple('"q" + str(ret)',)
    c.execute(sql)
    
    return ret


# Takes input for what the new question is and calls
# create_question in order to add it.
def new_question():
    new_question = input("New question: ")

    conn = create_connection(database)
    with conn:
        question = (new_question,)
        return create_question(conn, question)


# Main interactive piece of program.
def main_menu():

    # User chooses what he wants to do.
    options = [
        "0 Exit",
        "1 New game",
        "2 Add an animal",
        #"3 Add a question",
        ]

    # Display the options.
    for option in options:
        print(option)

    # Listen for the user's option selection.
    action = input()

    # Make sure action is an integer.
    try:
        action = int(action)
    except ValueError as e:
        print("Option must be a number")
        main_menu()

    # Make sure action is a valid integer.
    if action > len(options) or action < 0:
        print("Invalid option selected")
        main_menu()

    # Preform the action which the user selected.
    elif action == 0:
        quit()
    elif action == 1:
        new_game()
    elif action == 2:
        new_animal()
    elif action == 3:
        new_question()

    main_menu()


# Title screen.
def main():
    print("WELCOME TO 20 QUESTIONS")
    print("DEVELOPER EDITION")
    print("CREATED BY CASCAVAL&CO")
    print("\n\nWhat would you like to do?")
    main_menu()


# Start the program.
main()
