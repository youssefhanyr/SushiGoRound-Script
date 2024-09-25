from logging import debug, basicConfig, INFO, info, critical
from time import sleep, time
from os.path import join, abspath, dirname
from os import getcwd, chdir
import pyautogui
import pyscreeze

basicConfig(level=INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

COOKBOOK = {'onigiri':'210000', 'califonia_roll':'111000', 'gunmaki':'112000', 'sushi':'110020', 'shrimpushi': '110200', 'unagshi':'110002', 'dragon_roll':'211002'\
            , 'combo':'211111'}                                   
# order of ingredients will be the following, rice, nori, feggs, shrimps, salmon, unagi
DUR = 0.15


def getregion_coords():             #Full screen game coords 1365 x 1020, windowed mode does not work or just find the play button instead
    region = None                       #multiply any normal dist by 1365/640 with x and 1020/480
    while True:
        try:
            region = pyautogui.locateCenterOnScreen(getpath('play_button.png'), minSearchTime=30, confidence=0.8)
            if region is not None:
                break
        except (pyautogui.ImageNotFoundException, pyscreeze.ImageNotFoundException):
            info('Did not find the game frame, is the window not open or are you not on fullscreen?')
    return region



def getcurrent_orders(xo: int) -> tuple:       # returns the food ordered and when it was ordered for each seat
    foodlist = {f'seat{i}':None for i in range(1, 7)}
    timelist = {f'seat{i}':None for i in range(1, 7)}
    info('Reaciving orders... ')
    for order in ['onigiri.png', 'califonia_roll.png', 'gunmaki.png', 'sushi.png', 'shrimpushi.png', 'unagshi.png', 'dragon_roll.png'\
                  , 'combo.png']:
        try:
            fooditems = [pyautogui.center(item) for item in list(pyscreeze.locateAllOnScreen(getpath(order), confidence=0.9))]               # It returns two instances of the same seat, fix later
            debug(f'{order} was detected')
            for food in fooditems:
                foodlist[getseat(food[0], xo)] = order
                timelist[getseat(food[0], xo)] = round(time(), 2)           # round it to avoid mistaking the same order to two different others
                debug(f'{order} was found at {getseat(food[0], xo)}')
        except (pyautogui.ImageNotFoundException, pyscreeze.ImageNotFoundException):
            debug(f'{order} was not found..')
    debug('Displaying recieved orders...')
    debug(f'{foodlist} \n {timelist}')
    return foodlist, timelist


def getseat(x: int, xo: int) -> str:        # returns the seat according to postion
    debug(f'{x} was recieved')
    if 60 <= x - xo <= 80:
        return 'seat1'
    elif 190 <= x - xo <= 210:
        return 'seat2'
    elif 290 <= x - xo <= 350:
        return 'seat3'
    elif 440 <= x - xo <= 480:
        return 'seat4'
    elif 560 <= x - xo <= 610:
        return 'seat5'
    else:
        return 'seat6'

def getpath(Picname: str) -> str:
    """
    This returns a path to the image name provided

    :param Picname: The picture's name, must be in the folder
    :return: a path to the image name provided.
    """
    return join(join(getcwd(), 'pictrigger'), Picname)


class Kitchenbot:

    def __init__(self) -> None:                        # making one for lacking and another for unavailabilty is so we call ahead when its low, it then gets marked
        region = getregion_coords()                    # as lacking to prevent stopping cooking and calling again, and unavailable, when ingred is low it cant
        self.didcall = False                           # cant be used to make most dishes
        self.gamecoords = (round(region[0] - 640/1.57), round(region[1] - 480/1.87), 640, 480)
        print(f"{self.gamecoords[0]}, {self.gamecoords[1]}")
        self.inventory = {'shrimp': 5, 'rice': 10, 'nori': 10, 'feggs': 10, 'salmon': 5, 'unagi': 5}
        self.seatordersplate = {'seat1': None, 'seat2': None, 'seat3': None, 'seat4': None, 'seat5': None, 'seat6': None}
        self.seatorderstime = {'seat1': None, 'seat2': None, 'seat3': None, 'seat4': None, 'seat5': None, 'seat6': None}
        self.seatskipped = {'seat1': False, 'seat2': False, 'seat3': False, 'seat4': False, 'seat5': False, 'seat6': False}
        self.prevseatordersplate = {'seat1': None, 'seat2': None, 'seat3': None, 'seat4': None, 'seat5': None, 'seat6': None}
        self.ingred_lacking = {'shrimp': False, 'rice': False, 'nori': False, 'feggs': False, 'salmon': False, 'unagi': False}
        self.ingred_unavilable = {'shrimp': False, 'rice': False, 'nori': False, 'feggs': False, 'salmon': False, 'unagi': False}
        self.ingred_calltime = {'shrimp': 0.0, 'rice': 0.0, 'nori': 0.0, 'feggs': 0.0, 'salmon': 0.0, 'unagi': 0.0}
        pyautogui.click(self.gamecoords[0] + 408, self.gamecoords[1] + 258, duration=DUR)
        pyautogui.click(self.gamecoords[0] + 410, self.gamecoords[1] + 509, duration=DUR)
        pyautogui.click(self.gamecoords[0] + 740, self.gamecoords[1] + 573, duration=DUR)
        pyautogui.click(self.gamecoords[0] + 410, self.gamecoords[1] + 509, duration=DUR)      # now the real game has begun

    def recieve_orders(self, foodlist: dict, timelist: dict) -> None:
        """
        Compared time of orders recieved and ignores repeats,
        removes old orders and adds the new regardless if they are None or not
        """
        debug(f'Showing orders before update, {self.seatordersplate} \n {self.seatorderstime} \n {self.seatskipped}')
        info('Comparing recevied orders..')
        for seat in [f'seat{i}' for i in range(1, 7)]:
            plate_travel_time = 3.5*(int(seat[-1]) - 1) if int(seat[-1]) > 1 else 0 # plate travelling time for seats 2,3,..
            debug(f"Plate travel time is {plate_travel_time}..")
                    
            if self.seatorderstime[seat] is None:
                self.seatorderstime[seat] = round(time(), 2)
                        
            if (round(time(), 2) - self.seatorderstime[seat] > 5 + 5 + plate_travel_time + 0.5 and foodlist[seat] == self.prevseatordersplate[seat] \
                and self.prevseatordersplate[seat] is not None) or (self.seatskipped[seat] and foodlist[seat] is not None):
                            # 5 sec to reach the first seat, 5 (with dishes with 4 pieces its more) eating animation, and 0.5 to account for lost time(est)
                self.seatordersplate[seat] = foodlist[seat]
                self.seatorderstime[seat] = timelist[seat]
                debug(f'Added {foodlist[seat]} to the foodlist because it has been left over.. ')
                            
            elif self.seatordersplate[seat] != foodlist[seat] and self.prevseatordersplate[seat] != foodlist[seat]:       # takes a new order if its different
                debug(f'Changed {seat} order from {self.seatordersplate[seat]} to {foodlist[seat]}')
                self.seatordersplate[seat] = foodlist[seat]
                self.seatorderstime[seat] = timelist[seat]
                self.prevseatordersplate[seat] = self.seatordersplate[seat]
                        
            else:
                self.seatordersplate[seat] = None
                debug('Recieved same order, nullifing...')
                        
        debug(f'Showing orders after update {self.seatordersplate} \n {self.seatorderstime} \n {self.seatskipped}')
        info('Starting cooking each plate..')
                
        for seat in [f'seat{i}' for i in range(1, 7)]:
            if self.seatordersplate[seat] is not None:
                info(f'Cooking {self.seatordersplate[seat]}')
                self.cook_plate(self.seatordersplate[seat][:-4], seat)

    def collect_plates(self) -> None:
        """
        Call this to click on all the plates present or not
        """
        info('Collecting plates...')
        for i in range(6):
            pyautogui.click(self.gamecoords[0] + 106 + i*130, self.gamecoords[1] + 262, duration=0.1)         # forget the duration we want to call this func a lot
        return                                                                                  # dont want it to take much time so we can get on with it

    def cook_plate(self, plate: str, seat: str) -> None:
        ingreds = ('rice', 'nori', 'feggs', 'shrimp', 'salmon', 'unagi')
        recipe = COOKBOOK[plate]

        for ing_number in range(6):
            intingrd_number = int(recipe[ing_number])
            if intingrd_number != 0:
                if self.ingred_unavilable[ingreds[ing_number]]:
                    info(f'{ingreds[ing_number]} is currently unavailable, skipping doing {plate}.. ')
                    self.seatskipped[seat] = True           # this dict is to make seats skipped due to lack of ingrd get taken instantlly when they arrive
                    self.checkandcall()                  
                    return
        
        for ing_number in range(6):
            intingrd_number = int(recipe[ing_number])
            if intingrd_number != 0:
                for _ in range(intingrd_number):            # The clicking field
                            
                    if ingreds[ing_number] == 'rice':
                        pyautogui.click(self.gamecoords[0] + 120, self.gamecoords[1] + 417, duration=DUR)
                        debug('Clicked on rice..')
                    elif ingreds[ing_number] == 'nori':
                        pyautogui.click(self.gamecoords[0] + 50, self.gamecoords[1] + 486, duration=DUR)
                        debug('Clicked on nori..')
                    elif ingreds[ing_number] == 'feggs':
                        pyautogui.click(self.gamecoords[0] + 120, self.gamecoords[1] + 482, duration=DUR)
                        debug('Clicked on feggs..')
                    elif ingreds[ing_number] == 'shrimp':
                        pyautogui.click(self.gamecoords[0] + 49, self.gamecoords[1] + 412, duration=DUR)
                        debug('Clicked on shrimp..')
                    elif ingreds[ing_number] == 'salmon':
                        pyautogui.click(self.gamecoords[0] + 48, self.gamecoords[1] + 550, duration=DUR)
                        debug('Clicked on salmon..')
                    elif ingreds[ing_number] == 'unagi':
                        pyautogui.click(self.gamecoords[0] + 121, self.gamecoords[1] + 552, duration=DUR)
                        debug('Clicked on unagi..')
                    self.inventory[ingreds[ing_number]] -= 1
            else:
                continue
        debug('sleeping before clicking on the mat..')            # to try to prevent overclocking the belts from occuring
        sleep(0.6)
        pyautogui.click(self.gamecoords[0] + 259, self.gamecoords[1] + 488, duration=DUR)
        info(f'Clicked on the mat, {plate} is done..')
        debug('wait for mat animation..')
        sleep(0.8)                        # didn't measure the anim time, this is an est
        self.seatordersplate[seat] = None
        self.seatskipped[seat] = False
        self.checkandcall()

    def checkandcall(self):
        """
        Checks the status for all ingrediants, will call at the following situations:\n\n
        Rice, Nori, Fish eggs: if it is lower or equals to 3, call

        Shrimp, Salmon, Unagi: if it is lower or equals to 2, call
        """
        for ingred, amount in self.inventory.items():
            info(f'Checking the state of {ingred}, current amount is {amount}...')
            if ingred in ('rice', 'nori', 'feggs'):                        # The ones that arrive in tens
                        
                if amount <= 2 and not self.ingred_lacking[ingred]:            # not lacking as in didnt call already
                            
                    info(f'Calling for {ingred}..')
                    self.call(ingred)
                elif amount < 2 and self.ingred_lacking[ingred]:
                    self.ingred_unavilable[ingred] = True
                    debug(f"{ingred} is already called for, marking unavailable...")
                else:
                    debug(f'{ingred} is good..')
                            
            elif ingred in ('shrimp', 'salmon', 'unagi'):            # The ones that arrive in fives
                        
                if amount <= 2 and not self.ingred_lacking[ingred]:
                    info(f'Calling for {ingred}..')
                    self.call(ingred)
                elif amount < 2 and self.ingred_lacking[ingred]:
                    self.ingred_unavilable[ingred] = True
                    debug(f"{ingred} is already called for, marking unavailable...")
                else:
                    debug(f'{ingred} is good..')
        pass

    def update_inv(self, mode: bool) -> None:
        """
        Updates the inventory and checks how has it been since the last call

        :param mode: If it is false, then resets inv, else checks when was the last call made.
        """
        debug(f'Current inventory: {self.inventory}')
        if not mode:
                    
            info('Resting inventory and seats...')
            self.inventory = {'shrimp': 5, 'rice': 10, 'nori': 10, 'feggs': 10, 'salmon': 5, 'unagi': 5}
            self.seatordersplate = {'seat1': None, 'seat2': None, 'seat3': None, 'seat4': None, 'seat5': None, 'seat6': None}
            self.seatorderstime = {'seat1': None, 'seat2': None, 'seat3': None, 'seat4': None, 'seat5': None, 'seat6': None}
            self.ingred_lacking = {'shrimp': False, 'rice': False, 'nori': False, 'feggs': False, 'salmon': False, 'unagi': False}
            self.ingred_unavilable = {'shrimp': False, 'rice': False, 'nori': False, 'feggs': False, 'salmon': False, 'unagi': False}
            self.seatskipped = {'seat1': False, 'seat2': False, 'seat3': False, 'seat4': False, 'seat5': False, 'seat6': False}
                    
        else:
                    
            for ingred, amount in self.inventory.items():
                        
                if amount < 0:
                    critical(f'Shit just hit the fan, {ingred} is currently at the count: {amount}') # while this is bad, its not game-ending, as this means
                elif amount == 0:                                                                    # next time it calls for ingred, it will call it earlier
                    info(f'{ingred} has run out, disabling all dishes that needs it.. ')             # and besides, it will get reseted after a win
                    self.ingred_unavilable[ingred] = True
                            
            info('Checking if any ingredients arrived..')
            for ingred, status in self.ingred_lacking.items():
                if status and time() - self.ingred_calltime[ingred] >= 7:
                            
                    if ingred in ('shrimp', 'unagi', 'salmon'):
                        self.inventory[ingred] += 5
                        info(f'{ingred} arrived, increased it by 5')
                        self.ingred_lacking[ingred] = False
                        self.ingred_unavilable[ingred] = False
                        self.didcall = False
                                
                    else:
                        self.inventory[ingred] += 10
                        info(f'{ingred} arrived, increased it by 10')
                        self.ingred_lacking[ingred] = False
                        self.ingred_unavilable[ingred] = False
                        self.didcall = False
                                
        debug(f'Updated inventory: {self.inventory}')
                        
    def call(self, ingred: str) -> None:
        pyautogui.click(self.gamecoords[0] + 738, self.gamecoords[1] + 460)             # clicked on the phone
        toppings = ('shrimp', 'salmon', 'unagi', 'nori', 'feggs')                        # each button for ingred on the phone menu is ordered accordingly
        toppings_coords = ((626, 284), (627, 426), (730, 284), (627, 353), (731, 352))

        if ingred in toppings:
            info(f'Calling for {ingred}..')
            pyautogui.click(self.gamecoords[0] + 691, self.gamecoords[1] + 346, duration=DUR)
            """Had a huge deal with the module not detecting the unafford picture, it would give false pstvs no matter how much I fiddled so I 
            made it find the afford one instead"""
            try:
                pyautogui.locateCenterOnScreen(getpath(f'{ingred}_afford.png'), minSearchTime=0.8, grayscale=False, region=(self.gamecoords[0] + 575, self.gamecoords[1] + 223, 210, 240))
                pyautogui.click(self.gamecoords[0] + toppings_coords[toppings.index(ingred)][0], self.gamecoords[1] + toppings_coords[toppings.index(ingred)][1])
                pyautogui.click(self.gamecoords[0] + 628, self.gamecoords[1] + 375, duration=DUR)
                info(f'Called for {ingred}...')
                self.ingred_lacking[ingred] = True
                self.ingred_calltime[ingred] = round(time(), 2)
                self.didcall = True
                return
            
            except (pyautogui.ImageNotFoundException, pyscreeze.ImageNotFoundException):
                        
                self.ingred_unavilable[ingred] = True
                info(f'Can\'t afford {ingred}, marking it unavailable..')
                pyautogui.click(self.gamecoords[0] + 749, self.gamecoords[1] + 436, duration=DUR)
                return

        elif ingred == 'rice':
            info(f'Calling for rice..')
            pyautogui.click(self.gamecoords[0] + 693, self.gamecoords[1] + 372, duration=DUR)
                    
            try:
                pyautogui.locateCenterOnScreen(getpath(f'rice_afford.png'), grayscale=False, region=(self.gamecoords[0] + 575, self.gamecoords[1] + 223, 210, 240), minSearchTime=0.8)
                pyautogui.click(self.gamecoords[0] + 692, self.gamecoords[1] + 359, duration=DUR)
                pyautogui.click(self.gamecoords[0] + 628, self.gamecoords[1] + 375, duration=DUR)
                self.ingred_lacking[ingred] = True
                self.ingred_calltime[ingred] = round(time(), 2)
                info(f'Called for {ingred}...')
                self.didcall = True
                return
                        
            except (pyautogui.ImageNotFoundException, pyscreeze.ImageNotFoundException):

                self.ingred_unavilable[ingred] = True
                info('Can\'t afford rice, marking it unavailable..')
                pyautogui.click(self.gamecoords[0] + 749, self.gamecoords[1] + 436, duration=DUR)
                return
    
    def collect_shit(self):
        """Collects shit plates made by making wrong recipes, this is to prevent overclogging the belts and making more mistakes"""
        shit_region = (self.gamecoords[0] + 436, self.gamecoords[1] +393, 60, 211)
        info('Looking for shit plates..')
        while True:
                    
            try:
                coords = list(pyautogui.locateAllOnScreen(getpath('shit.png'), grayscale=False, confidence=0.9, \
                                                        region=shit_region))
                info('Found shit plates...')
                for plate in coords:
                            
                    xandy_coords = pyautogui.center(plate)
                    pyautogui.click(xandy_coords[0], xandy_coords[1])
                    debug(f'Clicked on {xandy_coords[0]} , {xandy_coords[1]}')
                            
            except (pyautogui.ImageNotFoundException, pyscreeze.ImageNotFoundException):
                info('Didn\'t find any, returning.. ')
                return


def regentcheck(kitchen: Kitchenbot) -> None:
    """
    I forgot what was this supposed to do
    i remembered, it was supposed to check if any moves are possible and if we broke
    so it doesn't keep looping when it has nothing to do

    UPDATE: made this obsolete, its pretty much useless since in all the times i ran the script it has never needed to go into such state
    """
    unavailable_sum = 0
    if kitchen.didcall:
        for status in kitchen.ingred_unavilable.values():
            unavailable_sum += int(status)
            if unavailable_sum > 3:
                info(f'Too many ingredients unavailable, resting for a while.')
                sleep(7 - time() + min(kitchen.ingred_calltime.values()))
                return
        return


def checkgameend(kitchen: Kitchenbot) -> None:
    """
    Checks if the game has ended, and proceeds if it has..
    To do: Change the approach, let it first find a continue button then find the you win or try again then find the you lost
    so we lose the least amount of time during playtime

    """
    try:
        check = pyautogui.locateOnScreen(getpath('contiune_button.png'), minSearchTime=1, confidence=0.9)
        info('Found a continue, checking if we won..')
        try:
            pyautogui.locateOnScreen(getpath('youwin.png'), minSearchTime=1, confidence=0.9)
            debug('found a win screen..')
            pyautogui.click(kitchen.gamecoords[0] + 410, kitchen.gamecoords[1] + 476, duration=DUR)
            pyautogui.click(kitchen.gamecoords[0] + 410, kitchen.gamecoords[1] + 476, duration=DUR)
            kitchen.update_inv(False)
        except(pyautogui.ImageNotFoundException, pyscreeze.ImageNotFoundException):
            try:
                pyautogui.locateOnScreen(getpath('todaysgoal.png'), minSearchTime=1, confidence=0.9)
                info('Found a todaysgoal, moving on..')
                pyautogui.click(kitchen.gamecoords[0] + 410, kitchen.gamecoords[1] + 476, duration=DUR)
            except(pyautogui.ImageNotFoundException, pyscreeze.ImageNotFoundException):
                info('We fokin lost mate, sleeping to cry..')
                sleep(10000)
    except(pyautogui.ImageNotFoundException, pyscreeze.ImageNotFoundException):
        info('Didn\'t find any screen, win or loss, moving on..')
    

if __name__ == '__main__':
    print('Sushi go round script\n made by youssefhanyr \n \n \n CURRENTLY ON STANDBY, MAKE SURE THE GAME')
    print('IS PRESENT IN THE BROWSER WINDOW AND NOT ON FULLSCREEN, INPUT ANYTHING TO PROCEED')
    input('')
    print('Will start locating the game..')
    cur_scriptdir = dirname(abspath(__file__))
    chdir(cur_scriptdir)

    kit = Kitchenbot()
    while True:
        d1, d2 = getcurrent_orders(kit.gamecoords[0])
        kit.recieve_orders(d1, d2)
        kit.collect_plates()
        kit.update_inv(True)
        kit.collect_shit()
#        regentcheck(kit)
        checkgameend(kit)

    

