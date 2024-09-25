# **Sushi Go Round Python Script**

This script mainly depends on the module pyautogui to detect images and automate the clicking.
I came to know about it in [Automate the Boring Stuff with Python](https://automatetheboringstuff.com/), by Al Sweigart, in the last chapter where he explained how it worked, and spoke about making a script
such as this for a game, and took this game as an example, it was then I set out to try my luck in making one.
<br><br><br>
### Quick detour to the general process of the script

![](https://inventwithpython.com/blogstatic/sushigoroundcoordinates2.png?27f655)
<br>
*Taken from [Programming a Bot to Play the "Sushi Go Round" Flash Game](https://inventwithpython.com/blog/2014/12/17/programming-a-bot-to-play-the-sushi-go-round-flash-game/)*

It starts by locating the play button, there's a thing about this module, when it finds an image, it returns a Box, which contains a tuple containing the coords
in a certain order: (Top left pixel X, Top left pixel Y, width, height), and not in a rectangular tuple which contains bottom left and top right coords.
we want to find the top left corner of the game, so we subtract the top left x by the width of the game (as long you are not in fullscreen it will always be the same size) divided by an estimated ratio I choose which represents the width of the screen to it before the play button (i think I don't really remember that well but that was the jest of it), After which we start the game clicking at distances from the origin point of the game that are manually calculated.

It starts by calling an external function to find all the orders currently and gives them to kitchen bot / main class, and it calls the receive orders method
to process them by doing the following:

- if its a brand new order different from the last one it had, take it in
- else if it is the same as the last one it had (it stores it in a dict) and 5 seconds (for the plate to reach the first seat) + 5 sec (its longer for some dishes) + 3*(seatnumber -  1 ) if its any seat other the first to account for the distance it travels, take it (it works in the sense of if i made it then it went all the way to the last guy before the guy I made the dish for originally, then surely it didn't reach him yet)
- if its not any of those, then it must be a repeat I just made, null it so we dont make it again.

it then cooks the plates, after checking if any of the ingredients are unavailable, which happens when it calls to check on ingredients if it called for one and it is marked as lacking (called for) then sees if enough time has passed (time is that of the normal delivery, the fast one is not used), it calls ahead of time when it is falling low and when it is lower than to be used for most dishes it is marked it as unavailable, which makes any dishes that need said ingred skipped, which triggers the skipped seat in the dict, which makes it the next time it checks the ingred to take it in (assuming the order is still there and the guy didn't leave) immediately, this function has a bool that allows it to act as a rester after the level ends in a win.

then it tries to find any shit plates, which are made when you cook something wrong, now I don't like having something like preparing for failing, i kinda hoped i would make something makes as few mistakes as it can but it is not like that (it makes other mistakes such as making unneeded dishes for people who have left, I call this wasting, not easy to avoid what so all), so instead of trying to do so we lessen the bleed as much as I can, it finds any plates in the clickable region for them (they are only clickable near the mat where you send off the dishes) and moves on, no need to keep looking as it will be called again soon enough.

after all of this, it checks for a win screen or a loss screen, if it wins it will proceed and reset its inventory, if it loses it will afk.

(Keep in mind anyone who will try it, that its not perfect as i said, sometimes with some bad RNG, it will keep making orders for further seats that gets taken by others who pop up and take it before it reaches the original orderer, making him wait the entire duration before he gets picked up again if this happens a lot or at the end of the day more than once it's GG).

Video of it beating the game: https://drive.google.com/file/d/128E8eqzv6BMw9rDnEfO8pAhu9lP-7VyH/view?usp=drive_link
High score was 31620, which is under the one the author of the game made by a bit, but I'm proud of it nonetheless. 
