

class Crib:
    """a superposition of several `Stencil`, where the perforated positions
    remain perforated if all `Stencil` are perforated at that position, and
    blocked otherwise
    (A la "breaking the Enigma" kind of Crib)

    # this could maybe be a function or method `make_crib(list of Stencil)`,
    # returning an aggregate Stencil?

    # Note (that probably takes us far out of scope):
    # Stencils forming a Crib could be moved/perturbated, to discover a
    # pattern?
    # the Masks forming a Stencil could also be slided?
    """


class Stencil:
    """a "cover" on a grid surface that is "perforated" at some positions to
    let the elements through, while the other positions are blocked and
    conceal the elements.
    an aggregate of `Mask`
    """