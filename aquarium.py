import json
import random

import pygame

from github_api import get_recent_commits


pygame.init()


# -------------------------
# GitHub
# -------------------------

commits = get_recent_commits()

print(f"GitQuarium found {len(commits)} commits.")

SEEN_COMMITS_FILE = "seen_commits.json"


def load_seen_commits():
    try:
        with open(SEEN_COMMITS_FILE, "r") as file:
            return set(json.load(file))
    except FileNotFoundError:
        return set()


def save_seen_commits(seen_commits):
    with open(SEEN_COMMITS_FILE, "w") as file:
        json.dump(
            list(seen_commits),
            file,
            indent=4,
        )


seen_commits = load_seen_commits()

if not seen_commits:
    # First run: establish baseline
    seen_commits = {
        commit["sha"]
        for commit in commits
    }

    save_seen_commits(seen_commits)

    new_commits = []

    print(
        f"Baseline created with {len(seen_commits)} existing commits."
    )

else:
    new_commits = [
        commit
        for commit in commits
        if commit["sha"] not in seen_commits
    ]

    print(
        f"GitQuarium found {len(new_commits)} new commits."
    )


# -------------------------
# Window
# -------------------------

WIDTH = 900
HEIGHT = 500

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "GitQuarium"
)

clock = pygame.time.Clock()


# -------------------------
# Background
# -------------------------

background_original = pygame.image.load(
    "assets/background.png"
).convert()

background = pygame.transform.scale(
    background_original,
    (WIDTH, HEIGHT),
)


# -------------------------
# Fish
# -------------------------

class Fish:
    def __init__(self, name, image_path):
        self.name = name

        original_image = pygame.image.load(
            image_path
        ).convert_alpha()

        scale = 3

        self.image_right = pygame.transform.scale(
            original_image,
            (
                original_image.get_width() * scale,
                original_image.get_height() * scale,
            ),
        )

        self.image_left = pygame.transform.flip(
            self.image_right,
            True,
            False,
        )

        # Random starting position
        self.x = random.randint(
            100,
            WIDTH - self.image_right.get_width() - 50,
        )

        self.y = random.randint(
            50,
            HEIGHT - self.image_right.get_height() - 50,
        )

        # Random swimming speed
        self.speed_x = random.choice(
            [-2, -1, 1, 2]
        )

        self.speed_y = random.choice(
            [-1, 0, 1]
        )

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

        # Left/right edges
        if self.x <= 0:
            self.x = 0
            self.speed_x = abs(
                self.speed_x
            )

        elif self.x >= WIDTH - self.image_right.get_width():
            self.x = (
                WIDTH
                - self.image_right.get_width()
            )

            self.speed_x = -abs(
                self.speed_x
            )

        # Top/bottom edges
        if self.y <= 0:
            self.y = 0
            self.speed_y = abs(
                self.speed_y
            )

        elif self.y >= HEIGHT - self.image_right.get_height():
            self.y = (
                HEIGHT
                - self.image_right.get_height()
            )

            self.speed_y = -abs(
                self.speed_y
            )

        # Occasionally change vertical direction
        if random.randint(1, 120) == 1:
            self.speed_y = random.choice(
                [-1, 0, 1]
            )

    def draw(self):
        if self.speed_x > 0:
            image = self.image_right
        else:
            image = self.image_left

        screen.blit(
            image,
            (self.x, self.y),
        )


# -------------------------
# Bubbles
# -------------------------

class Bubble:
    def __init__(self):
        original_image = pygame.image.load(
            "assets/bubble.png"
        ).convert_alpha()

        # Random bubble size
        scale = random.choice(
            [1, 2]
        )

        self.image = pygame.transform.scale(
            original_image,
            (
                original_image.get_width() * scale,
                original_image.get_height() * scale,
            ),
        )

        # Start below the aquarium
        self.x = random.randint(
            20,
            WIDTH - 20,
        )

        self.y = HEIGHT + random.randint(
            0,
            100,
        )

        # Random upward speed
        self.speed_y = random.uniform(
            0.5,
            1.5,
        )

        # Tiny sideways movement
        self.drift = random.uniform(
            -0.3,
            0.3,
        )

    def update(self):
        self.y -= self.speed_y
        self.x += self.drift

    def draw(self):
        screen.blit(
            self.image,
            (self.x, self.y),
        )

    def is_gone(self):
        return (
            self.y
            < -self.image.get_height()
        )


# -------------------------
# GitQuarium residents
# -------------------------

fish = [
    Fish(
        "James the Fish",
        "assets/james-the-fish.png",
    ),
    Fish(
        "Mikey",
        "assets/mikey.png",
    ),
    Fish(
        "Maude",
        "assets/maude.png",
    ),
]


# -------------------------
# Spawn new commit fish
# -------------------------

for commit in new_commits:
    commit_fish = Fish(
        commit["message"],
        "assets/james-the-fish.png",
    )

    fish.append(commit_fish)

    seen_commits.add(
        commit["sha"]
    )

    print(
        "New fish born:",
        commit["message"],
        "|",
        commit["repo"],
    )


if new_commits:
    save_seen_commits(
        seen_commits
    )


bubbles = []


# -------------------------
# Main loop
# -------------------------

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Aquarium background
    screen.blit(
        background,
        (0, 0),
    )

    # Occasionally spawn a bubble
    if random.randint(1, 35) == 1:
        bubbles.append(
            Bubble()
        )

    # Update and draw bubbles
    for bubble in bubbles:
        bubble.update()
        bubble.draw()

    # Remove bubbles that left the screen
    bubbles = [
        bubble
        for bubble in bubbles
        if not bubble.is_gone()
    ]

    # Update and draw our idiots
    for little_guy in fish:
        little_guy.update()
        little_guy.draw()

    pygame.display.flip()

    clock.tick(
        60
    )


pygame.quit()