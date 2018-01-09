

class Stencil:
    """a rectangular "cover" on a grid surface that is "perforated" at some
    positions to let the elements through, while the other positions are
    blocked and conceal the elements.
    an aggregate of `Mask` of same length, defining a rectangle of
    SOLID and PUNCHED positions
    """
    def __init__(self):
        self.num_rows: int = 0
        self.num_cols: int = 0
        self.masks = None        # array of blanks [Mask(size=num_cols) for _ in range(num_rows)]
        self.patterns = None
