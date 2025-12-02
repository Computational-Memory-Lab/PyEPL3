"""
Pool system for PyEPL3

Provides collections for managing and organizing stimuli (images, sounds, text).
"""

import random
from pathlib import Path
from typing import List, Optional, Any, Callable

from .exceptions import PoolError


class Pool(list):
    """
    Ordered collection of stimuli with filtering and randomization.

    Inherits from list, so all list operations work.
    """

    def __init__(self, *items):
        """
        Create a pool.

        Args:
            *items: Items to include in pool
        """
        super().__init__(items)

    def shuffle(self):
        """Shuffle the pool in place."""
        random.shuffle(self)

    def sample(self, n: int) -> 'Pool':
        """
        Get a random sample of n items.

        Args:
            n: Number of items to sample

        Returns:
            New Pool with sampled items
        """
        if n > len(self):
            raise PoolError(f"Cannot sample {n} items from pool of size {len(self)}")

        sampled = random.sample(self, n)
        return Pool(*sampled)

    def randomChoice(self) -> Any:
        """
        Get a random item from the pool.

        Returns:
            Random item
        """
        if not self:
            raise PoolError("Cannot choose from empty pool")
        return random.choice(self)

    def findBy(self, attribute: str, value: Any) -> Optional[Any]:
        """
        Find first item with matching attribute.

        Args:
            attribute: Attribute name
            value: Value to match

        Returns:
            First matching item, or None
        """
        for item in self:
            if hasattr(item, attribute) and getattr(item, attribute) == value:
                return item
        return None

    def findAllBy(self, attribute: str, value: Any) -> 'Pool':
        """
        Find all items with matching attribute.

        Args:
            attribute: Attribute name
            value: Value to match

        Returns:
            Pool of matching items
        """
        matches = [item for item in self
                   if hasattr(item, attribute) and getattr(item, attribute) == value]
        return Pool(*matches)

    def filter(self, predicate: Callable[[Any], bool]) -> 'Pool':
        """
        Filter pool by predicate function.

        Args:
            predicate: Function that returns True for items to keep

        Returns:
            Pool of filtered items
        """
        filtered = [item for item in self if predicate(item)]
        return Pool(*filtered)

    def sortBy(self, *attributes):
        """
        Sort pool by one or more attributes.

        Args:
            *attributes: Attribute names to sort by
        """
        def get_sort_key(item):
            key = []
            for attr in attributes:
                if hasattr(item, attr):
                    key.append(getattr(item, attr))
                else:
                    key.append(None)
            return tuple(key)

        self.sort(key=get_sort_key)

    def __repr__(self):
        return f"Pool({len(self)} items)"


class WordObject:
    """Simple object that wraps a word string with a .name attribute."""

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"WordObject('{self.name}')"

    def __str__(self):
        return self.name


class TextPool(Pool):
    """
    Pool of text items, typically loaded from a file.
    Items are converted to WordObject instances with .name attribute.
    """

    def __init__(self, *items):
        """
        Create a text pool.

        Args:
            *items: Text items or filename to load from
        """
        if len(items) == 1 and isinstance(items[0], str):
            # Check if it's a filename
            path = Path(items[0])
            if path.exists() and path.is_file():
                items = self._loadFromFile(path)

        super().__init__(*items)
        self._convertToObjects()

    def _loadFromFile(self, filepath: Path) -> List[str]:
        """
        Load text items from file (one per line).

        Args:
            filepath: Path to text file

        Returns:
            List of text items
        """
        items = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line:  # Skip empty lines
                    items.append(line)
        return items

    def _convertToObjects(self):
        """Convert simple strings to WordObjects with .name attribute."""
        for i in range(len(self)):
            if isinstance(self[i], str):
                self[i] = WordObject(self[i])

    def isInPool(self, name: Optional[str] = None, **kwargs) -> int:
        """
        Find index of word in pool.

        Args:
            name: Word name to find
            **kwargs: Other attribute=value pairs to match

        Returns:
            Index of word in pool, or -1 if not found
        """
        if name is not None:
            # Search by name
            for i, item in enumerate(self):
                if hasattr(item, 'name') and item.name == name:
                    return i
            return -1

        # Search by other attributes
        for i, item in enumerate(self):
            match = True
            for key, value in kwargs.items():
                if not hasattr(item, key) or getattr(item, key) != value:
                    match = False
                    break
            if match:
                return i

        return -1


class ImagePool(Pool):
    """
    Pool of images, typically loaded from a directory.
    """

    def __init__(self, *items):
        """
        Create an image pool.

        Args:
            *items: Image objects or directory to load from
        """
        if len(items) == 1 and isinstance(items[0], (str, Path)):
            # Check if it's a directory
            path = Path(items[0])
            if path.exists() and path.is_dir():
                items = self._loadFromDir(path)

        super().__init__(*items)

    def _loadFromDir(self, dirpath: Path) -> List['Image']:
        """
        Load images from directory.

        Args:
            dirpath: Path to directory

        Returns:
            List of Image objects
        """
        from .display import Image

        # Supported image extensions
        extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tif', '.tiff'}

        images = []
        for filepath in sorted(dirpath.iterdir()):
            if filepath.suffix.lower() in extensions:
                try:
                    img = Image(str(filepath))
                    images.append(img)
                except Exception as e:
                    print(f"Warning: Failed to load {filepath}: {e}")

        return images


class SoundPool(Pool):
    """
    Pool of sounds, typically loaded from a directory.
    """

    def __init__(self, *items):
        """
        Create a sound pool.

        Args:
            *items: Sound objects or directory to load from
        """
        if len(items) == 1 and isinstance(items[0], (str, Path)):
            # Check if it's a directory
            path = Path(items[0])
            if path.exists() and path.is_dir():
                items = self._loadFromDir(path)

        super().__init__(*items)

    def _loadFromDir(self, dirpath: Path) -> List['FileAudioClip']:
        """
        Load sounds from directory.

        Args:
            dirpath: Path to directory

        Returns:
            List of FileAudioClip objects
        """
        from .audio import FileAudioClip

        # Supported audio extensions
        extensions = {'.wav', '.aiff', '.aif', '.au', '.mp3', '.ogg', '.flac'}

        sounds = []
        for filepath in sorted(dirpath.iterdir()):
            if filepath.suffix.lower() in extensions:
                try:
                    sound = FileAudioClip(str(filepath))
                    sounds.append(sound)
                except Exception as e:
                    print(f"Warning: Failed to load {filepath}: {e}")

        return sounds


class PoolDict(dict):
    """
    Dictionary-based pool with attribute access.
    """

    def __getattr__(self, name: str) -> Any:
        """Allow attribute access to dictionary items."""
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        if name not in self:
            raise AttributeError(f"PoolDict has no attribute '{name}'")
        return self[name]

    def __setattr__(self, name: str, value: Any):
        """Allow attribute assignment to dictionary items."""
        self[name] = value
