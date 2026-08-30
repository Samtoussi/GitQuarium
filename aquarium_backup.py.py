import json
import os
import random
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import pygame

# When running as a PyInstaller executable,
# use the bundled resource directory as the working directory.
if getattr(sys, "frozen", False):
    os.chdir(sys._MEIPASS)

from github_api import (
    configure_github,
    get_recent_commits,
    validate_github_connection,
)

from gitquarium_config import (
    config_exists,
    get_app_data_dir,
    save_config,
)


pygame.init()

app_icon = pygame.image.load(
    "assets/docs/gq_logo.png"
)
pygame.display.set_icon(app_icon)


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
# First-run GitHub setup
# -------------------------

SETUP_PANEL = (7, 22, 31)
SETUP_PANEL_SHADOW = (2, 8, 12)
SETUP_BORDER = (210, 166, 92)
SETUP_BORDER_DIM = (126, 94, 52)
SETUP_TEXT = (235, 245, 245)
SETUP_MUTED = (145, 175, 180)
SETUP_INPUT = (3, 13, 19)
SETUP_SUCCESS = (90, 220, 120)
SETUP_ERROR = (235, 105, 105)
SETUP_BUTTON_HOVER = (235, 193, 111)
SETUP_BUTTON_SHADOW = (92, 61, 28)


def get_clipboard_text():
    try:
        if not pygame.scrap.get_init():
            pygame.scrap.init()

        raw_text = pygame.scrap.get(
            pygame.SCRAP_TEXT
        )

        if not raw_text:
            return ""

        return raw_text.decode(
            "utf-8",
            errors="ignore",
        ).replace("\x00", "").strip()

    except pygame.error:
        return ""


def run_first_time_setup():
    # Play the GitQuarium theme quietly while the player connects.
    pygame.mixer.music.load(
        "assets/music/gitquarium-theme.mp3"
    )
    pygame.mixer.music.set_volume(0.12)
    pygame.mixer.music.play(-1)

    title_font = pygame.font.Font(None, 44)
    subtitle_font = pygame.font.Font(None, 25)
    label_font = pygame.font.Font(None, 21)
    input_font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    button_font = pygame.font.Font(None, 25)

    # Use the actual GitQuarium tank behind the setup UI.
    setup_background_original = pygame.image.load(
        "assets/background.png"
    ).convert()

    setup_background = pygame.transform.scale(
        setup_background_original,
        (WIDTH, HEIGHT),
    )

    setup_dark_overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA,
    )
    setup_dark_overlay.fill((0, 8, 14, 125))

    # The mouse becomes one of GitQuarium's own bubbles.
    bubble_cursor_original = pygame.image.load(
        "assets/bubble.png"
    ).convert_alpha()

    bubble_cursor = pygame.transform.scale(
        bubble_cursor_original,
        (
            max(1, bubble_cursor_original.get_width() * 2),
            max(1, bubble_cursor_original.get_height() * 2),
        ),
    )

    # A few slow bubbles keep the setup screen alive without
    # introducing a separate animation system.
    setup_bubbles = []

    for _ in range(18):
        scale = random.choice((1, 1, 1, 2))
        image = pygame.transform.scale(
            bubble_cursor_original,
            (
                max(1, bubble_cursor_original.get_width() * scale),
                max(1, bubble_cursor_original.get_height() * scale),
            ),
        )

        setup_bubbles.append(
            {
                "image": image,
                "x": float(random.randint(15, WIDTH - 30)),
                "y": float(random.randint(0, HEIGHT)),
                "speed": random.uniform(0.25, 0.75),
                "drift": random.uniform(-0.12, 0.12),
            }
        )

    username = ""
    token = ""
    active_field = "username"
    status_message = ""
    status_success = False

    username_rect = pygame.Rect(
        WIDTH // 2 - 220,
        205,
        440,
        42,
    )

    token_rect = pygame.Rect(
        WIDTH // 2 - 220,
        295,
        440,
        42,
    )

    connect_rect = pygame.Rect(
        WIDTH // 2 - 90,
        375,
        180,
        44,
    )

    panel_rect = pygame.Rect(
        WIDTH // 2 - 280,
        55,
        560,
        400,
    )

    pygame.mouse.set_visible(False)

    def attempt_connection():
        nonlocal status_message
        nonlocal status_success

        clean_username = username.strip()
        clean_token = token.strip()

        if not clean_username:
            status_message = (
                "Enter your GitHub username."
            )
            status_success = False
            return False

        if not clean_token:
            status_message = (
                "Enter your GitHub token."
            )
            status_success = False
            return False

        status_message = "Connecting to GitHub..."
        status_success = False

        draw_setup_screen()
        pygame.display.flip()

        success, result = (
            validate_github_connection(
                clean_username,
                clean_token,
            )
        )

        if not success:
            status_message = str(result)
            status_success = False
            return False

        save_config(
            clean_username,
            clean_token,
        )

        configure_github(
            clean_username,
            clean_token,
        )

        status_message = (
            f"Connected as {result['login']}!"
        )
        status_success = True

        draw_setup_screen()
        pygame.display.flip()
        pygame.time.delay(700)

        return True

    def draw_pixel_frame(rect, color, width=2):
        pygame.draw.rect(
            screen,
            color,
            rect,
            width=width,
        )

        # Tiny corner blocks make the frame feel more like the
        # rest of GitQuarium's pixel UI than a web form.
        corner = 5
        pygame.draw.rect(
            screen,
            color,
            (rect.left, rect.top, corner, corner),
        )
        pygame.draw.rect(
            screen,
            color,
            (rect.right - corner, rect.top, corner, corner),
        )
        pygame.draw.rect(
            screen,
            color,
            (rect.left, rect.bottom - corner, corner, corner),
        )
        pygame.draw.rect(
            screen,
            color,
            (
                rect.right - corner,
                rect.bottom - corner,
                corner,
                corner,
            ),
        )

    def draw_input_box(
        rect,
        label,
        value,
        field_name,
        hidden=False,
    ):
        label_surface = label_font.render(
            label,
            True,
            SETUP_TEXT,
        )

        screen.blit(
            label_surface,
            (
                rect.left,
                rect.top - 25,
            ),
        )

        border_color = (
            SETUP_BORDER
            if active_field == field_name
            else SETUP_BORDER_DIM
        )

        shadow_rect = rect.move(4, 4)
        pygame.draw.rect(
            screen,
            SETUP_PANEL_SHADOW,
            shadow_rect,
        )

        pygame.draw.rect(
            screen,
            SETUP_INPUT,
            rect,
        )

        draw_pixel_frame(
            rect,
            border_color,
            width=2,
        )

        display_value = (
            "•" * len(value)
            if hidden
            else value
        )

        text_surface = input_font.render(
            display_value,
            True,
            SETUP_TEXT,
        )

        max_text_width = rect.width - 20

        if text_surface.get_width() > max_text_width:
            while (
                display_value
                and text_surface.get_width()
                > max_text_width
            ):
                display_value = display_value[1:]
                text_surface = input_font.render(
                    display_value,
                    True,
                    SETUP_TEXT,
                )

        screen.blit(
            text_surface,
            (
                rect.left + 10,
                rect.centery
                - text_surface.get_height() // 2,
            ),
        )

        # Small blinking caret for whichever field is active.
        if (
            active_field == field_name
            and (pygame.time.get_ticks() // 500) % 2 == 0
        ):
            caret_x = min(
                rect.left + 10 + text_surface.get_width() + 2,
                rect.right - 9,
            )

            pygame.draw.rect(
                screen,
                SETUP_BORDER,
                (
                    caret_x,
                    rect.top + 10,
                    2,
                    rect.height - 20,
                ),
            )

    def update_setup_bubbles():
        for bubble in setup_bubbles:
            bubble["y"] -= bubble["speed"]
            bubble["x"] += bubble["drift"]

            if bubble["y"] < -bubble["image"].get_height():
                bubble["y"] = float(
                    HEIGHT + random.randint(0, 60)
                )
                bubble["x"] = float(
                    random.randint(15, WIDTH - 30)
                )

    def draw_setup_bubbles():
        for bubble in setup_bubbles:
            screen.blit(
                bubble["image"],
                (
                    int(bubble["x"]),
                    int(bubble["y"]),
                ),
            )

    def draw_setup_screen():
        screen.blit(
            setup_background,
            (0, 0),
        )

        screen.blit(
            setup_dark_overlay,
            (0, 0),
        )

        draw_setup_bubbles()

        # Chunky offset shadow + square panel = much closer to
        # GitQuarium's collection/reveal UI than a rounded SaaS card.
        panel_shadow = panel_rect.move(7, 7)
        pygame.draw.rect(
            screen,
            SETUP_PANEL_SHADOW,
            panel_shadow,
        )

        panel_surface = pygame.Surface(
            panel_rect.size,
            pygame.SRCALPHA,
        )
        panel_surface.fill((*SETUP_PANEL, 232))
        screen.blit(
            panel_surface,
            panel_rect,
        )

        draw_pixel_frame(
            panel_rect,
            SETUP_BORDER,
            width=2,
        )

        # A simple double-line header gives the panel a game-menu feel.
        pygame.draw.line(
            screen,
            SETUP_BORDER_DIM,
            (panel_rect.left + 24, 158),
            (panel_rect.right - 24, 158),
            2,
        )
        pygame.draw.line(
            screen,
            SETUP_PANEL_SHADOW,
            (panel_rect.left + 24, 161),
            (panel_rect.right - 24, 161),
            2,
        )

        title = title_font.render(
            "WELCOME TO GITQUARIUM",
            True,
            SETUP_TEXT,
        )

        title_shadow = title_font.render(
            "WELCOME TO GITQUARIUM",
            True,
            SETUP_PANEL_SHADOW,
        )

        subtitle = subtitle_font.render(
            "Connect your GitHub account",
            True,
            SETUP_MUTED,
        )

        title_rect = title.get_rect(
            center=(WIDTH // 2, 102)
        )

        screen.blit(
            title_shadow,
            title_rect.move(3, 3),
        )

        screen.blit(
            title,
            title_rect,
        )

        screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(WIDTH // 2, 140)
            ),
        )

        draw_input_box(
            username_rect,
            "GITHUB USERNAME",
            username,
            "username",
        )

        draw_input_box(
            token_rect,
            "GITHUB TOKEN",
            token,
            "token",
            hidden=True,
        )

        # Tiny GitQuarium-style token help.
        token_help = small_font.render(
            "Don't know how to find your token?",
            True,
            SETUP_MUTED,
        )

        token_help_rect = token_help.get_rect(
            topleft=(
                token_rect.left,
                token_rect.bottom + 8,
            )
        )

        screen.blit(
            token_help,
            token_help_rect,
        )

        info_center = (
            token_help_rect.right + 12,
            token_help_rect.centery,
        )

        pygame.draw.circle(
            screen,
            SETUP_BORDER,
            info_center,
            7,
            1,
        )

        info_letter = small_font.render(
            "i",
            True,
            SETUP_BORDER,
        )

        screen.blit(
            info_letter,
            info_letter.get_rect(
                center=(
                    info_center[0],
                    info_center[1] - 1,
                )
            ),
        )

        info_hover_rect = pygame.Rect(
            info_center[0] - 10,
            info_center[1] - 10,
            20,
            20,
        )

        mouse_pos = pygame.mouse.get_pos()

        if info_hover_rect.collidepoint(mouse_pos):
            tooltip_text = small_font.render(
                "Ask ChatGPT lol",
                True,
                SETUP_TEXT,
            )

            tooltip_padding_x = 9
            tooltip_padding_y = 6

            tooltip_rect = pygame.Rect(
                info_center[0] + 14,
                info_center[1] - 15,
                tooltip_text.get_width()
                + tooltip_padding_x * 2,
                tooltip_text.get_height()
                + tooltip_padding_y * 2,
            )

            tooltip_shadow = tooltip_rect.move(3, 3)

            pygame.draw.rect(
                screen,
                SETUP_PANEL_SHADOW,
                tooltip_shadow,
            )

            pygame.draw.rect(
                screen,
                SETUP_INPUT,
                tooltip_rect,
            )

            draw_pixel_frame(
                tooltip_rect,
                SETUP_BORDER,
                width=1,
            )

            screen.blit(
                tooltip_text,
                (
                    tooltip_rect.left + tooltip_padding_x,
                    tooltip_rect.top + tooltip_padding_y,
                ),
            )

        connect_hovered = connect_rect.collidepoint(
            mouse_pos
        )

        button_shadow = connect_rect.move(5, 5)
        pygame.draw.rect(
            screen,
            SETUP_BUTTON_SHADOW,
            button_shadow,
        )

        pygame.draw.rect(
            screen,
            (
                SETUP_BUTTON_HOVER
                if connect_hovered
                else SETUP_BORDER
            ),
            connect_rect,
        )

        draw_pixel_frame(
            connect_rect,
            SETUP_TEXT if connect_hovered else SETUP_BORDER_DIM,
            width=2,
        )

        connect_text = button_font.render(
            "CONNECT",
            True,
            SETUP_PANEL_SHADOW,
        )

        screen.blit(
            connect_text,
            connect_text.get_rect(
                center=connect_rect.center
            ),
        )

        hint = small_font.render(
            "Token is stored locally",
            True,
            SETUP_MUTED,
        )

        screen.blit(
            hint,
            hint.get_rect(
                center=(WIDTH // 2, 445)
            ),
        )

        if status_message:
            status_color = (
                SETUP_SUCCESS
                if status_success
                else SETUP_ERROR
            )

            status = small_font.render(
                status_message,
                True,
                status_color,
            )

            status_shadow = small_font.render(
                status_message,
                True,
                SETUP_PANEL_SHADOW,
            )

            status_rect = status.get_rect(
                center=(WIDTH // 2, 357)
            )

            screen.blit(
                status_shadow,
                status_rect.move(1, 1),
            )

            screen.blit(
                status,
                status_rect,
            )

        # Draw our bubble cursor last so it always sits above the UI.
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cursor_rect = bubble_cursor.get_rect(
            center=(mouse_x, mouse_y)
        )
        screen.blit(
            bubble_cursor,
            cursor_rect,
        )

    try:
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
                    if username_rect.collidepoint(
                        event.pos
                    ):
                        active_field = "username"

                    elif token_rect.collidepoint(
                        event.pos
                    ):
                        active_field = "token"

                    elif connect_rect.collidepoint(
                        event.pos
                    ):
                        if attempt_connection():
                            return

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        active_field = (
                            "token"
                            if active_field == "username"
                            else "username"
                        )
                        continue

                    if event.key in (
                        pygame.K_RETURN,
                        pygame.K_KP_ENTER,
                    ):
                        if attempt_connection():
                            return
                        continue

                    if event.key == pygame.K_BACKSPACE:
                        if active_field == "username":
                            username = username[:-1]
                        else:
                            token = token[:-1]
                        continue

                    ctrl_down = (
                        event.mod & pygame.KMOD_CTRL
                    )

                    if (
                        ctrl_down
                        and event.key == pygame.K_v
                    ):
                        pasted = get_clipboard_text()

                        if active_field == "username":
                            username += pasted
                        else:
                            token += pasted

                        continue

                    if event.unicode and event.unicode.isprintable():
                        if active_field == "username":
                            username += event.unicode
                        else:
                            token += event.unicode

            update_setup_bubbles()
            draw_setup_screen()
            pygame.display.flip()
            clock.tick(60)

    finally:
        pygame.mixer.music.stop()
        pygame.mouse.set_visible(True)


# -------------------------
# GitHub connection check
# -------------------------

if not config_exists():
    run_first_time_setup()


github_connected, github_result = (
    validate_github_connection()
)

if not github_connected:
    print(
        "GitHub connection failed:",
        github_result,
    )

    pygame.quit()

    raise SystemExit

print(
    "Connected to GitHub as",
    github_result["login"],
)


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

# User data lives outside the game folder so updates can replace the
# executable/files without touching the player's aquarium.
SAVE_FILE = get_app_data_dir() / "save.json"

# One-time migration for existing development installs.
# If a save.json exists beside aquarium.py and AppData does not have one
# yet, copy it across before loading the game.
LEGACY_SAVE_FILE = (
    Path(__file__).resolve().parent
    / "save.json"
)

if (
    not SAVE_FILE.exists()
    and LEGACY_SAVE_FILE.exists()
):
    shutil.copy2(
        LEGACY_SAVE_FILE,
        SAVE_FILE,
    )

    print(
        "Migrated save data to:",
        SAVE_FILE,
    )


def load_save():
    try:
        with open(
            SAVE_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(
                file
            )

    except (
        FileNotFoundError,
        json.JSONDecodeError,
    ):
        return {
            "seen_commits": [],
            "fish": [],
        }


def save_game(save_data):
    with open(
        SAVE_FILE,
        "w",
        encoding="utf-8",
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
# First-time baseline
# -------------------------

if not seen_commits:
    seen_commits = {
        commit["sha"]
        for commit in commits
    }

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

sound_visible_rect = sound_on_image.get_bounding_rect()

sound_button_rect = pygame.Rect(
    sound_button_x + sound_visible_rect.x,
    sound_button_y + sound_visible_rect.y,
    sound_visible_rect.width,
    sound_visible_rect.height,
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
# Fish collection UI
# -------------------------

collection_ui_original = pygame.image.load(
    "assets/ui/collection_ui.png"
).convert_alpha()

info_button_original = pygame.image.load(
    "assets/ui/info_button.png"
).convert_alpha()


def crop_transparent(image):
    crop_rect = image.get_bounding_rect()

    if crop_rect.width == 0 or crop_rect.height == 0:
        return image

    return image.subsurface(
        crop_rect
    ).copy()


# The GIMP exports have transparent canvas around the artwork.
# Crop that away so positioning is based on the visible pixels.
collection_ui_original = crop_transparent(
    collection_ui_original
)

info_button_original = crop_transparent(
    info_button_original
)

COLLECTION_UI_SCALE = 1.6
INFO_BUTTON_SCALE = 2

collection_ui_image = pygame.transform.scale(
    collection_ui_original,
    (
        int(
            collection_ui_original.get_width()
            * COLLECTION_UI_SCALE
        ),
        int(
            collection_ui_original.get_height()
            * COLLECTION_UI_SCALE
        ),
    ),
)

info_button_image = pygame.transform.scale(
    info_button_original,
    (
        info_button_original.get_width()
        * INFO_BUTTON_SCALE,
        info_button_original.get_height()
        * INFO_BUTTON_SCALE,
    ),
)

# Visible collection artwork sits at the bottom center.
collection_ui_rect = collection_ui_image.get_rect(
    midbottom=(
        WIDTH // 2,
        HEIGHT - 5,
    )
)

# Visible collection button sits immediately beside the visible sound icon.
info_button_rect = info_button_image.get_rect(
    midleft=(
        30,
        42,
    )
)


info_visible_rect = info_button_image.get_bounding_rect()

info_button_hitbox = pygame.Rect(
    info_button_rect.x + info_visible_rect.x,
    info_button_rect.y + info_visible_rect.y,
    info_visible_rect.width,
    info_visible_rect.height,
)

collection_open = False
collection_index = 0

collection_counter_font = pygame.font.Font(None, 22)
collection_name_font = pygame.font.Font(None, 18)
collection_rarity_font = pygame.font.Font(None, 18)


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
    "mikey": {"name": "Mikey", "image": "assets/mikey.png"},
    "maude": {"name": "Maude", "image": "assets/maude.png"},
    "jake": {"name": "Jake", "image": "assets/jake.png"},
    "bentley": {"name": "Bentley", "image": "assets/Bentley.png"},
    "guy": {"name": "Guy", "image": "assets/Guy.png"},
    "clown": {"name": "Clown", "image": "assets/clown.png"},
    "goof": {"name": "Goof", "image": "assets/goof.png"},
    "puff_daddy": {"name": "Puff Daddy", "image": "assets/Puff Daddy.png"},
    "long": {"name": "Long", "image": "assets/long.png"},
    "bruce": {"name": "Bruce", "image": "assets/bruce.png"},
    "red": {"name": "Red", "image": "assets/Red.png"},
    "randall": {"name": "Randall", "image": "assets/Randall.png"},
    "boner": {"name": "Boner", "image": "assets/boner.png"},
    "apple": {"name": "Apple", "image": "assets/Apple.png"},
    "ralf": {"name": "Ralf", "image": "assets/Ralf.png"},
    "lucas": {"name": "Lucas", "image": "assets/Lucas.png"},
    "patrick": {"name": "Patrick", "image": "assets/Patrick.png"},
    "bella": {"name": "Bella", "image": "assets/bella.png"},
    "bubbles": {"name": "Bubbles", "image": "assets/Bubbles.png"},
}


# -------------------------
# Rarity pools
# -------------------------

RARITY_POOLS = {
    "common": ["mikey", "maude", "jake", "bentley", "guy"],
    "uncommon": ["clown", "goof", "puff_daddy"],
    "rare": ["long", "bruce", "red", "randall"],
    "epic": ["boner", "apple", "ralf", "lucas", "patrick"],
    "legendary": ["bella", "bubbles"],
}


COLLECTION_ORDER = [
    "james",
    "mikey", "maude", "jake", "bentley", "guy",
    "clown", "goof", "puff_daddy",
    "long", "bruce", "red", "randall",
    "boner", "apple", "ralf", "lucas", "patrick",
    "bella", "bubbles",
]

COLLECTION_RARITY = {
    species_id: rarity
    for rarity, species_ids in RARITY_POOLS.items()
    for species_id in species_ids
}
COLLECTION_RARITY["james"] = "starter"

COLLECTION_RARITY_COLORS = {
    "starter": (255, 215, 50),
    "common": (220, 220, 220),
    "uncommon": (90, 220, 120),
    "rare": (80, 150, 255),
    "epic": (210, 90, 255),
    "legendary": (255, 215, 50),
}


def get_collection_species(species_id):
    if species_id == "james":
        return {
            "name": "James the Fish",
            "image": "assets/james-the-fish.png",
        }

    return FISH_SPECIES[species_id]


def get_discovered_species():
    discovered = {"james"}

    discovered.update(
        owned_fish["species"]
        for owned_fish in saved_fish
    )

    return discovered


def get_collection_arrow_rects():
    left_arrow_center = (
        collection_ui_rect.left
        + int(
            collection_ui_rect.width
            * 0.29
        ),
        collection_ui_rect.top
        + int(
            collection_ui_rect.height
            * 0.69
        ),
    )

    right_arrow_center = (
        collection_ui_rect.left
        + int(
            collection_ui_rect.width
            * 0.72
        ),
        collection_ui_rect.top
        + int(
            collection_ui_rect.height
            * 0.69
        ),
    )

    left_arrow_rect = pygame.Rect(
        0,
        0,
        46,
        38,
    )
    left_arrow_rect.center = (
        left_arrow_center
    )

    right_arrow_rect = pygame.Rect(
        0,
        0,
        46,
        38,
    )
    right_arrow_rect.center = (
        right_arrow_center
    )

    return (
        left_arrow_rect,
        right_arrow_rect,
    )


def draw_collection_fish(
    species_id,
    center,
    max_width,
    max_height,
):
    if species_id not in get_discovered_species():
        return

    species = get_collection_species(species_id)

    fish_image = pygame.image.load(
        species["image"]
    ).convert_alpha()

    scale = min(
        max_width / fish_image.get_width(),
        max_height / fish_image.get_height(),
    )
    scale = max(1, int(scale))

    fish_image = pygame.transform.scale(
        fish_image,
        (
            fish_image.get_width() * scale,
            fish_image.get_height() * scale,
        ),
    )

    clear_rect = pygame.Rect(
        center[0] - max_width // 2,
        center[1] - max_height // 2,
        max_width,
        max_height,
    )

    pygame.draw.rect(
        screen,
        (0, 0, 0),
        clear_rect,
    )

    fish_rect = fish_image.get_rect(
        center=center
    )

    screen.blit(
        fish_image,
        fish_rect,
    )


def draw_collection():
    screen.blit(
        collection_ui_image,
        collection_ui_rect,
    )

    total = len(
        COLLECTION_ORDER
    )

    previous_species = COLLECTION_ORDER[
        (collection_index - 1) % total
    ]

    current_species = COLLECTION_ORDER[
        collection_index
    ]

    next_species = COLLECTION_ORDER[
        (collection_index + 1) % total
    ]

    center_x = collection_ui_rect.centerx

    # Positions are based on the visible artwork after transparent
    # canvas has been cropped away.
    main_center = (
        center_x,
        collection_ui_rect.top
        + int(
            collection_ui_rect.height
            * 0.35
        ),
    )

    left_center = (
        collection_ui_rect.left
        + int(
            collection_ui_rect.width
            * 0.15
        ),
        collection_ui_rect.top
        + int(
            collection_ui_rect.height
            * 0.53
        ),
    )

    right_center = (
        collection_ui_rect.right
        - int(
            collection_ui_rect.width
            * 0.15
        ),
        collection_ui_rect.top
        + int(
            collection_ui_rect.height
            * 0.53
        ),
    )

    draw_collection_fish(
        previous_species,
        left_center,
        58,
        38,
    )

    draw_collection_fish(
        current_species,
        main_center,
        120,
        70,
    )

    draw_collection_fish(
        next_species,
        right_center,
        58,
        38,
    )

    discovered = get_discovered_species()

    if current_species in discovered:
        species = get_collection_species(
            current_species
        )

        rarity = COLLECTION_RARITY[
            current_species
        ]

        name_text = collection_name_font.render(
            species["name"].upper(),
            True,
            (
                255,
                255,
                255,
            ),
        )

        rarity_text = collection_rarity_font.render(
            rarity.upper(),
            True,
            COLLECTION_RARITY_COLORS[
                rarity
            ],
        )

        name_rect = name_text.get_rect(
            center=(
                center_x,
                collection_ui_rect.top
                + int(
                    collection_ui_rect.height
                    * 0.61
                ),
            )
        )

        rarity_rect = rarity_text.get_rect(
            center=(
                center_x,
                collection_ui_rect.top
                + int(
                    collection_ui_rect.height
                    * 0.72
                ),
            )
        )

        screen.blit(
            name_text,
            name_rect,
        )

        screen.blit(
            rarity_text,
            rarity_rect,
        )

    # Page number goes in the small bottom tab built into the artwork.
    counter_text = collection_counter_font.render(
        f"{collection_index + 1} / {total}",
        True,
        (
            255,
            255,
            255,
        ),
    )

    counter_rect = counter_text.get_rect(
        center=(
            center_x,
            collection_ui_rect.top
            + int(
                collection_ui_rect.height
                * 0.91
            ),
        )
    )

    screen.blit(
        counter_text,
        counter_rect,
    )


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

    screen.blit(
        info_button_image,
        info_button_rect,
    )

    if collection_open:
        draw_collection()


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
                # Collection button
                # ---------------------

                elif info_button_hitbox.collidepoint(
                    event.pos
                ):
                    mouse_click_sound.play()

                    collection_open = (
                        not collection_open
                    )

                # ---------------------
                # Collection arrows
                # ---------------------

                elif collection_open:
                    (
                        left_arrow_rect,
                        right_arrow_rect,
                    ) = get_collection_arrow_rects()

                    if left_arrow_rect.collidepoint(
                        event.pos
                    ):
                        mouse_click_sound.play()

                        collection_index = (
                            collection_index - 1
                        ) % len(COLLECTION_ORDER)

                    elif right_arrow_rect.collidepoint(
                        event.pos
                    ):
                        mouse_click_sound.play()

                        collection_index = (
                            collection_index + 1
                        ) % len(COLLECTION_ORDER)

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


    # -------------------------
    # Collection UI
    # -------------------------

    screen.blit(
        info_button_image,
        info_button_rect,
    )

    if collection_open:
        draw_collection()


    pygame.display.flip()

    clock.tick(
        60
    )


pygame.quit()