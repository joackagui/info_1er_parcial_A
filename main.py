import math
import logging
import random
import arcade
import pymunk

from game_object import Beam, Bird, RedBird, BlueBird, YellowBird, Column, Pig, Sling
from game_logic import get_impulse_vector, Point2D, get_distance

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("arcade").setLevel(logging.WARNING)
logging.getLogger("pymunk").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

logger = logging.getLogger("main")

WIDTH = 1000
HEIGHT = 500
TITLE = "Angry Birds Demo"
GRAVITY = -500
MAX_DRAG_DISTANCE = 100
SLING_POS = Point2D(160, 30)

def check_button_resize(button: arcade.Sprite, x: float, y: float, base_scale: float, hover_scale: float):
    if button.collides_with_point((x, y)):
        button.scale = hover_scale
    else:
        button.scale = base_scale

# Clase del Juego (App)
class App(arcade.View):
    def __init__(self, game_level: int):
        super().__init__()
        self.flying_bird:Bird
        self.bird_on_sling: Bird
        self.background = arcade.load_texture("assets/img/background.png")
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)

        # Piso
        floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        floor_shape = pymunk.Segment(floor_body, [0, 10], [WIDTH, 10], 0.0) #type: ignore
        floor_shape.friction = 100
        self.space.add(floor_body, floor_shape)

        self.game_level = game_level
        self.draw_sling_bird = True

        # Manejo de los pájaros
        self.birds = arcade.SpriteList()
        self.pigs = arcade.SpriteList()
        self.world = arcade.SpriteList()

        self.generate_world()

        self.sling = Sling(0.65, SLING_POS.x, SLING_POS.y, self.space)
        self.world.append(self.sling)

        self.start_point = Point2D()
        self.end_point = Point2D()
        self.distance = 0
        self.draw_line = False
        self.ended = False

        self.level_failed = False
        self.level_won = False
        self.waiting_for_result = False
        self.result_timer = 0.0


        # Cooldown de 1 segundo para evitar clicks fantasma
        self.cooldown = 0.5
        self.time_since_start = 0.0

        # Handler de colisiones
        self.handler = self.space.add_default_collision_handler()
        self.handler.post_solve = self.collision_handler

        # Botones despues de jugar
        self.replay_button = arcade.Sprite("assets/img/replay-button.png", scale=0.15)
        self.replay_button.center_x = WIDTH // 2 - 150
        self.replay_button.center_y = HEIGHT // 2

        self.menu_button = arcade.Sprite("assets/img/menu-button.png", scale=0.15)
        self.menu_button.center_x = WIDTH // 2 + 150
        self.menu_button.center_y = HEIGHT // 2

        self.next_level_button = arcade.Sprite("assets/img/next-level-button.png", scale=0.15)
        self.next_level_button.center_x = WIDTH // 2
        self.next_level_button.center_y = HEIGHT // 2

        self.show_end_buttons = False

    def collision_handler(self, arbiter, space, data):
        impulse_norm = arbiter.total_impulse.length
        if impulse_norm < 100:
            return True
        if impulse_norm > 1000:
            for pig in self.pigs:
                if pig.shape in arbiter.shapes:
                    arcade.play_sound(pig.death_sound)
                    self.pigs.remove(pig)
                    self.space.remove(pig.shape, pig.body)
        return True

    # Generar los componentes que se van a mostrar
    def generate_world(self):
        self.add_columns()
        self.add_pigs()
        self.add_birds()

    # Añadir pájaros
    def add_birds(self):
        initial_data = (50, 50, self.space)
        red_bird = RedBird(*initial_data)
        blue_bird = BlueBird(*initial_data)
        yellow_bird = YellowBird(*initial_data)
        birds = [red_bird, blue_bird, yellow_bird]
        # Poner los pájaros de forma aleatoria
        random.shuffle(birds)

        for bird in birds: self.birds.append(bird)
            
        self.draw_sling_bird = True
        self.bird_on_sling = self.birds[0]

    # Añadir estructuras
    def add_columns(self):
        if self.game_level == 1:
            column = Column(WIDTH - 100, 50, self.space)
            self.world.append(column)
        elif self.game_level == 2:
            column1 = Column(WIDTH - 100, 50, self.space)
            column2 = Column(WIDTH - 200, 50, self.space)
            self.world.append(column1)
            self.world.append(column2)
        elif self.game_level == 3:
            column1 = Column(WIDTH - 120, 50, self.space)
            column2 = Column(WIDTH - 180, 50, self.space)
            beam = Beam(WIDTH - 150, 100, self.space)
            self.world.append(column1)
            self.world.append(column2)
            self.world.append(beam)
        elif self.game_level == 4:
            beam1 = Beam(WIDTH - 150, 50, self.space)
            beam2 = Beam(WIDTH - 300, 50, self.space)
            beam3 = Beam(WIDTH - 175, 75, self.space)
            beam4 = Beam(WIDTH - 275, 75, self.space)
            beam5 = Beam(WIDTH - 225, 100, self.space)
            self.world.append(beam1)
            self.world.append(beam2)
            self.world.append(beam3)
            self.world.append(beam4)
            self.world.append(beam5)
        elif self.game_level == 5:
            for i in range(2):
                column1 = Column(WIDTH - 120, 50 + 100*i, self.space)
                column2 = Column(WIDTH - 180, 50 + 100*i, self.space)
                beam = Beam(WIDTH - 150, 100 + 100*i, self.space)
                self.world.append(column1)
                self.world.append(column2)
                self.world.append(beam)
        elif self.game_level == 6:
            spacing = max(100, 300 - self.game_level * 40)
            for x in range(WIDTH // 2, WIDTH, spacing):
                column = Column(x, 50, self.space)
                beam = Beam(x, 100, self.space)
                self.world.append(column)
                self.world.append(beam)

    # Añadir cerdos
    def add_pigs(self):
        if self.game_level == 1:
            pig1 = Pig(WIDTH - 200, 20, self.space)
            pig2 = Pig(WIDTH - 100, 90, self.space)
            self.pigs.append(pig1)
            self.pigs.append(pig2)
        elif self.game_level == 2:
            pig1 = Pig(WIDTH - 300, 20, self.space)
            pig2 = Pig(WIDTH - 200, 90, self.space)
            pig3 = Pig(WIDTH - 100, 90, self.space)
            self.pigs.append(pig1)
            self.pigs.append(pig2)
            self.pigs.append(pig3)
        elif self.game_level == 3:
            pig1 = Pig(WIDTH - 150, 120, self.space)
            pig2 = Pig(WIDTH - 150, 20, self.space)
            self.pigs.append(pig1)
            self.pigs.append(pig2)
        elif self.game_level == 4:
            pig1 = Pig(WIDTH - 225, 20, self.space)
            pig2 = Pig(WIDTH - 225, 120, self.space)
            self.pigs.append(pig1)
            self.pigs.append(pig2)
        elif self.game_level == 5:
            pig1 = Pig(WIDTH - 150, 20, self.space)
            pig2 = Pig(WIDTH - 150, 120, self.space)
            pig3 = Pig(WIDTH - 150, 220, self.space)
            self.pigs.append(pig1)
            self.pigs.append(pig2)
            self.pigs.append(pig3)
        elif self.game_level == 6:
            spacing = max(100, 300 - self.game_level * 40)
            for x in range(WIDTH // 2, WIDTH, spacing):
                pig = Pig(x, 120, self.space)
                self.pigs.append(pig)

    def update_collisions(self):
        pass

    # Reproducir la música del nivel al entrar al view
    def on_show_view(self):
        self.game_music = arcade.load_sound("assets/msc/game-music.mp3")
        self.game_music_player = arcade.play_sound(self.game_music, loop=True, volume=0.5)

    # Detener la música
    def on_hide_view(self):
        if self.game_music_player:
            arcade.stop_sound(self.game_music_player)

    # Dibujar la cuerda para cuando se haga click
    def on_mouse_press(self, x, y, button, modifiers):
        # Pequeño cooldown para que no haya problemas al hacer click al entrar al nivel
        if self.time_since_start < self.cooldown:
            return
        if button == arcade.MOUSE_BUTTON_LEFT and self.birds:
            self.start_point = Point2D(SLING_POS.x - 10, SLING_POS.y + 45)
            self.end_point = Point2D(x, y)
            self.draw_line = True

            if not self.ended:
                self.sling_strech = arcade.load_sound("assets/msc/slingshot-streched.mp3")
                arcade.play_sound(self.sling_strech)

        if self.show_end_buttons:
            if self.replay_button.collides_with_point((x, y)):
                # Reiniciar nivel actual
                game_view = App(self.game_level)
                self.window.show_view(game_view)
                return

            if self.menu_button.collides_with_point((x, y)):
                from __main__ import LevelSelectView
                next_level = self.game_level
                if self.level_won:
                    next_level += 1 
                level_select = LevelSelectView(next_level)
                self.window.show_view(level_select)
                return
            
            if self.next_level_button.collides_with_point((x, y)):
                # Jugar el siguiente nivel
                if self.level_won:
                    game_view = App(self.game_level + 1)
                    self.window.show_view(game_view)
                    return

    # El pájaro y la cuerda siguen el mouse sin superar el límite
    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if self.time_since_start < self.cooldown:
            return
        if buttons == arcade.MOUSE_BUTTON_LEFT and self.birds:
            initial_x = Point2D(x, y)
            dist = get_distance(SLING_POS, initial_x)
            if dist > MAX_DRAG_DISTANCE:
                angle = math.atan2(initial_x.y - SLING_POS.y, initial_x.x - SLING_POS.x)
                new_x = SLING_POS.x + math.cos(angle) * MAX_DRAG_DISTANCE
                new_y = SLING_POS.y + math.sin(angle) * MAX_DRAG_DISTANCE
                self.end_point = Point2D(new_x, new_y)
            else:
                self.end_point = initial_x

            if self.birds and self.bird_on_sling:
                self.bird_on_sling.set_position(self.end_point.x, self.end_point.y)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        # Lanzar el pájaro hacia la dirección del mouse y actualizar la lista de pájaros
        if self.time_since_start < self.cooldown:
            return
        if button == arcade.MOUSE_BUTTON_LEFT and self.birds:
            self.draw_line = False
            impulse_vector = get_impulse_vector(self.end_point, self.start_point)
            if self.birds and self.bird_on_sling:
                self.bird_on_sling.impulse_vector = impulse_vector
                self.bird_on_sling.launch(impulse_vector)
            self.world.append(self.bird_on_sling)
            arcade.play_sound(self.bird_on_sling.flying_sound, volume=0.7)
            self.flying_bird = self.bird_on_sling
            self.birds.pop(0)
            if self.birds:
                self.bird_on_sling = self.birds[0]
            self.draw_sling_bird = True

            # Si ya no quedan pájaros, inicia el contador
            if not self.birds:
                self.waiting_for_result = True
                self.result_timer = 0.0

    def on_mouse_motion(self, x, y, dx, dy):
        check_button_resize(self.replay_button, x, y, 0.15, 0.20)
        check_button_resize(self.next_level_button, x, y, 0.15, 0.20)
        check_button_resize(self.menu_button, x, y, 0.15, 0.20)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(LevelSelectView(self.game_level))
        ## Usar el power-up
        elif symbol == arcade.key.SPACE and self.flying_bird:
            if not self.flying_bird.has_used_power:
                self.flying_bird.power_up()
                for bird in self.flying_bird.birds:
                    self.world.append(bird)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.background, arcade.LRBT(0, WIDTH, 0, HEIGHT))
        self.pigs.draw()
        self.world.draw()
        # Dibujar al próximo pájaro a ser lanzado
        if self.bird_on_sling:
            arcade.draw_sprite(self.bird_on_sling)
            if self.draw_sling_bird:
                self.bird_on_sling.set_position(SLING_POS.x - 25, SLING_POS.y + 18)
                self.draw_sling_bird = False
        # Dibujar la cuerda
        if self.draw_line:
            arcade.draw_line(SLING_POS.x - 10, SLING_POS.y + 45, self.end_point.x, self.end_point.y, arcade.color.DARK_BROWN, 3)
            arcade.draw_line(SLING_POS.x - 42, SLING_POS.y + 45, self.end_point.x, self.end_point.y, arcade.color.DARK_BROWN, 3)
        # Dibujar botones de reinicio o del menu
        if self.show_end_buttons:
            arcade.draw_sprite(self.replay_button)
            arcade.draw_sprite(self.menu_button)
            if self.level_won:
                arcade.draw_sprite(self.next_level_button)

    def on_update(self, delta_time: float):
        self.time_since_start += delta_time
        self.space.step(1 / 60.0)
        self.update_collisions()

        self.pigs.update(delta_time)
        self.birds.update(delta_time)
        self.world.update(delta_time)

        # Remover sprites fuera de pantalla
        for sprite in list(self.world) + list(self.pigs) + list(self.birds):
            if sprite.center_x < 0 or sprite.center_x > WIDTH or sprite.center_y < 0 or sprite.center_y > HEIGHT:
                try:
                    self.space.remove(sprite.shape, sprite.body)
                except Exception:
                    pass
                if sprite in self.world:
                    self.world.remove(sprite)
                if sprite in self.pigs:
                    arcade.play_sound(sprite.death_sound)
                    self.pigs.remove(sprite)
                if sprite in self.birds:
                    self.birds.remove(sprite)

        # Verificar si todos los cerdos muertos
        if not self.pigs and not self.ended:
            self.ended = True
            self.level_won = True
            self.show_end_buttons = True
            self.victory_music = arcade.load_sound("assets/msc/level-completed.mp3")
            arcade.play_sound(self.victory_music, volume=0.5)

        # Esperar despues de lanzar el último pájaro, si aún hay cerdos, se considera derrota
        if self.waiting_for_result and not self.ended:
            self.result_timer += delta_time
            # Pasaron los 3 segundos de espera
            if self.result_timer >= 3:
                self.waiting_for_result = False
                if self.pigs:
                    self.ended = True
                    self.level_failed = True
                    self.show_end_buttons = True

# Vista de Selector de Niveles
class LevelSelectView(arcade.View):
    def __init__(self, next_level):
        super().__init__()
        self.background = arcade.load_texture("assets/img/background.png")
        self.level_buttons = arcade.SpriteList()
        self.next_level = next_level

        start_x = 100
        start_y = 250
        spacing_x = (WIDTH - 200) //5
        # Dibujar los botones para selccionar el nivel
        for i in range(6):
            button = arcade.Sprite(f"assets/img/level-{i+1}.png", scale=0.15)
            button.center_x = start_x + i * spacing_x
            button.center_y = start_y
            setattr(button, "level_number", i + 1)
            self.level_buttons.append(button)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.background, arcade.LRBT(0, WIDTH, 0, HEIGHT))
        self.level_buttons.draw()

    # Al presionar sobre un boton te lleva a la pantalla del juego con el nivel seleccionado
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            for btn in self.level_buttons:
                if btn.collides_with_point((x, y)):
                    if btn.level_number <= self.next_level:
                        game_view = App(btn.level_number)
                        self.window.show_view(game_view)
                    else:
                        self.music = arcade.load_sound("assets/msc/error.mp3")
                        self.music_player = arcade.play_sound(self.music, volume=0.6)

    def on_mouse_motion(self, x, y, dx, dy):
        for btn in self.level_buttons:
            check_button_resize(btn, x, y, 0.15, 0.20)


    # Regresar a la Pantalla Inicial
    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(StartView())

# Vista de Inicio
class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = arcade.load_texture("assets/img/background.png")
        self.play_button = arcade.Sprite("assets/img/play-button.png", scale=0.3)
        self.play_button.center_x = WIDTH // 2
        self.play_button.center_y = HEIGHT // 2 - 100
        self.title = arcade.Sprite("assets/img/angry-birds-logo.png", scale=0.3)
        self.title.center_x = WIDTH // 2
        self.title.center_y = HEIGHT // 2 + 100

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.background, arcade.LRBT(0, WIDTH, 0, HEIGHT))
        arcade.draw_sprite(self.title)
        arcade.draw_sprite(self.play_button)

    # Reproducir la música inicial entrar al view
    def on_show_view(self):
        self.music = arcade.load_sound("assets/msc/main-theme.mp3")
        self.music_player = arcade.play_sound(self.music, loop = True, volume=0.5)

    # Detener la música
    def on_hide_view(self):
        if self.music_player:
            arcade.stop_sound(self.music_player)

    # Al presionar el boton de inicio se cambia al view de los niveles
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.play_button.collides_with_point((x, y)):
                level_view = LevelSelectView(1)
                self.window.show_view(level_view)

    def on_mouse_motion(self, x, y, dx, dy):
        check_button_resize(self.play_button, x, y, 0.3, 0.35)

    # Key-button para cerrar la pestaña
    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()

# Main
def main():
    window = arcade.Window(WIDTH, HEIGHT, TITLE)
    start = StartView()
    window.show_view(start)
    arcade.run()

if __name__ == "__main__":
    main()
