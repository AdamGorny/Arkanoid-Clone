import pygame as pg
import sys
import time
from settings import *
from sprites import Player, Ball, Block, Upgrade, LaserProj
from random import choice
import os

os.chdir(os.path.dirname(__file__) + "\..")

class Game:
    def __init__(self):
        pg.init()
        self.displayWindow = pg.display.set_mode((windowWidth, windowHeight))
        pg.display.set_caption("Arkanoid")

        self.background = self.get_background()

        self.allSprites = pg.sprite.Group()
        self.blockSprites = pg.sprite.Group()
        self.upgradeSprites = pg.sprite.Group()
        self.projSprties = pg.sprite.Group()

        self.player = Player(self.allSprites)
        self.ball = Ball(self.allSprites, self.player, self.blockSprites)
        self.generate_blocks()

        self.heartImg = pg.transform.scale_by(pg.image.load("Assets/heart.png"), 0.000024 * windowWidth)

        self.laserProjImg = pg.transform.scale_by(pg.image.load("Assets/laserProjImage.png"), 0.00003 * windowWidth)
        self.shootTime = 0

        self.laserSound = pg.mixer.Sound("Assets/Audio/laserSound.mp3")
        self.laserSound.set_volume(0.1)
        self.upgradeSound = pg.mixer.Sound("Assets/Audio/upgradeSound.mp3")
        self.upgradeSound.set_volume(0.1)
        self.laserHitSound = pg.mixer.Sound("Assets/Audio/laser_hit.wav")
        self.laserHitSound.set_volume(0.02)
        self.downgradeSound = pg.mixer.Sound("Assets/Audio/downgradeSound.mp3")
        self.downgradeSound.set_volume(0.2)
        self.music = pg.mixer.Sound("Assets/Audio/music.wav")
        self.music.set_volume(0.03)
        self.music.play(loops=-1)

    def run(self):
        prevTime = time.time()

        while True:
            dt = time.time() - prevTime
            prevTime = time.time()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.ball.moving = True
                    if event.key == pg.K_ESCAPE:
                        self.music.stop()
                        show_menu("MAIN MENU", "START", "EXIT")

            if self.player.lives <= 0:
                self.music.stop()
                show_menu("GAME OVER", "RESTART", "EXIT")
            
            if len(self.blockSprites) <= 0:
                self.music.stop()
                show_menu("YOU WON", "RESTART", "EXIT")

            if self.player.laserCount > 0:
                self.auto_laser_shoot()

            self.displayWindow.blit(self.background, (0,0))

            self.allSprites.update(dt)

            self.upgrade_collision()

            self.laser_block_collision()

            self.allSprites.draw(self.displayWindow)

            self.display_hearts()

            pg.display.update()
    
    def get_background(self):
        rawBg = pg.image.load("Assets/background.jpg")
        scaleFactor = windowHeight / rawBg.get_height()
        scaledBg = pg.transform.scale(rawBg, (rawBg.get_width() * scaleFactor, rawBg.get_height() * scaleFactor))
        return scaledBg

    def generate_blocks(self):
        rowNum = 0
        for row in blockLayout:
            colNum = 0
            for col in row:
                if col != " ":
                    blockX = colNum * (blockWidth + blockGap) + blockGap // 2
                    blockY = topOffset + rowNum * (blockHeight + blockGap) + blockGap // 2
                    Block(col, (blockX, blockY), [self.allSprites, self.blockSprites], colorDict[col], self.generate_upgrade)
                colNum += 1
            rowNum += 1
    
    def generate_upgrade(self, pos):
        upgradeType = choice(upgrades)
        Upgrade(pos, upgradeType, [self.allSprites, self.upgradeSprites])

    def upgrade_collision(self):
        overlapSprites = pg.sprite.spritecollide(self.player, self.upgradeSprites, True)
        for sprite in overlapSprites:
            self.player.upgrade_player(sprite.upgradeType)
            if sprite.upgradeType == "contract":
                self.downgradeSound.play()
            else:
                self.upgradeSound.play()    
    
    def display_hearts(self):
        for i in range(self.player.lives):
            x = 3 + i * (self.heartImg.get_width() + 3)
            self.displayWindow.blit(self.heartImg, (x,3))

    def create_laser_proj(self):
        self.laserSound.play()
        for proj in self.player.laserRects:
            LaserProj(proj.midtop - pg.math.Vector2(0,30), self.laserProjImg, [self.allSprites, self.projSprties])

    def auto_laser_shoot(self):
        if (pg.time.get_ticks() - self.shootTime > 600):
            self.create_laser_proj()
            self.shootTime = pg.time.get_ticks()

    def laser_block_collision(self):
        for proj in self.projSprties:
            overlapSprites = pg.sprite.spritecollide(proj, self.blockSprites, False)
            if overlapSprites:
                for sprite in overlapSprites:
                    sprite.get_damage(1)
                proj.kill()
                self.laserHitSound.play()


def show_menu(mainText, btn1Text, btn2Text):
    pg.init()
    screen = pg.display.set_mode((windowWidth, windowHeight))
    screen.blit(Game.get_background(Game), (0,0))
    
    def draw_text(text, font, color, surface, x, y):
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.center = (x, y)
        surface.blit(textobj, textrect)
    
    click = False
    while True:

        draw_text(mainText, pg.font.SysFont(None, 80), "white", screen, windowWidth // 2, windowHeight * 0.2)

        mx, my = pg.mouse.get_pos()

        button1 = pg.Rect(windowWidth * 0.5 - (windowWidth // 6)//2, windowHeight * 0.4, windowWidth // 6, 50)
        button2 = pg.Rect(windowWidth * 0.5 - (windowWidth // 6)//2, windowHeight * 0.55, windowWidth // 6, 50)

        if button1.collidepoint((mx, my)):
            if click:
                game = Game()
                game.run()

        if button2.collidepoint((mx, my)):
            if click:
                pg.quit()
                sys.exit()

        pg.draw.rect(screen, "black", button1)
        draw_text(btn1Text, pg.font.SysFont(None, 40), "white", screen, button1.centerx, button1.centery)
        pg.draw.rect(screen, "black", button2)
        draw_text(btn2Text, pg.font.SysFont(None, 40), "white", screen, button2.centerx, button2.centery)

        click = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pg.display.update()

show_menu("MAIN MENU", "START", "EXIT")