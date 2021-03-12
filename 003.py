import os
import sys
import pygame
import random
import math


def terminate():
    pygame.quit()
    sys.exit()


def additional_elements(r):
    sete = open("data/product.txt", mode='rt', encoding='utf8').readlines()
    if r == 'm':
        return [load_image(i.split()[0]) for i in sete[4:] if i.split()[1].rstrip() == '1']
    return [load_image(i.split()[0]) for i in sete[:4] if i.split()[1].rstrip() == '1']


def load_image(name, colorkey=None):
   fullname = os.path.join('data', name)
   if not os.path.isfile(fullname):
       print(f"Файл с изображением '{fullname}' не найден")
       sys.exit()
   image = pygame.image.load(fullname)
   if colorkey is not None:
       image = image.convert()
       if colorkey == -1:
           colorkey = image.get_at((0, 0))
       image.set_colorkey(colorkey)
   return image


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.jpg'),
    'barrel': additional_elements
}
player_image = load_image('mario.png')
shot_image = load_image('shot.png')
money_image = load_image('money.png')
monster_image = additional_elements
tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        if tile_type == 'barrel':
            self.image = tile_images[tile_type]('b')[random.randrange(0, len(tile_images[tile_type]('b')))]
        else:
            self.image = tile_images[tile_type]
        if tile_type != 'empty':
            borders.add(self)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Money(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(money_group, all_sprites)
        self.image = money_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.sound = pygame.mixer.Sound('data/money.mp3')

    def checking(self):
        if pygame.sprite.collide_mask(self, player):
            player.money += 1
            self.sound.play()
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, player_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.danger = 1
        self.danger_pr = 0
        self.money = 0
        self.sound_step = pygame.mixer.Sound('data/step.mp3')
        self.sound_pain = pygame.mixer.Sound('data/pain.mp3')

    def defeat(self):
        if self.danger == self.danger_pr + 1:
            self.sound_pain.play()
            self.danger_pr += 1
        self.danger += 0.25

    def drawing_of_the_hazard_level(self):
        pygame.draw.rect(screen, pygame.Color("red"),
                         (self.pos_x * tile_width, self.pos_y * tile_width - 7,
                          self.danger_pr * 10, 7))

    def next_move(self, x, y):
        self.rect = self.rect.move(x, y)
        self.pos_x += x / tile_width
        self.pos_y += y / tile_height
        if pygame.sprite.spritecollideany(player, borders):
            self.rect = self.rect.move(-x, -y)
            self.pos_x -= x / tile_width
            self.pos_y -= y / tile_height
        else:
            self.danger = self.danger_pr + 1
            self.sound_step.play()


class Monster(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(enemies, all_sprites)
        self.image = monster_image('m')[random.randrange(0, len(monster_image('m')))]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.speed, self.steps = 4, 0
        self.sound_hit = pygame.mixer.Sound('data/hit.mp3')
        self.sound_death = pygame.mixer.Sound('data/death.mp3')

    def defeat(self):
        self.speed += 1
        self.sound_hit.play()
        if self.speed == 7:
            self.sound_death.play()
            self.kill()

    def step_verification(self, x, y):
        self.pos_x += x
        self.pos_y += y
        self.rect = self.rect.move(x * tile_width, y * tile_height)
        if pygame.sprite.spritecollideany(self, borders):
            self.pos_x -= x
            self.pos_y -= y
            self.rect = self.rect.move(-x * tile_width, -y * tile_height)

    def next_move(self, x, y, a):
        pygame.draw.rect(screen, pygame.Color("red"),
                         (self.pos_x * tile_width, self.pos_y * tile_width - 7,
                          (self.speed - 4) * 15, 7))
        if self.steps == 0:
            self.steps = self.speed
            n = len(a)
            d = [1000000000] * n
            p = [[] for _ in range(n)]
            q = []
            s, f = int(self.pos_y * (len(a) ** 0.5) + self.pos_x),\
                   int(y * (len(a) ** 0.5) + x)
            q.append(s)
            d[s] = 0
            while q:
                i = q[-1]
                del q[-1]
                for j in range(n):
                    if a[i][j] and d[j] > d[i] + 1:
                        q.append(j)
                        d[j] = d[i] + 1
                        p[j] = p[i] + [i]
            n = int(len(a) ** 0.5)
            if d[f] < 6:
                if len(p[f]) > 1:
                    k = p[f][1]
                else:
                    k = f
                x, y = k % n - self.pos_x, k // n - self.pos_y
                self.pos_x += x
                self.rect = self.rect.move(x * tile_width, 0)
                self.pos_y += y
                self.rect = self.rect.move(0, y * tile_height)
            else:
                x, y = random.randrange(-1, 2), random.randrange(-1, 2)
                if 0 <= self.pos_x + x < n:
                    self.step_verification(x, 0)
                if 0 <= self.pos_y + y < n:
                    self.step_verification(0, y)
        self.steps -= 1
        if pygame.sprite.collide_mask(self, player):
            player.defeat()


class Shot(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, direction_x, direction_y):
        super().__init__(shots, all_sprites)
        self.image = shot_image
        if direction_x == 1:
            self.image = pygame.transform.rotate(self.image, 90)
        if direction_x == -1:
            self.image = pygame.transform.rotate(self.image, -90)
        if direction_y == -1:
            self.image = pygame.transform.rotate(self.image, 180)
        self.rect = self.image.get_rect().move(pos_x - 10, pos_y)
        self.mask = pygame.mask.from_surface(self.image)
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.steps = 5

    def next_move(self):
        self.steps -= 1
        self.rect = self.rect.move(self.direction_x * tile_width, self.direction_y * tile_height)
        if pygame.sprite.spritecollideany(self, borders) or self.steps == 0:
            self.kill()
        for enem in enemies:
            if pygame.sprite.collide_mask(self, enem):
                enem.defeat()
                self.kill()


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    sete = [[0 for _ in range(len(level) ** 2)] for _ in range(len(level) ** 2)]
    k = 0
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == 'b':
                Tile('empty', x, y)
                Tile('barrel', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == 'v':
                Tile('empty', x, y)
                Monster(x, y)
            elif level[y][x] == 'm':
                Tile('empty', x, y)
                Money(x, y)
            if level[y][x] not in ['#', 'b']:
                if y - 1 >= 0 and level[y - 1][x] not in ['#', 'b']:
                    sete[k - len(level)][k] = 1
                    sete[k][k - len(level)] = 1
                if y + 1 < len(level) and level[y + 1][x] not in ['#', 'b']:
                    sete[k + len(level)][k] = 1
                    sete[k][k + len(level)] = 1
                if x - 1 >= 0 and level[y][x - 1] not in ['#', 'b']:
                    sete[k - 1][k] = 1
                    sete[k][k - 1] = 1
                if x + 1 < len(level) and level[y][x + 1] not in ['#', 'b']:
                    sete[k + 1][k] = 1
                    sete[k][k + 1] = 1
            k += 1
    return new_player, x, y, sete


def inf(text_x, text_y, sl, r=50):
    font = pygame.font.Font(None, r)
    text = font.render(sl, True, (100, 255, 100))
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.draw.rect(screen, (0, 255, 0), (text_x - 10, text_y - 10,
                                           text_w + 20, text_h + 20), 1)


def pause():
    pygame.mixer.music.load('data/music3.mp3')
    pygame.mixer.music.play()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                arrow.rect.x = event.pos[0] - 20
                arrow.rect.y = event.pos[1] - 20
            if event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 150 <= x <= 369 and 200 <= y <= 235:
                    pygame.mixer.music.pause()
                    return 1
                if 40 <= x <= 529 and 300 <= y <= 335:
                    pygame.mixer.music.pause()
                    return 2
        screen.fill((0, 0, 0))
        for i in range(1000):
            screen.fill(pygame.Color('white'),
                        (random.random() * WIDTH,
                         random.random() * HEIGHT, 1, 1))
        inf(150, 200, "Продолжить")
        inf(40, 300, "Вернуться на главный экран")
        if pygame.mouse.get_focused():
            arrow_sprite.draw(screen)
        pygame.display.flip()


def level_digit(x, y, n):
    font = pygame.font.Font(None, 80)
    text = font.render(n, True, (100, 255, 100))
    screen.blit(text, (x, y))
    pygame.draw.rect(screen, (0, 255, 0), (x - 10, y - 10,
                                           80, 80), 1)
    zv = open("data/results.txt", mode='rt', encoding='utf8').read().split()[int(n)]
    for i in range(int(zv)):
        pygame.draw.circle(screen, (0, 255, 0), (x + 50, y + 10 + i * 20), 8)


def the_end_of_the_game(s, m, n, r):
    pygame.mixer.music.load('data/music3.mp3')
    pygame.mixer.music.play()
    f = open("data/results_level.txt", mode='rt', encoding='utf8').read().split()
    f[r] = str(n)
    f1 = open("data/results_level.txt", mode='wt', encoding='utf8')
    f1.write(' '.join(f))
    f1.close()
    f = open("data/results.txt", mode='rt', encoding='utf8').read().split()
    f[r + 1] = str(n)
    f[0] = str(int(f[0]) + m)
    f1 = open("data/results.txt", mode='wt', encoding='utf8')
    f1.write(' '.join(f))
    f1.close()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                arrow.rect.x = event.pos[0] - 20
                arrow.rect.y = event.pos[1] - 20
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 120 <= x <= 426 and 300 <= y <= 335:
                    pygame.mixer.music.pause()
                    return
        screen.fill((0, 0, 0))
        for i in range(1000):
            screen.fill(pygame.Color('white'),
                        (random.random() * WIDTH,
                         random.random() * HEIGHT, 1, 1))
        font = pygame.font.Font(None, 50)
        text = font.render(s, True, (100, 255, 100))
        screen.blit(text, (150, 200))
        inf(120, 300, "На главный экран")
        r = 10
        for i in range(n):
            kk = 0
            for k in range(1, 8):
                if k > 7 - 3:
                    kk = k + 3 - 7
                else:
                    kk = k + 3
                x = math.cos((math.pi) * 2 * k / 7) * 60 + 60 + r
                y = math.sin((math.pi) * 2 * k / 7) * 60 + 60
                x1 = math.cos((math.pi) * 2 * kk / 7) * 60 + 60 + r
                y1 = math.sin((math.pi) * 2 * kk / 7) * 60 + 60
                pygame.draw.line(screen, (0, 255, 0), (x, y), (x1, y1))
            r += 200
        if pygame.mouse.get_focused():
            arrow_sprite.draw(screen)
        pygame.display.flip()


def play(screen):
    draw = True
    pygame.mixer.music.load('data/music2.mp3')
    pygame.mixer.music.play()
    sound_shot = pygame.mixer.Sound('data/shot.mp3')
    nap = -1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                sete = list(pygame.key.get_pressed())
                if sete[79]:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        Shot(player.rect.x, player.rect.y, 1, 0)
                        sound_shot.play()
                    else:
                        nap = 1
                if sete[80]:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        Shot(player.rect.x, player.rect.y, -1, 0)
                        sound_shot.play()
                    else:
                        nap = 2
                if sete[82]:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        Shot(player.rect.x, player.rect.y, 0, -1)
                        sound_shot.play()
                    else:
                        nap = 3
                if sete[81]:
                    if pygame.key.get_mods() & pygame.KMOD_CTRL:
                        Shot(player.rect.x, player.rect.y, 0, 1)
                        sound_shot.play()
                    else:
                        nap = 4
                if sete[41]:
                    pygame.mixer.music.pause()
                    x = pause()
                    if x == 2:
                        return
                    pygame.mixer.music.load('data/music2.mp3')
                    pygame.mixer.music.play()
            if event.type == pygame.KEYUP:
                nap = -1
        if nap == 1:
            player.next_move(tile_width, 0)
        elif nap == 2:
            player.next_move(-tile_width, 0)
        elif nap == 3:
            player.next_move(0, -tile_height)
        elif nap == 4:
            player.next_move(0, tile_height)
        if draw:
            screen.fill((0, 0, 0))
            tiles_group.draw(screen)
            tiles_group.update()
            money_group.draw(screen)
            for m in money_group:
                m.checking()
            money_group.update()
            player_group.draw(screen)
            player_group.update()
            player.drawing_of_the_hazard_level()
            shots.draw(screen)
            shots.update()
            for shot in shots:
                shot.next_move()
            enemies.draw(screen)
            enemies.update()
            for enem in enemies:
                enem.next_move(player.pos_x, player.pos_y, pole)
        if player.danger_pr >= 6:
            the_end_of_the_game('Вы проиграли', player.money, 3 - len(enemies),
                                level - 1)
            return
        if len(money_group) == 0:
            the_end_of_the_game('Вы выиграли', player.money, 3 - len(enemies),
                                level - 1)
            return
        pygame.display.flip()
        clock.tick(FPS)


def the_level_of_play():
    pygame.mixer.music.load('data/music3.mp3')
    pygame.mixer.music.play()
    n = 6
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                arrow.rect.x = event.pos[0] - 20
                arrow.rect.y = event.pos[1] - 20
            if event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 20 <= x <= 509 and 480 <= y <= 515:
                    return 'as'
                k = 0
                for i in range(n):
                    if (i + 1) % 4 == 0:
                        k = 0
                    if 100 + k * 100 <= x <= 200 + k * 100 and\
                            100 + i // 3 * 100 <= y <= i // 3 * 100 + 200:
                        return i + 1
                    k += 1
        screen.fill((0, 0, 0))
        for i in range(1000):
            screen.fill(pygame.Color('white'),
                        (random.random() * WIDTH,
                         random.random() * HEIGHT, 1, 1))
        x = 0
        for i in range(n):
            if (i + 1) % 4 == 0:
                x = 0
            level_digit(100 + x * 100, 100 + i // 3 * 100, str(i + 1))
            x += 1
        inf(20, 480, "Вернуться на главный экран")
        if pygame.mouse.get_focused():
            arrow_sprite.draw(screen)
        pygame.display.flip()


def shop():
    money = open("data/results.txt", mode='rt', encoding='utf8').read().split()[0]
    pygame.mixer.music.load('data/music3.mp3')
    pygame.mixer.music.play()
    sete = open("data/product.txt", mode='rt', encoding='utf8').readlines()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                arrow.rect.x = event.pos[0] - 20
                arrow.rect.y = event.pos[1] - 20
            if event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 20 <= x <= 509 and 480 <= y <= 515:
                    return
                kx, ky = -30, 100
                for i in range(1, len(sete) + 1):
                    if i % 5 == 0:
                        kx, ky = -30, 300
                    kx += 80
                    if kx <= x <= kx + 57 and ky + 60 <= y <= ky + 80 and\
                            int(money) - int(sete[i - 1].split()[1]) >= 0:
                        sete[i - 1] = sete[i - 1].split()[0] + ' 1'
                        f = open("data/product.txt", mode='wt', encoding='utf8')
                        for j in sete:
                            f.write(j.rstrip() + '\n')
                        f.close()
                        money = str(int(money) - i * 10)
                        f = open("data/results.txt", mode='rt', encoding='utf8').read().split()
                        f[0] = str(money)
                        f1 = open("data/results.txt", mode='wt', encoding='utf8')
                        f1.write(' '.join(f))
                        f1.close()
        screen.fill((0, 0, 0))
        for i in range(1000):
            screen.fill(pygame.Color('white'),
                        (random.random() * WIDTH,
                         random.random() * HEIGHT, 1, 1))
        inf(340, 20, f"Money: {money}")
        inf(20, 480, "Вернуться на главный экран")
        kx, ky = -30, 100
        for i in range(1, len(sete) + 1):
            if i % 5 == 0:
                kx, ky = -30, 300
            kx += 80
            screen.blit(load_image(sete[i - 1].split()[0]), (kx, ky))
            if sete[i - 1].split()[1] == '0':
                inf(kx, ky + 60, f"Купить за {i * 10}", r=14)
        if pygame.mouse.get_focused():
            arrow_sprite.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    # главный экран
    pygame.init()
    pygame.display.set_caption('Игра "Зомби атакуют"')
    size = WIDTH, HEIGHT = 550, 550
    FPS = 10
    screen = pygame.display.set_mode(size)
    pygame.mixer.music.load('data/music1.mp3')
    pygame.mixer.music.play()
    pygame.mouse.set_visible(False)
    arrow = pygame.sprite.Sprite()
    arrow_image = load_image("arrow.png")
    arrow.image = arrow_image
    arrow.rect = arrow.image.get_rect()
    arrow_sprite = pygame.sprite.Group()
    arrow_sprite.add(arrow)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                arrow.rect.x = event.pos[0] - 20
                arrow.rect.y = event.pos[1] - 20
            if event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 220 <= x <= 334 and 100 <= y <= 135:
                    # переход к списку уровней
                    pygame.mixer.music.pause()
                    level = the_level_of_play()
                    if level != 'as':
                        # игра
                        clock = pygame.time.Clock()
                        all_sprites = pygame.sprite.Group()
                        tiles_group = pygame.sprite.Group()
                        player_group = pygame.sprite.Group()
                        borders = pygame.sprite.Group()
                        shots = pygame.sprite.Group()
                        enemies = pygame.sprite.Group()
                        money_group = pygame.sprite.Group()
                        player, level_x, level_y, pole = generate_level(load_level(f'map{level}.txt'))
                        play(screen)
                        pygame.mixer.music.load('data/music1.mp3')
                        pygame.mixer.music.play()
                if 206 <= x <= 348 and 200 <= y <= 234:
                    # магазин
                    shop()
                    pygame.mixer.music.load('data/music1.mp3')
                    pygame.mixer.music.play()
                if 225 <= x <= 335 and 300 <= y <= 334:
                    terminate()
        screen.fill((0, 0, 0))
        for i in range(1000):
            screen.fill(pygame.Color('white'),
                        (random.random() * WIDTH,
                         random.random() * HEIGHT, 1, 1))
        inf(220, 100, "Играть")
        inf(206, 200, "Магазин")
        inf(225, 300, "Выйти")
        if pygame.mouse.get_focused():
            arrow_sprite.draw(screen)
        pygame.display.flip()