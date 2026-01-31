# ZenkaiPrompt V5: Procedural Semantic Generation Assessment

## Executive Summary

The current ZenkaiPromptV4 system reads prompts from user-maintained `.txt` files, using `random.seed(seed)` and `random.sample()` for selection. This approach violates several ZeroBytes laws:

| Law | Current Violation |
|-----|-------------------|
| O(1) Access | `random.sample()` internally iterates |
| Determinism | `random` module has platform-specific edge cases |
| Hierarchy | Flat selection, no semantic structure |
| Parallelism | Sequential state mutation via `random.seed()` |

**The opportunity:** Replace finite file-based prompts with infinite procedurally-generated semantic compositions using xxhash32-based coordinate hashing.

---

## Part 1: The Semantic Coordinate Space

### Core Insight

A prompt is not a string—it's a **position in semantic space**. Just as terrain at coordinates (x, y) can be computed from those coordinates alone, a prompt at "coordinates" (subject_idx, style_idx, mood_idx, detail_idx) can be computed deterministically.

```
Prompt Space Hierarchy:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
seed (world seed)
  └─ subject_domain (hash(seed, 0))
       └─ subject (hash(domain_seed, subject_idx))
            └─ style (hash(subject_seed, style_idx))
                 └─ modifiers (hash(style_seed, mod_idx))
                      └─ details (hash(mod_seed, detail_idx))
```

### The Position-Hash-to-Prompt Pattern

```python
import struct
import xxhash

def prompt_hash(seed: int, *coords: int) -> int:
    """Pure O(1) hash from seed + arbitrary coordinate tuple."""
    h = xxhash.xxh32(seed=seed)
    h.update(struct.pack('<' + 'i' * len(coords), *coords))
    return h.intdigest()

def hash_to_index(h: int, pool_size: int) -> int:
    """Map hash to valid index in any pool."""
    return h % pool_size
```

---

## Part 2: Vocabulary Pools as Constants

Instead of reading from files, embed **vocabulary pools** as Python constants. These are not "stored prompts" but **atomic semantic units** that combine procedurally.

### Proposed Pool Architecture

```python
POOLS = {
    # SUBJECTS: ~200 entries → 40,000 pair combinations
    "subjects": [
        "a woman", "a man", "a child", "an elderly person", "a cyborg",
        "a knight", "a samurai", "a witch", "a detective", "an astronaut",
        "a dragon", "a phoenix", "a wolf", "a mechanical spider", "a ghost",
        "a floating city", "a ruined temple", "a neon street", "a forest shrine",
        # ... expandable
    ],
    
    # ACTIONS: ~100 entries
    "actions": [
        "standing in", "walking through", "fighting", "meditating near",
        "discovering", "fleeing from", "ascending toward", "falling into",
        "transforming into", "summoning", "observing", "dancing with",
        # ...
    ],
    
    # ENVIRONMENTS: ~150 entries
    "environments": [
        "a misty forest", "a cyberpunk alley", "an ancient library",
        "a volcanic wasteland", "a crystal cave", "a floating island",
        "a post-apocalyptic city", "a bioluminescent ocean floor",
        # ...
    ],
    
    # STYLES: ~80 entries
    "styles": [
        "photorealistic", "anime style", "oil painting", "watercolor",
        "concept art", "pixel art", "art nouveau", "brutalist",
        "vaporwave aesthetic", "dark fantasy", "studio ghibli style",
        # ...
    ],
    
    # LIGHTING: ~50 entries
    "lighting": [
        "golden hour lighting", "dramatic rim lighting", "neon glow",
        "moonlit", "volumetric fog", "harsh shadows", "soft diffused light",
        # ...
    ],
    
    # CAMERA: ~40 entries
    "camera": [
        "close-up portrait", "wide establishing shot", "dutch angle",
        "bird's eye view", "worm's eye view", "over the shoulder",
        # ...
    ],
    
    # DETAILS: ~100 entries
    "details": [
        "intricate details", "highly detailed", "4k", "8k",
        "masterpiece", "award winning", "trending on artstation",
        # ...
    ],
    
    # MOOD: ~60 entries
    "mood": [
        "serene", "ominous", "chaotic", "melancholic", "euphoric",
        "mysterious", "nostalgic", "surreal", "tense", "whimsical",
        # ...
    ]
}
```

### Combinatorial Explosion

With modest pool sizes:
- 200 subjects × 100 actions × 150 environments × 80 styles × 50 lighting × 40 camera × 100 details × 60 mood
- = **28,800,000,000,000,000** unique valid prompts (28.8 quadrillion)

**Zero bytes store infinity.**

---

## Part 3: The Generation Algorithm

### Template-Based Composition

```python
TEMPLATES = [
    "{subject} {action} {environment}, {style}, {lighting}, {camera}, {details}, {mood} atmosphere",
    "{camera} of {subject} in {environment}, {mood} {style}, {lighting}, {details}",
    "{style} {subject}, {environment} background, {lighting}, {mood}, {details}",
    "{subject} {action} {environment}, {mood} scene, {style}, {lighting}",
    # ... more structural variations
]

def generate_prompt(seed: int, prompt_idx: int) -> str:
    """
    O(1) prompt generation. No iteration, no files, pure hash.
    
    prompt_idx acts as the "position" in infinite prompt space.
    Same (seed, prompt_idx) → same prompt, always, everywhere.
    """
    # Select template
    template_hash = prompt_hash(seed, prompt_idx, 0)
    template = TEMPLATES[hash_to_index(template_hash, len(TEMPLATES))]
    
    # Generate each component with unique coordinate
    components = {}
    for i, (key, pool) in enumerate(POOLS.items()):
        component_hash = prompt_hash(seed, prompt_idx, i + 1)
        components[key] = pool[hash_to_index(component_hash, len(pool))]
    
    # Handle plurals/grammar if needed
    components = apply_grammar_rules(components)
    
    return template.format(**components)
```

### Blacklist Implementation (O(1) Skip)

```python
def generate_prompt_filtered(seed: int, prompt_idx: int, blacklist: set) -> str:
    """
    Generate prompt, skip if blacklisted, advance index deterministically.
    Still O(1) per attempt—no iteration through all prompts.
    """
    max_attempts = 100  # Prevent infinite loop on over-restrictive blacklist
    
    for attempt in range(max_attempts):
        # Use attempt as additional coordinate dimension
        candidate = generate_prompt(seed, prompt_idx + attempt * 1000000)
        
        if not any(term.lower() in candidate.lower() for term in blacklist):
            return candidate
    
    return "[Blacklist too restrictive—no valid prompts found]"
```

---

## Part 4: Coherent Prompt Neighborhoods

### The Problem with Pure Random

Pure hash gives maximum variety but zero **coherence**. Adjacent seeds produce completely unrelated prompts. Sometimes you want:

- Seeds 1000-1010 to all be "dark fantasy" themed
- A "region" of cyberpunk prompts
- Gradual style transitions

### Solution: Coherent Noise for Style Regions

```python
def coherent_style_bias(seed: int, prompt_idx: int) -> dict:
    """
    Use coherent noise to create 'style regions' in prompt space.
    Nearby prompt_idx values share stylistic tendencies.
    """
    # Treat prompt_idx as a 1D coordinate, sample coherent noise
    x = prompt_idx * 0.01  # Scale factor controls region size
    
    # Style tendency: -1 to 1 range
    fantasy_bias = coherent_value_1d(x, seed, octaves=3)
    tech_bias = coherent_value_1d(x, seed + 1000, octaves=3)
    mood_bias = coherent_value_1d(x, seed + 2000, octaves=3)
    
    return {
        "fantasy_weight": (fantasy_bias + 1) / 2,  # 0-1
        "tech_weight": (tech_bias + 1) / 2,
        "mood_weight": (mood_bias + 1) / 2,
    }

def coherent_value_1d(x: float, seed: int, octaves: int = 4) -> float:
    """1D coherent noise for prompt space."""
    value, amp, freq, max_amp = 0.0, 1.0, 1.0, 0.0
    for i in range(octaves):
        x0 = int(x * freq)
        sx = ((x * freq) % 1)
        sx = sx * sx * (3 - 2 * sx)  # Smoothstep
        
        n0 = hash_to_float(prompt_hash(seed + i, x0, 0)) * 2 - 1
        n1 = hash_to_float(prompt_hash(seed + i, x0 + 1, 0)) * 2 - 1
        
        value += amp * (n0 * (1 - sx) + n1 * sx)
        max_amp += amp
        amp *= 0.5
        freq *= 2.0
    
    return value / max_amp

def hash_to_float(h: int) -> float:
    return (h & 0xFFFFFFFF) / 0x100000000
```

### Weighted Pool Selection

```python
def weighted_select(pool: list, hash_val: int, weights: dict, pool_type: str) -> str:
    """
    Select from pool with bias based on coherent weights.
    """
    # Partition pools by category (would be pre-defined)
    if pool_type == "style":
        fantasy_styles = ["dark fantasy", "high fantasy", "art nouveau", ...]
        tech_styles = ["cyberpunk", "sci-fi", "brutalist", "vaporwave", ...]
        
        # Blend based on weight
        if weights.get("fantasy_weight", 0.5) > 0.7:
            pool = fantasy_styles
        elif weights.get("tech_weight", 0.5) > 0.7:
            pool = tech_styles
        # else: use full pool
    
    return pool[hash_to_index(hash_val, len(pool))]
```

---

## Part 5: Multi-Prompt Batch Generation

Current V4 behavior: select `num_prompts` from file, join with comma.

### ZeroBytes Approach

```python
def generate_batch(seed: int, start_idx: int, num_prompts: int, 
                   prefix: str = "", suffix: str = "", 
                   blacklist: set = None) -> str:
    """
    Generate batch of prompts. Each prompt is O(1) to compute.
    Total complexity: O(num_prompts), not O(file_size).
    """
    prompts = []
    for i in range(num_prompts):
        prompt_idx = start_idx + i
        
        if blacklist:
            prompt = generate_prompt_filtered(seed, prompt_idx, blacklist)
        else:
            prompt = generate_prompt(seed, prompt_idx)
        
        prompts.append(f"{prefix}{prompt}{suffix}")
    
    return ", ".join(prompts)
```

---

## Part 6: Maintaining Backward Compatibility

### File-Based Mode as Optional Input

Users who have curated prompt files shouldn't lose that capability:

```python
class ZenkaiPromptV5:
    @classmethod
    def INPUT_TYPES(cls):
        # Detect available text files (backward compat)
        prompts_folder = os.path.join(os.path.dirname(__file__), 'prompts')
        text_files = ["[PROCEDURAL]"]  # New default
        if os.path.exists(prompts_folder):
            text_files += [f for f in os.listdir(prompts_folder) if f.endswith('.txt')]
        
        return {
            "required": {
                "mode": (text_files,),  # "[PROCEDURAL]" or filename
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFF}),
                "prompt_index": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFF}),
                "num_prompts": ("INT", {"default": 1, "min": 1, "max": 100}),
            },
            "optional": {
                "prefix": ("STRING", {"default": ""}),
                "suffix": ("STRING", {"default": ""}),
                "blacklist": ("STRING", {"default": "", "multiline": False}),
                "style_coherence": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 1.0}),
            }
        }
```

---

## Part 7: Advanced Features Enabled by Procedural Approach

### 7.1 Prompt Space Navigation

```python
# "Nearby" prompts in semantic space
def get_variations(seed: int, base_idx: int, variation_radius: int = 10):
    """Get prompts similar to base_idx by exploring local neighborhood."""
    return [generate_prompt(seed, base_idx + offset) 
            for offset in range(-variation_radius, variation_radius + 1)]
```

### 7.2 Deterministic A/B Testing

```python
# Same prompt_idx with different seeds = same structure, different choices
prompt_a = generate_prompt(seed=42, prompt_idx=1000)
prompt_b = generate_prompt(seed=43, prompt_idx=1000)
# Both follow same template, both have "subject + action + environment" structure
# But different specific selections
```

### 7.3 Hierarchical Override

```python
def generate_with_lock(seed: int, prompt_idx: int, locked: dict) -> str:
    """
    Generate prompt but lock specific components.
    locked = {"subject": "a cyberpunk samurai", "style": "neon noir"}
    """
    components = {}
    for i, (key, pool) in enumerate(POOLS.items()):
        if key in locked:
            components[key] = locked[key]
        else:
            h = prompt_hash(seed, prompt_idx, i + 1)
            components[key] = pool[hash_to_index(h, len(pool))]
    
    template_hash = prompt_hash(seed, prompt_idx, 0)
    template = TEMPLATES[hash_to_index(template_hash, len(TEMPLATES))]
    return template.format(**components)
```

### 7.4 Prompt Archaeology

```python
def find_prompt_index(target_substring: str, seed: int, search_range: int = 100000) -> list:
    """
    Find which prompt_idx values produce prompts containing target.
    Useful for: "I liked that prompt with 'crystal cave', what was its index?"
    """
    matches = []
    for idx in range(search_range):
        prompt = generate_prompt(seed, idx)
        if target_substring.lower() in prompt.lower():
            matches.append((idx, prompt))
    return matches
```

---

## Part 8: Implementation Roadmap

### Phase 1: Core Engine
1. Implement `prompt_hash()` with xxhash32
2. Define initial vocabulary pools (~500 total entries)
3. Create 5-10 template structures
4. Basic `generate_prompt(seed, idx)` function

### Phase 2: ComfyUI Integration
1. Create `ZenkaiPromptV5` node class
2. Add backward-compatible file mode
3. Implement blacklist with hash-skip
4. Add prefix/suffix handling

### Phase 3: Coherence & Navigation  
1. Implement 1D coherent noise for style regions
2. Add style_coherence slider (0 = pure random, 1 = full regional coherence)
3. Build prompt neighborhood exploration

### Phase 4: Advanced Features
1. Component locking UI
2. Prompt archaeology search
3. Batch generation with spread control
4. Export/import of "discovered" prompt coordinates

---

## Part 9: Vocabulary Pool Design Principles

### Semantic Orthogonality

Pools should represent **independent dimensions** of prompt space:

| Pool | Semantic Axis | Independent From |
|------|---------------|------------------|
| subjects | WHO/WHAT | where, how, style |
| actions | DOING WHAT | who, where |
| environments | WHERE | who, what doing |
| styles | RENDER HOW | all content |
| lighting | LIGHT HOW | style (somewhat coupled) |
| camera | FRAME HOW | all |
| details | QUALITY | all |
| mood | FEEL HOW | weak coupling to all |

### Pool Expansion Strategy

Start minimal, expand based on:
1. User requests ("I wish it generated more X")
2. Identified gaps ("never generates underwater scenes")
3. Trend integration ("new popular style: X")

Each pool addition is **multiplicative**:
- Adding 10 subjects to 200 = 5% more subjects → 5% more total prompts
- Adding new pool of 30 items = 30x more prompts

---

## Part 10: Comparison Summary

| Aspect | V4 (File-Based) | V5 (Procedural) |
|--------|-----------------|-----------------|
| Storage | User maintains .txt files | Zero files needed |
| Prompt count | Limited by file size | Infinite (quadrillions) |
| Determinism | `random` module (weak) | xxhash32 (strong) |
| Access complexity | O(n) file read + sample | O(1) pure hash |
| Parallelizable | No (shared random state) | Yes (pure function) |
| Extendable | Edit files | Edit pool constants |
| Coherence | None | Configurable via noise |
| Reproducibility | Seed + file version | Seed + code version |

---

## Conclusion

The ZeroBytes methodology transforms ZenkaiPrompt from a **file retrieval system** into a **semantic universe generator**. The coordinate `(seed, prompt_idx)` becomes an address in infinite prompt space, computable in O(1) time with perfect determinism.

**The prompt doesn't come from a file. The prompt was always there, implicit in the mathematics of the hash. You're not selecting—you're discovering.**

---

## Appendix: Minimal Working Implementation

```python
import struct
import xxhash

# Minimal pools for testing
POOLS = {
    "subject": ["a warrior", "a witch", "a robot", "a dragon", "a child"],
    "action": ["standing in", "exploring", "fleeing from", "guarding"],
    "environment": ["a dark forest", "a neon city", "ancient ruins", "a crystal cave"],
    "style": ["photorealistic", "anime style", "oil painting", "concept art"],
}

TEMPLATES = [
    "{subject} {action} {environment}, {style}",
    "{style} depiction of {subject} in {environment}",
]

def prompt_hash(seed: int, *coords: int) -> int:
    h = xxhash.xxh32(seed=seed)
    h.update(struct.pack('<' + 'i' * len(coords), *coords))
    return h.intdigest()

def generate_prompt(seed: int, prompt_idx: int) -> str:
    template = TEMPLATES[prompt_hash(seed, prompt_idx, 0) % len(TEMPLATES)]
    
    components = {
        key: pool[prompt_hash(seed, prompt_idx, i + 1) % len(pool)]
        for i, (key, pool) in enumerate(POOLS.items())
    }
    
    return template.format(**components)

# Test determinism
for idx in range(5):
    print(f"[{idx}] {generate_prompt(seed=42, prompt_idx=idx)}")
```

Output:
```
[0] a witch standing in a crystal cave, concept art
[1] anime style depiction of a robot in a neon city
[2] a dragon exploring ancient ruins, photorealistic
[3] a warrior guarding a dark forest, oil painting
[4] photorealistic depiction of a child in a crystal cave
```

Same seed + index = same prompt. Always. Everywhere. Zero bytes stored.
