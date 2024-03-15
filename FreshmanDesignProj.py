from tkinter import *
import pickle
import RPi.GPIO as GPIO
from time import sleep, time

# initialize the current shelf
try:
    with open ("current_shelf.pickle", "rb") as f:
        current_shelf = pickle.load(f)
except FileNotFoundError:
    current_shelf = 1

class Motor:
    def __init__(self):
        self.pwmFreq = 1000
    def shelfCall(self, targetShelf):
        global current_shelf
        time_for_shelf = 1.85
        backwards_count = 0
        shelf_bvar = current_shelf
        while (shelf_bvar != targetShelf):
            if (shelf_bvar == 1):
                shelf_bvar = 6
            else:
                shelf_bvar -= 1
            backwards_count += 1
        print (backwards_count)
        forwards_count = 0
        shelf_fvar = current_shelf
        while (shelf_fvar != targetShelf):
            if (shelf_fvar == 6):
                shelf_fvar = 1
            else:
                shelf_fvar += 1
            forwards_count += 1
        print(forwards_count)
        if (backwards_count < forwards_count):
            if (targetShelf != current_shelf):
                GPIO.output(DIR_PIN_1, False)
                GPIO.output(DIR_PIN_2, True)
                for duty in range (0, 51):
                    pi_pwm.ChangeDutyCycle(duty)
                    sleep(0.01)
                sleep(time_for_shelf * backwards_count)
                for duty in range(50, -1, -1):
                    pi_pwm.ChangeDutyCycle(duty)
                    GPIO.output(DIR_PIN_1, False)
                    GPIO.output(DIR_PIN_2, False)
                    sleep(0.01)
                GPIO.output(DIR_PIN_1, False)
                GPIO.output(DIR_PIN_2, False)
                current_shelf = targetShelf

        else:
            if (targetShelf != current_shelf):
                GPIO.output(DIR_PIN_1, True)
                GPIO.output(DIR_PIN_2, False)
                for duty in range (0, 51):
                    pi_pwm.ChangeDutyCycle(duty)
                    sleep(0.01)
                sleep(time_for_shelf * forwards_count)
                for duty in range(50, -1, -1):
                    pi_pwm.ChangeDutyCycle(duty)
                    GPIO.output(DIR_PIN_1, False)
                    GPIO.output(DIR_PIN_2, False)
                    sleep(0.01)
                GPIO.output(DIR_PIN_1, False)
                GPIO.output(DIR_PIN_2, False)
                current_shelf = targetShelf

# class to initialize and calibrate the ultrasonic sensor
# class UltraSonic:
#     def __init__(self):
#         self.calibrationDistance = 10
#         # the previous measurement is used for determining if a shelf has gone by
#         self.previousMeasurement = self.calibrationDistance

#         # Calibrates the sensor for proper distance measurments
#     def calibrate(self):
#         print("Calibrating...")
#         print("Place the sensor a known distance away from am object")
#         knownDistance = self.calibrationDistance
#         print("Getting calibration measurements")
#         print("Done.")
#         distanceAverage = 0
        
#         # Compares known distance to average calibration distances
#         # Creates a calibration constant based on this comparison
#         for i in range(CALIBRATIONS):
#             distance = self.getDistance()
#             distanceAverage += distance
#             sleep(CALIBRATION_DELAY)
            
#         distanceAverage /= CALIBRATIONS
        
#         print(f"Average distance is {distanceAverage}")
        
#         correctionFactor = knownDistance / distanceAverage
        
#         print(f"Correction factor is {correctionFactor}")
#         print("")
        
#         return(correctionFactor)
        
#     # Finds the distance from the US sensor in cm
#     def getDistance(self):

#         GPIO.output(TRIG, GPIO.HIGH)
#         sleep(TRIGGER_TIME)
#         GPIO.output(TRIG, GPIO.LOW)
        
#         while (GPIO.input(ECHO) == GPIO.LOW):
#             start = time()
#         while (GPIO.input(ECHO) == GPIO.HIGH):
#             end = time()
            
#         duration = end - start
        
#         distance = duration * SPEED_OF_SOUND
        
#         distance /= 2
#         distance *= 100

#         return distance

#     def trackShelf(self):
#         global current_shelf
#         distance = sensor.getDistance() * correctionFactor
#         distance = round(distance, 4)
#         difference = distance - sensor.previousMeasurement
#         if (difference > 5):
#             if (current_shelf > 6):
#                 current_shelf = 1
#             else:
#                 current_shelf += 1
#         current_shelf_label.config(text=f"Current Shelf: {current_shelf}")
#         sensor.previousMeasurement = distance

# set all available color themes in a dictionary
color_themes = { "red": ["#ffe3e3", "#ffbfbf", "#850000", "#ff0000"], 
                "orange": ["#fff4d9", "#ffe3a1", "#b38314", "#ffb300"], 
                "yellow": ["#fdffde", "#fbffab", "#7f851d", "#cbd600"],
                "green": ["#dbffd9", "#a2ff9c", "#076900", "#11ff00"],
                "blue": ["#d6fffe", "#96fffc", "#00736f", "#00e0d9"],
                "indigo": ["#d4d4ff", "#a7a6ff", "#020073", "#0400ff"],
                "purple": ["#f0d1ff", "#e09cff", "#570080", "#ae00ff"],
                "pink": ["#fee3ff", "#ff94db", "#73004d", "#ff1988"],
                "gray": ["#dedae0", "#bdbabf", "#4a474d", "#79737d"] }

# initialize current shelf colors
try:
    with open("shelf_colors.pickle", "rb") as f:
        shelf_colors = pickle.load(f)
except FileNotFoundError:
    shelf_colors = ["red", "orange", "yellow", "green", "blue", "indigo", "purple", "pink", "gray"]

# initialize instructions settings
try:
    with open("instructions.pickle", "rb") as f:
        instructions = pickle.load(f)
except FileNotFoundError:
    instructions = [True, True, True, True, True, True, True, True, True]

# grab the barcodes from the previous section unless there are none
try:
    with open("barcodes.pickle", "rb") as f:
        barcodes = pickle.load(f)
except FileNotFoundError:
    barcodes = { }

# initialize shelf names
try:
    with open("frames.pickle", "rb") as f:
        frames = pickle.load(f)
except FileNotFoundError:
    frames = ["Home Page", "Shelf One", "Shelf Two", "Shelf Three", "Shelf Four", "Shelf Five", "Shelf Six", "Manage Barcodes", "Settings"]

# controls the framework and allows for switching between frames
class ShelfApp(Tk):
    def __init__(self, *args, **kwargs):
        # inherit from parent class
        Tk.__init__(self, *args, **kwargs)

        # create a container
        container = Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # initialize frames
        self.frames = {}

        # iterate through the different frames
        for F in (Home, One, Two, Three, Four, Five, Six, ManageBarcodes, Settings):
            frame = F(container, self)

            # add frames to the array
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(Home)

    # display the current frame
    def showFrame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# a class for creating, adding to, and removing from, the lists of items for each shelf
class ItemList():
    # initializes an empty shelf
    def __init__(self):
        self.items = []

    # method for printing the shelves
    def __str__(self):
        s = ""
        for item in self.items:
            s += item + "\n"
        return s

    # add an item to the list of items
    def addItem(self, event, entry, label):
        # pull the text from the entry field
        barcode = entry.get()
        # check to see if the item is stored in the barcodes list.
        # If not, it will simply add the item typed in to the shelf
        if (barcode in barcodes):
            item = barcodes[barcode]
        else:
            item = entry.get()
        # append the text from the entry field or the item stored with the barcode to the list of shelf items
        self.items.append(item.lower().strip())
        # delete everything out of the list box to reset it
        label.delete(0, END)
        # put everything back in the list box
        for i in range(len(self.items)):
            label.insert(i + 1, self.items[i])
        # delete the text from the entry field to reset it
        entry.delete(0, END)

    # remove an item from the list on the shelf object
    def removeItem(self, listbox, label):
        try: 
            # pull the text from the entry field
            item = listbox.get(listbox.curselection()[0])
            # remove the text from the list of items
            self.items.remove(item)
            # clear everything out the list box
            listbox.delete(0, END)
            # reset the list box
            for i in range(len(self.items)):
                listbox.insert(i + 1, self.items[i])
            label.config(text="")
        except IndexError:
            label.config(text="Select an item from\nthe list and try again.")

# if the pickles from previous sessions exist,
# open them and store them as the shelf objects
try:
    with open("pickled_shelf_one.pickle", "rb") as f:
        shelf_one_items = pickle.load(f)
    with open("pickled_shelf_two.pickle", "rb") as f:
        shelf_two_items = pickle.load(f)
    with open("pickled_shelf_three.pickle", "rb") as f:
        shelf_three_items = pickle.load(f)
    with open("pickled_shelf_four.pickle", "rb") as f:
        shelf_four_items = pickle.load(f)
    with open("pickled_shelf_five.pickle", "rb") as f:
        shelf_five_items = pickle.load(f)
    with open("pickled_shelf_six.pickle", "rb") as f:
        shelf_six_items = pickle.load(f)

# if the pickles from previous sessions don't exist,
# create new empty shelf objects
except FileNotFoundError:
    shelf_one_items = ItemList()
    shelf_two_items = ItemList()
    shelf_three_items = ItemList()
    shelf_four_items = ItemList()
    shelf_five_items = ItemList()
    shelf_six_items = ItemList()

# class for the home page
class Home(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        # initialize color
        color = shelf_colors[0]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        # set frame background
        Frame.configure(self, bg=self.BG_COLOR)
        
        # set fonts
        self.title_font = ("Cooper Black", 20)
        button_font = ("Century Gothic", 12, "bold")
        listbox_font = ("Century Gothic", 10)

        # create a title
        self.label = Label(self, text=f"Home Page")
        self.label.grid(row=0, column=1, padx=10, pady=10)
        self.label.config(font=self.title_font, bg=self.BG_COLOR, fg=self.TITLE_FG)
        
        # create buttons to navigate to each shelf
        self.button1 = Button(self, bg=self.BUTTON_BG, fg="black", text=f"{frames[1]}", command = lambda: controller.showFrame(One))
        self.button1.grid(row=1, column=0, padx=10, pady=10)
        self.button1.config(font=button_font)
        
        self.button2 = Button(self, bg=self.BUTTON_BG, fg="black", text=f"{frames[2]}", command = lambda: controller.showFrame(Two))
        self.button2.grid(row=2, column=0, padx=10, pady=10)
        self.button2.config(font=button_font)
        
        self.button3 = Button(self, bg=self.BUTTON_BG, fg="black", text=f"{frames[3]}", command = lambda: controller.showFrame(Three))
        self.button3.grid(row=1, column=1, padx=10, pady=10)
        self.button3.config(font=button_font)
        
        self.button4 = Button(self, bg=self.BUTTON_BG, fg="black", text=f"{frames[4]}", command = lambda: controller.showFrame(Four))
        self.button4.grid(row=2, column=1, padx=10, pady=10)
        self.button4.config(font=button_font)
        
        self.button5 = Button(self, bg=self.BUTTON_BG, fg="black", text=f"{frames[5]}", command = lambda: controller.showFrame(Five))
        self.button5.grid(row=1, column=2, padx=10, pady=10)
        self.button5.config(font=button_font)
        
        self.button6 = Button(self, bg=self.BUTTON_BG, fg="black", text=f"{frames[6]}", command = lambda: controller.showFrame(Six))
        self.button6.grid(row=2, column=2, padx=10, pady=10)
        self.button6.config(font=button_font)
        
        self.manage_barcodes = Button(self, bg=self.BUTTON_BG, fg="black", text=f"{frames[7]}", command = lambda: controller.showFrame(ManageBarcodes))
        self.manage_barcodes.grid(row=3, column=1, padx=10, pady=10)
        self.manage_barcodes.config(font=button_font)

        self.settings = Button(self, bg=self.BUTTON_BG, fg="black", text=f"{frames[8]}", command=lambda:controller.showFrame(Settings))
        self.settings.grid(row=3, column=0, padx=10, pady=10)
        self.settings.config(font=button_font)

        # create a label in case the text in the searchable field isn't found
        # set it to search until the search button is used
        self.not_found = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.not_found.grid(row=5, rowspan=2, column=1, padx=10, pady=10)
        self.not_found.config(font=listbox_font)

        # create a button to update the frame when clicked
        self.update = Button(self, bg=self.BUTTON_BG, fg="black", text="UPDATE SCREEN", command=lambda: self.changeTitle())
        self.update.grid(row=5, column=2, padx=10, pady=10)
        self.update.config(font=button_font)

        self.update_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.update_label.grid(row=6, column=2, padx=10, pady=10)
        self.update_label.config(font=listbox_font)

        self.shelf_instructions = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.shelf_instructions.grid(row=1, rowspan=2, column=3, padx=10, pady=10)
        self.shelf_instructions.config(font=listbox_font)

        # label to show current shelf
        self.cur_shelf = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Current Shelf: {frames[current_shelf]}")
        self.cur_shelf.grid(row=0, column=3, padx=10, pady=10)
        self.cur_shelf.config(font=button_font)

        self.instructions = Button(self, bg=self.BUTTON_BG, fg="black", command=lambda: self.hideInstructions())
        self.instructions.grid(row=3, column=3, padx=10, pady=10)
        if (instructions[0]):
            self.instructions.config(font=button_font, text="HIDE INSTRUCTIONS")
            self.update_label.config(text="Press update to refresh\ncolors and titles.")
            self.not_found.config(text="Type in an item name or\nscan a barcode. Press\nenter to search.")
            self.shelf_instructions.config(text="Click on a shelf\nor search from an item\nto go to that shelf.")
        else:
            self.instructions.config(font=button_font, text="SHOW INSTRUCTIONS")
            self.update_label.config(text="             ")
            self.not_found.config(text="Search")
            self.shelf_instructions.config(text="            ")

        # create a searchable field
        self.field = Entry(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.field.grid(row=4, column=1, padx=10, pady=10)
        self.field.config(font=listbox_font)
        self.field.bind("<Return>", self.searchItems)

    def hideInstructions(self):
        if (instructions[0]):
            self.instructions.config(text="SHOW INSTRUCTIONS")
            self.update_label.config(text="             ")
            self.not_found.config(text="Search")
            self.shelf_instructions.config(text="            ")
            del instructions[0]
            instructions.insert(0, False)
        else:
            self.instructions.config(text="HIDE INSTRUCTIONS")
            self.update_label.config(text="Press update to refresh\ncolors and titles.")
            self.not_found.config(text="Type in an item name or\nscan a barcode. Press\nenter to search.")
            self.shelf_instructions.config(text="Click on a shelf\nor search from an item\nto go to that shelf.")
            del instructions[0]
            instructions.insert(0, True)
    
    # change the titles of all buttons to match shelf titles
    # change colors if colors have been updated
    # once the update button is clicked
    def changeTitle(self):
        color = shelf_colors[0]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        Frame.configure(self, bg=self.BG_COLOR)

        # change titles and button colors
        self.label.config(text=f"{frames[0]}")
        self.manage_barcodes.config(text=f"{frames[7]}", bg=self.BUTTON_BG)
        self.settings.config(text=f"{frames[8]}", bg=self.BUTTON_BG)
        self.button1.config(text=f"{frames[1]}", bg=self.BUTTON_BG)
        self.button2.config(text=f"{frames[2]}", bg=self.BUTTON_BG)
        self.button3.config(text=f"{frames[3]}", bg=self.BUTTON_BG)
        self.button4.config(text=f"{frames[4]}", bg=self.BUTTON_BG)
        self.button5.config(text=f"{frames[5]}", bg=self.BUTTON_BG)
        self.button6.config(text=f"{frames[6]}", bg=self.BUTTON_BG)

        # change other colors
        self.label.config(fg=self.TITLE_FG, bg=self.BG_COLOR)
        self.not_found.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.field.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.update.config(bg=self.BUTTON_BG)
        self.cur_shelf.config(bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Current Shelf: {frames[current_shelf]}")
        self.update_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.instructions.config(bg=self.BUTTON_BG)
        self.shelf_instructions.config(bg=self.BG_COLOR, fg=self.LABEL_FG)

    # search for items in each list
    # the first list that the item is found in will be the list you're taken to
    def searchItems(self, event):
        # reset the item not found label to be empty
        self.not_found.config(text="")
        # grab the entry from the search field
        barcode = self.field.get()
        # check to see if the word is a barcode
        if (barcode in barcodes):
            word = barcodes[barcode]
             # exit if the word is quit
            if (word.lower().strip() == "quit"):
                app.destroy()
            # check the shelf for each item and clear the field
            elif (word.lower().strip() in shelf_one_items.items):
                self.controller.showFrame(One)
                self.field.delete(0, END)
            elif (word.lower().strip() in shelf_two_items.items):
                self.controller.showFrame(Two)
                self.field.delete(0, END)
            elif (word.lower().strip() in shelf_three_items.items):
                self.controller.showFrame(Three)
                self.field.delete(0, END)
            elif (word.lower().strip() in shelf_four_items.items):
                self.controller.showFrame(Four)
                self.field.delete(0, END)
            elif (word.lower().strip() in shelf_five_items.items):
                self.controller.showFrame(Five)
                self.field.delete(0, END)
            elif (word.lower().strip() in shelf_six_items.items):
                self.controller.showFrame(Six)
                self.field.delete(0, END)
            else:
                if (instructions[0]):
                    self.not_found.config(text="Item not found.\nCheck your spelling or\nsearch for another item.)", fg="red")
                else:
                    self.not_found.config(text="Item not found", fg="red")
                self.field.delete(0, END)
        # if not, set the search phrase to the word input
        else:
            word = self.field.get()
            # exit if the word is quit
            if (word.lower().strip() == "quit"):
                app.destroy()
            # check the shelf for each item and clear the field
            elif (word.lower().strip() in shelf_one_items.items):
                self.controller.showFrame(One)
                self.field.delete(0, END)
            elif (word.lower().strip() in shelf_two_items.items):
                self.controller.showFrame(Two)
                self.field.delete(0, END)
            elif (word.lower().strip() in shelf_three_items.items):
                self.controller.showFrame(Three)
                self.field.delete(0, END)
            elif (word.lower().strip() in shelf_four_items.items):
                self.controller.showFrame(Four)
                self.field.delete(0, END)
            elif (word.lower().strip() in shelf_five_items.items):
                self.controller.showFrame(Five)
                self.field.delete(0, END)
            elif (word.lower().strip() in shelf_six_items.items):
                self.controller.showFrame(Six)
                self.field.delete(0, END)
            else:
                self.not_found.config(text="Item not found", fg="red")
                self.field.delete(0, END)

class One(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        # initialize color
        color = shelf_colors[1]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        # set frame background
        Frame.configure(self, bg=self.BG_COLOR)
        
        # set fonts
        self.title_font = ("Cooper Black", 20)
        button_font = ("Century Gothic", 12, "bold")
        listbox_font = ("Century Gothic", 10)

        # label for title of the shelf
        self.title = Label(self, bg=self.BG_COLOR, fg=self.TITLE_FG, text=frames[1])
        self.title.grid(row=0, column=0, padx=10, pady=10)
        self.title.config(font=self.title_font)
        
        # button to return back to the home page
        self.home = Button(self, bg=self.BUTTON_BG, fg="black", text=f"{frames[0]}".upper(), command = lambda: controller.showFrame(Home))
        self.home.grid(row=1, column=0, padx=10, pady=10)
        self.home.config(font=button_font)

        # label for the listbox of items on the shelf
        self.items_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Items on {frames[1]}: ")
        self.items_label.grid(row=0, column=2, padx=10, pady=10)
        self.items_label.config(font=button_font)

        # listbox of items on the shelf
        self.items = Listbox(self, fg=self.LABEL_FG)
        self.items.grid(row=1, rowspan=4, column=2, padx=10, pady=10)
        # iterates through the list of items on shelf one
        # to put all items into the listbox
        for i in range(len(shelf_one_items.items)):
            self.items.insert(i + 1, shelf_one_items.items[i])
        self.items.config(font=listbox_font)

        # label for the field to add items to the shelf
        self.add_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.add_label.grid(row=1, column=1, padx=10, pady=10)
        self.add_label.config(font=listbox_font)

        # label to explain how to remove items from the shelf
        self.remove_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.remove_label.grid(row=6, column=2, padx=10, pady=10)
        self.remove_label.config(font=listbox_font)

        # field to add items to the shelf
        self.field = Entry(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.field.grid(row=2, column=1, padx=10, pady=10)
        self.field.config(font=listbox_font)
        self.field.bind("<Return>", lambda event: shelf_one_items.addItem(event, self.field, self.items))

        # button to remove an item from a shelf
        self.grab = Button(self, bg=self.BUTTON_BG, fg="black", text="REMOVE", command = lambda: shelf_one_items.removeItem(self.items, self.remove_error))
        self.grab.grid(row=5, column=2, padx=10, pady=10)
        self.grab.config(font=button_font)

        # # adds a scrollbar to the listbox of items on the shelf
        # scroll = Scrollbar(self)
        # scroll.grid(row=1, column=2)
        # self.items.config(yscrollcommand=scroll.set)
        # scroll.config(command=self.items.yview)

        # goes to shelf one
        self.move_to_shelf = Button(self, bg=self.BUTTON_BG, fg="black", text="Go to Shelf One", command=lambda: self.goToShelfOne())
        self.move_to_shelf.grid(row=4, column=0, padx=10, pady=10)
        self.move_to_shelf.config(font=button_font)

        # updates the widgets on the shelf to the text and color as updated in the settings
        self.update = Button(self, bg=self.BUTTON_BG, fg="black", text="UPDATE SCREEN", command=lambda: self.changeTitle())
        self.update.grid(row=5, column=1, padx=10, pady=10)
        self.update.config(font=button_font)

        # instructions for the update label
        self.update_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.update_label.grid(row=6, column=1, padx=10, pady=10)
        self.update_label.config(font=listbox_font)

        # label to explain error in removing items if it occurs
        self.remove_error = Label(self, bg=self.BG_COLOR, fg="red")
        self.remove_error.grid(row=1, column=3, padx=10, pady=10, rowspan=2)
        self.remove_error.config(font=listbox_font)

        # label to show current shelf
        self.cur_shelf = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Current Shelf: {frames[current_shelf]}")
        self.cur_shelf.grid(row=6, column=0, padx=10, pady=10)
        self.cur_shelf.config(font=button_font)

        # button to show or hide insturctions
        self.instructions = Button(self, bg=self.BUTTON_BG, fg="black", command = lambda: self.changeInstructions())
        self.instructions.grid(row=5, column=0, padx=10, pady=10)
        if (instructions[1]):
            self.instructions.config(font=button_font, text="HIDE INSTRUCTIONS")
            self.add_label.config(text="Type in an item\nor scan its barcode.\nPress enter to add\nit to the shelf.")
            self.update_label.config(text="Press update to see\nchanges made in settings.")
            self.remove_label.config(text="Select an item and\npress remove to take it\noff the shelf.")
        else:
            self.instructions.config(font=button_font, text="SHOW INSTRUCTIONS")
            self.update_label.config(text="                 ")
            self.remove_label.config(text="                 ")
            self.add_label.config(text="add to shelf")

    def changeInstructions(self):
        if (instructions[1]):
            self.update_label.config(text="                 ")
            self.add_label.config(text="add to shelf")
            self.remove_label.config(text="                 ")
            self.instructions.config(text="SHOW INSTRUCTIONS")
            del instructions[1]
            instructions.insert(1, False)
        else:
            self.update_label.config(text="Press update to see\nchanges made in settings.")
            self.remove_label.config(text="Select an item and\npress remove to take it\noff the shelf.")
            self.add_label.config(text="Type in an item\nor scan its barcode.\nPress enter to add\nit to the shelf.")
            self.instructions.config(text="HIDE INSTRUCTIONS")
            del instructions[1]
            instructions.insert(1, True)

    # updates the titles and colors of every widget
    def changeTitle(self):
        new_name = frames[1]
        self.title.config(text=new_name)
        color = shelf_colors[1]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        Frame.configure(self, bg=self.BG_COLOR)
        self.title.config(bg=self.BG_COLOR, fg=self.TITLE_FG)
        self.home.config(bg=self.BUTTON_BG, text=f"{frames[0]}")
        self.items_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Items on {frames[1]}: ")
        self.items.config(fg=self.LABEL_FG)
        self.field.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.grab.config(bg=self.BUTTON_BG)
        self.move_to_shelf.config(bg=self.BUTTON_BG)
        self.update.config(bg=self.BUTTON_BG)
        self.add_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.remove_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.update_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.instructions.config(bg=self.BUTTON_BG)
        self.remove_error.config(bg=self.BG_COLOR)
        self.cur_shelf.config(text=f"Current Shelf: {frames[current_shelf]}", bg=self.BG_COLOR, fg=self.LABEL_FG)

    # code to move to shelf one
    def goToShelfOne(self):
        motor.shelfCall(1)

class Two(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        # initialize color
        color = shelf_colors[2]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        # set frame background
        Frame.configure(self, bg=self.BG_COLOR)
        
        # set fonts
        self.title_font = ("Cooper Black", 20)
        button_font = ("Century Gothic", 12, "bold")
        listbox_font = ("Century Gothic", 10)

        # title of the current shelf
        self.title = Label(self, bg=self.BG_COLOR, fg=self.TITLE_FG, text=f"{frames[2]}")
        self.title.grid(row=0, column=0, padx=10, pady=10)
        self.title.config(font=self.title_font)
        
        # button to return to the home page frame
        self.home = Button(self, bg=self.BUTTON_BG, fg="black", text=f"{frames[0]}", command = lambda: controller.showFrame(Home))
        self.home.grid(row=1, column=0, padx=10, pady=10)
        self.home.config(font=button_font)

        # label for the listbox that lists all the items currently stored on the shelf
        self.items_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Items on {frames[2]}: ")
        self.items_label.grid(row=0, column=2, padx=10, pady=10)
        self.items_label.config(font=button_font)

        # listbox that stores all items currently on the shelf
        self.items = Listbox(self, fg=self.LABEL_FG)
        self.items.grid(row=1, column=2, rowspan=4, padx=10, pady=10)
        for i in range(len(shelf_two_items.items)):
            self.items.insert(i + 1, shelf_two_items.items[i])
        self.items.config(font=listbox_font)

        # entry field where users can type in an item or scan a barcode
        # to add the item to the shelf
        self.field = Entry(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.field.grid(row=2, column=1, padx=10, pady=10)
        self.field.config(font=listbox_font)
        self.field.bind("<Return>", lambda event: shelf_two_items.addItem(event, self.field, self.items))

        # button to remove an item from the shelf ( an item must be
        # selected in the listbox for this to function properly)
        self.grab = Button(self, bg=self.BUTTON_BG, fg="black", text="REMOVE", command = lambda: shelf_two_items.removeItem(self.items, self.remove_error))
        self.grab.grid(row=5, column=2, padx=10, pady=10)
        self.grab.config(font=button_font)

        # # adds a scrollbar to the list of items
        # scroll = Scrollbar(self)
        # scroll.grid(row=1, column=2)
        # self.items.config(yscrollcommand=scroll.set)
        # scroll.config(command=self.items.yview)

        # button to have the shelf code move to the correct shelf
        self.move_to_shelf = Button(self, bg=self.BUTTON_BG, fg="black", text="Go to Shelf Two", command=lambda: self.goToShelfTwo())
        self.move_to_shelf.grid(row=4, column=0, padx=10, pady=10)
        self.move_to_shelf.config(font=button_font)

        # button to update the text and color of the widgets on this shelf
        # as according to changes made in the settings frame
        self.update = Button(self, bg=self.BUTTON_BG, fg="black", text="UPDATE SCREEN", command=lambda: self.changeTitle())
        self.update.grid(row=5, column=1, padx=10, pady=10)
        self.update.config(font=button_font)

        # label for the entry field that adds items to the shelf
        self.add_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.add_label.grid(row=1, column=1, padx=10, pady=10)
        self.add_label.config(font=listbox_font)

        # instructions for the update label
        self.update_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.update_label.grid(row=6, column=1, padx=10, pady=10)
        self.update_label.config(font=listbox_font)

        # label to explain how to remove items from the shelf
        self.remove_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.remove_label.grid(row=6, column=2, padx=10, pady=10)
        self.remove_label.config(font=listbox_font)

        # label to describe an error in removing items from the shelf
        self.remove_error = Label(self, bg=self.BG_COLOR, fg="red")
        self.remove_error.grid(row=1, column=3, padx=10, pady=10, rowspan=2)
        self.remove_error.config(font=listbox_font)

        # label to show current shelf
        self.cur_shelf = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Current Shelf: {frames[current_shelf]}")
        self.cur_shelf.grid(row=6, column=0, padx=10, pady=10)
        self.cur_shelf.config(font=button_font)

        # button to show or hide insturctions
        self.instructions = Button(self, bg=self.BUTTON_BG, fg="black", command = lambda: self.changeInstructions())
        self.instructions.grid(row=5, column=0, padx=10, pady=10)
        if (instructions[2]):
            self.instructions.config(font=button_font, text="HIDE INSTRUCTIONS")
            self.add_label.config(text="Type in an item\nor scan its barcode.\nPress enter to add\nit to the shelf.")
            self.update_label.config(text="Press update to see\nchanges made in settings.")
            self.remove_label.config(text="Select an item and\npress remove to take it\noff the shelf.")
        else:
            self.instructions.config(font=button_font, text="SHOW INSTRUCTIONS")
            self.update_label.config(text="                 ")
            self.remove_label.config(text="                 ")
            self.add_label.config(text="add to shelf")

    def changeInstructions(self):
        if (instructions[2]):
            self.update_label.config(text="                 ")
            self.add_label.config(text="add to shelf")
            self.remove_label.config(text="                 ")
            self.instructions.config(text="SHOW INSTRUCTIONS")
            del instructions[2]
            instructions.insert(2, False)
        else:
            self.update_label.config(text="Press update to see\nchanges made in settings.")
            self.remove_label.config(text="Select an item and\npress remove to take it\noff the shelf.")
            self.add_label.config(text="Type in an item\nor scan its barcode.\nPress enter to add\nit to the shelf.")
            self.instructions.config(text="HIDE INSTRUCTIONS")
            del instructions[2]
            instructions.insert(2, True)

    # updates the text and color of the widgets
    def changeTitle(self):
        new_name = frames[2]
        self.title.config(text=new_name)
        color = shelf_colors[2]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        Frame.configure(self, bg=self.BG_COLOR)
        self.title.config(bg=self.BG_COLOR, fg=self.TITLE_FG)
        self.home.config(bg=self.BUTTON_BG, text=f"{frames[0]}")
        self.items_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Items on {frames[2]}: ")
        self.items.config(fg=self.LABEL_FG)
        self.field.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.grab.config(bg=self.BUTTON_BG)
        self.move_to_shelf.config(bg=self.BUTTON_BG)
        self.update.config(bg=self.BUTTON_BG)
        self.add_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.remove_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.update_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.instructions.config(bg=self.BUTTON_BG)
        self.remove_error.config(bg=self.BG_COLOR)
        self.cur_shelf.config(text=f"Current Shelf: {frames[current_shelf]}", bg=self.BG_COLOR, fg=self.LABEL_FG)

    # moves the shelf to this shelf
    def goToShelfTwo(self):
        motor.shelfCall(2)

class Three(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        # initialize color
        color = shelf_colors[3]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        # set frame background
        Frame.configure(self, bg=self.BG_COLOR)
        
        # set fonts
        self.title_font = ("Cooper Black", 20)
        button_font = ("Century Gothic", 12, "bold")
        listbox_font = ("Century Gothic", 10)

        # sets the title to the current title of the shelf
        self.title = Label(self, bg=self.BG_COLOR, fg=self.TITLE_FG, text=f"{frames[3]}")
        self.title.grid(row=0, column=0, padx=10, pady=10)
        self.title.config(font=self.title_font)
        
        # sets the home button to return to the home page
        self.home = Button(self, bg=self.BUTTON_BG, fg="black", text=f"{frames[0]}", command = lambda: controller.showFrame(Home))
        self.home.grid(row=1, column=0, padx=10, pady=10)
        self.home.config(font=button_font)

        # labels the listbox of items
        self.items_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Items on {frames[3]}: ")
        self.items_label.grid(row=0, column=2, padx=10, pady=10)
        self.items_label.config(font=button_font)

        # puts the items on the shelf into the listbox to display
        self.items = Listbox(self, fg=self.LABEL_FG)
        self.items.grid(row=1, column=2, rowspan=4, padx=10, pady=10)
        for i in range(len(shelf_three_items.items)):
            self.items.insert(i + 1, shelf_three_items.items[i])
        self.items.config(font=listbox_font)

        # labels the box to add items
        self.add_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="add item")
        self.add_label.grid(row=1, column=1, padx=10, pady=10)
        self.add_label.config(font=button_font)

        # entry field that adds items to the shelf
        self.field = Entry(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.field.grid(row=2, column=1, padx=10, pady=10)
        self.field.config(font=listbox_font)
        self.field.bind("<Return>", lambda event: shelf_three_items.addItem(event, self.field, self.items))

        # button to remove items from the shelf when they are selected in the listbox
        self.grab = Button(self, bg=self.BUTTON_BG, fg="black", text="REMOVE", command = lambda: shelf_three_items.removeItem(self.items, self.remove_error))
        self.grab.grid(row=5, column=2, padx=10, pady=10)
        self.grab.config(font=button_font)

        # # bar to scroll through the listbox
        # scroll = Scrollbar(self)
        # scroll.grid(row=1, column=2)
        # self.items.config(yscrollcommand=scroll.set)
        # scroll.config(command=self.items.yview)

        # button to have the shelf rotate to this shelf
        self.move_to_shelf = Button(self, bg=self.BUTTON_BG, fg="black", text="Go to Shelf Three", command=lambda: self.goToShelfThree())
        self.move_to_shelf.grid(row=4, column=0, padx=10, pady=10)
        self.move_to_shelf.config(font=button_font)

        # button to update the text and color of the widgets on the shelf
        self.update = Button(self, bg=self.BUTTON_BG, fg="black", text="UPDATE SCREEN", command=lambda: self.changeTitle())
        self.update.grid(row=5, column=1, padx=10, pady=10)
        self.update.config(font=button_font)

        # label for the entry field that adds items to the shelf
        self.add_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.add_label.grid(row=1, column=1, padx=10, pady=10)
        self.add_label.config(font=listbox_font)

        # instructions for the update label
        self.update_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.update_label.grid(row=6, column=1, padx=10, pady=10)
        self.update_label.config(font=listbox_font)

        # label to explain how to remove items from the shelf
        self.remove_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.remove_label.grid(row=6, column=2, padx=10, pady=10)
        self.remove_label.config(font=listbox_font)

        self.remove_error = Label(self, bg=self.BG_COLOR, fg="red")
        self.remove_error.grid(row=1, column=3, padx=10, pady=10, rowspan=2)
        self.remove_error.config(font=listbox_font)

        # label to show current shelf
        self.cur_shelf = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Current Shelf: {frames[current_shelf]}")
        self.cur_shelf.grid(row=6, column=0, padx=10, pady=10)
        self.cur_shelf.config(font=button_font)

        # button to show or hide insturctions
        self.instructions = Button(self, bg=self.BUTTON_BG, fg="black", command = lambda: self.changeInstructions())
        self.instructions.grid(row=5, column=0, padx=10, pady=10)
        if (instructions[3]):
            self.instructions.config(font=button_font, text="HIDE INSTRUCTIONS")
            self.add_label.config(text="Type in an item\nor scan its barcode.\nPress enter to add\nit to the shelf.")
            self.update_label.config(text="Press update to see\nchanges made in settings.")
            self.remove_label.config(text="Select an item and\npress remove to take it\noff the shelf.")
        else:
            self.instructions.config(font=button_font, text="SHOW INSTRUCTIONS")
            self.update_label.config(text="                 ")
            self.remove_label.config(text="                 ")
            self.add_label.config(text="add to shelf")

    def changeInstructions(self):
        if (instructions[3]):
            self.update_label.config(text="                 ")
            self.add_label.config(text="add to shelf")
            self.remove_label.config(text="                 ")
            self.instructions.config(text="SHOW INSTRUCTIONS")
            del instructions[3]
            instructions.insert(3, False)
        else:
            self.update_label.config(text="Press update to see\nchanges made in settings.")
            self.remove_label.config(text="Select an item and\npress remove to take it\noff the shelf.")
            self.add_label.config(text="Type in an item\nor scan its barcode.\nPress enter to add\nit to the shelf.")
            self.instructions.config(text="HIDE INSTRUCTIONS")
            del instructions[3]
            instructions.insert(3, True)

    # function triggered when pressing the update button
    # updates the text and widgets on the shelf
    def changeTitle(self):
        new_name = frames[3]
        self.title.config(text=new_name)
        color = shelf_colors[3]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        Frame.configure(self, bg=self.BG_COLOR)
        self.title.config(bg=self.BG_COLOR, fg=self.TITLE_FG)
        self.home.config(bg=self.BUTTON_BG, text=f"{frames[0]}")
        self.items_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Items on {frames[3]}: ")
        self.items.config(fg=self.LABEL_FG)
        self.field.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.grab.config(bg=self.BUTTON_BG)
        self.move_to_shelf.config(bg=self.BUTTON_BG)
        self.update.config(bg=self.BUTTON_BG)
        self.add_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.remove_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.update_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.instructions.config(bg=self.BUTTON_BG)
        self.remove_error.config(bg=self.BG_COLOR)
        self.cur_shelf.config(text=f"Current Shelf: {frames[current_shelf]}", bg=self.BG_COLOR, fg=self.LABEL_FG)

    # function to rotate the shelves to the third shelf
    # triggers when the mvoe to shelf button is activated
    def goToShelfThree(self):
        motor.shelfCall(3)

class Four(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        # initialize color
        color = shelf_colors[4]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        # set frame background
        Frame.configure(self, bg=self.BG_COLOR)
        
        # set fonts
        self.title_font = ("Cooper Black", 20)
        button_font = ("Century Gothic", 12, "bold")
        listbox_font = ("Century Gothic", 10)

        self.title = Label(self, bg=self.BG_COLOR, fg=self.TITLE_FG, text=f"{frames[4]}")
        self.title.grid(row=0, column=0, padx=10, pady=10)
        self.title.config(font=self.title_font)
        
        self.home = Button(self, bg=self.BUTTON_BG, fg="black", text=f"{frames[0]}", command = lambda: controller.showFrame(Home))
        self.home.grid(row=1, column=0, padx=10, pady=10)
        self.home.config(font=button_font)

        self.add_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="add item")
        self.add_label.grid(row=1, column=1, padx=10, pady=10)
        self.add_label.config(font=button_font)

        self.items_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Items on {frames[4]}: ")
        self.items_label.grid(row=0, column=2, padx=10, pady=10)
        self.items_label.config(font=button_font)

        self.items = Listbox(self, fg=self.LABEL_FG)
        self.items.grid(row=1, column=2, rowspan=4, padx=10, pady=10)
        for i in range(len(shelf_four_items.items)):
            self.items.insert(i + 1, shelf_four_items.items[i])
        self.items.config(font=listbox_font)

        self.field = Entry(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.field.grid(row=2, column=1, padx=10, pady=10)
        self.field.config(font=listbox_font)
        self.field.bind("<Return>", lambda event: shelf_four_items.addItem(event, self.field, self.items))

        self.grab = Button(self, bg=self.BUTTON_BG, fg="black", text="REMOVE", command = lambda: shelf_four_items.removeItem(self.items, self.remove_error))
        self.grab.grid(row=5, column=2, padx=10, pady=10)
        self.grab.config(font=button_font)

        # scroll = Scrollbar(self)
        # scroll.grid(row=1, column=2)
        # self.items.config(yscrollcommand=scroll.set)
        # scroll.config(command=self.items.yview)

        self.move_to_shelf = Button(self, bg=self.BUTTON_BG, fg="black", text="Go to Shelf Four", command=lambda: self.goToShelfFour())
        self.move_to_shelf.grid(row=4, column=0, padx=10, pady=10)
        self.move_to_shelf.config(font=button_font)

        self.update = Button(self, bg=self.BUTTON_BG, fg="black", text="UPDATE SCREEN", command=lambda: self.changeTitle())
        self.update.grid(row=5, column=1, padx=10, pady=10)
        self.update.config(font=button_font)

        # label for the entry field that adds items to the shelf
        self.add_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.add_label.grid(row=1, column=1, padx=10, pady=10)
        self.add_label.config(font=listbox_font)

        # instructions for the update label
        self.update_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.update_label.grid(row=6, column=1, padx=10, pady=10)
        self.update_label.config(font=listbox_font)

        # label to explain how to remove items from the shelf
        self.remove_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.remove_label.grid(row=6, column=2, padx=10, pady=10)
        self.remove_label.config(font=listbox_font)

        self.remove_error = Label(self, bg=self.BG_COLOR, fg="red")
        self.remove_error.grid(row=1, column=3, padx=10, pady=10, rowspan=2)
        self.remove_error.config(font=listbox_font)

        # label to show current shelf
        self.cur_shelf = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Current Shelf: {frames[current_shelf]}")
        self.cur_shelf.grid(row=6, column=0, padx=10, pady=10)
        self.cur_shelf.config(font=button_font)

        # button to show or hide insturctions
        self.instructions = Button(self, bg=self.BUTTON_BG, fg="black", command = lambda: self.changeInstructions())
        self.instructions.grid(row=5, column=0, padx=10, pady=10)
        if (instructions[4]):
            self.instructions.config(font=button_font, text="HIDE INSTRUCTIONS")
            self.add_label.config(text="Type in an item\nor scan its barcode.\nPress enter to add\nit to the shelf.")
            self.update_label.config(text="Press update to see\nchanges made in settings.")
            self.remove_label.config(text="Select an item and\npress remove to take it\noff the shelf.")
        else:
            self.instructions.config(font=button_font, text="SHOW INSTRUCTIONS")
            self.update_label.config(text="                 ")
            self.remove_label.config(text="                 ")
            self.add_label.config(text="add to shelf")

    def changeInstructions(self):
        if (instructions[4]):
            self.update_label.config(text="                 ")
            self.add_label.config(text="add to shelf")
            self.remove_label.config(text="                 ")
            self.instructions.config(text="SHOW INSTRUCTIONS")
            del instructions[4]
            instructions.insert(4, False)
        else:
            self.update_label.config(text="Press update to see\nchanges made in settings.")
            self.remove_label.config(text="Select an item and\npress remove to take it\noff the shelf.")
            self.add_label.config(text="Type in an item\nor scan its barcode.\nPress enter to add\nit to the shelf.")
            self.instructions.config(text="HIDE INSTRUCTIONS")
            del instructions[4]
            instructions.insert(4, True)

    def changeTitle(self):
        new_name = frames[4]
        self.title.config(text=new_name)
        color = shelf_colors[4]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        Frame.configure(self, bg=self.BG_COLOR)
        self.title.config(bg=self.BG_COLOR, fg=self.TITLE_FG)
        self.home.config(bg=self.BUTTON_BG, text=f"{frames[0]}")
        self.items_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Items on {frames[4]}: ")
        self.items.config(fg=self.LABEL_FG)
        self.field.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.grab.config(bg=self.BUTTON_BG)
        self.move_to_shelf.config(bg=self.BUTTON_BG)
        self.update.config(bg=self.BUTTON_BG)
        self.add_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.remove_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.update_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.instructions.config(bg=self.BUTTON_BG)
        self.remove_error.config(bg=self.BG_COLOR)
        self.cur_shelf.config(text=f"Current Shelf: {frames[current_shelf]}", bg=self.BG_COLOR, fg=self.LABEL_FG)

    def goToShelfFour(self):
        motor.shelfCall(4)

class Five(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        # initialize color
        color = shelf_colors[5]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        # set frame background
        Frame.configure(self, bg=self.BG_COLOR)
        
        # set fonts
        self.title_font = ("Cooper Black", 20)
        button_font = ("Century Gothic", 12, "bold")
        listbox_font = ("Century Gothic", 10)

        self.title = Label(self, bg=self.BG_COLOR, fg=self.TITLE_FG, text=f"{frames[5]}")
        self.title.grid(row=0, column=0, padx=10, pady=10)
        self.title.config(font=self.title_font)
        
        self.add_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="add item")
        self.add_label.grid(row=1, column=1, padx=10, pady=10)
        self.add_label.config(font=button_font)

        self.home = Button(self, bg=self.BUTTON_BG, fg="black", text=f"{frames[0]}", command = lambda: controller.showFrame(Home))
        self.home.grid(row=1, column=0, padx=10, pady=10)
        self.home.config(font=button_font)

        self.items_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Items on {frames[5]}: ")
        self.items_label.grid(row=0, column=2, padx=10, pady=10)
        self.items_label.config(font=button_font)

        self.items = Listbox(self, fg=self.LABEL_FG)
        self.items.grid(row=1, column=2, rowspan=4, padx=10, pady=10)
        for i in range(len(shelf_five_items.items)):
            self.items.insert(i + 1, shelf_five_items.items[i])
        self.items.config(font=listbox_font)

        self.field = Entry(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.field.grid(row=2, column=1, padx=10, pady=10)
        self.field.config(font=listbox_font)
        self.field.bind("<Return>", lambda event: shelf_five_items.addItem(event, self.field, self.items))

        self.grab = Button(self, bg=self.BUTTON_BG, fg="black", text="REMOVE", command = lambda: shelf_five_items.removeItem(self.items, self.remove_error))
        self.grab.grid(row=5, column=2, padx=10, pady=10)
        self.grab.config(font=button_font)

        # scroll = Scrollbar(self)
        # scroll.grid(row=1, column=2)
        # self.items.config(yscrollcommand=scroll.set)
        # scroll.config(command=self.items.yview)

        self.move_to_shelf = Button(self, fg="black", bg=self.BUTTON_BG, text="Go to Shelf Five", command=lambda: self.goToShelfFive())
        self.move_to_shelf.grid(row=4, column=0, padx=10, pady=10)
        self.move_to_shelf.config(font=button_font)

        self.update = Button(self, bg=self.BUTTON_BG, fg="black", text="UPDATE SCREEN", command=lambda: self.changeTitle())
        self.update.grid(row=5, column=1, padx=10, pady=10)
        self.update.config(font=button_font)

        # label for the entry field that adds items to the shelf
        self.add_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.add_label.grid(row=1, column=1, padx=10, pady=10)
        self.add_label.config(font=listbox_font)

        # instructions for the update label
        self.update_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.update_label.grid(row=6, column=1, padx=10, pady=10)
        self.update_label.config(font=listbox_font)

        # label to explain how to remove items from the shelf
        self.remove_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.remove_label.grid(row=6, column=2, padx=10, pady=10)
        self.remove_label.config(font=listbox_font)

        self.remove_error = Label(self, bg=self.BG_COLOR, fg="red")
        self.remove_error.grid(row=1, column=3, padx=10, pady=10, rowspan=2)
        self.remove_error.config(font=listbox_font)

        # label to show current shelf
        self.cur_shelf = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Current Shelf: {frames[current_shelf]}")
        self.cur_shelf.grid(row=6, column=0, padx=10, pady=10)
        self.cur_shelf.config(font=button_font)

        # button to show or hide insturctions
        self.instructions = Button(self, bg=self.BUTTON_BG, fg="black", command = lambda: self.changeInstructions())
        self.instructions.grid(row=5, column=0, padx=10, pady=10)
        if (instructions[5]):
            self.instructions.config(font=button_font, text="HIDE INSTRUCTIONS")
            self.add_label.config(text="Type in an item\nor scan its barcode.\nPress enter to add\nit to the shelf.")
            self.update_label.config(text="Press update to see\nchanges made in settings.")
            self.remove_label.config(text="Select an item and\npress remove to take it\noff the shelf.")
        else:
            self.instructions.config(font=button_font, text="SHOW INSTRUCTIONS")
            self.update_label.config(text="                 ")
            self.remove_label.config(text="                 ")
            self.add_label.config(text="add to shelf")

    def changeInstructions(self):
        if (instructions[5]):
            self.update_label.config(text="                 ")
            self.add_label.config(text="add to shelf")
            self.remove_label.config(text="                 ")
            self.instructions.config(text="SHOW INSTRUCTIONS")
            del instructions[5]
            instructions.insert(5, False)
        else:
            self.update_label.config(text="Press update to see\nchanges made in settings.")
            self.remove_label.config(text="Select an item and\npress remove to take it\noff the shelf.")
            self.add_label.config(text="Type in an item\nor scan its barcode.\nPress enter to add\nit to the shelf.")
            self.instructions.config(text="HIDE INSTRUCTIONS")
            del instructions[5]
            instructions.insert(5, True)

    def changeTitle(self):
        new_name = frames[5]
        self.title.config(text=new_name)
        color = shelf_colors[5]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        Frame.configure(self, bg=self.BG_COLOR)
        self.title.config(bg=self.BG_COLOR, fg=self.TITLE_FG)
        self.home.config(bg=self.BUTTON_BG, text=f"{frames[0]}")
        self.items_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Items on {frames[5]}: ")
        self.items.config(fg=self.LABEL_FG)
        self.field.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.grab.config(bg=self.BUTTON_BG)
        self.move_to_shelf.config(bg=self.BUTTON_BG)
        self.add_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.update.config(bg=self.BUTTON_BG)
        self.add_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.remove_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.update_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.instructions.config(bg=self.BUTTON_BG)
        self.remove_error.config(bg=self.BG_COLOR)
        self.cur_shelf.config(bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Current Shelf: {frames[current_shelf]}")

    def goToShelfFive(self):
        motor.shelfCall(5)

class Six(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        # initialize color
        color = shelf_colors[6]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        # set frame background
        Frame.configure(self, bg=self.BG_COLOR)
        
        # set fonts
        self.title_font = ("Cooper Black", 20)
        button_font = ("Century Gothic", 12, "bold")
        listbox_font = ("Century Gothic", 10)

        self.title = Label(self, bg=self.BG_COLOR, fg=self.TITLE_FG, text=f"{frames[6]}")
        self.title.grid(row=0, column=0, padx=10, pady=10)
        self.title.config(font=self.title_font)
        
        self.add_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="add item")
        self.add_label.grid(row=1, column=1, padx=10, pady=10)
        self.add_label.config(font=button_font)

        self.home = Button(self, bg=self.BUTTON_BG, fg="black", text=f"{frames[0]}", command = lambda: controller.showFrame(Home))
        self.home.grid(row=1, column=0, padx=10, pady=10)
        self.home.config(font=button_font)

        self.items_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Items on {frames[6]}: ")
        self.items_label.grid(row=0, column=2, padx=10, pady=10)
        self.items_label.config(font=button_font)

        self.items = Listbox(self, fg=self.LABEL_FG)
        self.items.grid(row=1, column=2, rowspan=4, padx=10, pady=10)
        for i in range(len(shelf_six_items.items)):
            self.items.insert(i + 1, shelf_six_items.items[i])
        self.items.config(font=listbox_font)

        self.field = Entry(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.field.grid(row=2, column=1, padx=10, pady=10)
        self.field.config(font=listbox_font)
        self.field.bind("<Return>", lambda event: shelf_six_items.addItem(event, self.field, self.items))

        self.grab = Button(self, fg="black", bg=self.BUTTON_BG, text="REMOVE", command = lambda: shelf_six_items.removeItem(self.items, self.remove_error))
        self.grab.grid(row=5, column=2, padx=10, pady=10)
        self.grab.config(font=button_font)

        # scroll = Scrollbar(self)
        # scroll.grid(row=1, column=2)
        # self.items.config(yscrollcommand=scroll.set)
        # scroll.config(command=self.items.yview)

        self.move_to_shelf = Button(self, fg="black", bg=self.BUTTON_BG, text="Go to Shelf Six", command=lambda: self.goToShelfSix())
        self.move_to_shelf.grid(row=4, column=0, padx=10, pady=10)
        self.move_to_shelf.config(font=button_font)

        self.update = Button(self, bg=self.BUTTON_BG, fg="black", text="UPDATE SCREEN", command=lambda: self.changeTitle())
        self.update.grid(row=5, column=1, padx=10, pady=10)
        self.update.config(font=button_font)

        # label for the entry field that adds items to the shelf
        self.add_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.add_label.grid(row=1, column=1, padx=10, pady=10)
        self.add_label.config(font=listbox_font)

        # instructions for the update label
        self.update_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.update_label.grid(row=6, column=1, padx=10, pady=10)
        self.update_label.config(font=listbox_font)

        # label to explain how to remove items from the shelf
        self.remove_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.remove_label.grid(row=6, column=2, padx=10, pady=10)
        self.remove_label.config(font=listbox_font)

        self.remove_error = Label(self, bg=self.BG_COLOR, fg="red")
        self.remove_error.grid(row=1, column=3, padx=10, pady=10, rowspan=2)
        self.remove_error.config(font=listbox_font)

        # label to show current shelf
        self.cur_shelf = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Current Shelf: {frames[current_shelf]}")
        self.cur_shelf.grid(row=6, column=0, padx=10, pady=10)
        self.cur_shelf.config(font=button_font)

        # button to show or hide insturctions
        self.instructions = Button(self, bg=self.BUTTON_BG, fg="black", command = lambda: self.changeInstructions())
        self.instructions.grid(row=5, column=0, padx=10, pady=10)
        if (instructions[6]):
            self.instructions.config(font=button_font, text="HIDE INSTRUCTIONS")
            self.add_label.config(text="Type in an item\nor scan its barcode.\nPress enter to add\nit to the shelf.")
            self.update_label.config(text="Press update to see\nchanges made in settings.")
            self.remove_label.config(text="Select an item and\npress remove to take it\noff the shelf.")
        else:
            self.instructions.config(font=button_font, text="SHOW INSTRUCTIONS")
            self.update_label.config(text="                 ")
            self.remove_label.config(text="                 ")
            self.add_label.config(text="add to shelf")

    def changeInstructions(self):
        if (instructions[6]):
            self.update_label.config(text="                 ")
            self.add_label.config(text="add to shelf")
            self.remove_label.config(text="                 ")
            self.instructions.config(text="SHOW INSTRUCTIONS")
            del instructions[6]
            instructions.insert(6, False)
        else:
            self.update_label.config(text="Press update to see\nchanges made in settings.")
            self.remove_label.config(text="Select an item and\npress remove to take it\noff the shelf.")
            self.add_label.config(text="Type in an item\nor scan its barcode.\nPress enter to add\nit to the shelf.")
            self.instructions.config(text="HIDE INSTRUCTIONS")
            del instructions[6]
            instructions.insert(6, True)

    def changeTitle(self):
        new_name = frames[6]
        self.title.config(text=new_name)
        color = shelf_colors[6]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        Frame.configure(self, bg=self.BG_COLOR)
        self.title.config(bg=self.BG_COLOR, fg=self.TITLE_FG)
        self.home.config(bg=self.BUTTON_BG, text=f"{frames[0]}")
        self.items_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Items on {frames[6]}: ")
        self.items.config(fg=self.LABEL_FG)
        self.field.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.grab.config(bg=self.BUTTON_BG)
        self.move_to_shelf.config(bg=self.BUTTON_BG)
        self.update.config(bg=self.BUTTON_BG)
        self.add_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.remove_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.update_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.instructions.config(bg=self.BUTTON_BG)
        self.remove_error.config(bg=self.BG_COLOR)
        self.cur_shelf.config(bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Current Shelf: {current_shelf}")

    def goToShelfSix(self):
        motor.shelfCall(6)

class ManageBarcodes(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        # initialize color
        color = shelf_colors[7]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        # set frame background
        Frame.configure(self, bg=self.BG_COLOR)
        
        # set fonts
        self.title_font = ("Cooper Black", 20)
        button_font = ("Century Gothic", 12, "bold")
        listbox_font = ("Century Gothic", 10)

        self.title = Label(self, text=f"{frames[7]}", bg=self.BG_COLOR, fg=self.TITLE_FG)
        self.title.grid(row=0, column=0, padx=10, pady=10)
        self.title.config(font=self.title_font)
        
        self.home = Button(self, text=f"{frames[0]}", bg=self.BUTTON_BG, fg="black", command = lambda: controller.showFrame(Home))
        self.home.grid(row=1, column=0, padx=10, pady=10)
        self.home.config(font=button_font)

        self.items_label = Label(self, bg=self.BG_COLOR, fg=self.TITLE_FG, text=f"Items Saved to Barcodes: ")
        self.items_label.grid(row=0, column=1, padx=10, pady=10)
        self.items_label.config(font=button_font)

        self.items = Listbox(self, fg=self.LABEL_FG)
        self.items.grid(row=1, column=1, rowspan=4, padx=10, pady=10)
        count = 0
        for barcode in barcodes:
            self.items.insert(count + 1, barcodes[barcode])
            count += 1
        self.items.config(font=listbox_font)

        # scroll = Scrollbar(self)
        # scroll.grid(row=2, column=2)
        # self.items.config(yscrollcommand=scroll.set)
        # scroll.config(command=self.items.yview)

        self.field = Entry(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.field.grid(row=3, column=1, padx=10, pady=10)
        self.field.config(font=listbox_font)
        self.field.bind("<Return>", lambda event: self.addItem(self.items, self.field, event))
        self.field.grid_forget()

        self.scan = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="Scan a barcode")
        self.scan.grid(row=2, column=1, padx=10, pady=10)
        self.scan.config(font=listbox_font)
        self.scan.grid_forget()

        self.remove = Button(self, bg=self.BUTTON_BG, text="REMOVE", command = lambda: self.removeItem(self.items))
        self.remove.grid(row=5, column=1, padx=10, pady=10)
        self.remove.config(font=button_font)

        self.item_name = Entry(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.item_name.grid(row=3, column=0, padx=10, pady=10)
        self.item_name.config(font=listbox_font)

        self.name_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.name_label.grid(row=2, column=0, padx=10, pady=10)
        self.name_label.config(font=listbox_font)

        self.button = Button(self, bg=self.BUTTON_BG, text="NAME", command= lambda: self.getItemName(self.item_name))
        self.button.grid(row=4, column=0, padx=10, pady=10)
        self.button.config(font=button_font)

        self.double_barcode = Label(self, bg=self.BG_COLOR, fg="red", text="")
        self.double_barcode.grid(row=5, column=0, padx=10, pady=10)
        self.double_barcode.config(font=listbox_font)

        self.update = Button(self, bg=self.BUTTON_BG, fg="black", text="UPDATE SCREEN", command=lambda: self.changeTitle())
        self.update.grid(row=6, column=0, padx=10, pady=10)
        self.update.config(font=button_font)

        self.update_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.update_label.grid(row=5, column=0, padx=10, pady=10)
        self.update_label.config(font=listbox_font)

        self.remove_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.remove_label.grid(row=6, rowspan=2, column=1, padx=10, pady=10)
        self.remove_label.config(font=listbox_font)

        self.remove_error = Label(self, bg=self.BG_COLOR, fg="red")
        self.remove_error.grid(row=1, column=3, rowspan=3, padx=10, pady=10)
        self.remove_error.config(font=listbox_font)

        # label to show current shelf
        self.cur_shelf = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Current Shelf: {frames[current_shelf]}")
        self.cur_shelf.grid(row=0, column=3, padx=10, pady=10)
        self.cur_shelf.config(font=button_font)

        self.instructions = Button(self, bg=self.BUTTON_BG, fg="black", command=lambda: self.changeInstructions())
        self.instructions.grid(row=7, column=0, padx=10, pady=10)
        if (instructions[7]):
            self.instructions.config(text="HIDE INSTRUCTIONS", font=button_font)
            self.remove_label.config(text="Click on the item you\nwant to remove, then\nclick 'REMOVE' to clear\nthis item from the barcode")
            self.name_label.config(text="What would you like to name this item?\nType in the name and press 'NAME'.")
            self.update_label.config(text="Press 'UPDATE' to refresh colors and titles.")
        else:
            self.instructions.config(text="SHOW INSTRUCTIONS", font=button_font)
            self.remove_label.config(text="             ")
            self.update_label.config(text="")
            self.name_label.config(text="What would you like to name this item?")
    
    def changeInstructions(self):
        if (instructions[7]):
            self.instructions.config(text="SHOW INSTRUCTIONS")
            self.remove_label.config(text="             ")
            self.update_label.config(text="")
            self.name_label.config(text="What would you like to name this item?")
            del instructions[7]
            instructions.insert(7, False)
        else:
            self.instructions.config(text="HIDE INSTRUCTIONS")
            self.remove_label.config(text="Click on the item you\nwant to remove, then\nclick 'REMOVE' to clear\nthis item from the barcode")
            self.name_label.config(text="What would you like to name this item?\nType in the name and press 'NAME'.")
            self.update_label.config(text="Press 'UPDATE' to refresh colors and titles.")
            del instructions[7]
            instructions.insert(7, True)

    def changeColor(self):
        color = shelf_colors[7]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        Frame.configure(self, bg=self.BG_COLOR)
        self.title.config(bg=self.BG_COLOR, fg=self.TITLE_FG, text=f"{frames[7]}")
        self.home.config(bg=self.BUTTON_BG, text=f"{frames[0]}")
        self.items_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.items.config(fg=self.LABEL_FG)
        self.field.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.scan.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.remove.config(bg=self.BUTTON_BG)
        self.item_name.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.name_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.button.config(bg=self.BUTTON_BG)
        self.double_barcode.config(bg=self.BG_COLOR)
        self.update.config(bg=self.button)
        self.remove_error.config(bg=self.BG_COLOR)
        self.update_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.instructions.config(bg=self.BUTTON_BG)
        self.remove_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.cur_shelf.config(bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Current Shelf: {frames[current_shelf]}")

    def getItemName(self, entry):
        self.new_item = entry.get()
        self.scan.grid(row=2, column=2, padx=10, pady=10)
        self.field.grid(row=3, column=2, padx=10, pady=10)
        self.double_barcode.config(text="")
        entry.delete(0, END)

    def addItem(self, listbox, entry, event):
        barcode = entry.get()
        if (barcode in barcodes):
            index = listbox.get(0, "end").index(barcodes[barcode])
            listbox.selection_set(index)
            listbox.see(index)
            self.double_barcode.config(text=f"This barcode is already set as {barcodes[barcode]}.\nTry using another barcode\nor removing {barcodes[barcode]} from the list.")
        else:
            self.scan.grid_forget()
            self.field.grid_forget()
            if (self.new_item is not None):
                barcodes[barcode] = self.new_item.lower()
            listbox.delete(0, END)
            count = 0
            for barcode in barcodes:
                listbox.insert(count + 1, barcodes[barcode])
                count += 1
            self.new_item = None
        entry.delete(0, END)

    def removeItem(self, listbox):
        try:
            item = listbox.get(listbox.curselection()[0])
            keys = list(barcodes.keys())
            names = list(barcodes.values())
            index = names.index(item)
            barcode = keys[index]
            del barcodes[barcode]
            listbox.delete(0, END)
            count = 0
            for barcode in barcodes:
                listbox.insert(count + 1, barcodes[barcode])
                count += 1
            if (item in shelf_one_items.items):
                shelf_one_items.items.remove(item)
            if (item in shelf_two_items.items):
                shelf_two_items.items.remove(item)
            if (item in shelf_three_items.items):
                shelf_three_items.items.remove(item)
            if (item in shelf_four_items.items):
                shelf_four_items.items.remove(item)
            if (item in shelf_five_items.items):
                shelf_five_items.items.remove(item)
            if (item in shelf_six_items.items):
                shelf_six_items.items.remove(item)
            self.remove_error.config(text="")
        except IndexError:
            self.remove_error.config(text="Select an item from\nthe list and try again.")

class Settings(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.controller = controller

        # initialize color
        color = shelf_colors[8]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        # set frame background
        Frame.configure(self, bg=self.BG_COLOR)
        
        # set fonts
        self.title_font = ("Cooper Black", 20)
        button_font = ("Century Gothic", 12, "bold")
        listbox_font = ("Century Gothic", 10)

        self.title = Label(self, text=f"{frames[8]}", bg=self.BG_COLOR, fg=self.TITLE_FG)
        self.title.grid(row=0, column=0, padx=10, pady=10)
        self.title.config(font=self.title_font)
        
        self.home = Button(self, text=f"{frames[0]}", bg=self.BUTTON_BG, fg="black", command = lambda: controller.showFrame(Home))
        self.home.grid(row=1, column=0, padx=10, pady=10)
        self.home.config(font=button_font)

        self.shelf_names = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="Shelf Names")
        self.shelf_names.grid(row=0, column=1, padx=10, pady=10)
        self.shelf_names.config(font=button_font)

        self.shelf_scroll = Listbox(self, fg=self.LABEL_FG)
        self.shelf_scroll.grid(row=1, rowspan=3, column=1, padx=10, pady=10)
        self.shelf_scroll.config(font=listbox_font)
        for i in range(len(frames)):
            self.shelf_scroll.insert(i, frames[i])

        self.edit_name = Button(self, bg=self.BUTTON_BG, fg="black", text="RENAME SHELF", command=lambda: self.editName())
        self.edit_name.grid(row=4, column=1, padx=10, pady=10)
        self.edit_name.config(font=button_font)

        self.shelf_colors = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="Color Themes")
        self.shelf_colors.grid(row=0, column=2, padx=10, pady=10)
        self.shelf_colors.config(font=button_font)

        self.colors_box = Listbox(self, fg=self.LABEL_FG)
        self.colors_box.grid(row=1, column=2, rowspan=3, padx=10, pady=10)
        self.colors_box.config(font=listbox_font)
        colors = list(color_themes.keys())
        for i in range(len(colors)):
            self.colors_box.insert(i, colors[i])

        self.change_color = Button(self, bg=self.BUTTON_BG, fg="black", text="CHANGE A COLOR", command=lambda: self.editColor())
        self.change_color.grid(row=4, column=2, padx=10, pady=10)
        self.change_color.config(font=button_font)

        self.edit_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text="")
        self.edit_label.grid(row=2, column=0, padx=10, pady=10)
        self.edit_label.config(font=listbox_font)
        self.edit_label.bind("<Button-1>", lambda event: self.changeColor(event))

        self.select_shelf = Button(self, bg=self.BUTTON_BG, fg="black", text="SELECT SHELF", command=lambda: self.selectShelf())
        self.select_shelf.config(font=button_font)

        self.select_color = Button(self, bg=self.BUTTON_BG, fg="black", text="SELECT COLOR", command=lambda: self.selectColor())
        self.select_color.config(font=button_font)

        self.edit_field = Entry(self, bg=self.BG_COLOR)
        self.edit_field.config(font=listbox_font)
        self.edit_field.bind("<Return>", lambda event: self.changeTitle(event))

        self.current_shelf = frames[0]

        self.update = Button(self, bg=self.BUTTON_BG, fg="black", text="UPDATE SCREEN", command=lambda: self.changeColor())
        self.update.grid(row=5, column=1, padx=10, pady=10)
        self.update.config(font=button_font)

        # label to show current shelf
        self.cur_shelf = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Current Shelf: {frames[current_shelf]}")
        self.cur_shelf.grid(row=0, column=3, padx=10, pady=10)
        self.cur_shelf.config(font=button_font)

        self.reset_label = Label(self, bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.reset_label.grid(row=2, column=3, padx=10, pady=10)
        self.reset_label.config(font=listbox_font)

        self.reset_button = Button(self, bg=self.BUTTON_BG, fg="black", text="RESET", command=lambda: self.resetCurShelf())
        self.reset_button.grid(row=3, column=3, padx=10, pady=10)
        self.reset_button.config(font=button_font)

        self.current_shelf_button = Button(self, bg=self.BUTTON_BG, fg="black", text="CURRENT SHELF", command=lambda: self.resetCurShelfPart2())
        self.current_shelf_button.grid_forget()
        self.current_shelf_button.config(font=button_font)

        self.instructions = Button(self, bg=self.BUTTON_BG, fg="black", command=lambda: self.changeInstructions())
        self.instructions.grid(row=5, column=0, padx=10, pady=10)
        if (instructions[8]):
            self.instructions.config(text="HIDE\nINSTRUCTIONS", font=button_font)
            self.reset_label.config(text="Click here to reset\nthe current shelf if\nthe labeled current shelf\nis not correct.\nPress update to\nsee the change.")
        else:
            self.instructions.config(text="SHOW\nINSTRUCTIONS", font=button_font)
            self.instructions.config(text="Reset current shelf.")
    
    def resetCurShelf(self):
        self.edit_label.config(text="Select the correct\nshelf from the list,\nthen press 'CURRENT SHELF'")
        self.current_shelf_button.grid(row=4, column=0, padx=10, pady=10)

    def resetCurShelfPart2(self):
        global current_shelf
        new_shelf = self.shelf_scroll.get(self.shelf_scroll.curselection())
        try:
            if (new_shelf not in frames[1:7]):
                self.edit_label.config(text="Select a shelf\nand try again.")
            else:
                self.edit_label.config(text="")
                self.current_shelf_button.grid_forget()
                current_shelf = frames.index(new_shelf)
        except TclError:
            self.edit_label.config(text="Select a shelf\nand try again.")

    def changeInstructions(self):
        if (instructions[8]):
            self.instructions.config(text="SHOW\nINSTRUCTIONS")
            self.reset_label.config(text="Reset current shelf.")
            del instructions[8]
            instructions.insert(8, False)
        else:
            self.instructions.config(text="HIDE\nINSTRUCTIONS")
            self.reset_label.config(text="Click here to reset\nthe current shelf if\nthe labeled current shelf\nis not correct.\nPress update to\nsee the change.")
            del instructions[8]
            instructions.insert(8, True)

    def changeColor(self):
        color = shelf_colors[8]
        self.BG_COLOR = (color_themes[color])[0]
        self.BUTTON_BG = (color_themes[color])[1]
        self.LABEL_FG = (color_themes[color])[2]
        self.TITLE_FG = (color_themes[color])[3]
        Frame.configure(self, bg=self.BG_COLOR)
        self.title.config(text=f"{frames[8]}", bg=self.BG_COLOR, fg=self.TITLE_FG)
        self.home.config(text=f"{frames[0]}", bg=self.BUTTON_BG)
        self.shelf_names.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.shelf_scroll.config(fg=self.LABEL_FG)
        self.edit_name.config(bg=self.BUTTON_BG)
        self.shelf_colors.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.colors_box.config(fg=self.LABEL_FG)
        self.change_color.config(bg=self.BUTTON_BG)
        self.edit_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.select_shelf.config(bg=self.BUTTON_BG)
        self.select_color.config(bg=self.BUTTON_BG)
        self.edit_field.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.update.config(bg=self.BUTTON_BG)
        self.cur_shelf.config(bg=self.BG_COLOR, fg=self.LABEL_FG, text=f"Current Shelf: {frames[current_shelf]}")
        self.reset_label.config(bg=self.BG_COLOR, fg=self.LABEL_FG)
        self.reset_button.config(bg=self.BUTTON_BG)
        self.current_shelf_button.config(bg=self.BUTTON_BG)

        self.current_shelf_button.grid_forget()
        self.select_shelf.grid_forget()
        self.select_color.grid_forget()

    def editName(self):
        if (instructions[8]):
            self.edit_label.config(text="What would you like\nto name this shelf?\n(Select a shelf from the\nlist, type in a name,\nand press enter.)")
        else:
            self.edit_label.config(text="What would you like\nto name this shelf?")
        self.edit_field.grid(row=3, column=0, padx=10, pady=10)

    def editColor(self):
        if (instructions[8]):
            self.edit_label.config(text="Select a shelf,\nthen press 'SELECT SHELF'.")
        else:
            self.edit_label.config(text="Select a shelf.")
        self.select_shelf.grid(row=4, column=0, padx=10, pady=10)

    def selectShelf(self):
        try:
            self.current_shelf = self.shelf_scroll.get(self.shelf_scroll.curselection())
            self.edit_label.config(text=f"What color would you\nlike to make {self.current_shelf}?\nSelect a color from\nthe list then press\n'SELECT COLOR'.")
            self.select_shelf.grid_forget()
            self.select_color.grid(row=4, column=0, padx=10, pady=10)
        except TclError:
            self.edit_label.config(text="Select a shelf and try again.")
        
    def selectColor(self):
        try:
            color = self.colors_box.get(self.colors_box.curselection())
            index = frames.index(self.current_shelf)
            del shelf_colors[index]
            shelf_colors.insert(index, color)
            self.select_color.grid_forget()
            self.edit_label.config(text="")
        except TclError:
            self.edit_label.config(text="Select a color and try again.")

    def changeTitle(self, event):
        new_name = self.edit_field.get()
        self.edit_field.delete(0, END)
        item = self.shelf_scroll.get(self.shelf_scroll.curselection())
        index = frames.index(item)
        frames.remove(frames[index])
        frames.insert(index, new_name)
        self.shelf_scroll.delete(0, END)
        for i in range(len(frames)):
            self.shelf_scroll.insert(i, frames[i])

# constants
# SETTLE_TIME = 2
# CALIBRATIONS = 5

# CALIBRATION_DELAY = 1

# TRIGGER_TIME = 0.00001

# SPEED_OF_SOUND = 343

# pin sets
GPIO.setmode(GPIO.BCM)

# pins
TRIG = 12
ECHO = 20
MOTOR_SIGNAL = 27
DIR_PIN_1 = 26
DIR_PIN_2 = 25

# pin setups
# GPIO.setup(TRIG, GPIO.OUT)
# GPIO.setup(ECHO, GPIO.IN)
GPIO.setwarnings(False)			#disable warnings
GPIO.setup(MOTOR_SIGNAL,GPIO.OUT)
GPIO.setup(DIR_PIN_1, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(DIR_PIN_2, GPIO.OUT, initial = GPIO.LOW)

# sensor = UltraSonic()
# correctionFactor = sensor.calibrate()
motor = Motor()
pi_pwm = GPIO.PWM(MOTOR_SIGNAL, 1000)		#create PWM instance with frequency
pi_pwm.start(0)				#start PWM of required Duty Cycle 

# finDist = sensor.calibrationDistance

# sensor.calibrate()

app = ShelfApp()
app.title("The Shelfinator")
# app.attributes("-fullscreen", True)
app.mainloop()
with open ("pickled_shelf_one.pickle", "wb") as f:
    pickle.dump(shelf_one_items, f)
with open ("pickled_shelf_two.pickle", "wb") as f:
    pickle.dump(shelf_two_items, f)
with open ("pickled_shelf_three.pickle", "wb") as f:
    pickle.dump(shelf_three_items, f)
with open ("pickled_shelf_four.pickle", "wb") as f:
    pickle.dump(shelf_four_items, f)
with open ("pickled_shelf_five.pickle", "wb") as f:
    pickle.dump(shelf_five_items, f)
with open ("pickled_shelf_six.pickle", "wb") as f:
    pickle.dump(shelf_six_items, f)
with open ("barcodes.pickle", "wb") as f:
    pickle.dump(barcodes, f)
with open("frames.pickle", "wb") as f:
    pickle.dump(frames, f)
with open("shelf_colors.pickle", "wb") as f:
    pickle.dump(shelf_colors, f)
with open("instructions.pickle", "wb") as f:
    pickle.dump(instructions, f)
with open("current_shelf.pickle", "wb") as f:
    pickle.dump(current_shelf, f)
# =======

