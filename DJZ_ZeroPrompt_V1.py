"""
DJZ-ZeroPrompt-V1 - Procedural Semantic Prompt Generation
ComfyUI Custom Node using ZeroBytes Position-is-Seed Methodology

Generates infinite deterministic prompts using O(1) coordinate hashing.
Same (seed, prompt_index) → same prompt, always, everywhere.
Zero files. Zero storage. Infinite prompts.
"""

import struct

try:
    import xxhash
except ImportError:
    raise ImportError(
        "DJZ-ZeroPrompt requires xxhash. Install with: pip install xxhash"
    )


# =============================================================================
# VOCABULARY POOLS - Semantic Building Blocks
# =============================================================================

SUBJECTS = [
    # People
    "a woman", "a man", "a young woman", "a young man", "an elderly woman",
    "an elderly man", "a child", "a teenager", "a couple", "a group of people",
    # Fantasy Characters
    "a knight", "a wizard", "a witch", "a sorceress", "a necromancer",
    "a paladin", "a rogue", "an assassin", "a ranger", "a barbarian",
    "a druid", "a monk", "a bard", "a warlock", "an elven archer",
    "a dwarven smith", "an orc warrior", "a goblin", "a fairy", "a nymph",
    # Sci-Fi Characters
    "a cyborg", "an android", "a robot", "a mech pilot", "an astronaut",
    "a space marine", "an alien", "a hacker", "a scientist", "a bounty hunter",
    # Historical/Cultural
    "a samurai", "a ninja", "a viking", "a gladiator", "a pharaoh",
    "a geisha", "a shogun", "a roman soldier", "a medieval peasant", "a noble",
    # Modern
    "a detective", "a soldier", "a pilot", "a doctor", "an artist",
    "a musician", "a dancer", "an athlete", "a chef", "a photographer",
    # Creatures
    "a dragon", "a phoenix", "a griffin", "a unicorn", "a werewolf",
    "a vampire", "a demon", "an angel", "a ghost", "a spirit",
    "a wolf", "a lion", "a tiger", "an eagle", "a raven",
    "a serpent", "a whale", "a shark", "a butterfly", "a spider",
    # Constructs
    "a mechanical spider", "a clockwork automaton", "a golem", "a sentient statue",
    "a living shadow", "an elemental being", "a slime creature", "a treant",
]

ACTIONS = [
    # Static
    "standing in", "sitting in", "kneeling in", "floating above", "hovering over",
    "resting in", "meditating in", "posing in", "waiting in", "watching over",
    # Movement
    "walking through", "running through", "flying over", "swimming in", "climbing",
    "falling into", "descending into", "ascending toward", "emerging from", "diving into",
    # Combat
    "fighting in", "battling through", "defending", "attacking", "dueling in",
    "charging through", "retreating from", "ambushing in", "hunting in",
    # Discovery
    "exploring", "discovering", "searching through", "investigating",
    "uncovering secrets in", "finding treasure in", "mapping",
    # Interaction
    "summoning power in", "casting a spell in", "channeling energy in",
    "communing with nature in", "praying in", "performing a ritual in",
    "transforming in", "shapeshifting in", "awakening in",
    # Emotional
    "mourning in", "celebrating in", "contemplating in", "dreaming in",
    "remembering in", "lost in thought in",
]

ENVIRONMENTS = [
    # Natural
    "a dark forest", "an enchanted forest", "a misty forest", "a bamboo forest",
    "a snowy mountain", "a volcanic mountain", "a floating mountain",
    "a vast desert", "an oasis", "a canyon", "a waterfall", "a river",
    "a beach at sunset", "a stormy sea", "a coral reef", "an underwater cavern",
    # Urban Fantasy
    "a medieval castle", "a ruined fortress", "a gothic cathedral",
    "an ancient temple", "a hidden shrine", "a sacred grove",
    "a wizard's tower", "an alchemist's laboratory", "a royal throne room",
    "a dungeon", "catacombs", "a crypt", "a graveyard at midnight",
    # Sci-Fi
    "a cyberpunk city", "a neon-lit alley", "a futuristic metropolis",
    "a space station", "an alien planet", "a terraformed moon",
    "a dystopian wasteland", "a post-apocalyptic city", "a megastructure",
    "a virtual reality world", "inside a computer mainframe",
    # Mystical
    "a crystal cave", "a bioluminescent cavern", "a floating island",
    "the astral plane", "between dimensions", "the void",
    "a pocket dimension", "a mirror world", "a dream realm",
    # Atmospheric
    "cherry blossom gardens", "an autumn forest", "a field of flowers",
    "under the northern lights", "during a solar eclipse",
    "at the edge of the world", "at the crossroads of fate",
]

STYLES = [
    # Realistic
    "photorealistic", "hyperrealistic", "cinematic", "film still",
    "documentary photography", "portrait photography", "fashion photography",
    # Traditional Art
    "oil painting", "watercolor painting", "acrylic painting", "gouache",
    "charcoal drawing", "pencil sketch", "ink drawing", "fresco",
    # Art Movements
    "art nouveau", "art deco", "baroque", "renaissance", "romanticism",
    "impressionist", "expressionist", "surrealist", "cubist",
    "pre-raphaelite", "ukiyo-e", "chinese ink wash",
    # Digital/Modern
    "concept art", "digital painting", "matte painting", "3D render",
    "low poly 3D", "voxel art", "pixel art", "vector art",
    # Animation Styles
    "anime style", "manga style", "studio ghibli style", "disney style",
    "pixar style", "cartoon style", "comic book style", "graphic novel style",
    # Aesthetic
    "vaporwave aesthetic", "synthwave", "cyberpunk aesthetic", "solarpunk",
    "dark academia", "cottagecore", "steampunk", "dieselpunk", "biopunk",
    # Game-Adjacent
    "dark souls style", "elden ring style", "final fantasy style",
    "metal gear style", "borderlands style", "breath of the wild style",
]

LIGHTING = [
    # Natural Light
    "golden hour lighting", "blue hour lighting", "harsh midday sun",
    "soft overcast light", "dappled forest light", "sunset backlight",
    "sunrise light", "moonlight", "starlight",
    # Dramatic
    "dramatic rim lighting", "chiaroscuro lighting", "spotlight",
    "harsh shadows", "silhouette lighting", "contre-jour",
    # Artificial
    "neon lighting", "fluorescent lighting", "candlelight", "firelight",
    "bioluminescent glow", "magical glow", "holographic light",
    # Atmospheric
    "volumetric lighting", "god rays", "light shafts", "foggy atmosphere",
    "misty atmosphere", "dusty atmosphere", "rainy atmosphere",
    # Color Temperature
    "warm lighting", "cool lighting", "neutral lighting",
    "high contrast", "low key lighting", "high key lighting",
]

CAMERA = [
    # Distance
    "extreme close-up", "close-up portrait", "medium shot", "full body shot",
    "wide shot", "extreme wide shot", "establishing shot",
    # Angle
    "eye level", "low angle shot", "high angle shot", "bird's eye view",
    "worm's eye view", "dutch angle", "overhead shot",
    # Perspective
    "first person view", "over the shoulder", "point of view shot",
    "three-quarter view", "profile view", "frontal view", "rear view",
    # Technical
    "shallow depth of field", "deep focus", "bokeh background",
    "motion blur", "long exposure", "tilt-shift", "fisheye lens",
    "wide angle lens", "telephoto compression", "macro shot",
]

DETAILS = [
    # Quality
    "highly detailed", "intricate details", "fine details", "subtle details",
    "sharp focus", "crystal clear", "pristine quality",
    # Resolution
    "4k", "8k", "high resolution", "ultra HD",
    # Recognition
    "masterpiece", "award winning", "professional", "museum quality",
    "trending on artstation", "featured on behance", "gallery quality",
    # Technical
    "ray tracing", "global illumination", "subsurface scattering",
    "ambient occlusion", "realistic textures", "photogrammetry",
    # Artistic
    "expressive brushwork", "visible brushstrokes", "smooth gradients",
    "rich colors", "vibrant palette", "muted tones", "monochromatic",
]

MOOD = [
    # Positive
    "serene", "peaceful", "tranquil", "joyful", "euphoric",
    "whimsical", "playful", "romantic", "hopeful", "triumphant",
    # Negative
    "ominous", "foreboding", "melancholic", "sorrowful", "tragic",
    "terrifying", "horrific", "unsettling", "disturbing",
    # Neutral/Complex
    "mysterious", "enigmatic", "surreal", "dreamlike", "ethereal",
    "nostalgic", "bittersweet", "contemplative", "introspective",
    # Intensity
    "tense", "intense", "chaotic", "explosive", "dynamic",
    "calm", "still", "quiet", "subtle", "understated",
    # Atmosphere
    "epic", "grand", "intimate", "cozy", "lonely", "isolated",
    "crowded", "bustling", "abandoned", "timeless",
]

# Pool registry
POOLS = {
    "subject": SUBJECTS,
    "action": ACTIONS,
    "environment": ENVIRONMENTS,
    "style": STYLES,
    "lighting": LIGHTING,
    "camera": CAMERA,
    "details": DETAILS,
    "mood": MOOD,
}

# Template variations - each produces a single coherent prompt
TEMPLATES = [
    "{subject} {action} {environment}, {style}, {lighting}, {camera}, {details}, {mood} atmosphere",
    "{camera} of {subject} {action} {environment}, {style}, {lighting}, {details}, {mood}",
    "{style} {subject}, {environment}, {lighting}, {mood} mood, {details}",
    "{subject} in {environment}, {mood} {style}, {lighting}, {camera}, {details}",
    "{mood} scene of {subject} {action} {environment}, {style}, {lighting}, {details}",
    "{style} depicting {subject}, {environment} setting, {lighting}, {camera}",
    "{camera}, {subject} {action} {environment}, {style}, {mood}, {details}",
    "{subject}, {environment}, {style}, {lighting}, {mood} atmosphere, {details}",
]


# =============================================================================
# CORE HASH FUNCTIONS - O(1) Position-Based Generation
# =============================================================================

def prompt_hash(seed: int, *coords: int) -> int:
    """
    Pure O(1) hash from seed + arbitrary coordinate tuple.
    Uses xxhash32 for speed and cross-platform determinism.
    """
    h = xxhash.xxh32(seed=seed & 0xFFFFFFFF)
    h.update(struct.pack('<' + 'i' * len(coords), *coords))
    return h.intdigest()


def hash_to_index(h: int, pool_size: int) -> int:
    """Map hash to valid index in any pool."""
    return h % pool_size


# =============================================================================
# PROMPT GENERATION
# =============================================================================

def generate_prompt(seed: int, prompt_idx: int) -> str:
    """
    O(1) prompt generation from seed and index.
    
    Args:
        seed: World seed for consistent generation
        prompt_idx: Position in infinite prompt space
    
    Returns:
        Complete formatted prompt as a single line paragraph
    """
    # Select template using coordinate 0
    template_hash = prompt_hash(seed, prompt_idx, 0)
    template = TEMPLATES[hash_to_index(template_hash, len(TEMPLATES))]
    
    # Generate each component with unique coordinate
    components = {}
    for i, (key, pool) in enumerate(POOLS.items()):
        component_hash = prompt_hash(seed, prompt_idx, i + 1)
        components[key] = pool[hash_to_index(component_hash, len(pool))]
    
    return template.format(**components)


# =============================================================================
# COMFYUI NODE CLASS
# =============================================================================

class DJZZeroPromptV1:
    """
    DJZ Zero Prompt V1 - Procedural Semantic Prompt Generator
    
    Generates infinite deterministic prompts using position-is-seed methodology.
    Same (seed, prompt_index) always produces the same prompt.
    
    Zero files. Zero storage. Infinite prompts.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFF,
                    "tooltip": "World seed - different seeds explore different prompt universes"
                }),
                "prompt_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xFFFFFFFF,
                    "tooltip": "Position in infinite prompt space - each index is a unique prompt"
                }),
            },
            "optional": {
                "prefix": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Text to prepend to the generated prompt"
                }),
                "suffix": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "tooltip": "Text to append to the generated prompt"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    OUTPUT_TOOLTIPS = ("Generated prompt as a single line paragraph",)
    FUNCTION = "generate"
    CATEGORY = "DJZ-Nodes"
    DESCRIPTION = "Generates deterministic prompts from seed + index. Same inputs = same output, always."
    
    def generate(self, seed: int, prompt_index: int, 
                 prefix: str = "", suffix: str = "") -> tuple:
        """
        Generate a single prompt from seed and index.
        
        Returns:
            Tuple containing the generated prompt string
        """
        prompt = generate_prompt(seed, prompt_index)
        
        # Apply prefix/suffix if provided
        if prefix or suffix:
            prompt = f"{prefix}{prompt}{suffix}"
        
        return (prompt,)
    
    @classmethod
    def IS_CHANGED(cls, seed: int, prompt_index: int, prefix: str = "", suffix: str = ""):
        """Ensure node updates when inputs change."""
        return prompt_hash(seed, prompt_index, 0)


# =============================================================================
# COMFYUI REGISTRATION
# =============================================================================

NODE_CLASS_MAPPINGS = {
    "DJZ-ZeroPrompt-V1": DJZZeroPromptV1
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DJZ-ZeroPrompt-V1": "DJZ Zero Prompt V1"
}


# =============================================================================
# STANDALONE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("DJZ-ZeroPrompt-V1 - Procedural Semantic Prompt Generation")
    print("=" * 70)
    
    # Test basic generation
    print("\n[Test 1] Basic generation - seed=42, indices 0-9:")
    print("-" * 70)
    for idx in range(10):
        prompt = generate_prompt(seed=42, prompt_idx=idx)
        print(f"[{idx}] {prompt}")
        print()
    
    # Test determinism
    print("\n[Test 2] Determinism verification:")
    print("-" * 70)
    test_cases = [(42, 1000), (12345, 0), (0, 99999)]
    for seed, idx in test_cases:
        p1 = generate_prompt(seed=seed, prompt_idx=idx)
        p2 = generate_prompt(seed=seed, prompt_idx=idx)
        match = "✓ MATCH" if p1 == p2 else "✗ MISMATCH"
        print(f"seed={seed}, idx={idx}: {match}")
    
    # Pool statistics
    print("\n[Statistics]")
    print("-" * 70)
    total_combinations = 1
    for name, pool in POOLS.items():
        print(f"  {name}: {len(pool)} entries")
        total_combinations *= len(pool)
    total_combinations *= len(TEMPLATES)
    print(f"  templates: {len(TEMPLATES)} variations")
    print(f"\n  Total unique prompts: {total_combinations:,}")
    print(f"  Scientific notation: {total_combinations:.2e}")
