import pygame


class Block:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        color,
        speed=0,
        is_debris=False,
        velocity_y=0,
        rotation=0,
        rotation_speed=0
    ):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.color = color
        self.speed = speed
        self.direction = 1

        # Debris properties
        self.is_debris = is_debris
        self.velocity_y = float(velocity_y)
        self.rotation = float(rotation)
        self.rotation_speed = float(rotation_speed)

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x),
            int(self.y),
            int(self.width),
            int(self.height)
        )

    def update(self, screen_width):
        # Normal moving block
        if not self.is_debris:
            if self.speed == 0:
                return

            self.x += self.speed * self.direction

            if self.x <= 20:
                self.x = 20
                self.direction = 1

            elif self.x + self.width >= screen_width - 20:
                self.x = screen_width - 20 - self.width
                self.direction = -1

        # Falling debris
        else:
            gravity = 0.45

            self.velocity_y += gravity
            self.y += self.velocity_y

            self.rotation += self.rotation_speed

            # Small horizontal drift
            self.x += 0.5

    def render(self, surface):
        # Normal block
        if not self.is_debris:
            draw_rect = self.rect

            pygame.draw.rect(
                surface,
                self.color,
                draw_rect,
                border_radius=4
            )

            pygame.draw.rect(
                surface,
                (245, 245, 250),
                draw_rect,
                width=2,
                border_radius=4
            )

            return

        # Rotating debris
        debris_surface = pygame.Surface(
            (int(self.width), int(self.height)),
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            debris_surface,
            self.color,
            (0, 0, int(self.width), int(self.height)),
            border_radius=4
        )

        pygame.draw.rect(
            debris_surface,
            (245, 245, 250),
            (0, 0, int(self.width), int(self.height)),
            width=2,
            border_radius=4
        )

        rotated_surface = pygame.transform.rotate(
            debris_surface,
            self.rotation
        )

        rotated_rect = rotated_surface.get_rect(
            center=(
                int(self.x + self.width / 2),
                int(self.y + self.height / 2)
            )
        )

        surface.blit(rotated_surface, rotated_rect)