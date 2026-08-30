import json
import random
from datetime import datetime, timezone

import pygame

from github_api import get_recent_commits


pygame.init()


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
# Intro
# -------------------------

INTRO_SIZE = 500

intro_paths = [
    "assets/intro.png",
    "assets/intro1.png",
    "assets/intro2.png",
    "assets/intro3.png",
]

intro_images = []

for path in intro_paths:
    original = pygame.image.load(
        path
    ).convert()

    scaled = pygame.transform.scale(
        original,
        (
            INTRO_SIZE,
            INTRO_SIZE,
        ),
    )

    intro_images.append(
        scaled
    )


intro_click_sound = pygame.mixer.Sound(
    "assets/music/gq_intro_click.mp3"
)

intro_bang_sound = pygame.mixer.Sound(
    "assets/music/gq_intro_bang.mp3"
)

intro_ambient_sound = pygame.mixer.Sound(
    "assets/music/gq_intro_ambient.mp3"
)


intro_click_sound.set_volume(0.6)
intro_bang_sound.set_volume(0.7)
intro_ambient_sound.set_volume(0.4)


def draw_intro_image(image):
    screen.fill(
        (0, 0, 0)
    )

    image_x = (
        WIDTH - image.get_width()
    ) // 2

    image_y = (
        HEIGHT - image.get_height()
    ) // 2

    screen.blit(
        image,
        (
            image_x,
            image_y,
        ),
    )

    pygame.display.flip()


def wait_for_intro(milliseconds):
    start_time = pygame.time.get_ticks()

    while (
        pygame.time.get_ticks()
        - start_time
        < milliseconds
    ):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                intro_ambient_sound.stop()

                pygame.quit()

                raise SystemExit

        clock.tick(60)


# Start ambience
intro_ambient_sound.play(
    loops=-1
)


# Empty city
draw_intro_image(
    intro_images[0]
)

wait_for_intro(
    1500
)


# SAM'S
draw_intro_image(
    intro_images[1]
)

intro_click_sound.play()

wait_for_intro(
    500
)


# GAMING
draw_intro_image(
    intro_images[2]
)

intro_click_sound.play()

wait_for_intro(
    500
)


# STUDIO
draw_intro_image(
    intro_images[3]
)

intro_bang_sound.play()

wait_for_intro(
    1000
)


# -------------------------
# GitHub
# -------------------------

commits = get_recent_commits()

print(
    f"GitQuarium found "
    f"{len(commits)} commits."
)


# -------------------------
# Tank cleanliness
# -------------------------

def get_tank_background(commits):
    if not commits:
        print(
            "No commits found."
        )

        print(
            "Tank status: "
            "ABSOLUTE SWAMP"
        )

        return "assets/background-03.png"

    latest_commit_date = datetime.fromisoformat(
        commits[0]["created_at"].replace(
            "Z",
            "+00:00",
        )
    )

    now = datetime.now(
        timezone.utc
    )

    days_since_commit = (
        now - latest_commit_date
    ).days

    if days_since_commit <= 2:
        background_path = (
            "assets/background.png"
        )

        tank_status = "CLEAN"

    elif days_since_commit <= 4:
        background_path = (
            "assets/background-01.png"
        )

        tank_status = "SLIGHTLY DIRTY"

    elif days_since_commit <= 6:
        background_path = (
            "assets/background-02.png"
        )

        tank_status = "DIRTY"

    else:
        background_path = (
            "assets/background-03.png"
        )

        tank_status = "ABSOLUTE SWAMP"

    print(
        f"Last commit: "
        f"{days_since_commit} "
        f"day(s) ago."
    )

    print(
        f"Tank status: "
        f"{tank_status}"
    )

    return background_path


background_path = get_tank_background(
    commits
)


# -------------------------
# Save system
# -------------------------

SAVE_FILE = "save.json"

INITIAL_GITQUARIUM_SHA = "e245a90"


def load_save():
    try:
        with open(
            SAVE_FILE,
            "r",
        ) as file:
            return json.load(
                file
            )

    except FileNotFoundError:
        return {
            "seen_commits": [],
            "fish": [],
        }


def save_game(save_data):
    with open(
        SAVE_FILE,
        "w",
    ) as file:
        json.dump(
            save_data,
            file,
            indent=4,
        )


save_data = load_save()

seen_commits = set(
    save_data.get(
        "seen_commits",
        [],
    )
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
                "commit_sha": (
                    initial_commit["sha"]
                ),
                "commit_message": (
                    initial_commit[
                        "message"
                    ]
                ),
                "repo": (
                    initial_commit[
                        "repo"
                    ]
                ),
            }
        )

        print(
            "Restored Fish #1:",
            initial_commit[
                "message"
            ],
        )

    save_data[
        "seen_commits"
    ] = list(
        seen_commits
    )

    save_data[
        "fish"
    ] = saved_fish

    save_game(
        save_data
    )

    new_commits = []

    print(
        f"Baseline created with "
        f"{len(seen_commits)} "
        f"existing commits."
    )

else:
    new_commits = [
        commit
        for commit in commits
        if commit["sha"]
        not in seen_commits
    ]

    print(
        f"GitQuarium found "
        f"{len(new_commits)} "
        f"new commits."
    )


# -------------------------
# Background
# -------------------------

background_original = pygame.image.load(
    background_path
).convert()

background = pygame.transform.scale(
    background_original,
    (
        WIDTH,
        HEIGHT,
    ),
)


# -------------------------
# Sound button
# -------------------------

sound_on_original = pygame.image.load(
    "assets/ui/sound_on.png"
).convert_alpha()

sound_off_original = pygame.image.load(
    "assets/ui/sound_off.png"
).convert_alpha()

SOUND_BUTTON_SCALE = 2

sound_on_image = pygame.transform.scale(
    sound_on_original,
    (
        sound_on_original.get_width()
        * SOUND_BUTTON_SCALE,

        sound_on_original.get_height()
        * SOUND_BUTTON_SCALE,
    ),
)

sound_off_image = pygame.transform.scale(
    sound_off_original,
    (
        sound_off_original.get_width()
        * SOUND_BUTTON_SCALE,

        sound_off_original.get_height()
        * SOUND_BUTTON_SCALE,
    ),
)

sound_button_x = -20
sound_button_y = 10

sound_button_rect = pygame.Rect(
    sound_button_x,
    sound_button_y,
    sound_on_image.get_width(),
    sound_on_image.get_height(),
)

music_muted = False


# -------------------------
# Sound effects
# -------------------------

mouse_click_sound = pygame.mixer.Sound(
    "assets/music/gq_mouse_fx.mp3"
)

mouse_click_sound.set_volume(
    0.5
)

fish_poke_sound = pygame.mixer.Sound(
    "assets/music/gq_fish_fx.mp3"
)

fish_poke_sound.set_volume(
    0.5
)


# -------------------------
# Reveal sounds
# -------------------------

reveal_common_sound = pygame.mixer.Sound(
    "assets/music/gq_reveal_common.mp3"
)

reveal_rare_sound = pygame.mixer.Sound(
    "assets/music/gq_reveal_rare.mp3"
)

reveal_legendary_sound = pygame.mixer.Sound(
    "assets/music/gq_reveal_legendary.mp3"
)

reveal_common_sound.set_volume(
    0.7
)

reveal_rare_sound.set_volume(
    0.8
)

reveal_legendary_sound.set_volume(
    0.9
)


new_fish_sound = pygame.mixer.Sound(
    "assets/music/new_fish_sound.mp3"
)

new_fish_sound.set_volume(
    0.7
)


# -------------------------
# Reveal assets
# -------------------------

reveal_image = pygame.image.load(
    "assets/fish-reveal.png"
).convert_alpha()

reveal_rect = reveal_image.get_rect(
    center=(
        WIDTH // 2,
        HEIGHT // 2,
    )
)

spark_original = pygame.image.load(
    "assets/spark.png"
).convert_alpha()


# -------------------------
# Fish
# -------------------------

class Fish:
    def __init__(
        self,
        name,
        image_path,
    ):
        self.name = name

        original_image = pygame.image.load(
            image_path
        ).convert_alpha()

        scale = 3

        self.image_right = (
            pygame.transform.scale(
                original_image,
                (
                    original_image.get_width()
                    * scale,

                    original_image.get_height()
                    * scale,
                ),
            )
        )

        self.image_left = (
            pygame.transform.flip(
                self.image_right,
                True,
                False,
            )
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
            [
                -2,
                -1,
                1,
                2,
            ]
        )

        self.speed_y = random.choice(
            [
                -1,
                0,
                1,
            ]
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

        if random.randint(
            1,
            120,
        ) == 1:
            self.speed_y = random.choice(
                [
                    -1,
                    0,
                    1,
                ]
            )

    def draw(self):
        if self.speed_x > 0:
            image = self.image_right

        else:
            image = self.image_left

        screen.blit(
            image,
            (
                self.x,
                self.y,
            ),
        )

    def get_rect(self):
        return self.image_right.get_rect(
            topleft=(
                self.x,
                self.y,
            )
        )

    def poke(self):
        self.y -= 12

        self.speed_x *= -1


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
        RARITY_POOLS[
            rarity
        ]
    )

    return (
        species,
        rarity,
    )


# -------------------------
# Pending reveals
# -------------------------

pending_reveals = []

for commit in new_commits:
    species_id, rarity = (
        roll_species()
    )

    pending_reveals.append(
        {
            "species": species_id,
            "rarity": rarity,
            "commit": commit,
        }
    )

    print(
        "Pending fish reveal:",
        rarity.upper(),
        "|",
        FISH_SPECIES[
            species_id
        ][
            "name"
        ],
    )


# -------------------------
# Bubbles
# -------------------------

class Bubble:
    def __init__(self):
        original_image = pygame.image.load(
            "assets/bubble.png"
        ).convert_alpha()

        scale = random.choice(
            [
                1,
                2,
            ]
        )

        self.image = (
            pygame.transform.scale(
                original_image,
                (
                    original_image.get_width()
                    * scale,

                    original_image.get_height()
                    * scale,
                ),
            )
        )

        self.x = random.randint(
            20,
            WIDTH - 20,
        )

        self.y = (
            HEIGHT
            + random.randint(
                0,
                100,
            )
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
            (
                self.x,
                self.y,
            ),
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
    species_id = (
        owned_fish[
            "species"
        ]
    )

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
# Bubbles
# -------------------------

bubbles = []


# -------------------------
# Draw aquarium
# -------------------------

def draw_aquarium_scene():
    screen.blit(
        background,
        (
            0,
            0,
        ),
    )

    for little_guy in fish:
        little_guy.draw()

    if music_muted:
        screen.blit(
            sound_off_image,
            (
                sound_button_x,
                sound_button_y,
            ),
        )

    else:
        screen.blit(
            sound_on_image,
            (
                sound_button_x,
                sound_button_y,
            ),
        )


# -------------------------
# Fade transition
# -------------------------

def fade_into_aquarium(
    duration=500,
):
    overlay = pygame.Surface(
        (
            WIDTH,
            HEIGHT,
        )
    )

    overlay.fill(
        (
            0,
            0,
            0,
        )
    )


    # Intro -> black
    start_time = pygame.time.get_ticks()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                intro_ambient_sound.stop()

                pygame.quit()

                raise SystemExit

        elapsed = (
            pygame.time.get_ticks()
            - start_time
        )

        progress = min(
            elapsed / duration,
            1,
        )

        draw_intro_image(
            intro_images[3]
        )

        overlay.set_alpha(
            int(
                255 * progress
            )
        )

        screen.blit(
            overlay,
            (
                0,
                0,
            ),
        )

        pygame.display.flip()

        if progress >= 1:
            break

        clock.tick(60)


    intro_ambient_sound.stop()


    # Start game theme
    pygame.mixer.music.load(
        "assets/music/gitquarium-theme.mp3"
    )

    pygame.mixer.music.set_volume(
        0.4
    )

    pygame.mixer.music.play(
        -1
    )


    # Black -> aquarium
    start_time = pygame.time.get_ticks()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()

                pygame.quit()

                raise SystemExit

        elapsed = (
            pygame.time.get_ticks()
            - start_time
        )

        progress = min(
            elapsed / duration,
            1,
        )

        draw_aquarium_scene()

        overlay.set_alpha(
            int(
                255
                * (
                    1 - progress
                )
            )
        )

        screen.blit(
            overlay,
            (
                0,
                0,
            ),
        )

        pygame.display.flip()

        if progress >= 1:
            break

        clock.tick(60)


# -------------------------
# Reveal helpers
# -------------------------

def get_reveal_sound(
    rarity,
):
    if rarity in (
        "common",
        "uncommon",
    ):
        return reveal_common_sound

    if rarity in (
        "rare",
        "epic",
    ):
        return reveal_rare_sound

    return reveal_legendary_sound


def get_spark_count(
    rarity,
):
    if rarity in (
        "common",
        "uncommon",
    ):
        return random.randint(
            4,
            6,
        )

    if rarity in (
        "rare",
        "epic",
    ):
        return random.randint(
            8,
            12,
        )

    return random.randint(
        18,
        25,
    )


def create_sparks(
    rarity,
):
    sparks = []

    spark_count = get_spark_count(
        rarity
    )

    for _ in range(
        spark_count
    ):
        scale = random.choice(
            [
                1,
                1,
                2,
                2,
                3,
            ]
        )

        spark_image = pygame.transform.scale(
            spark_original,
            (
                spark_original.get_width()
                * scale,

                spark_original.get_height()
                * scale,
            ),
        )

        rotation = random.choice(
            [
                0,
                90,
                180,
                270,
            ]
        )

        spark_image = pygame.transform.rotate(
            spark_image,
            rotation,
        )

        spark_x = random.randint(
            reveal_rect.left + 20,
            reveal_rect.right
            - spark_image.get_width()
            - 20,
        )

        spark_y = random.randint(
            reveal_rect.top + 20,
            reveal_rect.bottom - 20,
        )

        sparks.append(
            {
                "image": spark_image,
                "x": float(spark_x),
                "y": float(spark_y),
                "speed_y": random.uniform(
                    0.3,
                    0.8,
                ),
                "drift": random.uniform(
                    -0.25,
                    0.25,
                ),
            }
        )

    return sparks


def update_sparks(
    sparks,
):
    for spark in sparks:
        spark["y"] -= spark["speed_y"]
        spark["x"] += spark["drift"]

        if (
            spark["y"]
            < reveal_rect.top
            - spark["image"].get_height()
        ):
            spark["y"] = float(
                reveal_rect.bottom
                + random.randint(
                    0,
                    30,
                )
            )

            spark["x"] = float(
                random.randint(
                    reveal_rect.left + 20,
                    reveal_rect.right
                    - spark["image"].get_width()
                    - 20,
                )
            )

            spark["drift"] = random.uniform(
                -0.25,
                0.25,
            )


def create_revealed_card(
    species_id,
    rarity,
):
    card = pygame.Surface(
        (
            300,
            300,
        ),
        pygame.SRCALPHA,
    )

    card.fill(
        (
            0,
            0,
            0,
            255,
        )
    )

    pygame.draw.rect(
        card,
        (
            55,
            55,
            55,
        ),
        (
            2,
            2,
            296,
            296,
        ),
        width=3,
    )

    species = FISH_SPECIES[
        species_id
    ]

    fish_image = pygame.image.load(
        species["image"]
    ).convert_alpha()

    max_width = 180
    max_height = 120

    scale = min(
        max_width
        / fish_image.get_width(),

        max_height
        / fish_image.get_height(),
    )

    scale = max(
        1,
        int(scale),
    )

    fish_image = pygame.transform.scale(
        fish_image,
        (
            fish_image.get_width()
            * scale,

            fish_image.get_height()
            * scale,
        ),
    )

    fish_rect = fish_image.get_rect(
        center=(
            150,
            125,
        )
    )

    card.blit(
        fish_image,
        fish_rect,
    )


    # Fonts
    name_font = pygame.font.Font(
        None,
        32,
    )

    rarity_font = pygame.font.Font(
        None,
        25,
    )

    continue_font = pygame.font.Font(
        None,
        18,
    )


    name_text = name_font.render(
        species["name"].upper(),
        True,
        (
            255,
            255,
            255,
        ),
    )

    rarity_colors = {
        "common": (
            220,
            220,
            220,
        ),

        "uncommon": (
            90,
            220,
            120,
        ),

        "rare": (
            80,
            150,
            255,
        ),

        "epic": (
            210,
            90,
            255,
        ),

        "legendary": (
            255,
            215,
            50,
        ),
    }

    rarity_text = rarity_font.render(
        rarity.upper(),
        True,
        rarity_colors[
            rarity
        ],
    )

    continue_text = continue_font.render(
        "CLICK TO CONTINUE",
        True,
        (
            170,
            170,
            170,
        ),
    )


    name_rect = name_text.get_rect(
        center=(
            150,
            210,
        )
    )

    rarity_rect = rarity_text.get_rect(
        center=(
            150,
            240,
        )
    )

    continue_rect = continue_text.get_rect(
        center=(
            150,
            278,
        )
    )


    card.blit(
        name_text,
        name_rect,
    )

    card.blit(
        rarity_text,
        rarity_rect,
    )

    card.blit(
        continue_text,
        continue_rect,
    )


    return card


def claim_reveal(
    reveal,
):
    species_id = reveal[
        "species"
    ]

    rarity = reveal[
        "rarity"
    ]

    commit = reveal[
        "commit"
    ]

    species = FISH_SPECIES[
        species_id
    ]


    # Add fish to aquarium
    fish.append(
        Fish(
            species["name"],
            species["image"],
        )
    )


    # Save fish
    saved_fish.append(
        {
            "species": species_id,
            "rarity": rarity,
            "commit_sha": (
                commit["sha"]
            ),
            "commit_message": (
                commit["message"]
            ),
            "repo": (
                commit["repo"]
            ),
        }
    )


    seen_commits.add(
        commit["sha"]
    )


    save_data[
        "seen_commits"
    ] = list(
        seen_commits
    )

    save_data[
        "fish"
    ] = saved_fish

    save_game(
        save_data
    )


    print(
        f"Revealed "
        f"{rarity.upper()} fish:",
        species["name"],
        "|",
        commit["message"],
        "|",
        commit["repo"],
    )


# -------------------------
# Fish reveal
# -------------------------

def run_fish_reveal(
    reveal,
):
    revealed = False

    revealed_card = None

    sparks = []

    dark_overlay = pygame.Surface(
        (
            WIDTH,
            HEIGHT,
        )
    )

    dark_overlay.fill(
        (
            0,
            0,
            0,
        )
    )

    dark_overlay.set_alpha(
        150
    )


    new_fish_sound.play()

    while True:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()

                raise SystemExit


            if (
                event.type
                == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                if reveal_rect.collidepoint(
                    event.pos
                ):

                    # -----------------
                    # CLICK TO REVEAL
                    # -----------------

                    if not revealed:
                        intro_click_sound.play()

                        pygame.time.delay(
                            100
                        )

                        reveal_sound = (
                            get_reveal_sound(
                                reveal[
                                    "rarity"
                                ]
                            )
                        )

                        reveal_sound.play()

                        revealed_card = (
                            create_revealed_card(
                                reveal[
                                    "species"
                                ],

                                reveal[
                                    "rarity"
                                ],
                            )
                        )

                        sparks = create_sparks(
                            reveal[
                                "rarity"
                            ]
                        )

                        revealed = True


                    # -----------------
                    # CONTINUE
                    # -----------------

                    else:
                        claim_reveal(
                            reveal
                        )

                        return


        # Aquarium behind reveal
        draw_aquarium_scene()


        # Darken aquarium
        screen.blit(
            dark_overlay,
            (
                0,
                0,
            ),
        )


        # -------------------------
        # Question mark card
        # -------------------------

        if not revealed:
            screen.blit(
                reveal_image,
                reveal_rect,
            )


        # -------------------------
        # Revealed fish card
        # -------------------------

        else:
            screen.blit(
                revealed_card,
                reveal_rect,
            )


            # Sparks
            update_sparks(
                sparks
            )

            for spark in sparks:
                screen.blit(
                    spark["image"],
                    (
                        spark["x"],
                        spark["y"],
                    ),
                )


        pygame.display.flip()

        clock.tick(
            60
        )


# -------------------------
# Enter GitQuarium
# -------------------------

fade_into_aquarium(
    duration=500
)


# -------------------------
# Run pending reveals
# -------------------------

for pending_reveal in pending_reveals:
    run_fish_reveal(
        pending_reveal
    )


# -------------------------
# Main loop
# -------------------------

running = True

while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


        if (
            event.type
            == pygame.MOUSEBUTTONDOWN
        ):

            if event.button == 1:

                # ---------------------
                # Sound button
                # ---------------------

                if (
                    sound_button_rect.collidepoint(
                        event.pos
                    )
                ):
                    mouse_click_sound.play()

                    music_muted = (
                        not music_muted
                    )

                    if music_muted:
                        pygame.mixer.music.pause()

                    else:
                        pygame.mixer.music.unpause()


                # ---------------------
                # Fish poke
                # ---------------------

                else:
                    for little_guy in reversed(
                        fish
                    ):

                        if (
                            little_guy
                            .get_rect()
                            .collidepoint(
                                event.pos
                            )
                        ):
                            fish_poke_sound.play()

                            little_guy.poke()

                            break


    # -------------------------
    # Background
    # -------------------------

    screen.blit(
        background,
        (
            0,
            0,
        ),
    )


    # -------------------------
    # Bubble spawn
    # -------------------------

    if random.randint(
        1,
        35,
    ) == 1:

        bubbles.append(
            Bubble()
        )


    # -------------------------
    # Bubbles
    # -------------------------

    for bubble in bubbles:
        bubble.update()

        bubble.draw()


    bubbles = [
        bubble
        for bubble in bubbles
        if not bubble.is_gone()
    ]


    # -------------------------
    # Fish
    # -------------------------

    for little_guy in fish:
        little_guy.update()

        little_guy.draw()


    # -------------------------
    # Sound button
    # -------------------------

    if music_muted:
        screen.blit(
            sound_off_image,
            (
                sound_button_x,
                sound_button_y,
            ),
        )

    else:
        screen.blit(
            sound_on_image,
            (
                sound_button_x,
                sound_button_y,
            ),
        )


    pygame.display.flip()

    clock.tick(
        60
    )


pygame.quit()