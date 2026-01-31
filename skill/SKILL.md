---
name: zeroprompt-profile-builder
description: Reverse-engineer prompt text files into ZeroPrompt V2 JSON profiles. Use when user provides a .txt file containing prompts (one per line) and wants to convert it into a vocabulary-based procedural generation profile. Triggers on phrases like "convert prompts to profile", "make a zeroprompt profile", "reverse engineer this prompt list", "create profile from prompts", "build zeroprompt json", or when user uploads a .txt prompt file and mentions ZeroPrompt/JSON/profile.
---

# ZeroPrompt Profile Builder

Convert corpus-based prompt lists (.txt) into procedural generation profiles (.json) for DJZ-ZeroPrompt-V2.

## Overview

This skill transforms a collection of human-written prompts into a vocabulary decomposition that can procedurally generate similar prompts. The goal is to capture the **semantic essence** of the corpus while enabling infinite novel combinations.

## The Conversion Pipeline

```
INPUT: prompts.txt (N lines of human-written prompts)
           ↓
    [1] Pattern Analysis
           ↓
    [2] Vocabulary Extraction
           ↓
    [3] Template Synthesis
           ↓
    [4] Profile Assembly
           ↓
OUTPUT: profile.json (ZeroPrompt V2 compatible)
```

---

## Step 1: Pattern Analysis

Read the entire prompt corpus and identify:

### 1.1 Structural Patterns
- What elements appear consistently? (subjects, styles, quality tags)
- What is the typical prompt structure? (subject-first? style-first?)
- Are there recurring phrase patterns?

### 1.2 Semantic Categories
Map observed content to standard pools:

| Pool | Look For |
|------|----------|
| `subject` | People, characters, creatures, objects - the "who/what" |
| `action` | Verbs, activities, poses - the "doing what" |
| `environment` | Locations, settings, backgrounds - the "where" |
| `style` | Art styles, aesthetic references, artist names |
| `lighting` | Light sources, atmosphere, time of day |
| `camera` | Shot types, angles, framing, lens effects |
| `details` | Quality modifiers, resolution, technical specs |
| `mood` | Emotions, atmosphere descriptors, tone |

### 1.3 Custom Categories
If the corpus has domain-specific vocabulary that doesn't fit standard pools, create custom pools:
- `outfit` - for fashion/character prompts
- `color_palette` - for specific color schemes
- `texture` - for material-focused prompts
- `era` - for historical/period pieces
- `weather` - for environmental conditions
- `species` - for creature-focused prompts
- `vehicle` - for transportation themes
- `weapon` - for combat/action themes

---

## Step 2: Vocabulary Extraction

### 2.1 Tokenization Strategy

Split prompts on common delimiters: `,` `- ` ` | ` and classify each segment.

### 2.2 Classification Heuristics

**Subject Detection:**
- Starts with articles: "a", "an", "the"
- Contains person words: "woman", "man", "girl", "boy", "person"
- Contains creature words: "dragon", "wolf", "robot", "alien"
- Contains role words: "warrior", "wizard", "detective", "pilot"

**Style Detection:**
- Contains "style", "aesthetic", "art"
- Matches known styles: "photorealistic", "anime", "oil painting"
- Contains artist references: "by [Name]", "[Name] style"
- Contains movement names: "art nouveau", "baroque", "impressionist"

**Environment Detection:**
- Contains location words: "forest", "city", "room", "planet"
- Contains prepositions: "in a", "at the", "inside", "within"
- Contains setting descriptors: "ancient", "futuristic", "abandoned"

**Lighting Detection:**
- Contains "light", "lighting", "lit", "glow"
- Contains time words: "sunset", "dawn", "night", "golden hour"
- Contains atmosphere: "foggy", "misty", "volumetric"

**Camera Detection:**
- Contains shot types: "close-up", "wide shot", "portrait"
- Contains angles: "low angle", "bird's eye", "dutch angle"
- Contains lens terms: "bokeh", "depth of field", "fisheye"

**Details Detection:**
- Contains quality words: "detailed", "intricate", "sharp"
- Contains resolution: "4k", "8k", "HD"
- Contains platform references: "artstation", "behance"

**Mood Detection:**
- Emotion words: "serene", "ominous", "joyful"
- Atmosphere words: "mysterious", "epic", "intimate"
- Tone words: "dark", "bright", "melancholic"

### 2.3 Deduplication & Normalization

- Remove duplicates (case-insensitive comparison)
- Strip trailing punctuation
- Standardize spacing
- Sort alphabetically within pools

---

## Step 3: Template Synthesis

### 3.1 Analyze Prompt Structure

Identify the dominant ordering patterns in the corpus:

```
Pattern A: {subject}, {environment}, {style}, {lighting}, {details}
Pattern B: {style} {subject} in {environment}, {mood}, {details}
Pattern C: {camera} of {subject}, {style}, {lighting}, {mood}
```

### 3.2 Generate Templates

Create 4-8 templates that:
1. Cover the most common structures in the corpus
2. Use all extracted pools at least once across templates
3. Maintain grammatical coherence

### 3.3 Template Rules

- Use `{pool_name}` syntax for variables
- Keep articles/prepositions in templates, not pools
- Include connecting words: "in", "of", "with", "at"

**Good:**
```
"{subject} in {environment}, {style}, {lighting}"
```

**Bad:**
```
"{subject} {preposition} {environment}"  # Don't make preposition a pool
```

---

## Step 4: Profile Assembly

### 4.1 JSON Structure

```json
{
  "name": "Profile Name",
  "description": "What this profile generates - converted from [source]",
  "version": "1.0.0",
  
  "templates": [
    "template string with {pool} references",
    "another template with {different} {structure}"
  ],
  
  "pools": {
    "subject": ["item1", "item2"],
    "action": ["item1", "item2"],
    "environment": ["item1", "item2"],
    "style": ["item1", "item2"],
    "lighting": ["item1", "item2"],
    "camera": ["item1", "item2"],
    "details": ["item1", "item2"],
    "mood": ["item1", "item2"]
  }
}
```

### 4.2 Validation Checklist

- [ ] All `{pool}` references in templates exist in pools
- [ ] No empty pools
- [ ] Valid JSON syntax
- [ ] Reasonable pool sizes (5-100 items typical)
- [ ] Templates produce grammatical output
- [ ] No duplicate items within pools

---

## Reference: Profile Examples

### Default Profile (188 trillion combinations)

Full vocabulary covering all categories:

```json
{
  "name": "Default",
  "description": "Full vocabulary profile with all categories - 188+ trillion combinations",
  "version": "1.0.0",
  
  "templates": [
    "{subject} {action} {environment}, {style}, {lighting}, {camera}, {details}, {mood} atmosphere",
    "{camera} of {subject} {action} {environment}, {style}, {lighting}, {details}, {mood}",
    "{style} {subject}, {environment}, {lighting}, {mood} mood, {details}",
    "{subject} in {environment}, {mood} {style}, {lighting}, {camera}, {details}",
    "{mood} scene of {subject} {action} {environment}, {style}, {lighting}, {details}",
    "{style} depicting {subject}, {environment} setting, {lighting}, {camera}",
    "{camera}, {subject} {action} {environment}, {style}, {mood}, {details}",
    "{subject}, {environment}, {style}, {lighting}, {mood} atmosphere, {details}"
  ],
  
  "pools": {
    "subject": [
      "a woman", "a man", "a young woman", "a young man", "an elderly woman",
      "an elderly man", "a child", "a teenager", "a couple", "a group of people",
      "a knight", "a wizard", "a witch", "a sorceress", "a necromancer",
      "a paladin", "a rogue", "an assassin", "a ranger", "a barbarian",
      "a druid", "a monk", "a bard", "a warlock", "an elven archer",
      "a dwarven smith", "an orc warrior", "a goblin", "a fairy", "a nymph",
      "a cyborg", "an android", "a robot", "a mech pilot", "an astronaut",
      "a space marine", "an alien", "a hacker", "a scientist", "a bounty hunter",
      "a samurai", "a ninja", "a viking", "a gladiator", "a pharaoh",
      "a geisha", "a shogun", "a roman soldier", "a medieval peasant", "a noble",
      "a detective", "a soldier", "a pilot", "a doctor", "an artist",
      "a musician", "a dancer", "an athlete", "a chef", "a photographer",
      "a dragon", "a phoenix", "a griffin", "a unicorn", "a werewolf",
      "a vampire", "a demon", "an angel", "a ghost", "a spirit",
      "a wolf", "a lion", "a tiger", "an eagle", "a raven",
      "a serpent", "a whale", "a shark", "a butterfly", "a spider",
      "a mechanical spider", "a clockwork automaton", "a golem", "a sentient statue",
      "a living shadow", "an elemental being", "a slime creature", "a treant"
    ],
    "action": [
      "standing in", "sitting in", "kneeling in", "floating above", "hovering over",
      "resting in", "meditating in", "posing in", "waiting in", "watching over",
      "walking through", "running through", "flying over", "swimming in", "climbing",
      "falling into", "descending into", "ascending toward", "emerging from", "diving into",
      "fighting in", "battling through", "defending", "attacking", "dueling in",
      "charging through", "retreating from", "ambushing in", "hunting in",
      "exploring", "discovering", "searching through", "investigating",
      "uncovering secrets in", "finding treasure in", "mapping",
      "summoning power in", "casting a spell in", "channeling energy in",
      "communing with nature in", "praying in", "performing a ritual in",
      "transforming in", "shapeshifting in", "awakening in",
      "mourning in", "celebrating in", "contemplating in", "dreaming in",
      "remembering in", "lost in thought in"
    ],
    "environment": [
      "a dark forest", "an enchanted forest", "a misty forest", "a bamboo forest",
      "a snowy mountain", "a volcanic mountain", "a floating mountain",
      "a vast desert", "an oasis", "a canyon", "a waterfall", "a river",
      "a beach at sunset", "a stormy sea", "a coral reef", "an underwater cavern",
      "a medieval castle", "a ruined fortress", "a gothic cathedral",
      "an ancient temple", "a hidden shrine", "a sacred grove",
      "a wizard's tower", "an alchemist's laboratory", "a royal throne room",
      "a dungeon", "catacombs", "a crypt", "a graveyard at midnight",
      "a cyberpunk city", "a neon-lit alley", "a futuristic metropolis",
      "a space station", "an alien planet", "a terraformed moon",
      "a dystopian wasteland", "a post-apocalyptic city", "a megastructure",
      "a virtual reality world", "inside a computer mainframe",
      "a crystal cave", "a bioluminescent cavern", "a floating island",
      "the astral plane", "between dimensions", "the void",
      "a pocket dimension", "a mirror world", "a dream realm",
      "cherry blossom gardens", "an autumn forest", "a field of flowers",
      "under the northern lights", "during a solar eclipse",
      "at the edge of the world", "at the crossroads of fate"
    ],
    "style": [
      "photorealistic", "hyperrealistic", "cinematic", "film still",
      "documentary photography", "portrait photography", "fashion photography",
      "oil painting", "watercolor painting", "acrylic painting", "gouache",
      "charcoal drawing", "pencil sketch", "ink drawing", "fresco",
      "art nouveau", "art deco", "baroque", "renaissance", "romanticism",
      "impressionist", "expressionist", "surrealist", "cubist",
      "pre-raphaelite", "ukiyo-e", "chinese ink wash",
      "concept art", "digital painting", "matte painting", "3D render",
      "low poly 3D", "voxel art", "pixel art", "vector art",
      "anime style", "manga style", "studio ghibli style", "disney style",
      "pixar style", "cartoon style", "comic book style", "graphic novel style",
      "vaporwave aesthetic", "synthwave", "cyberpunk aesthetic", "solarpunk",
      "dark academia", "cottagecore", "steampunk", "dieselpunk", "biopunk",
      "dark souls style", "elden ring style", "final fantasy style",
      "metal gear style", "borderlands style", "breath of the wild style"
    ],
    "lighting": [
      "golden hour lighting", "blue hour lighting", "harsh midday sun",
      "soft overcast light", "dappled forest light", "sunset backlight",
      "sunrise light", "moonlight", "starlight",
      "dramatic rim lighting", "chiaroscuro lighting", "spotlight",
      "harsh shadows", "silhouette lighting", "contre-jour",
      "neon lighting", "fluorescent lighting", "candlelight", "firelight",
      "bioluminescent glow", "magical glow", "holographic light",
      "volumetric lighting", "god rays", "light shafts", "foggy atmosphere",
      "misty atmosphere", "dusty atmosphere", "rainy atmosphere",
      "warm lighting", "cool lighting", "neutral lighting",
      "high contrast", "low key lighting", "high key lighting"
    ],
    "camera": [
      "extreme close-up", "close-up portrait", "medium shot", "full body shot",
      "wide shot", "extreme wide shot", "establishing shot",
      "eye level", "low angle shot", "high angle shot", "bird's eye view",
      "worm's eye view", "dutch angle", "overhead shot",
      "first person view", "over the shoulder", "point of view shot",
      "three-quarter view", "profile view", "frontal view", "rear view",
      "shallow depth of field", "deep focus", "bokeh background",
      "motion blur", "long exposure", "tilt-shift", "fisheye lens",
      "wide angle lens", "telephoto compression", "macro shot"
    ],
    "details": [
      "highly detailed", "intricate details", "fine details", "subtle details",
      "sharp focus", "crystal clear", "pristine quality",
      "4k", "8k", "high resolution", "ultra HD",
      "masterpiece", "award winning", "professional", "museum quality",
      "trending on artstation", "featured on behance", "gallery quality",
      "ray tracing", "global illumination", "subsurface scattering",
      "ambient occlusion", "realistic textures", "photogrammetry",
      "expressive brushwork", "visible brushstrokes", "smooth gradients",
      "rich colors", "vibrant palette", "muted tones", "monochromatic"
    ],
    "mood": [
      "serene", "peaceful", "tranquil", "joyful", "euphoric",
      "whimsical", "playful", "romantic", "hopeful", "triumphant",
      "ominous", "foreboding", "melancholic", "sorrowful", "tragic",
      "terrifying", "horrific", "unsettling", "disturbing",
      "mysterious", "enigmatic", "surreal", "dreamlike", "ethereal",
      "nostalgic", "bittersweet", "contemplative", "introspective",
      "tense", "intense", "chaotic", "explosive", "dynamic",
      "calm", "still", "quiet", "subtle", "understated",
      "epic", "grand", "intimate", "cozy", "lonely", "isolated",
      "crowded", "bustling", "abandoned", "timeless"
    ]
  }
}
```

### Cyberpunk Profile (31 billion combinations)

Focused vocabulary for neon-soaked dystopian imagery:

```json
{
  "name": "Cyberpunk",
  "description": "Focused cyberpunk/sci-fi vocabulary for neon-soaked dystopian imagery",
  "version": "1.0.0",
  
  "templates": [
    "{subject} {action} {environment}, {style}, {lighting}, {camera}, {details}, {mood} atmosphere",
    "{camera} of {subject} {action} {environment}, {style}, {lighting}, {details}, {mood}",
    "{style} {subject} in {environment}, {lighting}, {mood} mood, {details}",
    "{mood} scene of {subject} {action} {environment}, {style}, {lighting}, {details}",
    "cinematic {camera}, {subject} {action} {environment}, {style}, {lighting}, {mood}"
  ],
  
  "pools": {
    "subject": [
      "a cyborg", "an android", "a hacker", "a street samurai", "a netrunner",
      "a corporate soldier", "a bounty hunter", "a rogue AI", "a synth",
      "a mercenary", "a fixer", "a smuggler", "a chrome-armed warrior",
      "a neural hacker", "a biohacked human", "a synthetic human",
      "a megacorp executive", "a street vendor", "a neon preacher",
      "a cybernetic ninja", "a drone pilot", "a data thief",
      "a augmented detective", "a rebel leader", "a tech priest"
    ],
    "action": [
      "standing in", "running through", "hacking into", "surveilling",
      "infiltrating", "escaping from", "fighting in", "hiding in",
      "jacking into", "downloading data in", "stalking through",
      "fleeing through", "pursuing targets in", "making deals in",
      "scavenging in", "patrolling", "ambushing in"
    ],
    "environment": [
      "a neon-lit alley", "a cyberpunk city", "a futuristic metropolis",
      "a rain-soaked street", "a megacorp tower", "a black market",
      "a underground club", "a hacker den", "a chop shop",
      "a corporate plaza", "a slum district", "a rooftop garden",
      "a virtual reality world", "inside a computer mainframe",
      "a abandoned factory", "a neon arcade", "a synth bar",
      "a augmentation clinic", "a data center", "a skybridge",
      "a flooded lower city", "a holographic plaza", "a smuggler's hideout"
    ],
    "style": [
      "cyberpunk aesthetic", "blade runner style", "ghost in the shell style",
      "cinematic", "hyperrealistic", "neon noir", "tech noir",
      "akira style", "concept art", "digital painting", "3D render",
      "photorealistic", "dystopian realism", "neo-tokyo style",
      "synthwave", "vaporwave aesthetic", "gritty realism"
    ],
    "lighting": [
      "neon lighting", "holographic light", "rain-refracted neon",
      "harsh fluorescent", "bioluminescent glow", "LED strips",
      "volumetric fog", "dramatic rim lighting", "low key lighting",
      "high contrast", "glitching light", "pulsing neon",
      "cool blue lighting", "magenta and cyan neon", "foggy atmosphere"
    ],
    "camera": [
      "close-up portrait", "medium shot", "wide shot", "establishing shot",
      "low angle shot", "dutch angle", "over the shoulder",
      "first person view", "shallow depth of field", "bokeh background",
      "long exposure light trails", "motion blur", "surveillance camera angle"
    ],
    "details": [
      "highly detailed", "intricate details", "8k", "ultra HD",
      "ray tracing", "realistic textures", "sharp focus",
      "trending on artstation", "cinematic quality", "film grain",
      "chromatic aberration", "lens flare", "rain droplets on lens"
    ],
    "mood": [
      "ominous", "tense", "mysterious", "dystopian", "melancholic",
      "intense", "dangerous", "lonely", "alienating", "chaotic",
      "oppressive", "paranoid", "desperate", "rebellious", "noir"
    ]
  }
}
```

### Fantasy Profile (55 billion combinations)

Epic high fantasy and medieval vocabulary:

```json
{
  "name": "Fantasy",
  "description": "High fantasy and medieval vocabulary for epic magical imagery",
  "version": "1.0.0",
  
  "templates": [
    "{subject} {action} {environment}, {style}, {lighting}, {camera}, {details}, {mood} atmosphere",
    "{camera} of {subject} {action} {environment}, {style}, {lighting}, {details}",
    "{style} {subject} in {environment}, {lighting}, {mood} mood, {details}",
    "epic {mood} scene of {subject} {action} {environment}, {style}, {lighting}, {details}",
    "{style} depicting {subject}, {environment} setting, {lighting}, {camera}, {mood}",
    "majestic {subject} {action} {environment}, {style}, {lighting}, {details}"
  ],
  
  "pools": {
    "subject": [
      "a knight in shining armor", "a wise wizard", "a dark sorceress", "an elven queen",
      "a dwarven king", "a young hero", "a battle-worn paladin", "a mysterious ranger",
      "a fierce barbarian", "a cunning rogue", "a holy cleric", "a wild druid",
      "a noble prince", "a warrior princess", "an ancient dragon", "a phoenix rising",
      "a majestic griffin", "a ethereal unicorn", "a fearsome werewolf", "an elegant vampire",
      "a celestial angel", "a fallen angel", "a bound demon", "a forest spirit",
      "a water nymph", "an earth elemental", "a fire elemental", "a storm giant",
      "a treant guardian", "a wise centaur", "a mysterious sphinx", "a noble pegasus"
    ],
    "action": [
      "standing guard in", "riding through", "battling evil in", "casting a spell in",
      "defending the realm in", "seeking wisdom in", "training warriors in",
      "forging legendary weapons in", "communing with spirits in", "leading an army through",
      "discovering ancient secrets in", "breaking a curse in", "protecting the innocent in",
      "ascending the throne in", "fulfilling a prophecy in", "making a last stand in",
      "embarking on a quest in", "returning victorious to"
    ],
    "environment": [
      "an enchanted forest", "a mystical glade", "ancient ruins", "a dragon's lair",
      "a towering castle", "a medieval throne room", "a wizard's tower",
      "a sacred temple", "a hidden elven city", "a dwarven mountain hall",
      "a battlefield at dawn", "a mystical lake", "the edge of a cliff",
      "a fairy ring", "an ancient library", "a cursed swamp",
      "a floating citadel", "the realm between worlds", "a celestial palace",
      "a volcanic forge", "an ice fortress", "a garden of statues",
      "a crystal cavern", "the world tree", "a moonlit clearing"
    ],
    "style": [
      "oil painting", "renaissance masterpiece", "pre-raphaelite style", "romanticism",
      "concept art", "epic fantasy art", "book cover illustration", "classical painting",
      "digital painting", "fantasy realism", "dark fantasy style", "high fantasy art",
      "studio ghibli style", "lord of the rings style", "game of thrones style",
      "frazetta style", "boris vallejo style", "medieval manuscript illumination"
    ],
    "lighting": [
      "golden hour lighting", "ethereal glow", "magical light", "divine rays",
      "moonlight", "firelight", "candlelight", "torchlight",
      "dramatic god rays", "mystical fog", "aurora borealis",
      "sunset light", "dawn light", "starlight", "bioluminescent glow"
    ],
    "camera": [
      "wide establishing shot", "epic wide shot", "medium shot", "portrait shot",
      "low angle heroic shot", "high angle view", "dramatic close-up",
      "bird's eye view", "three-quarter view", "profile silhouette"
    ],
    "details": [
      "highly detailed", "intricate details", "ornate details", "masterfully crafted",
      "8k resolution", "museum quality", "award winning", "masterpiece",
      "rich textures", "gilded accents", "jeweled embellishments", "fine craftsmanship"
    ],
    "mood": [
      "epic", "majestic", "triumphant", "heroic", "noble",
      "mysterious", "ancient", "magical", "ethereal", "divine",
      "ominous", "foreboding", "dark", "tragic", "melancholic",
      "serene", "peaceful", "hopeful", "romantic", "legendary"
    ]
  }
}
```

---

## Workflow Summary

### When User Provides a .txt Prompt File:

1. **Read and analyze** the entire file
2. **Count prompts** and report corpus size
3. **Identify dominant patterns** (show 2-3 examples)
4. **Extract vocabulary** into semantic pools
5. **Synthesize templates** from observed structures
6. **Generate complete JSON profile**
7. **Calculate and report statistics:**
   - Pool sizes
   - Total combinations (multiply: templates × pool1 × pool2 × ...)
8. **Demonstrate** with 3-5 sample generated prompts

### Output Format

Always provide:

```
## Analysis Summary
- Corpus size: N prompts
- Dominant structure: [description]
- Identified pools: [list]

## Generated Profile
[Complete JSON]

## Statistics
- Templates: N
- Pool sizes: subject(N), action(N), ...
- Total combinations: N (scientific notation)

## Sample Outputs
Using seed=42, indices 0-4:
[0] generated prompt...
[1] generated prompt...
...
```

---

## Edge Cases

### Sparse Corpus (<50 prompts)
- Warn user that extracted vocabulary may be limited
- Suggest manual expansion of pools
- Generate profile anyway with available content

### Highly Varied Corpus
- Focus on most common patterns
- May need multiple profiles for different styles
- Suggest splitting into themed subsets

### Domain-Specific Vocabulary
- Create custom pools as needed
- Document custom pool meanings in description
- Ensure templates reference all custom pools

### Missing Categories
- Not all prompts have all categories
- Make incomplete pools optional in some templates
- Create templates that work with available pools

---

## Quality Checklist

Before finalizing a profile:

- [ ] JSON is valid and parseable
- [ ] All template `{variables}` have corresponding pools
- [ ] Pool items are grammatically consistent
- [ ] No duplicate items within pools (case-insensitive)
- [ ] Templates produce natural-sounding prompts
- [ ] Profile generates output similar in style to input corpus
- [ ] Statistics calculated and reported
- [ ] Sample outputs demonstrated

---

## Calculation Reference

### Total Combinations Formula

```
total = len(templates) × len(pool_1) × len(pool_2) × ... × len(pool_n)
```

### Example
- 5 templates
- 25 subjects × 17 actions × 23 environments × 17 styles × 15 lighting × 13 camera × 13 details × 15 mood
- = 5 × 25 × 17 × 23 × 17 × 15 × 13 × 13 × 15
- = 31,594,021,875 combinations
