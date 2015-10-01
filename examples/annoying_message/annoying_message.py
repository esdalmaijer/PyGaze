# Display a message on your display until space is pressed
import random
from pygaze.defaults import DISPSIZE
from pygaze.libinput import Keyboard
from pygaze.libscreen import Display, Screen


MESSAGE = "AFK; BRB"


disp = Display()
scr = Screen()
kb = Keyboard(keylist=['space'], timeout=1)


while not kb.get_key()[0]:
    col = (random.randint(0, 255), random.randint(0, 255),
           random.randint(0, 255))

    pos = (random.randint(0, DISPSIZE[0]), random.randint(0, DISPSIZE[1]))

    scr.draw_text(text=MESSAGE, colour=col, pos=pos, fontsize=84)

    disp.fill(scr)
    disp.show()

    scr.clear()

disp.close()
