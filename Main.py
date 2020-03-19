from random import randrange, choice
import GameObjects
import pygameMenu
import pygame
import os

# Иницилизация pygame
pygame.init()

# Инофрмация об разработчиков
ABOUT = ['Leonid  Litvinov',
         'Stepan  Fedorov']

# Определение констант

# Цвета
COLOR_BACKGROUND = (255, 104, 0)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
MENU_BACKGROUND_COLOR = (228, 55, 36)


# Выбранная сложность
DIFFICULTY = ['EASY']

# Системыне настройки
FPS = 60
WINDOW_SIZE = (0, 0)

clock = None
main_menu = None
surface = None


def change_difficulty(value, difficulty, debag=False):
    """Изменяет выбранную сложность"""

    if debag:
        selected, index = value
        print(f'Selected difficulty: "{selected}"',
              f'({difficulty}) at index {index}')

    DIFFICULTY[0] = difficulty


def play_function(difficulty, value):
    # Define globals
    global main_menu
    global clock

    pygame.mixer.music.pause()

    # Заглушка
    value = None

    # Путь до изображений к игре
    path_from_background = 'Data\\Image\\Map1.png'
    path_from_person = pygame.image.load('Data\\Image\\12345.png')
    path_from_person = pygame.transform.scale2x(path_from_person)
    path_from_zombie = ['Data\\Image\\Zombie.png',
                        'Data\\Image\\Zombie1.png',
                        'Data\\Image\\Zombie2.png',
                        'Data\\Image\\Zombie3.png',
                        'Data\\Image\\Zombie4.png']

    # Изменение игровых коэфицентов в зависимости от сложности
    if difficulty[0] == 'EASY':
        add_hp, add_speed, add_damage = 0.0625, 0.0625, 0.0625
    elif difficulty[0] == 'MEDIUM':
        add_hp, add_speed, add_damage = 0.125, 0.125, 0.125
    else:
        add_hp, add_speed, add_damage = 0.25, 0.25, 0.25

    counter_kill = 0  # Счётчик убийст зомби

    # Иницилизация групп

    # Сюда входят все обьекты кроме игрока и камеры
    all_sprite = pygame.sprite.Group()

    # Сюда входят только видимые обьекты
    visible_objects = pygame.sprite.Group()

    # Сюда входят только выстрелы
    bullet = pygame.sprite.Group()

    # Сюда входят только враги
    enemy = pygame.sprite.Group()

    # Шрифты применяющиеся в игре
    counter = pygame.font.Font(None, 48)  # Для счётчика убийст зомби
    damage_indicator = pygame.font.Font(None, 16)   # Для отображения дамага
    hp_indicator = pygame.font.Font(None, 32)  # Для отоброжения хп персонажа

    # Добавления Фона
    background = GameObjects.GameObject((0, 0), path_from_background)
    background.set_mask()
    background.disabled_alpha()
    all_sprite.add(background)
    visible_objects.add(background)

    # Добавления игрока
    person = GameObjects.Person((900, 900), path_from_person, hp=10000, speed_move=(600, 600))
    visible_objects.add(person)

    # Добавление границ
    wall_up = GameObjects.EmptyObject((0, 0), (WINDOW_SIZE[0] + 1, 1))
    wall_botton = GameObjects.EmptyObject((0, WINDOW_SIZE[1] - 1), (WINDOW_SIZE[0] + 1, 1))
    wall_left = GameObjects.EmptyObject((0, 0), (1, WINDOW_SIZE[1] + 1))
    wall_right = GameObjects.EmptyObject((WINDOW_SIZE[0] - 1, 0), (1, WINDOW_SIZE[1] + 1))

    # Создание камеры
    camera = GameObjects.TargetCamera(all_sprite, person,
                                      traffic_restriction=background.get_size(),
                                      flags=pygame.FULLSCREEN | pygame.HWSURFACE)
    screen = camera.get_screen()    # Поялучаем экран камеры

    clock = pygame.time.Clock()  # Регулятор FPS
    pause = False  # Переменная отвечающая за паузу


    counter_shot = 0
    # Основной цикл игры
    command_exit = False
    while not command_exit and person.get_hp() > 0:
        screen.fill((0, 0, 0))  # Избавление от шлейфов

        # Обрабатываем нажаните клавишь
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # По нажатию на кнопки выхода выход
                command_exit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Если нажата, остановка игры
                    pause = not pause
                if event.key == pygame.K_z:  # Если нажата +100 к счётчику
                    counter_kill += 100
                elif event.key == pygame.K_g:  # Если нажата, обнуляет счётчик
                    counter_kill = 0

        if not pause:
            # Получаем всё нажатые клавиши
            keys = pygame.key.get_pressed()
            buttons = pygame.mouse.get_pressed()

            # Обрабатываем все удержанные клавиши
            x, y = 0, 0
            if keys[pygame.K_d]:
                x += 1
            if keys[pygame.K_a]:
                x -= 1
            if keys[pygame.K_w]:
                y -= 1
            if keys[pygame.K_s]:
                y += 1
            if buttons[0]:
                if not counter_shot % 2:
                    person.shoot().add(all_sprite, visible_objects, bullet)

            if counter_shot == 999:
                counter_shot = 0

            counter_shot += 1

            # Определяем столкновение персонажа с границами
            top, botton, left, right = True, True, True, True
            if pygame.sprite.collide_rect(person, wall_up):
                top = False
            if pygame.sprite.collide_rect(person, wall_botton):
                botton = False
            if pygame.sprite.collide_rect(person, wall_left):
                left = False
            if pygame.sprite.collide_rect(person, wall_right):
                right = False

            # Устанавливаем куда персонаж не может ходить
            person.set_ability_move(top=top, botton=botton, left=left, right=right)

            # Двигаем камеру с персонажем
            camera.sled((x, y))

            # Обнавление всех обьектов
            person.update()
            all_sprite.update()

            # Добавляем зомби если их < 100
            if len(enemy) < 100:
                pos_spanw_x = randrange(-200, WINDOW_SIZE[0] * 1.5)
                if 0 < pos_spanw_x < WINDOW_SIZE[0]:
                    pos_spanw_y = -200 if randrange(2) else WINDOW_SIZE[1] * 1.5
                else:
                    pos_spanw_y = randrange(-200, WINDOW_SIZE[1] * 1.5)

                GameObjects.Enemy((pos_spanw_x, pos_spanw_y), choice(path_from_zombie), speed_move=randrange(100, round(101 + counter_kill * add_speed)),
                    target=person,
                    damage=randrange(1, round(2 + counter_kill * add_damage)),
                    rotate=(1, lambda: person.get_rect().center),
                    hp=randrange(1, round(2 + counter_kill * add_hp))).add(all_sprite, visible_objects, enemy)

            # Изменяем скорость персанажу в зависимости от убитых зомби
            person.edit_speed_move(round(600 + (counter_kill ** 0.5)))

            # Обработка столкновение зомби с персонажем
            for enem in pygame.sprite.spritecollide(person, enemy, False, collided=pygame.sprite.collide_rect):
                if pygame.sprite.collide_mask(person, enem):
                    person.hit(enem.get_damage())
                    pos = person.get_rect().center
                    indicator = GameObjects.GameObject(
                        (pos[0] + randrange(25), pos[1] + randrange(25)),
                        path_image=damage_indicator.render(
                            str(-enem.get_damage()), True, (255, 255, 0)),
                        time_life=10)
                    indicator.add(all_sprite, visible_objects)

            # Обработка пуль с зомби
            for bull, enem in pygame.sprite.groupcollide(bullet, enemy, False, False).items():
                for enemys in enem:
                    if pygame.sprite.collide_mask(bull, enemys):
                        enemys.hit(bull.get_damage())
                        pos = enemys.get_rect().center
                        indicator = GameObjects.GameObject((pos[0] + randrange(25), pos[1] + randrange(25)), path_image=damage_indicator.render(str(-enemys.get_damage()), True, (255, 0, 0)), time_life=10)
                        indicator.add(all_sprite, visible_objects)
                        if randrange(4):
                            bull.kill()
                        if not enemys.get_hp():
                            counter_kill += 1

        # Отрисовка всех элементов на экране
        visible_objects.draw(screen)
        xol = counter.render(f"Всего убито: {counter_kill}", True, [0, 0, 0])
        screen.blit(xol, (0, 0))
        xol = hp_indicator.render(f"Hp: {person.get_hp()}", True, [255, 0, 255])
        screen.blit(xol, (WINDOW_SIZE[0] - xol.get_rect().size[0], WINDOW_SIZE[1] - xol.get_rect().size[1]))
        clock.tick(FPS)
        pygame.display.flip()

    # Вывод конечного экрана и выход в меню
    screen.blit(pygame.transform.scale(pygame.image.load("Data\\Image\\End.jpg"),
                                       WINDOW_SIZE), (0, 0))
    pygame.display.flip()
    pygame.time.wait(2500)

    main_menu.reset(True)
    pygame.mixer.music.play(True)
    return


def main(test=False):
    global clock
    global main_menu
    global surface
    global WINDOW_SIZE

    def fill_background():
        """Заливка фона"""
        global surface
        surface.fill(COLOR_BACKGROUND)

    os.environ['SDL_VIDEO_CENTERED'] = '1'

    # Создание окна с названием
    surface = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)
    pygame.display.set_caption('Shooter')

    WINDOW_SIZE = surface.get_size()
    clock = pygame.time.Clock()

    cat = pygame.transform.scale(pygame.image.load('Data\\Image\\3.png'), (1000, 250))

    cat = GameObjects.GameObject((0, 0), cat, animation=(4, 1, 1, 1))
    surface.blit(cat.get_surface(), cat.get_position())

    # Содание меню
    play_menu = pygameMenu.Menu(surface,
                                bgfun=fill_background,
                                color_selected=COLOR_WHITE,
                                font=pygameMenu.font.FONT_BEBAS,
                                font_color=COLOR_BLACK,
                                font_size=30,
                                menu_alpha=100,
                                menu_color=MENU_BACKGROUND_COLOR,
                                menu_height=int(WINDOW_SIZE[1] * 0.7),
                                menu_width=int(WINDOW_SIZE[0] * 0.7),
                                onclose=pygameMenu.events.DISABLE_CLOSE,
                                option_shadow=False,
                                title='Play menu',
                                window_height=WINDOW_SIZE[1],
                                window_width=WINDOW_SIZE[0]
                                )

    play_submenu = pygameMenu.Menu(surface,
                                   bgfun=fill_background,
                                   color_selected=COLOR_WHITE,
                                   font=pygameMenu.font.FONT_BEBAS,
                                   font_color=COLOR_BLACK,
                                   font_size=30,
                                   menu_alpha=100,
                                   menu_color=MENU_BACKGROUND_COLOR,
                                   menu_height=int(WINDOW_SIZE[1] * 0.5),
                                   menu_width=int(WINDOW_SIZE[0] * 0.7),
                                   option_shadow=False,
                                   title='Submenu',
                                   window_height=WINDOW_SIZE[1],
                                   window_width=WINDOW_SIZE[0]
                                   )
    play_submenu.add_option('Back', pygameMenu.events.BACK)
    play_menu.add_option('Start',
                         play_function,
                         DIFFICULTY,
                         pygame.font.Font(pygameMenu.font.FONT_FRANCHISE, 30))
    play_menu.add_selector('Select difficulty',
                           [('1 - Easy', 'EASY'),
                            ('2 - Medium', 'MEDIUM'),
                            ('3 - Hard', 'HARD')],
                           onchange=change_difficulty,
                           selector_id='select_difficulty')
    play_menu.add_option('Return to main menu', pygameMenu.events.BACK)
    about_menu = pygameMenu.TextMenu(surface,
                                     bgfun=fill_background,
                                     color_selected=COLOR_WHITE,
                                     font=pygameMenu.font.FONT_BEBAS,
                                     font_color=COLOR_BLACK,
                                     font_size_title=30,
                                     font_title=pygameMenu.font.FONT_8BIT,
                                     menu_color=MENU_BACKGROUND_COLOR,
                                     menu_color_title=COLOR_WHITE,
                                     menu_height=int(WINDOW_SIZE[1] * 0.6),
                                     menu_width=int(WINDOW_SIZE[0] * 0.6),
                                     onclose=pygameMenu.events.DISABLE_CLOSE,
                                     option_shadow=False,
                                     text_color=COLOR_BLACK,
                                     text_fontsize=50,
                                     title='About',
                                     window_height=WINDOW_SIZE[1],
                                     window_width=WINDOW_SIZE[0]
                                     )

    # Добавление информации об авторах
    for m in ABOUT:
        about_menu.add_line(m)

    about_menu.add_line(pygameMenu.locals.TEXT_NEWLINE)
    about_menu.add_option('Return to menu', pygameMenu.events.BACK)
    main_menu = pygameMenu.Menu(surface,
                                bgfun=fill_background,
                                color_selected=COLOR_WHITE,
                                font=pygameMenu.font.FONT_BEBAS,
                                font_color=COLOR_BLACK,
                                font_size=30,
                                menu_alpha=100,
                                menu_color=MENU_BACKGROUND_COLOR,
                                menu_height=int(WINDOW_SIZE[1] * 0.6),
                                menu_width=int(WINDOW_SIZE[0] * 0.6),
                                onclose=pygameMenu.events.DISABLE_CLOSE,
                                option_shadow=False,
                                title='Main menu',
                                window_height=WINDOW_SIZE[1],
                                window_width=WINDOW_SIZE[0]
                                )

    # Добавление кнопок в меню
    main_menu.add_option('Play', play_menu)
    main_menu.add_option('About', about_menu)
    main_menu.add_option('Quit', pygameMenu.events.EXIT)

    pygame.mixer.music.load('Data\\Sound\\lolka.ogg')
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(True)



    # Игровой цикл
    while True:
        # обработка событий
        cat.update()

        main_menu.mainloop(disable_loop=True)
        surface.blit(cat.get_surface(), cat.get_position())

        # Обновление экрана
        pygame.display.flip()


main()
