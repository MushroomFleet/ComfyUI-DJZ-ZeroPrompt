# ComfyUI-DJZ-ZeroPrompt

**Zero files. Zero storage. Infinite prompts.**

A ComfyUI custom node pack that generates deterministic prompts using position-is-seed procedural generation. Instead of reading from user-maintained text files, these nodes compute prompts directly from mathematical coordinates—the same seed and index will always produce the same prompt, everywhere, every time.

![ZeroPrompt Banner](https://img.shields.io/badge/Prompts-188%20Trillion+-blue?style=for-the-badge)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

## 🚀 Features

- **Infinite Prompts**: 188+ trillion unique prompt combinations from the default profile
- **Perfect Determinism**: `seed=42, index=1000` produces identical output across all machines
- **O(1) Generation**: Direct hash computation—no file I/O, no iteration
- **Zero Maintenance**: No text files to curate, organize, or update
- **Reproducible Results**: Share seed+index coordinates to recreate exact prompts
- **Custom Profiles (V2)**: JSON-based vocabulary profiles for specialized generation

## 📦 Installation

### Method 1: ComfyUI Manager (Recommended)
1. Open ComfyUI Manager
2. Search for "DJZ-ZeroPrompt"
3. Click Install

### Method 2: Manual Installation
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/MushroomFleet/ComfyUI-DJZ-ZeroPrompt
cd ComfyUI-DJZ-ZeroPrompt
pip install -r requirements.txt
```

### Method 3: Direct Download
1. Download the repository as ZIP
2. Extract to `ComfyUI/custom_nodes/ComfyUI-DJZ-ZeroPrompt`
3. Install dependencies: `pip install xxhash`

## 🎯 Nodes

### DJZ Zero Prompt V1
The original node with built-in vocabulary. Simple and fast.

| Input | Type | Description |
|-------|------|-------------|
| `seed` | INT | World seed (0 to 4,294,967,295) |
| `prompt_index` | INT | Position in prompt space |
| `prefix` | STRING | Optional text to prepend |
| `suffix` | STRING | Optional text to append |

### DJZ Zero Prompt V2
Enhanced node with JSON profile support for customizable vocabulary.

| Input | Type | Description |
|-------|------|-------------|
| `profile` | DROPDOWN | Select vocabulary profile |
| `seed` | INT | World seed (0 to 4,294,967,295) |
| `prompt_index` | INT | Position in prompt space |
| `prefix` | STRING | Optional text to prepend |
| `suffix` | STRING | Optional text to append |

### DJZ Zero Prompt Profile Info
Utility node to display profile statistics (pool sizes, total combinations).

## 📁 Profile System (V2)

V2 introduces JSON profiles for customizable prompt generation. Profiles are stored in the `/profiles` folder.

### Included Profiles

| Profile | Description | Combinations |
|---------|-------------|--------------|
| `default.json` | Full vocabulary, all categories | 188+ trillion |
| `cyberpunk.json` | Neon-soaked dystopian sci-fi | 31+ billion |
| `fantasy.json` | Epic high fantasy and medieval | 4+ billion |

### Creating Custom Profiles

1. Copy an existing profile from `/profiles`
2. Rename it (e.g., `my_style.json`)
3. Edit the vocabulary pools and templates
4. Restart ComfyUI—your profile appears in the dropdown

### Profile JSON Structure

```json
{
  "name": "My Custom Profile",
  "description": "Description of the style",
  "version": "1.0.0",
  
  "templates": [
    "{subject} {action} {environment}, {style}, {lighting}",
    "{style} {subject} in {environment}, {mood} atmosphere"
  ],
  
  "pools": {
    "subject": ["a warrior", "a wizard", "a robot"],
    "action": ["standing in", "exploring", "fighting in"],
    "environment": ["a forest", "a city", "a cave"],
    "style": ["photorealistic", "anime style", "oil painting"],
    "lighting": ["golden hour", "neon lighting", "moonlight"],
    "mood": ["epic", "mysterious", "serene"]
  }
}
```

### Template Variables

Templates use `{pool_name}` syntax. Available variables depend on the pools defined:
- `{subject}` - Character or entity
- `{action}` - What they're doing
- `{environment}` - Where they are
- `{style}` - Art style
- `{lighting}` - Light conditions
- `{camera}` - Shot type
- `{details}` - Quality modifiers
- `{mood}` - Atmosphere

You can add custom pools—just define them in `pools` and reference them in `templates`.

## 💡 How It Works

### The ZeroBytes Methodology

Traditional prompt systems store prompts in files and select randomly. This approach has limitations:
- Finite prompts (limited by file size)
- Maintenance burden (curating text files)
- Non-deterministic selection (different results on different runs)

**ZeroPrompt** uses **position-is-seed** procedural generation:

```
(seed, prompt_index, [profile]) → xxhash32 → deterministic component selection → formatted prompt
```

A prompt is not retrieved—it's **computed** from coordinates in semantic space.

### Architecture

```
Prompt Space Hierarchy:
━━━━━━━━━━━━━━━━━━━━━━━
seed (world seed)
  └─ prompt_index (position)
       ├─ template[hash(seed, idx, 0)]
       ├─ subject[hash(seed, idx, 1)]
       ├─ action[hash(seed, idx, 2)]
       ├─ environment[hash(seed, idx, 3)]
       ├─ style[hash(seed, idx, 4)]
       ├─ lighting[hash(seed, idx, 5)]
       ├─ camera[hash(seed, idx, 6)]
       ├─ details[hash(seed, idx, 7)]
       └─ mood[hash(seed, idx, 8)]
```

### Vocabulary Pools (Default Profile)

| Pool | Entries | Examples |
|------|---------|----------|
| Subjects | 88 | "a knight", "a cyborg", "a dragon", "a witch" |
| Actions | 51 | "standing in", "exploring", "battling through" |
| Environments | 56 | "a dark forest", "a cyberpunk city", "the void" |
| Styles | 58 | "photorealistic", "anime style", "oil painting" |
| Lighting | 35 | "golden hour", "neon lighting", "volumetric fog" |
| Camera | 31 | "close-up portrait", "wide shot", "dutch angle" |
| Details | 31 | "highly detailed", "8k", "masterpiece" |
| Mood | 48 | "serene", "ominous", "mysterious", "epic" |
| Templates | 8 | Various composition structures |

**Total combinations: 188,274,509,660,160** (188+ trillion)

## 📊 Example Outputs

### Default Profile (seed=42)
```
[0] a dwarven smith, the astral plane, hyperrealistic, blue hour lighting, 
    intense atmosphere, intricate details

[1] a wolf in inside a computer mainframe, timeless vector art, sunset backlight, 
    point of view shot, pristine quality
```

### Cyberpunk Profile (seed=42)
```
[0] cinematic bokeh background, a data thief making deals in a augmentation clinic, 
    cinematic, pulsing neon, mysterious

[3] oppressive scene of a chrome-armed warrior running through a skybridge, 
    dystopian realism, volumetric fog, realistic textures
```

### Fantasy Profile (seed=42)
```
[0] a noble prince standing guard in a mystical lake, epic fantasy art, 
    moonlight, medium shot, masterfully crafted, triumphant atmosphere

[2] lord of the rings style a fearsome werewolf in a garden of statues, 
    aurora borealis, mysterious mood, 8k resolution
```

## 🔄 Determinism Guarantee

The same `(seed, prompt_index, profile)` tuple will **always** produce the same prompt:

```python
# These will always be identical
prompt_a = generate(seed=42, idx=1000, profile="default.json")  # Run 1
prompt_b = generate(seed=42, idx=1000, profile="default.json")  # Run 2
prompt_c = generate(seed=42, idx=1000, profile="default.json")  # Different machine

assert prompt_a == prompt_b == prompt_c  # Always True
```

This enables:
- **Reproducible workflows**: Save seed+index+profile instead of prompt text
- **Collaboration**: Share coordinates, not strings
- **Version control**: Track prompt changes via seed/index history

## 🛠️ Technical Details

### Dependencies

- `xxhash` - Fast, deterministic hashing (xxhash32)
- Python 3.8+

### Why xxhash32?

| Property | xxhash32 | Python `random` | `hash()` |
|----------|----------|-----------------|----------|
| Deterministic | ✓ | ✓ (with seed) | ✗ (randomized per session) |
| Cross-platform | ✓ | Edge cases | ✗ |
| O(1) direct access | ✓ | ✗ (iterates) | ✓ |
| Designed for this | ✓ | ✗ | ✗ |

### Performance

- **Generation time**: <1ms per prompt
- **Memory**: ~50KB (vocabulary pools in code/JSON)
- **No I/O**: Pure computation (V1) or single JSON read (V2, cached)

## 🎨 Workflow Tips

### Exploring Prompt Space

- **Fixed seed, varying index**: Explore one "universe" of prompts
- **Varying seed, fixed index**: See how the same "position" differs across universes
- **Random seed + random index**: Maximum variety
- **Different profiles**: Same seed+index, different vocabulary = different genre

### Finding Good Prompts

1. Start with seed=0, index=0
2. Increment index to browse prompts
3. When you find a style you like, note the seed
4. Explore nearby indices for variations
5. Try different profiles for genre variations

### Batch Generation

Connect to a primitive that increments `prompt_index` to generate batches:
```
prompt_index = batch_number * batch_size + item_index
```

## 📁 Repository Structure

```
ComfyUI-DJZ-ZeroPrompt/
├── __init__.py              # ComfyUI node registration
├── DJZ_ZeroPrompt_V1.py     # V1 node (built-in vocabulary)
├── DJZ_ZeroPrompt_V2.py     # V2 node (JSON profiles)
├── profiles/                # Vocabulary profiles
│   ├── default.json         # Full vocabulary (188T combinations)
│   ├── cyberpunk.json       # Cyberpunk/sci-fi focused (31B)
│   └── fantasy.json         # High fantasy focused (55B)
├── skills/                  # Claude Code skills
│   └── zeroprompt-profile-builder/
│       └── SKILL.md         # Prompt-to-profile conversion skill
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── LICENSE                  # MIT License
```

## 🧠 Claude Code Skill

The `/skills/zeroprompt-profile-builder/` folder contains a Claude Code skill for converting your existing prompt text files into ZeroPrompt profiles.

### Installation

Copy the skill to your Claude Code skills directory:
```bash
cp -r skills/zeroprompt-profile-builder ~/.claude/skills/
```

### Usage

1. Upload your `.txt` prompt file (one prompt per line)
2. Ask Claude:
   - "Convert this prompt list into a ZeroPrompt profile"
   - "Create a JSON profile from these prompts"
   - "Reverse engineer this into vocabulary pools"

The skill will analyze your prompts, extract vocabulary into semantic pools, synthesize templates, and generate a ready-to-use JSON profile.

## 🤝 Contributing

Contributions welcome! Areas of interest:
- Additional vocabulary entries
- New profile themes (horror, romance, nature, etc.)
- Template structure improvements
- Performance optimizations
- Documentation improvements

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 📚 Citation

### Academic Citation

If you use this codebase in your research or project, please cite:

```bibtex
@software{djz_zeroprompt,
  title = {ComfyUI-DJZ-ZeroPrompt: Procedural Semantic Prompt Generation using Position-is-Seed Methodology},
  author = {Drift Johnson},
  year = {2025},
  url = {https://github.com/MushroomFleet/ComfyUI-DJZ-ZeroPrompt},
  version = {1.0.0}
}
```

### Donate

[![Ko-Fi](https://cdn.ko-fi.com/cdn/kofi3.png?v=3)](https://ko-fi.com/driftjohnson)
