# Wanderer
Python implementation of the 80's boulders and arrows puzzle game Wanderer.

### Rationale
There's two reasons I wrote this Python version of Wanderer. 
1. I remember Wanderer as one of the most intriguing puzzle games of it's time. 
However it took me some Googling to find the actual name of the game.
2. As a test project to test my [GridWorld](https://github.com/hpharmsen/gridworld) array based grid module.

### Installation

### Dependencies
As mentioned Wanderer uses my my [GridWorld](https://github.com/hpharmsen/gridworld) array based grid module which in turn depends on Pygame.

```bash
pip3 install pygame
pip3 install git+https://github.com/hpharmsen/gridworld
```

Furthermore you need **Python 3.6**.\
Older versions do not work (but why should you?) because I use Python3.6's invaluable fstrings.\
Newer versions (as of now 3.7 is the only newer stable release) do not work with Pygame!

### How to play
**arrow keys** to move the hero trough the field.\
**space** to proceed without moving.\
**F** to switch to full screen mode which is usually a lot faster in Pygame.\
**S** to save current level progress.\
**L** to load your saved level progress.\
**R** to restart the level.\
**Q** to quit the game.

#### Objects
**Granite** and **Bricks** are impenetrable.\
**Earth** is though.\
**Bombs** will instantly kill you.\
**Boulders** will fall if you get near. Beware, falling boulders are lethal.\
**Arrows** are like boulders but horizontally.\
**Baloons** act likewise but up and they are not lethal.\
**Money bags** can be collected. As soon as you collected them all the **exit (X)** is available.\
**The transporter (T)** will bring you to it's **Arrival point (A)**.\
**Deflectors (/ and \\)** make boulders and arrows move sideways.\
Finaly there's **monsters** wich will chase you and **baby monsters** which will only kill you but do not chase. 

You can always choose to play another level just by clicking it's number in the right top.

### Credits
Wanderer was written by Steven Shipway in the 1980's. 
See The [original credits](https://csijh.github.io/wanderer/javascript/credits.html). 

Ian Holyer wrote a [Java version](https://csijh.github.io/wanderer/) in October 2011 
and an [online playable version](https://csijh.github.io/wanderer/javascript/index.html) 
in Javascript which helped me a lot getting the flow of events right\
Plus I borrowed his version of the level files.