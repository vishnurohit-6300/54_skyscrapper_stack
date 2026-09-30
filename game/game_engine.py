import random
import pygame
from game.block import Block


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.block_height = 28
        self.base_width = 180

        self.font_title = pygame.font.SysFont(None, 38)
        self.font_hud = pygame.font.SysFont(None, 28)
        self.font_big = pygame.font.SysFont(None, 46)
        self.font_perfect = pygame.font.SysFont(None, 42)

        self.reset()

    def get_color(self, index):
        palette = [
            (230, 75, 75),
            (240, 140, 45),
            (245, 210, 50),
            (60, 195, 110),
            (50, 150, 240),
            (165, 80, 225),
        ]
        return palette[index % len(palette)]

    def reset(self):
        self.score = 0
        self.game_over = False
        self.perfect_streak = 0
        self.perfect_popup_timer = 0

        self.debris = []

        base_x = (self.width - self.base_width) // 2
        base_y = self.height - 60

        base_block = Block(
            base_x,
            base_y,
            self.base_width,
            self.block_height,
            self.get_color(0),
            speed=0
        )

        self.stack = [base_block]

        self.spawn_active_block()

    def spawn_active_block(self):
        top_block = self.stack[-1]

        next_y = top_block.y - self.block_height - 4
        speed = min(10.0, 4.5 + (len(self.stack) * 0.35))
        color = self.get_color(len(self.stack))

        start_x = (
            25
            if random.choice([True, False])
            else self.width - 25 - top_block.width
        )

        self.active_block = Block(
            start_x,
            next_y,
            top_block.width,
            self.block_height,
            color,
            speed=speed
        )

    def create_debris(self, x, y, width, color):
        if width <= 0:
            return

        debris = Block(
            x,
            y,
            width,
            self.block_height,
            color,
            speed=0,
            is_debris=True,
            velocity_y=-2.0,
            rotation=0,
            rotation_speed=random.choice([-6, -4, 4, 6])
        )

        self.debris.append(debris)

    def drop_block(self):
        if self.game_over:
            return

        top_block = self.stack[-1]
        act = self.active_block

        left = max(act.x, top_block.x)
        right = min(
            act.x + act.width,
            top_block.x + top_block.width
        )

        overlap = right - left

        is_successful_drop = overlap > 0

        if is_successful_drop:

            # PERFECT PLACEMENT
            is_perfect = abs(act.x - top_block.x) <= 3

            if is_perfect:
                new_x = top_block.x
                new_width = top_block.width

                new_block = Block(
                    new_x,
                    act.y,
                    new_width,
                    self.block_height,
                    act.color,
                    speed=0
                )

                self.stack.append(new_block)

                self.score += 3
                self.perfect_streak += 1
                self.perfect_popup_timer = 45

                if self.perfect_streak >= 3:
                    expanded_width = min(
                        self.base_width,
                        new_block.width + 10
                    )
                    new_block.width = expanded_width

            else:
                self.perfect_streak = 0

                # LEFT OVERHANG
                if act.x < top_block.x:
                    debris_width = top_block.x - act.x

                    self.create_debris(
                        act.x,
                        act.y,
                        debris_width,
                        act.color
                    )

                # RIGHT OVERHANG
                elif act.x + act.width > top_block.x + top_block.width:
                    debris_x = top_block.x + top_block.width

                    debris_width = (
                        act.x + act.width
                        - (top_block.x + top_block.width)
                    )

                    self.create_debris(
                        debris_x,
                        act.y,
                        debris_width,
                        act.color
                    )

                trimmed_width = max(10.0, overlap)

                new_block = Block(
                    left,
                    act.y,
                    trimmed_width,
                    self.block_height,
                    act.color,
                    speed=0
                )

                self.stack.append(new_block)
                self.score += 1

            if new_block.y < 180:
                shift_amount = self.block_height + 4

                for b in self.stack:
                    b.y += shift_amount

            self.spawn_active_block()

        else:
            self.game_over = True
            self.perfect_streak = 0

    def handle_event(self, event):
        if self.game_over:
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_r
            ) or (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                self.reset()

            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.drop_block()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.drop_block()

    def update(self):
        if not self.game_over:
            self.active_block.update(self.width)

        for debris in self.debris:
            debris.update(self.width)

        self.debris = [
            debris
            for debris in self.debris
            if debris.y < self.height + 100
        ]

        if self.perfect_popup_timer > 0:
            self.perfect_popup_timer -= 1

    def get_background_color(self):
        """
        Calculate the sky color from the current tower height.

        The background gradually moves through:
        twilight blue -> dusk purple -> night -> stratosphere black.
        """

        height = self.score

        stages = [
            (0, (24, 27, 36)),
            (8, (45, 55, 100)),
            (16, (75, 55, 120)),
            (25, (35, 25, 75)),
            (35, (8, 10, 25)),
            (50, (2, 4, 12)),
        ]

        for i in range(len(stages) - 1):
            current_height, current_color = stages[i]
            next_height, next_color = stages[i + 1]

            if height <= next_height:
                progress = (
                    height - current_height
                ) / (
                    next_height - current_height
                )

                progress = max(0.0, min(1.0, progress))

                r = int(
                    current_color[0]
                    + (next_color[0] - current_color[0])
                    * progress
                )

                g = int(
                    current_color[1]
                    + (next_color[1] - current_color[1])
                    * progress
                )

                b = int(
                    current_color[2]
                    + (next_color[2] - current_color[2])
                    * progress
                )

                return (r, g, b)

        return stages[-1][1]

    def render(self, screen):
        # TASK 4:
        # Gradually change the sky as the tower becomes taller.
        background_color = self.get_background_color()

        screen.fill(background_color)

        title_surf = self.font_title.render(
            "Skyscraper Stack",
            True,
            (245, 245, 245)
        )

        screen.blit(
            title_surf,
            (
                self.width // 2
                - title_surf.get_width() // 2,
                16
            )
        )

        score_surf = self.font_hud.render(
            f"Height: {self.score}",
            True,
            (255, 220, 80)
        )

        screen.blit(
            score_surf,
            (
                self.width // 2
                - score_surf.get_width() // 2,
                54
            )
        )

        for b in self.stack:
            b.render(screen)

        for debris in self.debris:
            debris.render(screen)

        if not self.game_over:
            self.active_block.render(screen)

        # PERFECT popup
        if self.perfect_popup_timer > 0:
            perfect_surf = self.font_perfect.render(
                "PERFECT!",
                True,
                (255, 215, 0)
            )

            popup_y = 100 - (
                45 - self.perfect_popup_timer
            )

            screen.blit(
                perfect_surf,
                (
                    self.width // 2
                    - perfect_surf.get_width() // 2,
                    popup_y
                )
            )

        if self.game_over:
            overlay = pygame.Surface(
                (self.width, self.height),
                pygame.SRCALPHA
            )

            overlay.fill((0, 0, 0, 195))
            screen.blit(overlay, (0, 0))

            over_surf = self.font_big.render(
                "TOWER COLLAPSED!",
                True,
                (240, 75, 75)
            )

            screen.blit(
                over_surf,
                (
                    self.width // 2
                    - over_surf.get_width() // 2,
                    self.height // 2 - 40
                )
            )

            final_surf = self.font_hud.render(
                f"Final Height: {self.score}",
                True,
                (255, 255, 255)
            )

            screen.blit(
                final_surf,
                (
                    self.width // 2
                    - final_surf.get_width() // 2,
                    self.height // 2 + 10
                )
            )

            restart_surf = self.font_hud.render(
                "Press [Space] or [R] to Play Again",
                True,
                (200, 200, 200)
            )

            screen.blit(
                restart_surf,
                (
                    self.width // 2
                    - restart_surf.get_width() // 2,
                    self.height // 2 + 50
                )
            )