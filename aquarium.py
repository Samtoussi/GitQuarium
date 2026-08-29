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


# -------------------------
# Save system
# -------------------------

SAVE_FILE = "save.json"

INITIAL_GITQUARIUM_SHA = "e245a90"


def load_save():
    try:
        with open(SAVE_FILE, "r") as file:
            return json.load(file)

    except FileNotFoundError:
        return {
            "seen_commits": [],
            "fish": [],
        }


def save_game(save_data):
    with open(SAVE_FILE, "w") as file:
        json.dump(
            save_data,
            file,
            indent=4,
        )


save_data = load_save()

seen_commits = set(
    save_data.get("seen_commits", [])
)

saved_fish = save_data.get(
    "fish",
    [],
)


# -------------------------
# First-time migration
# -------------------------

if not seen_commits:
    seen_commits = {
        commit["sha"]
        for commit in commits
    }

    initial_commit = next(
        (
            commit
            for commit in commits
            if commit["sha"].startswith(
                INITIAL_GITQUARIUM_SHA
            )
        ),
        None,
    )

    if initial_commit:
        saved_fish.append(
            {
                "species": "mikey",
                "commit_sha": initial_commit["sha"],
                "commit_message": initial_commit["message"],
                "repo": initial_commit["repo"],
            }
        )

        print(
            "Restored Fish #1:",
            initial_commit["message"],
        )

    save_data["seen_commits"] = list(
        seen_commits
    )

    save_data["fish"] = saved_fish

    save_game(
        save_data
    )

    new_commits = []

    print(
        f"Baseline created with "
        f"{len(seen_commits)} existing commits."
    )

else:
    new_commits = [
        commit
        for commit in commits
        if commit["sha"] not in seen_commits
    ]

    print(
        f"GitQuarium found "
        f"{len(new_commits)} new commits."
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

        self.x = random.randint(
            100,
            WIDTH
            - self.image_right.get_width()
            - 50,
        )

        self.y = random.randint(
            50,
            HEIGHT
            - self.image_right.get_height()
            - 50,
        )

        self.speed_x = random.choice(
            [-2, -1, 1, 2]
        )

        self.speed_y = random.choice(
            [-1, 0, 1]
        )

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x <= 0:
            self.x = 0
            self.speed_x = abs(
                self.speed_x
            )

        elif self.x >= (
            WIDTH
            - self.image_right.get_width()
        ):
            self.x = (
                WIDTH
                - self.image_right.get_width()
            )

            self.speed_x = -abs(
                self.speed_x
            )

        if self.y <= 0:
            self.y = 0
            self.speed_y = abs(
                self.speed_y
            )

        elif self.y >= (
            HEIGHT
            - self.image_right.get_height()
        ):
            self.y = (
                HEIGHT
                - self.image_right.get_height()
            )

            self.speed_y = -abs(
                self.speed_y
            )

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
# Fish species
# -------------------------

FISH_SPECIES = {
    "mikey": {
        "name": "Mikey",
        "image": "assets/mikey.png",
    },
    "maude": {
        "name": "Maude",
        "image": "assets/maude.png",
    },
    "jake": {
        "name": "Jake",
        "image": "assets/jake.png",
    },
    "clown": {
        "name": "Clown",
        "image": "assets/clown.png",
    },
    "goof": {
        "name": "Goof",
        "image": "assets/goof.png",
    },
    "long": {
        "name": "Long",
        "image": "assets/long.png",
    },
    "bruce": {
        "name": "Bruce",
        "image": "assets/bruce.png",
    },
    "boner": {
        "name": "Boner",
        "image": "assets/boner.png",
    },
    "bella": {
        "name": "Bella",
        "image": "assets/bella.png",
    },
}


# -------------------------
# Rarity pools
# -------------------------

RARITY_POOLS = {
    "common": [
        "mikey",
        "maude",
        "jake",
    ],
    "uncommon": [
        "clown",
        "goof",
    ],
    "rare": [
        "long",
        "bruce",
    ],
    "epic": [
        "boner",
    ],
    "legendary": [
        "bella",
    ],
}


def roll_rarity():
    roll = random.randint(
        1,
        100,
    )

    if roll <= 55:
        return "common"

    if roll <= 80:
        return "uncommon"

    if roll <= 93:
        return "rare"

    if roll <= 99:
        return "epic"

    return "legendary"


def roll_species():
    rarity = roll_rarity()

    species = random.choice(
        RARITY_POOLS[rarity]
    )

    return species, rarity


# -------------------------
# Bubbles
# -------------------------

class Bubble:
    def __init__(self):
        original_image = pygame.image.load(
            "assets/bubble.png"
        ).convert_alpha()

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

        self.x = random.randint(
            20,
            WIDTH - 20,
        )

        self.y = HEIGHT + random.randint(
            0,
            100,
        )

        self.speed_y = random.uniform(
            0.5,
            1.5,
        )

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
    )
]


# -------------------------
# Load owned fish
# -------------------------

for owned_fish in saved_fish:
    species_id = owned_fish["species"]

    species = FISH_SPECIES[
        species_id
    ]

    fish.append(
        Fish(
            species["name"],
            species["image"],
        )
    )


# -------------------------
# Spawn new commit fish
# -------------------------

for commit in new_commits:
    species_id, rarity = roll_species()

    species = FISH_SPECIES[
        species_id
    ]

    fish.append(
        Fish(
            species["name"],
            species["image"],
        )
    )

    saved_fish.append(
        {
            "species": species_id,
            "rarity": rarity,
            "commit_sha": commit["sha"],
            "commit_message": commit["message"],
            "repo": commit["repo"],
        }
    )

    seen_commits.add(
        commit["sha"]
    )

    print(
        f"New {rarity.upper()} fish born:",
        species["name"],
        "|",
        commit["message"],
        "|",
        commit["repo"],
    )


if new_commits:
    save_data["seen_commits"] = list(
        seen_commits
    )

    save_data["fish"] = saved_fish

    save_game(
        save_data
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

    screen.blit(
        background,
        (0, 0),
    )

    if random.randint(1, 35) == 1:
        bubbles.append(
            Bubble()
        )

    for bubble in bubbles:
        bubble.update()
        bubble.draw()

    bubbles = [
        bubble
        for bubble in bubbles
        if not bubble.is_gone()
    ]

    for little_guy in fish:
        little_guy.update()
        little_guy.draw()

    pygame.display.flip()

    clock.tick(
        60
    )


pygame.quit()