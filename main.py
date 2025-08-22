import math
import logging
import arcade
import pymunk

from game_object import Bird, RedBird, BlueBird, YellowBird, Column, Pig, Sling
from game_logic import get_impulse_vector, Point2D, get_distance

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("arcade").setLevel(logging.WARNING)
logging.getLogger("pymunk").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

logger = logging.getLogger("main")

WIDTH = 900
HEIGHT = 400
TITLE = "Angry Birds Demo"
GRAVITY = -500
MAX_DRAG_DISTANCE = 100
SLING_POS = Point2D(140, 75)

class App(arcade.View):
    def __init__(self):
        super().__init__()
        self.flying_bird = None
        self.background = arcade.load_texture("assets/img/background.png")
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)

        # agregar piso
        floor_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        floor_shape = pymunk.Segment(floor_body, [0, 10], [WIDTH, 10], 0.0) # type: ignore
        floor_shape.friction = 100
        self.space.add(floor_body, floor_shape)

        self.game_level = 3
        self.set_initial_position = True

        self.birds = arcade.SpriteList()
        self.pigs = arcade.SpriteList()
        self.world = arcade.SpriteList()
        self.current_birds = arcade.SpriteList()
        self.add_columns()
        self.add_pigs()
        self.add_birds()

        self.sling = Sling(0.65, 150, 30, self.space)
        self.world.append(self.sling)

        self.start_point = Point2D()
        self.end_point = Point2D()
        self.distance = 0
        self.draw_line = False
        self.ended = False

        # agregar un collision handler
        self.handler = self.space.add_default_collision_handler()
        self.handler.post_solve = self.collision_handler

    def collision_handler(self, arbiter, space, data):
        impulse_norm = arbiter.total_impulse.length
        if impulse_norm < 100:
            return True
        ##logger.debug(impulse_norm)
        if impulse_norm > 1000:
            for pig in self.pigs:
                if pig.shape in arbiter.shapes:
                    self.pigs.remove(pig)
                    self.space.remove(pig.shape, pig.body)

        return True

    def add_birds(self): 
        initial_data = (50, 50, self.space)
        red_bird = RedBird(*initial_data)
        blue_bird = BlueBird(*initial_data) 
        yellow_bird = YellowBird(*initial_data) 
        self.birds.append(blue_bird)
        self.birds.append(red_bird)
        self.birds.append(yellow_bird)

        self.set_initial_position = True
        self.current_birds.append(self.birds[0])

    def add_columns(self):
        spacing = max(100, 300 - self.game_level * 40)
        for x in range(WIDTH // 2, WIDTH, spacing):
            column = Column(x, 50, self.space)
            self.world.append(column)

    def add_pigs(self):
        spacing = max(100, 300 - self.game_level * 40)
        for x in range(WIDTH // 2, WIDTH, spacing):
            pig = Pig(x, 90, self.space)
            self.pigs.append(pig)

    def on_update(self, delta_time: float):
        self.space.step(1 / 60.0)
        self.update_collisions()

        self.pigs.update(delta_time)
        self.birds.update(delta_time)
        self.world.update(delta_time)

        for sprite in list(self.world) + list(self.pigs) + list(self.birds):
            if sprite.center_x < 0 or sprite.center_x > WIDTH or sprite.center_y < 0 or sprite.center_y > HEIGHT:
                try:
                    self.space.remove(sprite.shape, sprite.body)
                except Exception:
                    pass
                if sprite in self.world:
                    self.world.remove(sprite)
                if sprite in self.pigs:
                    self.pigs.remove(sprite)
                if sprite in self.birds:
                    self.birds.remove(sprite)

        if not self.pigs:
            self.ended = True
            while self.world:
                self.world.pop()
            while self.birds:
                self.birds.pop()

    def update_collisions(self):
        pass

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            arcade.close_window()
        elif symbol == arcade.key.SPACE and self.flying_bird:
            if not self.flying_bird.has_used_power:
                self.flying_bird.power_up()

                for bird in self.flying_bird.birds:
                    self.world.append(bird)
                    self.birds.append(bird)
                ##logger.debug(f"Bird {self.flying_bird.__class__.__name__} used its power-up")

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and self.birds:
            self.start_point = Point2D(140, 75)
            self.end_point = Point2D(x, y)
            self.draw_line = True
            
            # self.current_birds.append(self.birds[0])
            ##logger.debug(f"Start drag with bird at: {self.start_point}")

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if buttons == arcade.MOUSE_BUTTON_LEFT and self.birds:
            raw_point = Point2D(x, y)

            dist = get_distance(SLING_POS, raw_point)
            if dist > MAX_DRAG_DISTANCE:
                angle = math.atan2(raw_point.y - SLING_POS.y, raw_point.x - SLING_POS.x)
                new_x = SLING_POS.x + math.cos(angle) * MAX_DRAG_DISTANCE
                new_y = SLING_POS.y + math.sin(angle) * MAX_DRAG_DISTANCE
                self.end_point = Point2D(new_x, new_y)
            else:
                self.end_point = raw_point

            if self.birds and self.current_birds:
                self.current_birds[0].set_position(self.end_point.x, self.end_point.y)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT and self.birds:
            #logger.debug(f"Releasing bird from: {self.end_point}")
            self.draw_line = False
            
            impulse_vector = get_impulse_vector(self.end_point, self.start_point)
            if self.birds and self.current_birds:
                self.current_birds[0].impulse_vector = impulse_vector
                self.current_birds[0].launch(impulse_vector)
            
            self.world.append(self.current_birds[0])
            self.flying_bird = self.current_birds[0]
            self.birds.pop(0)
            
            self.current_birds.pop()

            if self.birds:
                self.current_birds.append(self.birds[0])
            self.set_initial_position = True

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.background, arcade.LRBT(0, WIDTH, 0, HEIGHT))
        self.pigs.draw()
        self.world.draw()
        if self.current_birds:
            self.current_birds.draw()
            if self.set_initial_position:
                self.current_birds[0].set_position(125, 48)
                self.set_initial_position = False
        if self.draw_line:
            arcade.draw_line(self.start_point.x, self.start_point.y, self.end_point.x, self.end_point.y, arcade.color.DARK_BROWN, 3)
            arcade.draw_line(self.start_point.x - 35, self.start_point.y, self.end_point.x, self.end_point.y, arcade.color.DARK_BROWN, 3)

class StartView(arcade.View):
    def __init__(self):
        super().__init__()
        self.background = arcade.load_texture("assets/img/background.png")
        self.play_button = arcade.Sprite("assets/img/play-button.png", scale=0.3)
        self.play_button.center_x = WIDTH // 2
        self.play_button.center_y = HEIGHT // 2

        self.sprites = arcade.SpriteList()
        self.sprites.append(self.play_button)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(self.background, arcade.LRBT(0, WIDTH, 0, HEIGHT))
        self.sprites.draw()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
               arcade.close_window()
        if symbol == arcade.key.SPACE:
            game_view = App()
            self.window.show_view(game_view)

def main():
    window = arcade.Window(WIDTH, HEIGHT, TITLE)
    start = StartView()
    window.show_view(start)
    arcade.run()

if __name__ == "__main__":
    main()