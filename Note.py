# Author: Matt Patek
# Date: 2017-09-01
#
# Description:
#   This program allows a user to either create "notecards" from which to quiz
#   themselves on, via a CLI, or to create and reference "journal" entries long
#   or short.

# modules
import sys # command line input
import re # regular expressions
import subprocess # allows us to write shell commands
import os # allows us to delete files
from random import shuffle # shuffles list randomly
import shutil # delete non-empty directory

# provides main flow of execution for this program
def main(argv):
    global directory # root directory
    directory = "D:/Programming/Python/Note"
    # define commandset
    myCommandSet = "^(-c|-d|-rn|-f|-r|-a|-j|ls|cd|x|cat|exit)"
    # clear terminal and display informational message
    execCommand("x")
    # program loop
    while(1):
        # get new input
        userInput = raw_input(directory + ">")
        # possible input cases
        if(re.search(myCommandSet, userInput)):
            execCommand(userInput)
        elif(userInput == "help"):
            displayHelpMenu()
        elif(userInput != ""):
            path = directory + "/" + userInput + ".txt"
            # read file into memory
            try:
                myFile = readFile(path)
                # shuffle cards
                myFile = shuffleCards(myFile)
            except IOError:
                print("ERROR: invalid path " + path + "\nPlease try again.")
            else:
                verifyDataIntegrity(myFile, path)
                # quiz user on contents
                global numCorrect, numTotal
                numCorrect = 0; numTotal = 0
                quizUser(myFile)
                # output local score for run
                print("Your score is: " + str(numCorrect) + "/" + str(numTotal))
                # export new file
                reWriteFile(myFile, path)
    # end while
# end main

# displays the informational message
def displayWelcomeMessage():
    print("Type 'help' to display help menu, or enter a command.\nNote that you never need to add '.txt'.\nOtherwise, enter notecards file to parse.")
# end displayWelcomeMessage

# displays a text-based help menu to show various functions a user can username
def displayHelpMenu():
    print("Help Menu\n---------")
    print("'-c' + name:\t\tCreates new directory in current folder.")
    print("'-j' + name:\t\tCreates/appends journal entry in current folder.")
    print("'-r' + name:\t\tResets local scores on file.")
    print("'-a' + name:\t\tAdd new 'notecard' to file, or creates new file.")
    print("'-d' + name:\t\tDeletes file or directory.")
    print("'-rn' + name + newName:\tRenames file to newName. Needs extension if applicable.")
    print("'cd' + name:\t\tChanges to specified directory. '..' goes up a level.")
    print("'ls':\t\t\tDisplays local directories.")
    print("'cat' + name:\t\tPrints out file contents.")
    print("'x':\t\t\tClears terminal.")
    print("'exit:'\t\t\tExits program gracefully.")
# end helpMenu

# executes one of the commands specified by the user and found in the help menu
def execCommand(command):
    global directory # current directory
    # parse name if applicable
    name = re.sub("(.)+\s", "", command)
    # exit program
    if(command == "exit"):
        sys.exit()
    # display immediate subdirectories
    elif(re.search("^ls", command)):
        for d in os.listdir(directory):
            print(d)
    # change directory
    elif(re.search("^cd", command)):
        if(name == ".."):
            # go up a level
            directory = re.sub("(/){1}(\w)+$", "", directory)
        elif(re.search("/", command)):
            if(os.path.isdir(directory + "/" + name)):
                directory = directory + "/" + name
        else:
            myList = initSubDirectories()
            for d in myList:
                if(name == d):
                    directory = directory + "/" + name
    # create folder
    elif(re.search("^-c", command)):
        myPath = directory + "/" + name
        if(not os.path.exists(myPath)):
            os.makedirs(myPath)
    # clears terminal
    elif(re.search("^x", command)):
        subprocess.call("cls", shell=True)
        # inform user on how to use this program
        displayWelcomeMessage()
    # append notecard file
    elif(re.search("^-a", command)):
        if(verifyDirectory("-a")):
            with open(directory + "/" + name + ".txt", "a") as file_object:
                while(1):
                    title = raw_input("Title?")
                    description = raw_input("Description?")
                    file_object.write("\nTitle: " + title + "\n")
                    file_object.write("Description: " + description + "\n")
                    file_object.write("Score: 0/0\n")
                    if(raw_input("Continue? (y/n)") != "y"):
                        break
        else:
            print("ERROR: invalid directory for creating/appending file " + directory)
    # rename file or directory
    elif(re.search("^-rn", command)):
        first = re.sub("^-rn\s", "", command) # file/dir to be renamed
        first = re.sub("\s" + name, "", first)
        os.rename(directory + "/" + first, directory + "/" + name)
    # reset local score
    elif(re.search("^-r", command)):
        try:
            myFile = readFile(directory + "/" + name + ".txt")
        except IOError:
            print("ERROR: " + directory + "/" + name + ".txt" + " doesn't exist.")
        else:
            for i, line in enumerate(myFile):
                if(re.search("^Score:\s", line)):
                    myFile[i] = re.sub("(\s){1}(\d)+(/){1}(\d)+", " 0/0", line)
            reWriteFile(myFile, directory + "/" + name + ".txt")
    # create/append journal entry
    elif(re.search("^-j", command)):
        if(verifyDirectory("-j")):
            raw_input("Entering journal mode. Exit by typing '!w'.")
            with open(directory + "/" + name + ".txt", "a") as myJournal:
                userInput = ""
                while(1):
                    userInput = raw_input("")
                    if(userInput == "!w"):
                        break
                    myJournal.write(userInput + "\n")
            raw_input("Exiting journal mode...")
        else:
            print("ERROR: invalid directory for journal: " + directory)
    # delete file
    elif(re.search("^-d", command)):
        myPath = directory + "/" + name
        if(re.search("(Data|Journal)/", myPath)):
            if(os.path.isfile(myPath + ".txt")):
                os.remove(myPath + ".txt")
            elif(os.path.isdir(myPath)):
                try:
                    os.rmdir(myPath)
                except WindowsError:
                    shutil.rmtree(myPath)
            else:
                print("ERROR: " + myPath + " doesn't exist.")
        else:
            print("ERROR: permission denied to delete " + myPath)
    # print file contents
    elif(re.search("^cat", command)):
        try:
            myFile = readFile(directory + "/" + name + ".txt")
        except IOError:
            print("ERROR: " + directory + "/" + name + ".txt" + " doesn't exist.")
        else:
            for line in myFile:
                print(line)
# end execCommand

# creates a list of immediate subdirectories
def initSubDirectories():
    global directory
    myList = []
    for d in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, d)):
            myList.append(d)
    return myList
# end initSubDirectories

# verifies that a file is being created in the correct directory
def verifyDirectory(command):
    global directory
    if(command == "-a" and re.search("Data", directory)):
        return 1
    elif(command == "-j" and re.search("Journal", directory)):
        return 1
    return 0
# end verifyDirectory

# reads file into memory
def readFile(path):
    with open(path, "r") as file_object:
        return file_object.read().splitlines()
# end readFile

# deletes old file and re-creates it with new contents
def reWriteFile(myFile, path):
    if(os.path.isfile(path)):
        # delete file
        os.remove(path)
    # create new file
    with open(path, "w") as newFile:
        for line in myFile:
            newFile.write(line + "\n")
# end reWriteFile

# loops through file and makes sure it's in the correct format
def verifyDataIntegrity(myFile, path):
    stringMatch = "^(Title|Description|Score)+(:\s)"
    lineNumber = 1
    for line in myFile:
        # match header
        if(line != "" and not re.search(stringMatch, line)):
            print("ERROR: something in " + path + " is amiss. Please fix:\n" + "line: " + str(lineNumber) + " '" + line + "'")
            return
        lineNumber += 1
# end verifyDataIntegrity

# quizzes user on notecards in file and keeps score
def quizUser(myFile):
    # loop through contents
    for i, line in enumerate(myFile):
        if(re.search("(Title|Description)", line)):
            raw_input(line)
        elif(re.search("Score", line)):
            # update score
            myFile[i] = updateScore(line)
            # print newline to make flow easier to read
            print("")
# end quizUser

# shuffles notecards
def shuffleCards(myFile):
    dictList = []
    title = ""; description = ""; score = "" # temp vars
    # store dictionaries
    for line in myFile:
        # set temp vars
        if(re.search("Title:", line)): title = line
        elif(re.search("Description:", line)): description = line
        elif(re.search("Score:", line)): score = line
        # add new dictionary to list
        if(title != "" and description != "" and score != ""):
            dictList.append({"title" : title, "description" : description, "score" : score})
            title = ""; description = ""; score = "" # reset vars
    shuffle(dictList)
    # reconstruct file
    myFile = []
    for d in dictList:
        myFile.append(d["title"])
        myFile.append(d["description"])
        myFile.append(d["score"])
        myFile.append("")
    return myFile
# end shuffleCards

# updates local score for a "notecard"
def updateScore(line):
    global numCorrect, numTotal # overall statistics
    isCorrect = raw_input("Enter 1 if correct, else nothing: ")
    score = re.sub("Score:\s", "", line)
    correct = int(re.sub("(/)+(.){0,99}$", "", score))
    total = int(re.sub("^(.)+(/)", "", score))
    if(isCorrect == "1"):
        correct += 1
        numCorrect += 1
    total += 1
    numTotal += 1
    score = "Score: " + str(correct) + "/" + str(total)
    print(score)
    return "Score: " + str(correct) + "/" + str(total)
# end updateScore

########## run program ##########
main(sys.argv)
########## end program ##########
