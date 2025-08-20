import arcade
import pymunk
from game_logic import ImpulseVector

class Bird(arcade.Sprite):
    def __init__(
        self,
        image_path: str,
        image_scale: float,
        impulse_vector: ImpulseVector,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 5,
        radius: float = 12,
        max_impulse: float = 100,
        power_multiplier: float = 40,
        elasticity: float = 0.8,
        friction: float = 1,
        collision_layer: int = 0,
    ):
        super().__init__(image_path, image_scale)
        moment = pymunk.moment_for_circle(mass, 0, radius)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)

        self.initial_impulse_vector = impulse_vector
        self.max_impulse = max_impulse
        self.power_multiplier = power_multiplier

        shape = pymunk.Circle(body, radius)
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer

        space.add(body, shape)

        self.body = body
        self.shape = shape

    def launch(self, impulse_vector: ImpulseVector):
        impulse = min(self.max_impulse, impulse_vector.impulse) * self.power_multiplier
        impulse_pymunk = impulse * pymunk.Vec2d(1, 0)
        self.body.apply_impulse_at_local_point(impulse_pymunk.rotated(impulse_vector.angle))

    def update(self, delta_time):
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle

    def power_up(self):
        pass

class RedBird(Bird):
    def __init__(self, x: float, y: float, space: pymunk.Space):
        impulse_vector = ImpulseVector(angle=0, impulse=0)
        super().__init__("assets/img/red-bird.png", 1, impulse_vector, x, y, space)

    def power_up(self):
        pass
        ##This class should not have a change with the power_up method,

class BlueBird(Bird):
    def __init__(self, x: float, y: float, space: pymunk.Space):
        impulse_vector = ImpulseVector(angle=0, impulse=0)
        super().__init__("assets/img/blue-bird.png", 0.1, impulse_vector, x, y, space)
    
    def power_up(self):
        pass
        ##This class should create 3 birds when the power_up method is called,

class YellowBird(Bird):
    def __init__(self, x: float, y: float, space: pymunk.Space):
        impulse_vector = ImpulseVector(angle=0, impulse=0)
        super().__init__("assets/img/yellow-bird.png", 0.035, impulse_vector, x, y, space)

    def power_up(self):
        pass
        ##This class should double the impulse of the bird when the power_up method is called,

class Pig(arcade.Sprite):
    def __init__(
        self,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 2,
        elasticity: float = 0.8,
        friction: float = 0.4,
        collision_layer: int = 0,
    ):
        super().__init__("assets/img/pig.png", 0.1)
        moment = pymunk.moment_for_circle(mass, 0, self.width / 2 - 3)
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        shape = pymunk.Circle(body, self.width / 2 - 3)
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer
        space.add(body, shape)
        self.body = body
        self.shape = shape

    def update(self, delta_time):
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle


class PassiveObject(arcade.Sprite):
    """
    Passive object that can interact with other objects.
    """
    def __init__(
        self,
        image_path: str,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 2,
        elasticity: float = 0.8,
        friction: float = 1,
        collision_layer: int = 0,
    ):
        super().__init__(image_path, 1)

        moment = pymunk.moment_for_box(mass, (self.width, self.height))
        body = pymunk.Body(mass, moment)
        body.position = (x, y)
        shape = pymunk.Poly.create_box(body, (self.width, self.height))
        shape.elasticity = elasticity
        shape.friction = friction
        shape.collision_type = collision_layer
        space.add(body, shape)
        self.body = body
        self.shape = shape

    def update(self, delta_time):
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.radians = self.shape.body.angle


class Column(PassiveObject):
    def __init__(self, x, y, space):
        super().__init__("assets/img/column.png", x, y, space)

class StaticObject(arcade.Sprite):
    def __init__(
            self,
            image_path: str,
            image_scale: float,
            x: float,
            y: float,
            space: pymunk.Space,
            mass: float = 2,
            elasticity: float = 0.8,
            friction: float = 1,
            collision_layer: int = 0,
    ):
        super().__init__(image_path, image_scale, x, y)

class Sling(StaticObject):
    def __init__(self, image_scale, x, y, space: pymunk.Space):
        super().__init__("assets/img/sling.png", image_scale, x, y, space)