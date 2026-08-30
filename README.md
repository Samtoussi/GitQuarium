<p align="center">
  <img src="assets/docs/gq_logo.png" alt="GitQuarium Logo" width="500">
</p>

<h1 align="center">GitQuarium</h1>

<p align="center">
  <strong>Your GitHub activity, but fish.</strong>
</p>

<p align="center">
  A tiny pixel-art aquarium where your GitHub commits become fish.
</p>

---

<p align="center">
  <img src="assets/docs/gq_hero.png" alt="GitQuarium Aquarium" width="900">
</p>

## 🐟 What is GitQuarium?

GitQuarium turns your GitHub activity into a living pixel-art aquarium.

The rule is simple:

> **1 commit = 1 fish**

Make a commit, launch GitQuarium, and a new fish is waiting to be discovered.

Each fish belongs to a rarity tier, joins your aquarium permanently, and becomes part of your collection.

No productivity scores.  
No contribution streak optimization.  
Just fish.

## ✨ How it works

When GitQuarium starts, it checks your GitHub activity for commits it hasn't seen before.

If a new commit is found:

<p align="center">
  <img src="assets/docs/gq_new_fish.png" alt="New Fish Detected" width="650">
</p>

You get a fish reveal with a randomly rolled species and rarity.

<p align="center">
  <img src="assets/docs/gq_reveal.png" alt="Epic Fish Reveal" width="650">
</p>

The fish is then saved permanently and joins the aquarium.

## 🎲 Fish rarity

Every new commit rolls one of five rarity tiers:

| Rarity | Chance |
|---|---:|
| Common | 55% |
| Uncommon | 25% |
| Rare | 13% |
| Epic | 6% |
| Legendary | 1% |

The species is then randomly selected from that rarity's pool.

There are currently **20 fish species** to discover, including **James the Fish**, the one-of-one starter fish who cannot be rolled.

## 📖 Fish Collection

Your discoveries are tracked in the Fish Collection.

<p align="center">
  <img src="assets/docs/gq_info.png" alt="GitQuarium Fish Collection" width="700">
</p>

Discovered species reveal their name and rarity, while fish you haven't found yet remain hidden.

Duplicates still join the aquarium — because apparently one Maude was not enough.

## 🌊 Your aquarium changes with you

GitQuarium doesn't just count commits.

Your aquarium reacts to how active you've been:

- **0–2 days since your last commit:** Clean
- **3–4 days:** Slightly dirty
- **5–6 days:** Dirty
- **7+ days:** Absolute swamp

<p align="center">
  <img src="assets/docs/gq_swamp.png" alt="GitQuarium Absolute Swamp" width="650">
</p>

<p align="center">
  <em>Neglect your commits long enough and this is where your fish live.</em>
</p>

Stop coding long enough and your fish will be forced to live with the consequences.

## 🎮 Features

- GitHub commit detection
- 1 commit = 1 fish
- 20 unique fish species
- Five rarity tiers
- Animated fish with randomized movement
- Fish reveal system
- Persistent aquarium and collection
- GitHub activity-based tank decay
- Bubble effects
- Original pixel-art graphics
- Original GitQuarium soundtrack
- Sound effects and music controls
- Interactive fish
- Fish Collection browser
- Extremely important fish named things like Boner

## 🛠️ Built with

- **Python**
- **Pygame**
- **GitHub REST API**

Fish, environments and UI assets were created as custom pixel art.

## 🚀 Running GitQuarium

> **Note:** GitQuarium v1.0.0 currently requires a small amount of manual setup. Making GitQuarium easier for other people to connect to their own GitHub account is the next step.

### 1. Clone the repository

```bash
git clone https://github.com/Samtoussi/GitQuarium.git
cd GitQuarium
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install pygame requests python-dotenv
```

### 4. Configure GitHub

Create a `.env` file in the project root:

```env
GITHUB_USERNAME=your_github_username
GITHUB_TOKEN=your_github_token
```

Your `.env` file is ignored by Git and should never be committed.

### 5. Start GitQuarium

```bash
python aquarium.py
```

That's it.

Your GitHub activity is now fish.

## 💾 Save data

GitQuarium stores your local aquarium state in:

```text
save.json
```

This tracks previously seen commits and the fish you've collected.

The save file is local and excluded from Git.

## 🗺️ What's next?

Version **1.0.0** represents the complete first version of the GitQuarium game.

The next goal is not to add more gameplay systems — it's to make GitQuarium easier for other people to use with their own GitHub accounts.

That means improving setup and onboarding without turning a tiny fish game into enterprise infrastructure.

## 🐠 Philosophy

GitQuarium started as a deliberately small side project.

It is not trying to optimize your productivity.

It is not trying to gamify your career.

It turns commits into fish.

That's enough.

---

<p align="center">
  <strong>GitQuarium v1.0.0</strong>
  <br>
  Your GitHub activity, but fish.
</p>