import arcade
import pymunk
from game_logic import ImpulseVector

class Bird(arcade.Sprite):
    def __init__(
        self,
        image_path: str,
        image_scale: float,
        x: float,
        y: float,
        space: pymunk.Space,
        mass: float = 5,
        radius: float = 12,
        max_impulse: float = 180,
        power_multiplier: float = 35,
        elasticity: float = 0.8,
        friction: float = 1,
        collision_layer: int = 0
    ):
        super().__init__(image_path, image_scale)
        self.birds = arcade.SpriteList()
        self.center_x = x
        self.center_y = y
        
        self.space = space
        self.mass = mass
        self.radius = radius
        self.elasticity = elasticity
        self.friction = friction
        self.collision_layer = collision_layer
        self.max_impulse = max_impulse
        self.power_multiplier = power_multiplier
        
        self.body = None
        self.shape = None
        self.in_physics_space = False
        self.has_used_power = False
        self.impulse_vector = None 

    def add_to_physics_space(self):
        if self.in_physics_space:
            return
            
        moment = pymunk.moment_for_circle(self.mass, 0, self.radius)
        body = pymunk.Body(self.mass, moment)
        body.position = (self.center_x, self.center_y)

        shape = pymunk.Circle(body, self.radius)
        shape.elasticity = self.elasticity
        shape.friction = self.friction
        shape.collision_type = self.collision_layer

        self.space.add(body, shape)

        self.body = body
        self.shape = shape
        self.in_physics_space = True

    def launch(self, impulse_vector: ImpulseVector):
        if not self.in_physics_space:
            self.add_to_physics_space()
        
        if self.body is not None:
            impulse = min(self.max_impulse, impulse_vector.impulse) * self.power_multiplier
            impulse_pymunk = impulse * pymunk.Vec2d(1, 0)
            self.body.apply_impulse_at_local_point(impulse_pymunk.rotated(impulse_vector.angle))

    def update(self, delta_time):
        if self.in_physics_space and self.shape is not None:
            self.center_x = self.shape.body.position.x
            self.center_y = self.shape.body.position.y
            self.radians = self.shape.body.angle

    def set_position(self, x, y):
        self.center_x = x
        self.center_y = y
        if self.in_physics_space and self.body:
            self.body.position = (x, y)

class RedBird(Bird):
    def __init__(self, x: float, y: float, space: pymunk.Space):
        super().__init__("assets/img/red-bird.png", 1, x, y, space, 4.5)

    def power_up(self):
        pass

class BlueBird(Bird):
    def __init__(self, x: float, y: float, space: pymunk.Space):
        super().__init__("assets/img/blue-bird.png", 0.1, x, y, space, 4.5)
        
    def power_up(self):
        if not self.has_used_power and self.impulse_vector:
            positions = [15, -15]
            
            for position in positions:
                clone = BlueBird(self.center_x, self.center_y + position, self.space)
                clone.add_to_physics_space()
                
                angle_variation = 0.2 if position > 0 else -0.2
                modified_impulse = ImpulseVector(
                    self.impulse_vector.angle + angle_variation,
                    self.impulse_vector.impulse * 0.8
                )
                clone.launch(modified_impulse)
                self.birds.append(clone)
            
            self.has_used_power = True

class YellowBird(Bird):
    def __init__(self, x: float, y: float, space: pymunk.Space):
        super().__init__("assets/img/yellow-bird.png", 0.035, x, y, space, 4.5)

    def power_up(self):
        if not self.has_used_power and self.in_physics_space and self.body:
            boost_factor = 2.0
            current_velocity = self.body.velocity
            self.body.velocity = (current_velocity.x * boost_factor, current_velocity.y * boost_factor)
            self.has_used_power = True

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