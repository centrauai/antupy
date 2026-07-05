# Unit system roadmap: parser and design cleanup

This roadmap captures the next small, focused refactors for `antupy.core.units`. The goal is to harden unit-string parsing, make the internal logic easier to reason about, and reduce duplicated behavior between parsing and unit composition, while keeping the current API and the simple style of the codebase.

## 1. Validate and normalize unit labels

- Name: Unit label validation and normalization
- Intention: Reject malformed unit strings early and normalize harmless variations before parsing.
- Recommendation: Add a preprocessing step that strips whitespace, enforces a single `/` at most, and rejects empty tokens or repeated separators.
- Where to apply: `Unit._split_unit` and the start of `Unit._parse_unit_comps` in `antupy/core/units.py`.
- Suggested implementation function: `validate_and_normalize_unit_label(label: str) -> str`

## 2. Parse positive integer exponents with more than one digit

- Name: Multi-digit exponent parsing
- Intention: Support labels such as `m10` and `s12` while keeping the grammar simple.
- Recommendation: Replace the current single-character exponent extraction with a helper that parses a trailing positive integer suffix only.
- Where to apply: `Unit._parse_unit_comps` in `antupy/core/units.py`.
- Suggested implementation function: `split_token_name_exponent(token: str) -> tuple[str, int]`

## 3. Unify parsing and unit composition logic

- Name: Canonical unit representation
- Intention: Make parsing, multiplication, and division use the same internal model instead of two separate string-manipulation paths.
- Recommendation: Introduce one canonical intermediate representation for unit tokens, then render the final string from that representation.
- Where to apply: `Unit._split_unit`, `Unit.__mul__`, `Unit.__truediv__`, `_mul_units`, and `_div_units` in `antupy/core/units.py`.
- Suggested implementation function: `render_unit_tokens(top_tokens: list[str], bottom_tokens: list[str]) -> str`

## 4. Keep aliases only in RELATED_UNITS and simplify adim handling

- Name: Alias normalization policy
- Intention: Make `RELATED_UNITS` the only place where accepted aliases are declared, while treating blank and whitespace-padded adimensional labels consistently.
- Recommendation: Remove hardcoded alias lists from the parsing helpers and normalize `""`, `"1"`, `"-"`, and `"adim"` through the same path.
- Where to apply: `RELATED_UNITS`, `Unit._split_unit`, and any helper that prepares the label before parsing.
- Suggested implementation function: `normalize_adim_label(label: str) -> str`

## 5. Improve equality behavior and document the affine-temperature boundary

- Name: Equality and semantics cleanup
- Intention: Make equality more robust for chained conversions and keep temperature handling conceptually separate from pure unit algebra.
- Recommendation: Use a tolerance for `base_factor` comparison in `Unit.__eq__`, and keep Celsius/Kelvin offsets handled by value-conversion code rather than by `Unit` itself.
- Where to apply: `Unit.__eq__` in `antupy/core/units.py`, plus the temperature conversion helpers in `antupy/core/units.py` and the corresponding docstrings.
- Suggested implementation function: `unit_factors_close(a: float, b: float) -> bool`

## Note on Celsius

- The current Celsius/Kelvin behavior should remain a value-conversion concern, not a change to the `Unit` grammar or algebra.
