import pygame
from random import randint,uniform
pygame.init()
import time
#w = pygame.display.Info().current_w // 2
#h = pygame.display.Info().current_h // 2
w = 540
h = 980
screen = pygame.display.set_mode((w,h))
hsfont = pygame.font.SysFont("timesnewroman", 36)
sfont = pygame.font.SysFont("timesnewroman", 20)
best_time_easy = float('inf')
best_time_hard = float('inf')
best_time_huge = float('inf')

def getside(rect,offset):
  
  if offset[0] == 1:
    if offset[2]>0:
      return (rect.bottom>w,1,-w)
    else:
      return (rect.top<0,1,w)
  else:
    if offset[2]>0:
      return (rect.right>w,0,-w)
    else:
      return (rect.left<0,0,w)
class Board:
  def __init__(self,dim,shuffle = True):
    self.dim = dim
    self.won = False
    self.state = [[x*dim+y+1 for x in range(dim)]for y in range(dim)]
    self.winstate = [[x*dim+y+1 for x in range(dim)]for y in range(dim)]
    self.colmods = (uniform(1,3.5),uniform(1,3.5),uniform(1,3.5))
    if shuffle:
      for i in range(2*dim**2):
        self.move((randint(0,self.dim-1),randint(0,self.dim-1)),randint(0,1),randint(-(dim-1),(dim-1)))
    
  def __str__(self):
    out = ""
    for item in self.state:
      for k in item:
        out += str(k)+" "*(3-len(str(k)))
      out+= "\n"
    return out
  def move(self,pos,axis,dir):
    if axis == 0:
      for i in range(abs(dir)):
        k = self.state[pos[0]]
        if dir<0:
          self.state[pos[0]] = [k[-1]]+k[:-1]
        else:
          self.state[pos[0]] = k[1:] +[k[0]]
    else:
      for i in range(abs(dir)):
        k = []
        for item in self.state:
          k.append(item[pos[1]])
        if dir<0:
          k = [k[-1]]+k[:-1]
        else:
          k = k[1:] +[k[0]]
        for x,item in enumerate(self.state):
          item[pos[1]] = k[x]
    if self.state == self.winstate:
      self.won = True
    else:
      self.won = False
  def draw(self, screen, offset=False):
    boxsize = w // self.dim
    centerx = (w - self.dim * boxsize) // 2
    centery = (h - self.dim * boxsize) // 2
    
    board = pygame.Surface((self.dim * boxsize, self.dim * boxsize))
    
    for x, xitem in enumerate(self.state):
        for y, yitem in enumerate(xitem):
            #boxsize = w // self.dim
            im = pygame.Surface((boxsize, boxsize))
            
            darkness = 255 * yitem / (self.dim ** 2)
            tcol = 255
            
            if darkness > 127.5:
                tcol = 0
                
            im.fill((darkness / self.colmods[0], darkness / self.colmods[1], darkness / self.colmods[2]))
            
            if self.dim < 10:
                text = hsfont.render(str(yitem), True, (tcol, tcol, tcol))
            else:
                text = sfont.render(str(yitem), True, (tcol, tcol, tcol))
            
            im.blit(text, text.get_rect(center=(boxsize / 2, boxsize / 2)))
            
            blitPos = [x * boxsize, y * boxsize]
            
            if offset != False:
                if offset[0] == 0 and offset[1][0] == y:
                    blitPos[0] += offset[2]
                elif offset[0] == 1 and offset[1][1] == x:
                    blitPos[1] += offset[2]
                    
                wrapTest = getside(im.get_rect(topleft=blitPos), offset)
                
                if wrapTest[0]:
                    wBlit = blitPos[::-1][::-1]
                    wBlit[wrapTest[1]] += wrapTest[2]
                    board.blit(im, wBlit)
            
            board.blit(im, blitPos)
    
    screen.blit(board, (centerx, centery))


def game(difficulty):
  b = Board(difficulty)
  global best_time_easy
  global best_time_hard
  global best_time_huge
  done = False
  held = False
  hold_pos = (0,0)
  axis = None
  offset = (0,(0,0),0)
  c = pygame.time.Clock()
  taken = 0
  timer = hsfont.render("Время:",True,(0,0,0))
  quit = hsfont.render("Сдаться?",True,(0,0,0))
  quitw = quit.get_width()
  quith = quit.get_height()
  textx = (w - quitw) // 2
  texty = h - quith - 10
  quit = (quit,quit.get_rect(topright = (textx - 30,texty)))
  timer = (timer,timer.get_rect(topright = (textx + 200,texty)))
  while not done:
    c.tick(60)
    taken+=c.get_time()
    screen.fill((255,255,255))
    b.draw(screen,offset)
    time_surf = hsfont.render(str(round(taken/1000,2)),True,(0,0,0))
    screen.blit(time_surf,time_surf.get_rect(topleft = (textx + 210,texty)))
    screen.blit(quit[0],quit[1])
    screen.blit(timer[0],timer[1])
    #pygame.draw.circle(screen,(0,0,0),pygame.mouse.get_pos(),7,3)
    
    pygame.display.flip()
    if b.won:
      time.sleep(1.5)
      done = True
      if best_time_easy > taken and difficulty == 3:
        best_time_easy = taken
      elif best_time_hard > taken and difficulty == 5:
        best_time_hard = taken
      elif best_time_huge > taken and difficulty == 10:
        best_time_huge = taken
      ui()

    k = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1] - 215)
    kk = pygame.mouse.get_pos()
    for event in pygame.event.get():
      if event.type == pygame.MOUSEBUTTONDOWN:
        if k[1]<w:
          held = True
          hold_pos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1] - 215)
          axis = None
        if quit[1].collidepoint(kk):
          done = True
          ui()
      elif event.type == pygame.MOUSEBUTTONUP:
        
          held = False
          offset = (0,(0,0),0)
          if axis!= None:
            m = (k[axis]-hold_pos[axis])
            if abs(m)>(w/b.dim)/2 :
              b.move((int(hold_pos[0]//(w/b.dim)),int(hold_pos[1]//(w/b.dim))),abs(1-axis),int(round(-m/(w/b.dim),0)))
            hold_pos = (pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1] - 215)
   
    if held:
      
      if abs(k[0]-hold_pos[0])>abs(k[1]-hold_pos[1]):
        axis = 0
      else:
        axis = 1
    if held and axis!=None:
      m = (k[axis]-hold_pos[axis])
      offset = (axis,(hold_pos[1]//(w/b.dim),hold_pos[0]//(w/b.dim)),m)
def load(imname):
  return pygame.transform.scale(pygame.image.load(imname),(300,150))
def ui():
  
  easy = load("easy.png")
  easy = (easy,easy.get_rect(center = (w//2,h//7.5)))
  e_record = hsfont.render("Best time: " + str(round(best_time_easy / 1000, 2)), True, (0, 0, 0))
  e_record = (e_record,e_record.get_rect(topright = ((w//2) + 50,(h//7.5) + 75)))
  hard = load("hard.png")
  hard = (hard,hard.get_rect(center = (w//2,h//3)))
  ha_record = hsfont.render("Best time: " + str(round(best_time_hard / 1000, 2)), True, (0, 0, 0))
  ha_record = (ha_record,ha_record.get_rect(topright = ((w//2) + 50,(h//3) + 75)))
  huge = load("huge.png")
  huge = (huge,huge.get_rect(center = (w//2,h//1.875)))
  hu_record = hsfont.render("Best time: " + str(round(best_time_huge / 1000, 2)), True, (0, 0, 0))
  hu_record = (hu_record,hu_record.get_rect(topright = ((w//2) + 50,(h//1.875)+75)))
  exit = load("exit.png")
  exit = (exit,exit.get_rect(center = (w//2,h//1.35)))
  while True:
    pygame.event.pump()
    
    
    
    screen.fill((255,255,255))
    
    screen.blit(easy[0],easy[1])
    screen.blit(hard[0],hard[1])
    screen.blit(huge[0],huge[1])
    screen.blit(exit[0],exit[1])
    screen.blit(e_record[0],e_record[1])
    screen.blit(ha_record[0],ha_record[1])
    screen.blit(hu_record[0],hu_record[1])

   
    #pygame.draw.circle(screen,(0,0,0),pygame.mouse.get_pos(),7,3)
    
    for event in pygame.event.get():
      if event.type == pygame.MOUSEBUTTONDOWN:
        
        mp = pygame.mouse.get_pos()
        #pygame.draw.circle(screen,(0,0,0),mp,5,3)
        
        
          
        if easy[1].collidepoint(mp):
          game(3)
        elif hard[1].collidepoint(mp):
          game(5)
        elif huge[1].collidepoint(mp):
          game(10)
        elif exit[1].collidepoint(mp):
          pygame.quit() 
          quit()
    pygame.display.flip()
ui()