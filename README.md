# ComfyUI-DJZ-ZeroPrompt

**Zero files. Zero storage. Infinite prompts.**

A ComfyUI custom node that generates deterministic prompts using position-is-seed procedural generation. Instead of reading from user-maintained text files, this node computes prompts directly from mathematical coordinates—the same seed and index will always produce the same prompt, everywhere, every time.

![ZeroPrompt Banner](https://img.shields.io/badge/Prompts-188%20Trillion+-blue?style=for-the-badge)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

## 🚀 Features

- **Infinite Prompts**: 188+ trillion unique prompt combinations from ~400 vocabulary entries
- **Perfect Determinism**: `seed=42, index=1000` produces identical output across all machines
- **O(1) Generation**: Direct hash computation—no file I/O, no iteration
- **Zero Maintenance**: No text files to curate, organize, or update
- **Reproducible Results**: Share seed+index coordinates to recreate exact prompts

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

## 🎯 Usage

### Basic Usage

1. Add the **DJZ Zero Prompt V1** node to your workflow
2. Connect the `prompt` output to your sampler or text input
3. Adjust `seed` and `prompt_index` to explore different prompts

### Inputs

| Input | Type | Description |
|-------|------|-------------|
| `seed` | INT | World seed (0 to 4,294,967,295). Different seeds = different prompt universes |
| `prompt_index` | INT | Position in prompt space (0 to 4,294,967,295). Each index = unique prompt |
| `prefix` | STRING | Optional text prepended to the generated prompt |
| `suffix` | STRING | Optional text appended to the generated prompt |

### Output

| Output | Type | Description |
|--------|------|-------------|
| `prompt` | STRING | Generated prompt as a single line paragraph |

## 💡 How It Works

### The ZeroBytes Methodology

Traditional prompt systems store prompts in files and select randomly. This approach has limitations:
- Finite prompts (limited by file size)
- Maintenance burden (curating text files)
- Non-deterministic selection (different results on different runs)

**ZeroPrompt** uses **position-is-seed** procedural generation:

```
(seed, prompt_index) → xxhash32 → deterministic component selection → formatted prompt
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

### Vocabulary Pools

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

```
seed=42, index=0:
a dwarven smith, the astral plane, hyperrealistic, blue hour lighting, 
intense atmosphere, trending on artstation

seed=42, index=1:
a wolf in inside a computer mainframe, timeless vector art, sunset backlight, 
point of view shot, realistic textures

seed=42, index=2:
steampunk a nymph, a vast desert, holographic light, unsettling mood, 
realistic textures

seed=42, index=1000:
ominous scene of a golem floating above a dystopian wasteland, 
studio ghibli style, bioluminescent glow, intricate details
```

## 🔄 Determinism Guarantee

The same `(seed, prompt_index)` pair will **always** produce the same prompt:

```python
# These will always be identical
prompt_a = generate_prompt(seed=42, prompt_idx=1000)  # Run 1
prompt_b = generate_prompt(seed=42, prompt_idx=1000)  # Run 2
prompt_c = generate_prompt(seed=42, prompt_idx=1000)  # Different machine

assert prompt_a == prompt_b == prompt_c  # Always True
```

This enables:
- **Reproducible workflows**: Save seed+index instead of prompt text
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
- **Memory**: ~50KB (vocabulary pools in code)
- **No I/O**: Pure computation

## 🎨 Workflow Tips

### Exploring Prompt Space

- **Fixed seed, varying index**: Explore one "universe" of prompts
- **Varying seed, fixed index**: See how the same "position" differs across universes
- **Random seed + random index**: Maximum variety

### Finding Good Prompts

1. Start with seed=0, index=0
2. Increment index to browse prompts
3. When you find a style you like, note the seed
4. Explore nearby indices for variations

### Batch Generation

Connect to a primitive that increments `prompt_index` to generate batches:
```
prompt_index = batch_number * batch_size + item_index
```

## 📁 Repository Structure

```
ComfyUI-DJZ-ZeroPrompt/
├── __init__.py           # ComfyUI node registration
├── DJZ-ZeroPrompt-V1.py  # Main node implementation
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── LICENSE              # MIT License
```

## 🤝 Contributing

Contributions welcome! Areas of interest:
- Additional vocabulary entries
- New template structures
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
