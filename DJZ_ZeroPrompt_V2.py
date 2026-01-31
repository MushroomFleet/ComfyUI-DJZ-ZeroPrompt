"""
DJZ-ZeroPrompt-V2 - Procedural Semantic Prompt Generation with JSON Profiles
ComfyUI Custom Node using ZeroBytes Position-is-Seed Methodology

Generates infinite deterministic prompts using O(1) coordinate hashing.
Same (seed, prompt_index, profile) → same prompt, always, everywhere.

V2 Features:
- JSON profile support for customizable vocabulary pools
- Auto-discovery of custom profiles
- Profile-specific prompt statistics
- Backward compatible with V1 generation algorithm
"""

import json
import os
import struct
from pathlib import Path

try:
    import xxhash
except ImportError:
    raise ImportError(
        "DJZ-ZeroPrompt requires xxhash. Install with: pip install xxhash"
    )


# =============================================================================
# PROFILE MANAGEMENT
# =============================================================================

def get_profiles_dir() -> Path:
    """Get the profiles directory path."""
    return Path(__file__).parent / "profiles"


def discover_profiles() -> list[str]:
    """
    Discover all available JSON profiles.
    Returns list of profile filenames (without path).
    """
    profiles_dir = get_profiles_dir()
    
    if not profiles_dir.exists():
        profiles_dir.mkdir(parents=True, exist_ok=True)
        return ["default.json"]
    
    profiles = sorted([
        f.name for f in profiles_dir.glob("*.json")
        if f.is_file()
    ])
    
    # Ensure default is first if it exists
    if "default.json" in profiles:
        profiles.remove("default.json")
        profiles.insert(0, "default.json")
    
    return profiles if profiles else ["default.json"]


def load_profile(profile_name: str) -> dict:
    """
    Load a profile from JSON file.
    Returns profile dict with 'templates' and 'pools'.
    """
    profiles_dir = get_profiles_dir()
    profile_path = profiles_dir / profile_name
    
    if not profile_path.exists():
        raise FileNotFoundError(f"Profile not found: {profile_name}")
    
    with open(profile_path, 'r', encoding='utf-8') as f:
        profile = json.load(f)
    
    # Validate required fields
    if 'templates' not in profile:
        raise ValueError(f"Profile {profile_name} missing 'templates' field")
    if 'pools' not in profile:
        raise ValueError(f"Profile {profile_name} missing 'pools' field")
    
    return profile


def calculate_combinations(profile: dict) -> int:
    """Calculate total unique prompt combinations for a profile."""
    total = len(profile.get('templates', []))
    for pool in profile.get('pools', {}).values():
        total *= len(pool)
    return total


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

def generate_prompt(seed: int, prompt_idx: int, profile: dict) -> str:
    """
    O(1) prompt generation from seed, index, and profile.
    
    Args:
        seed: World seed for consistent generation
        prompt_idx: Position in infinite prompt space
        profile: Loaded profile dict with 'templates' and 'pools'
    
    Returns:
        Complete formatted prompt as a single line paragraph
    """
    templates = profile['templates']
    pools = profile['pools']
    
    # Select template using coordinate 0
    template_hash = prompt_hash(seed, prompt_idx, 0)
    template = templates[hash_to_index(template_hash, len(templates))]
    
    # Generate each component with unique coordinate
    components = {}
    for i, (key, pool) in enumerate(pools.items()):
        component_hash = prompt_hash(seed, prompt_idx, i + 1)
        components[key] = pool[hash_to_index(component_hash, len(pool))]
    
    # Format template with available components
    # Use safe formatting to handle missing keys gracefully
    try:
        return template.format(**components)
    except KeyError as e:
        # If template references a key not in pools, return partial
        for key in pools.keys():
            template = template.replace(f"{{{key}}}", components.get(key, f"[{key}]"))
        return template


# =============================================================================
# COMFYUI NODE CLASS
# =============================================================================

class DJZZeroPromptV2:
    """
    DJZ Zero Prompt V2 - Procedural Semantic Prompt Generator with Profiles
    
    Generates infinite deterministic prompts using position-is-seed methodology.
    Same (seed, prompt_index, profile) always produces the same prompt.
    
    V2 adds JSON profile support for customizable vocabulary pools.
    """
    
    # Class-level cache for profiles
    _profile_cache: dict = {}
    _last_profile_scan: float = 0
    
    @classmethod
    def INPUT_TYPES(cls):
        # Discover available profiles
        profiles = discover_profiles()
        
        return {
            "required": {
                "profile": (profiles, {
                    "default": profiles[0] if profiles else "default.json",
                    "tooltip": "Select vocabulary profile (JSON files in /profiles folder)"
                }),
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
    DESCRIPTION = "Generates deterministic prompts from seed + index + profile. Same inputs = same output, always."
    
    def generate(self, profile: str, seed: int, prompt_index: int,
                 prefix: str = "", suffix: str = "") -> tuple:
        """
        Generate a single prompt from seed, index, and selected profile.
        
        Returns:
            Tuple containing the generated prompt string
        """
        # Load profile (with caching)
        if profile not in self._profile_cache:
            try:
                self._profile_cache[profile] = load_profile(profile)
            except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
                # Return error message as prompt
                return (f"[Error loading profile '{profile}': {str(e)}]",)
        
        profile_data = self._profile_cache[profile]
        
        # Generate prompt
        prompt = generate_prompt(seed, prompt_index, profile_data)
        
        # Apply prefix/suffix if provided
        if prefix or suffix:
            prompt = f"{prefix}{prompt}{suffix}"
        
        return (prompt,)
    
    @classmethod
    def IS_CHANGED(cls, profile: str, seed: int, prompt_index: int,
                   prefix: str = "", suffix: str = ""):
        """Ensure node updates when inputs change."""
        # Include profile name hash for cache invalidation
        profile_hash = xxhash.xxh32(profile.encode()).intdigest()
        return prompt_hash(seed ^ profile_hash, prompt_index, 0)


# =============================================================================
# PROFILE INFO NODE (Optional utility node)
# =============================================================================

class DJZZeroPromptProfileInfo:
    """
    Utility node to display profile statistics.
    Shows pool sizes and total combinations for selected profile.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        profiles = discover_profiles()
        
        return {
            "required": {
                "profile": (profiles, {
                    "default": profiles[0] if profiles else "default.json",
                }),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("info",)
    FUNCTION = "get_info"
    CATEGORY = "DJZ-Nodes"
    DESCRIPTION = "Display statistics about a ZeroPrompt profile"
    
    def get_info(self, profile: str) -> tuple:
        """Get profile information as formatted string."""
        try:
            profile_data = load_profile(profile)
        except Exception as e:
            return (f"Error loading profile: {e}",)
        
        lines = [
            f"Profile: {profile_data.get('name', profile)}",
            f"Description: {profile_data.get('description', 'N/A')}",
            f"Version: {profile_data.get('version', 'N/A')}",
            "",
            "Pool Sizes:",
        ]
        
        for pool_name, pool_items in profile_data.get('pools', {}).items():
            lines.append(f"  {pool_name}: {len(pool_items)} entries")
        
        lines.append(f"  templates: {len(profile_data.get('templates', []))} variations")
        lines.append("")
        
        total = calculate_combinations(profile_data)
        lines.append(f"Total unique prompts: {total:,}")
        lines.append(f"Scientific notation: {total:.2e}")
        
        return ("\n".join(lines),)
    
    @classmethod
    def IS_CHANGED(cls, profile: str):
        """Check if profile file has changed."""
        profile_path = get_profiles_dir() / profile
        if profile_path.exists():
            return profile_path.stat().st_mtime
        return 0


# =============================================================================
# COMFYUI REGISTRATION
# =============================================================================

NODE_CLASS_MAPPINGS = {
    "DJZ-ZeroPrompt-V2": DJZZeroPromptV2,
    "DJZ-ZeroPrompt-ProfileInfo": DJZZeroPromptProfileInfo,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DJZ-ZeroPrompt-V2": "DJZ Zero Prompt V2",
    "DJZ-ZeroPrompt-ProfileInfo": "DJZ Zero Prompt Profile Info",
}


# =============================================================================
# STANDALONE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("DJZ-ZeroPrompt-V2 - Procedural Prompt Generation with Profiles")
    print("=" * 70)
    
    # Discover profiles
    print("\n[Profile Discovery]")
    print("-" * 70)
    profiles = discover_profiles()
    print(f"Found {len(profiles)} profile(s): {', '.join(profiles)}")
    
    # Test each profile
    for profile_name in profiles:
        print(f"\n[Testing Profile: {profile_name}]")
        print("-" * 70)
        
        try:
            profile_data = load_profile(profile_name)
            
            # Show info
            print(f"Name: {profile_data.get('name', 'N/A')}")
            print(f"Description: {profile_data.get('description', 'N/A')}")
            
            # Pool stats
            print("\nPool sizes:")
            for pool_name, pool_items in profile_data.get('pools', {}).items():
                print(f"  {pool_name}: {len(pool_items)}")
            print(f"  templates: {len(profile_data.get('templates', []))}")
            
            # Calculate combinations
            total = calculate_combinations(profile_data)
            print(f"\nTotal combinations: {total:,} ({total:.2e})")
            
            # Generate sample prompts
            print(f"\nSample prompts (seed=42, indices 0-4):")
            for idx in range(5):
                prompt = generate_prompt(seed=42, prompt_idx=idx, profile=profile_data)
                print(f"  [{idx}] {prompt}")
            
            # Verify determinism
            print(f"\nDeterminism check:")
            p1 = generate_prompt(seed=42, prompt_idx=1000, profile=profile_data)
            p2 = generate_prompt(seed=42, prompt_idx=1000, profile=profile_data)
            print(f"  seed=42, idx=1000: {'✓ MATCH' if p1 == p2 else '✗ MISMATCH'}")
            
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "=" * 70)
    print("Testing complete!")
