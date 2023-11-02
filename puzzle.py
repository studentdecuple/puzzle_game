import math
import random
import time
from threading import Thread
from tkinter import *
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk



class Puzzle:

    grid: list[list[int]] = []
    btn_list: list[list[tuple[int, Button]]] = []
    root: Tk = None
    puzzle_frame: Frame = None
    started_at: int = None
    


    def __init__(self):
        self.started_at = math.floor(time.time())

        self.initialize_interface()
        self.load_image()
        self.initialize_puzzle_frame()
        self.initialize_puzzle_grid()
        self.initialize_timer()
        self.update_puzzle_image()
        self.root.mainloop()

    
    def initialize_interface(self):
        self.root = Tk()
        self.puzzle_frame = Frame(self.root)
        self.puzzle_frame.pack()


    # Loads the puzzle image.
    def load_image(self):
        image_name = IMAGE_FILE
        image = Image.open(image_name)
        self.image = image
        
        img_w, img_h = image.size
        cnt_w, cnt_h = GRID_COUNT

        self.grid_size = (
            math.floor(img_w / cnt_w), math.floor(img_h / cnt_h)
        )

    
    # Creates and places the puzzle buttons.
    def initialize_puzzle_frame(self):
        cnt_w, cnt_h = GRID_COUNT
        grid_w, grid_h = self.grid_size

        idx = 0
        for y in range(0, cnt_h):
            self.btn_list.append([])
            for x in range(0, cnt_w):
                piece = Button(self.puzzle_frame, highlightthickness=0,
                               width=grid_w, height=grid_h, 
                               command=lambda idx = idx: self.on_piece_click(idx))
                piece.grid(column=x, row=y)
                self.btn_list[y].append(piece)
                idx += 1

    
    # Shuffle the puzzle pieces.
    def initialize_puzzle_grid(self):
        cnt_w, cnt_h = GRID_COUNT
        piece_list = []
        
        for i in range(0, cnt_w * cnt_h - 1):
            piece_list.append(i)
        random.shuffle(piece_list)
        piece_list.append(None)

        for i in range(0, cnt_w * cnt_h):
            piece_item = piece_list[i]
            y = math.floor(i / cnt_w)

            if (len(self.grid) <= y):
                self.grid.append([])
            self.grid[y].append(piece_item)

    
    # Show the puzzle.
    def update_puzzle_image(self):
        grid_w, grid_h = self.grid_size
        cnt_w, cnt_h = GRID_COUNT

        for y in range(0, cnt_h):
            for x in range(0, cnt_w):
                idx, piece = self.grid[y][x], self.btn_list[y][x]
            
                piece_image = None
                if (idx == None): # If is current space empty
                    piece_image = Image.new("RGB", (grid_w, grid_h), (255, 255, 0))
                    piece_image = ImageTk.PhotoImage(piece_image)
                else: # If is current space not empty
                    og_x, og_y = idx % cnt_w, math.floor(idx / cnt_w)
                    sx, sy = og_x * grid_w, og_y * grid_h
                    piece_image = self.image.crop((sx, sy, sx + grid_w, sy + grid_h))
                    piece_image = ImageTk.PhotoImage(piece_image)

                piece.configure(image = piece_image, width = grid_w, height = grid_h)
                piece.image = piece_image


    # Piece swapper.
    def swap_piece(self, from_idx: tuple, to_idx: tuple):
        fx, fy = from_idx
        tx, ty = to_idx

        temp = self.grid[fy][fx]
        self.grid[fy][fx] = self.grid[ty][tx]
        self.grid[ty][tx] = temp

        self.update_puzzle_image()
        self.check_game_over()

    
    # Handles the click event of the puzzle piece.
    def on_piece_click(self, btn_idx: int):
        cnt_x, cnt_y = GRID_COUNT
        bx = btn_idx % cnt_x
        by = math.floor(btn_idx / cnt_y)
        grid = self.grid

        if (grid[by][bx] == None):
            return # Ignore
        
        # Find empty space
        tx, ty = None, None

        for (x, y) in [(bx, by - 1), (bx, by + 1), (bx - 1, by), (bx + 1, by)]:
            try:
                if (x < 0 or y < 0):
                    continue
                if (grid[y][x] == None):
                    tx, ty = x, y
                    break
            except IndexError:
                continue
        
        if (tx == None): return # Ignore
        self.swap_piece((bx, by), (tx, ty))

    
    # Checks all pieces.
    def check_game_over(self):
        cnt_x, cnt_y = GRID_COUNT
        for i in range(0, cnt_x * cnt_y - 1):
            x = i % cnt_x
            y = math.floor(i / cnt_x)

            if (self.grid[y][x] != i):
                return
            
        self.game_over()

    
    # Handles the game over event.
    def game_over(self):
        cnt_x, cnt_y = GRID_COUNT
        h, m, s = self.get_ETA()

        self._timer.stop()
        self.grid[cnt_y - 1][cnt_x - 1] = cnt_x * cnt_y - 1
        self.update_puzzle_image()

        messagebox.showinfo(title = "Congraturations!", message = f"클리어했습니다! {h}시간 {m}분 {s}초 걸렸습니다!")
        self.root.destroy() # Terminates the program.
            
        
    # Returns attempting time information.
    def get_ETA(self):
        cur = math.floor(time.time())
        ETA = cur - self.started_at
        
        s = math.floor(ETA) % 60
        m = math.floor(ETA / 60) % 60
        h = math.floor(ETA / 60 / 60)

        return (h, m, s)


    # Shows the stopwatch.
    def initialize_timer(self):
        self._timer = PuzzleTimerThread(1, self)
        self._timer.start()




# Helper class of the puzzle instance's timer
class PuzzleTimerThread(Thread):

    def __init__(self, intv, puzzle: Puzzle):
        Thread.__init__(self)
        self._stopped = False
        self._interval = intv
        self._game = puzzle

    def stop(self):
        self._stopped = True

    def run(self):
        while not self._stopped:
            try:
                h, m, s = self._game.get_ETA()
                pw, ph = GRID_COUNT
                self._game.root.title(f"퍼즐 {pw}x{ph}, {h}시간 {m}분 {s}초 소요됨")
            except RuntimeError:
                break
            time.sleep(self._interval)




### ------------------------------------------- ###
# Utility functions



def choose_file():
    file = filedialog.askopenfilename(\
                                      title = "퍼즐 파일 선택하기", \
                                      filetypes = (("PNG File", "*.PNG"), ("JPG File", "*.JPG")))
    if (file == ''):
        messagebox.showwarning("Error", "파일을 선택하십시오.")
        return choose_file()
    
    return file



### ------------------------------------------- ###
### Configuration ###


global IMAGE_FILE, GRID_SIZE
IMAGE_FILE = choose_file()
GRID_COUNT = (5, 5)



### ------------------------------------------- ###
### Execution ###

Puzzle()
