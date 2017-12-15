# Simple pong game - don't let the ball hit the bottom!
# KidsCanCode - Intro to Programming
from Tkinter import *
import random
import time

# Define ball properties and functions

class Brick:
    def __init__(self, canvas,x,y):
        self.canvas = canvas
        self.image = res['brick']
        self.id = canvas.create_image(10, 10, image=self.image)
        self.canvas.move(self.id, x, y)
        self.hit = False
        self.width = self.image.width()
        self.height = self.image.height()

class Ball:
    def __init__(self, canvas, color, paddle,bricks):
        self.canvas = canvas
        self.paddle = paddle
        self.bricks = bricks
        #self.id = canvas.create_oval(10, 10, size, size, fill=color)
        self.image = res['ball']
        self.id = canvas.create_image(10, 10, image=self.image)
        self.canvas.move(self.id, *self.canvas.coords(self.paddle.id))
        self.xspeed = random.randrange(-3,3)
        self.yspeed = -1
        self.hit_bottom = False
        self.score = 0
        self.width = self.image.width()
        self.height = self.image.height()
        self.won = 0

    def draw(self):
        self.canvas.move(self.id, self.xspeed, self.yspeed)
        pos = self.canvas.coords(self.id)
        pos = [pos[0]-self.width/2,pos[1]-self.height/2,pos[0]+self.width/2,pos[1]+self.height/2]
        #print pos
        if pos[1] <= 0:
            self.yspeed = 3
        if pos[3] >= YSIZE:
            self.hit_bottom = True
        if pos[0] <= 0:
            self.xspeed = 3
        if pos[2] >= XSIZE:
            self.xspeed = -3
        if self.hit_paddle(pos) == True:
            self.yspeed = -3
            self.xspeed = random.randrange(-3,3)
#            self.score += 1
        if self.hit_brick(pos) == True:
            self.score +=1
        if self.score == len(self.bricks):
            self.won = 1

    def hit_paddle(self, pos):
        paddle_pos = self.canvas.coords(self.paddle.id)
        paddle_pos = [paddle_pos[0]-self.paddle.width/2,paddle_pos[1]-self.paddle.height/2,paddle_pos[0]+self.paddle.width/2,paddle_pos[1]+self.paddle.height/2]
        if pos[2] >= paddle_pos[0] and pos[0] <= paddle_pos[2]:
            if pos[3] >= paddle_pos[1] and pos[3] <= paddle_pos[3]:
                return True
        return False

    def hit_brick(self, pos):
        for brick in self.bricks:
            if not brick.hit:
                paddle_pos = self.canvas.coords(brick.id)
                paddle_pos = [paddle_pos[0]-self.paddle.width/2,paddle_pos[1]-self.paddle.height/2,paddle_pos[0]+self.paddle.width/2,paddle_pos[1]+self.paddle.height/2]
                if pos[2] >= paddle_pos[0]-5 and pos[0] <= paddle_pos[2]-5:
                    if pos[3] >= paddle_pos[1]-5 and pos[3] <= paddle_pos[3]-5:
                        self.yspeed *= -1
                        #self.xspeed *= -0.5# random.randrange(-3,3)
                        brick.hit = True
                        self.canvas.delete(brick.id)
                        return True
        return False
    
# Define paddle properties and functions
class Paddle:
    def __init__(self, canvas, color):
        self.canvas = canvas
        self.image = res['paddle']
        self.width = self.image.width()
        self.height = self.image.height()
        self.id = canvas.create_image(0,0, image=self.image)
#        self.id = canvas.create_rectangle(0,0, 100, 10, fill=color)
        self.canvas.move(self.id, 200, YSIZE-100)
        self.xspeed = 0
        self.canvas.bind_all('<KeyPress-Left>', self.move_left)
        self.canvas.bind_all('<KeyPress-Right>', self.move_right)
        self.canvas.bind_all('<KeyRelease>', self.move_stop)

    def draw(self):
        pos = self.canvas.coords(self.id)
        pos = [pos[0]-self.width/2,pos[1]-self.height/2,pos[0]+self.width/2,pos[1]+self.height/2]
        self.xspeed = min(self.xspeed,XSIZE-pos[2]) if self.xspeed>0 else max(self.xspeed,-pos[0])
        self.canvas.move(self.id, self.xspeed, 0)
        pos = self.canvas.coords(self.id)
        pos = [pos[0]-self.width/2,pos[1]-self.height/2,pos[0]+self.width/2,pos[1]+self.height/2]
        #print pos
        if pos[0] <= 0:
            self.xspeed = 0
        if pos[2] >= XSIZE:
            self.xspeed = 0

    def move_left(self, evt):
        self.xspeed = -3
    def move_right(self, evt):
        self.xspeed = 3
    def move_stop(self, evt):
        self.xspeed = 0

# Create window and canvas to draw on
def game_on():
    global res,XSIZE,YSIZE
    XSIZE = 700
    YSIZE = 500
    NUM_BRICKS = 20
    tk = Tk()
    tk.title("Ball Game")

    #res = {'ball':PhotoImage(file="ball_sm.gif"),"paddle": PhotoImage(file="paddle_sm.gif"),"brick":PhotoImage(file="brick_sm.gif")}
    ball = "R0lGODlhGQAZAPcAAAAAAAIAAAQBAQQCAgUCAgEGAQIGAgAABAICBQICBggCAg8EBAIKAgILAgICCBkHBx4JCQQEEwQEFC0ODg8tCgoyCgs6Cww6DAw8DAw/DAcHJAgIKwsdKQoKMQwMPBM6N0gWFksWFlQZGVQbGVMcGWAdHWEdHUUjFlQpG0UzGWAuH3UjI30lJX0nJX8mJmgxIg5FDg9MDxBUEBFVERJcEi1NFxNiExVoFRVqGRZxFhl7Ghl8GRl9GRp+Hht4KU5FHkBFOg0NQxAQUxIrQxU6RxY8RRMTYBQXYRUVbBYWbhYWcBgYeBkZfBkZfhYlYRYoYIAmJo4qKpMsLJ0vL4MpNqEwMKMxMaozM60zM7E1Nb85OcA9OsU8O80/PZhZNMpAPcNLPN1CQt5CQt1FQuBDQ+xGRu1HR/1LS/5MTP9MTP5NTP1OTNZvRxmAGRqAGhqCGhqEGhuHGxyLHByNHB2RHR6HLSCEPCChICKsIiOuIyOvIyOwIyOxIyW8JSa9Jia/JiSlNCShPCfBJyrDKCjIKCnLKSnOKSnPKSrRKivZKyzbLCvIOi3hLS/sLy/tLzHuMDH2MTH3MTL7MjL8MjP9MzP+MzP/MzT9MzL5NDP7NDP+NDP8NlTNNELUMFndOHLFOiuqWyiIajO1fTPWWzPZWTPxQTPMZoeQN4C7PBsbhR0djx0dkSAgnyM8lSAgoCMjsCMjsSZngDN2uyYmwCkpzisyzioq0Ssr2S8v6y8v7DEx9zIy+TIy+jIy+zIy/DMz/TMz/jMz/zM1/TM2/DNY2TNlzTNN5S6BkTOfkzOXmTOTnjOZmTOYmgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH5BAEAAM0ALAAAAAAZABkAAAj+AJsJHEiwoMGDBSvIMGAQgokJCAdiOGTJUqYPBKOk2ajlAUIDjiqWIhYMVxIAIzaqxHIQQaCKlooFm0nEECcoLFho2UjA4CxmFUfNDHakkSASZTZOWZFGQUEjwYQtsrTMmLJkOiylOKMyzRQWBlMFqxWLD6CKkN7EqdI1zZmeBYv04BEHEkxMBvCQaZuGQkEAJsqcCYPiT0VZHCyxaRvmDZ6BEVJ2PaGIVLAnljx1PaOiogWBGsK0fUEDh5MhdHjUYNFlzA9ElSztELhk45ZTnR7dlZGjIqY3NmBawiBQyRdUkixVkiPcEg7heBDBPCQwCQ/hiSyZQiYKk6U+wgmNCWfQjACYTzBBGRs6zMcc4YZhkmex0cugQ7SGzlSFp5L/7zAZIlAWKnEBhH4z8fKGcrEx4lsMAknRFRUIznRdbHYcE8odnwkUQldWvIIgKzAcUkcrQzlQUAhJpXFFB7kMZYsEr+iCYBAGAbAAXAgwkUoSCDSzSoVBRnTQBggyYWREHriiyy1CLCnlQQEBADs="
    paddle = "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"
    brick = "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"


    canvas = Canvas(tk, width=XSIZE, height=YSIZE, bd=0, bg='papaya whip')
    canvas.pack()
    res = {'ball': PhotoImage(master=canvas, data=ball), "paddle": PhotoImage(master=canvas, data=paddle),
           "brick": PhotoImage(master=canvas, data=brick)}
    #print res
    label = canvas.create_text(5, 5, anchor=NW, text="Score: 0")
    tk.update()
    paddle = Paddle(canvas, 'blue')
    bricks = []
    bw,bh = res['brick'].width(),res['brick'].height()
    #field = [[0 for x in xrange(YSIZE)] for y in xrange(XSIZE)]
    x,y = 5,30
    NUM_BRICKS = (XSIZE / (bw+x))*((YSIZE-y-100-100-paddle.height/2)/(bh+5))
    for i in xrange(NUM_BRICKS):
        bricks.append(Brick(canvas,x,y))
        x+=bw+5
        if x+bw>XSIZE:
            x =5
            y+=bh+5

    ball = Ball(canvas, 'red', paddle,bricks)

    # Animation loop
    while ball.hit_bottom == False and ball.won == False:
        ball.draw()
        paddle.draw()
        canvas.itemconfig(label, text="Score: "+str(ball.score))
        tk.update_idletasks()
        tk.update()
        time.sleep(0.01)

    # Game Over
    if ball.won:
        go_label = canvas.create_text(XSIZE/2,YSIZE/2,text="CONGRATS :)",font=("Helvetica",40))
    else:
        go_label = canvas.create_text(XSIZE/2,YSIZE/2,text="GAME OVER",font=("Helvetica",40))
    tk.update()
    x=0
    while x<3:
        x+=1
        time.sleep(1)
    #tk.quit()
    tk.destroy()
    return

if __name__ == "__main__":
    game_on()