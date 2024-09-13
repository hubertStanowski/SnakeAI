# SnakeAI
Pure python implementation of NEAT algorithm for Snake game. (graphics in pygame).

**TODO embed video**

> [!WARNING]
> Due to random nature of this algorithm, it is possible there are bugs that I haven't encountered

# Downloading and running
### Clone this repository
    git clone https://github.com/hubertStanowski/SnakeAI.git

### Go to its directory
    cd SnakeAI

### Install packages (pygame)
    pip install -r requirements.txt

### Run the program
    python main.py
  
# Usage
### Default settings
You can modify these settings in user_config.py file **TODO**

- Population size = 100
- Human playing = False

### Simulating generations
- You can choose the generation you want to simulate by **clicking (LMB)** on a button
- If you choose "BEST" option it will simulate the player that got the best score ever (may not necessarily perform the best in all situations)
- If the chosen generation has not been reached, it will be simulated as soon as evolution reaches it
- If you want to simulate the most recently evolved generation press **ENTER (RETURN)** button
### Resetting
- If you want to reset the population press **BACKSPACE** or **DELETE** button.
### Game speed (FPS)
- You can speed up the game by pressing **PLUS** button
- You can slow down the game by pressing **MINUS** button
- This will cycle throught three available speed options
### Additional information
- You can pause the simulation by pressing **SPACE** button, to unpause press **SPACE** again
# Resources
- **TODO** https://youtu.be/0mKHcnQlVi0 - my demo video on YouTube (same as embedded above)
 
## NEAT
- https://neat-python.readthedocs.io/en/latest/neat_overview.html - overview

- https://www.youtube.com/watch?v=yVtdp1kF0I4 - great visual explanation

- https://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf - original paper

- https://stackoverflow.com/questions/45463821/neat-what-is-a-good-compatability-threshold - compatibility threshold help

## Graphics
- https://www.youtube.com/watch?v=lAjcH-hCusg&t=346s - graphics inspiration
