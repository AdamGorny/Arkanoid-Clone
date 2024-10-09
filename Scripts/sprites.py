import pygame as pg
from pygame.sprite import Group
from settings import *
from random import choice, randint
import threading

class Player(pg.sprite.Sprite):

    def __init__(self, groups):
        super().__init__(groups)

        self.image = pg.Surface((windowWidth // 10, windowHeight // 30))
        self.image.fill("white")
        self.displaySurf = pg.display.get_surface()

        self.rect = self.image.get_rect(midbottom = (windowWidth // 2, windowHeight - 20))
        self.oldRect = self.rect.copy()
        self.moveDirectrion = pg.math.Vector2()
        self.pos = pg.math.Vector2(self.rect.topleft)
        self.moveSpeed = 350

        self.lives = 3

        self.laserCount = 0
        self.laserImg = pg.transform.scale_by(pg.image.load("Assets/laserimage.png"), 0.00005 * windowWidth)
        self.laserRects = []


    def input(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.moveDirectrion.x = 1
        elif keys[pg.K_LEFT] or keys[pg.K_a]:
            self.moveDirectrion.x = -1
        else:
            self.moveDirectrion.x = 0

    def screen_bound(self):
        if self.rect.right > windowWidth:
            self.rect.right = windowWidth
            self.pos.x = self.rect.x

        if self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.x

    def upgrade_player(self, upgradeType):
        t = threading.Timer(15, self.downgrade_player, args=(upgradeType,))

        if upgradeType == "speed":
            self.moveSpeed += 50

        if upgradeType == "stretch" or upgradeType == "contract":
            newWidth = self.rect.width * (1.1 if upgradeType == "stretch" else 0.9)
            self.image = pg.Surface((newWidth, self.rect.height))
            self.image.fill("white")
            self.rect = self.image.get_rect(center = self.rect.center)
            self.pos.x = self.rect.x
            t.start()

        if upgradeType == "laser":
            self.laserCount += 1
            t.start()
        
    def downgrade_player(self, upgradeType):
        if upgradeType == "stretch" or upgradeType == "contract":
            newWidth = self.rect.width * (0.9 if upgradeType == "stretch" else 1.1)
            self.image = pg.Surface((newWidth, self.rect.height))
            self.image.fill("white")
            self.rect = self.image.get_rect(center = self.rect.center)
            self.pos.x = self.rect.x
                    
        if upgradeType == "laser":
            self.laserCount -= 1

    def display_lasers(self):
        self.laserRects = []
        if self.laserCount > 0 :
            playerDivider = self.rect.width / (self.laserCount + 1)
            for i in range(0,self.laserCount):
                x = self.rect.left + playerDivider * (i + 1)
                laserRect = self.laserImg.get_rect(midbottom = (x, self.rect.top))
                self.laserRects.append(laserRect)

            for laserRect in self.laserRects:
                self.displaySurf.blit(self.laserImg, laserRect)

    def update(self, dt):
        self.oldRect = self.rect.copy()        
        self.input()
        self.pos.x += self.moveDirectrion.x * self.moveSpeed * dt
        self.rect.x = round(self.pos.x)
        self.screen_bound()
        self.display_lasers()

class Ball(pg.sprite.Sprite):
    def __init__(self, groups, player, blocks):
        super().__init__(groups)

        self.player = player
        self.blocks = blocks

        self.image = self.get_ball_img(player, 1)
        self.rect = self.image.get_rect(midbottom = player.rect.midtop)
        self.oldRect = self.rect.copy()
        self.moveDirectrion = pg.math.Vector2((choice((-1,1)),-1))
        self.pos = pg.math.Vector2(self.rect.topleft)
        self.moveSpeed = 400

        self.moving = False

        self.impactSound = pg.mixer.Sound("Assets/Audio/impact.wav")
        self.impactSound.set_volume(0.1)
        self.failSound = pg.mixer.Sound("Assets/Audio/fail.wav")
        self.failSound.set_volume(0.1)

    def screen_collision(self, axis):
        if axis == "horizontal":
            if self.rect.left < 0:
                self.rect.left = 0
                self.pos.x = self.rect.x
                self.moveDirectrion.x *= -1
                self.impactSound.play()

            if self.rect.right > windowWidth:
                self.rect.right = windowWidth
                self.pos.x = self.rect.x
                self.moveDirectrion.x *= -1 
                self.impactSound.play()

        if axis == "vertical":
            if self.rect.top < 0:
                self.rect.top = 0
                self.pos.y = self.rect.y
                self.moveDirectrion.y *= -1
                self.impactSound.play()

            if self.rect.bottom > windowHeight:
                self.moving = False
                self.moveDirectrion.y = -1
                self.player.lives -= 1
                self.failSound.play()

    def colision(self, direction):
        overlapSprites = pg.sprite.spritecollide(self, self.blocks, False)
        if self.rect.colliderect(self.player.rect):
            overlapSprites.append(self.player)

        if overlapSprites:
            if direction == "horizontal":
                for sprite in overlapSprites:
                    if self.rect.right >= sprite.rect.left and self.oldRect.right <= sprite.oldRect.left:
                        self.rect.right = sprite.rect.left - 1 
                        self.pos.x  = self.rect.x
                        self.moveDirectrion.x *= -1
                        self.impactSound.play()
                    if self.rect.right <= sprite.rect.left and self.oldRect.left >= sprite.oldRect.right:
                        self.rect.left = sprite.rect.right + 1
                        self.pos.x  = self.rect.x
                        self.moveDirectrion.x *= -1
                        self.impactSound.play()

                    if getattr(sprite, "health", None):
                        sprite.get_damage(1)

            if direction == "vertical":
                for sprite in overlapSprites:
                    if self.rect.bottom >= sprite.rect.top and self.oldRect.bottom <= sprite.oldRect.top:
                        self.rect.bottom = sprite.rect.top - 1
                        self.pos.y  = self.rect.y
                        self.moveDirectrion.y *= -1
                        self.impactSound.play()

                    if self.rect.top <= sprite.rect.bottom and self.oldRect.top >= sprite.oldRect.bottom:
                        self.rect.top = sprite.rect.bottom + 1
                        self.pos.y  = self.rect.y
                        self.moveDirectrion.y *= -1
                        self.impactSound.play()

                    if getattr(sprite, "health", None):
                        sprite.get_damage(1)
                
    def update(self, dt):
        if self.moving:
        
            if self.moveDirectrion.magnitude() != 0:
                self.moveDirectrion = self.moveDirectrion.normalize()

            self.oldRect = self.rect.copy()
            self.pos.x += self.moveDirectrion.x * self.moveSpeed * dt
            self.rect.x = round(self.pos.x)
            self.colision("horizontal")
            self.screen_collision("horizontal")

            self.pos.y += self.moveDirectrion.y * self.moveSpeed * dt
            self.rect.y = round(self.pos.y)
            self.colision("vertical")
            self.screen_collision("vertical")

        else:
            self.rect.midbottom = self.player.rect.midtop
            self.pos = pg.math.Vector2(self.rect.topleft)

    def get_ball_img(self, player, playerSize):
        rawImg = pg.image.load("Assets/ball.png")
        scaledImg = pg.transform.scale(rawImg, (player.image.get_height() * playerSize , player.image.get_height() * playerSize)).convert_alpha()
        return scaledImg

class Block(pg.sprite.Sprite):
    def __init__(self, blockType, pos, groups, color, generate_upgrade):
        super().__init__(groups)

        self.image = pg.Surface((blockWidth, blockHeight))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft = pos)
        self.oldRect = self.rect.copy()

        self.health = int(blockType)

        self.generate_upgrade = generate_upgrade

    def get_damage(self, damage):
        self.health -= damage

        if self.health > 0:
            self.image.fill(colorDict[str(self.health)])
        else:
            if randint(0,10) <= 4:
                self.generate_upgrade(self.rect.center)
            self.kill()
            
class Upgrade(pg.sprite.Sprite):
    def __init__(self, pos, upgradeType, groups):
        super().__init__(groups)
        
        self.upgradeType = upgradeType
        self.image = pg.transform.scale_by(pg.image.load(f"Assets/upgrades/{upgradeType}.png"), 0.00004 * windowWidth)
        self.rect = self.image.get_rect(midtop = pos)

        self.pos = pg.math.Vector2(self.rect.topleft)
        self.moveSpeed = 200

    def update(self, dt):
        self.pos.y += self.moveSpeed * dt
        self.rect.y = round(self.pos.y)

        if self.rect.top > windowHeight + 100:
            self.kill()

class LaserProj(pg.sprite.Sprite):
    def __init__(self, pos, img, groups):
        super().__init__(groups)

        self.image = img
        self.rect = self.image.get_rect(midbottom = pos)

        self.pos = pg.math.Vector2(self.rect.topleft)
        self.moveSpeed = 300

    def update(self, dt):
        self.pos.y -= self.moveSpeed * dt
        self.rect.y = round(self.pos.y)

        if self.rect.bottom <= -100:
            self.kill()