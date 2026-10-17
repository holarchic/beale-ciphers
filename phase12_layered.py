"""
---
version: 0.1.0
created: 2026-10-17
updated: 2026-10-17
---

phase12_layered.py — Second-layer cipher tests on the DoI decodes of B1 and B3.

Pelling's double-encipherment hypothesis: B1 and B3 are genuine DoI book
ciphers whose plaintext was first put through a classical cipher, so every
single-layer test fails even for a real message. Each family below
brute-forces that second layer on the decoded letters:

  1. Columnar transposition: periods 2-25 in identity column order, and every
     column order for periods 2-6.
  2. Hill 2x2: all 157,248 invertible matrices mod 26.
  3. Keyed substitution: plaintext-autokey Vigenere, and Vigenere and Beaufort
     with a repeating key; every key of length 1-3 plus thematic long keys.
  4. Index of coincidence by period 1-25 against a unigram-preserving shuffle
     null. A periodic polyalphabetic layer of any key length shows here.

The test families follow Hsieh, "A reproducible re-examination of Beale
ciphers B1 and B3", Cryptologia 50(5):550-561 (2026),
doi:10.1080/01611194.2026.2698071. Here the decodes use the Beale-variant DoI
numbering that B2 decodes against; the paper used the standard numbering.

Each search's best score is compared with the best the same search finds on
shuffled letters (a best-of-brute null). Each family is also checked by
planting a random key on B2's plaintext and confirming the search recovers
English, so a negative result is not a blind search.

Usage:
    python3 phase12_layered.py --transposition
    python3 phase12_layered.py --hill
    python3 phase12_layered.py --keyed
    python3 phase12_layered.py --ioc
    python3 phase12_layered.py --all --n-null 100
"""

from __future__ import annotations

import argparse
import functools
import itertools
import string
import sys
import time
from typing import Callable

import numpy as np

from beale import B1, B3, B2_PLAINTEXT, BEALE_DOI, BIGRAM_LOGPROB, decode_book_cipher


ALPHABET = string.ascii_lowercase
BIGRAM_TABLE = np.array([[BIGRAM_LOGPROB[a + b] for b in ALPHABET] for a in ALPHABET])

# B2's plaintext scores -2.79 and shuffled B1/B3 decodes about -3.37, so a
# decode at or above -3.0 reads as English.
ENGLISH_THRESHOLD = -3.0

THEMATIC_KEYS = (
    "abcdefghiijklmmno", "defghiijklmmno", "abcdefghijklmnopqrstuvwxyz",
    "zyxwvutsrqponmlkjihgfedcba", "beale", "thomasbeale", "ward", "morriss",
    "buford", "bedford", "virginia", "lynchburg", "liberty", "declaration",
    "independence",
)

# A search returns its best score, that key in words, and the decrypt it gives.
Search = Callable[[np.ndarray], tuple[float, str, np.ndarray]]


# ============================================================================
# LETTERS AND SCORING
# ============================================================================

def to_ints(text: str) -> np.ndarray:
    """Letters as 0-25; anything else (a '?' for an out-of-range number) as -1."""
    return np.array([ALPHABET.index(c) if c in ALPHABET else -1 for c in text],
                    dtype=np.int64)


def to_text(x: np.ndarray) -> str:
    return "".join(ALPHABET[v] if v >= 0 else "?" for v in x)


def cipher_letters() -> dict[str, np.ndarray]:
    """B1 and B3 decoded with the Beale-variant DoI. B1's out-of-range numbers
    stay as -1 so every other letter keeps its position."""
    return {"B1": to_ints(decode_book_cipher(B1, BEALE_DOI)),
            "B3": to_ints(decode_book_cipher(B3, BEALE_DOI))}


def score(x: np.ndarray) -> np.ndarray:
    """Mean bigram log-prob along the last axis, skipping bigrams with an unknown."""
    a, b = x[..., :-1], x[..., 1:]
    known = (a >= 0) & (b >= 0)
    logp = BIGRAM_TABLE[np.clip(a, 0, 25), np.clip(b, 0, 25)]
    return (logp * known).sum(-1) / known.sum(-1)


def shuffle_known(x: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Permute the known letters among their positions; unknowns stay put."""
    y = x.copy()
    idx = np.flatnonzero(x >= 0)
    y[idx] = rng.permutation(x[idx])
    return y


def masked_like(c: np.ndarray, x: np.ndarray) -> np.ndarray:
    """A planted ciphertext loses the letters the real cipher is missing."""
    c = c.copy()
    c[x[:len(c)] < 0] = -1
    return c


def longest_known_run(x: np.ndarray) -> np.ndarray:
    """The longest stretch of x with no unknown letter."""
    best_start, best_len, start = 0, 0, 0
    for i in range(len(x) + 1):
        if i == len(x) or x[i] < 0:
            if i - start > best_len:
                best_start, best_len = start, i - start
            start = i + 1
    return x[best_start:best_start + best_len]


# ============================================================================
# 1. COLUMNAR TRANSPOSITION
# ============================================================================

def transposition_orders() -> list[tuple[int, ...]]:
    orders = [tuple(range(period)) for period in range(7, 26)]
    for period in range(2, 7):
        orders += list(itertools.permutations(range(period)))
    return orders


def columnar_positions(n: int, order: tuple[int, ...]) -> np.ndarray:
    """Plaintext position of each ciphertext letter when the plaintext is
    written in rows of len(order) and read off column by column in `order`."""
    period = len(order)
    return np.concatenate([np.arange(col, n, period) for col in order])


def columnar_encrypt(p: np.ndarray, order: tuple[int, ...]) -> np.ndarray:
    return p[columnar_positions(len(p), order)]


@functools.lru_cache(maxsize=None)
def _transposition_gathers(n: int) -> np.ndarray:
    """Row i gathers ciphertext into plaintext order for transposition_orders()[i]."""
    return np.stack([np.argsort(columnar_positions(n, o)) for o in transposition_orders()])


def search_transposition(x: np.ndarray) -> tuple[float, str, np.ndarray]:
    decrypts = x[_transposition_gathers(len(x))]
    scores = score(decrypts)
    i = int(scores.argmax())
    order = transposition_orders()[i]
    return float(scores[i]), f"period {len(order)}, column order {order}", decrypts[i]


# ============================================================================
# 2. HILL 2x2
# ============================================================================

@functools.lru_cache(maxsize=None)
def invertible_2x2() -> np.ndarray:
    """Every invertible 2x2 matrix mod 26 as a row (a, b, c, d)."""
    m = np.array(np.meshgrid(*[np.arange(26)] * 4, indexing="ij")).reshape(4, -1).T
    det = (m[:, 0] * m[:, 3] - m[:, 1] * m[:, 2]) % 26
    return m[np.gcd(det, 26) == 1]


def hill_apply(m: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Apply each matrix in m (K x 4) to x's letter pairs; a pair holding an
    unknown comes out unknown. Encrypts with a key, decrypts with its inverse."""
    n = len(x) - len(x) % 2
    pairs = x[:n].reshape(-1, 2)
    unknown = np.flatnonzero((pairs < 0).any(1))
    pairs = np.where(pairs < 0, 0, pairs)
    out = np.empty((len(m), n), dtype=np.int64)
    out[:, 0::2] = (m[:, 0:1] * pairs[:, 0] + m[:, 1:2] * pairs[:, 1]) % 26
    out[:, 1::2] = (m[:, 2:3] * pairs[:, 0] + m[:, 3:4] * pairs[:, 1]) % 26
    out[:, 2 * unknown] = -1
    out[:, 2 * unknown + 1] = -1
    return out


def search_hill(x: np.ndarray) -> tuple[float, str, np.ndarray]:
    matrices = invertible_2x2()
    best, best_m = -np.inf, matrices[0]
    for chunk in np.array_split(matrices, 16):
        scores = score(hill_apply(chunk, x))
        i = int(scores.argmax())
        if scores[i] > best:
            best, best_m = float(scores[i]), chunk[i]
    return (best, f"decryption matrix {best_m.reshape(2, 2).tolist()}",
            hill_apply(best_m[None, :], x)[0])


# ============================================================================
# 3. KEYED SUBSTITUTION: AUTOKEY, VIGENERE, BEAUFORT
# ============================================================================

@functools.lru_cache(maxsize=None)
def key_batches() -> tuple[np.ndarray, ...]:
    """Every key of length 1-3 (one batch per length), then each thematic key."""
    short = [np.array(list(itertools.product(range(26), repeat=n))) for n in (1, 2, 3)]
    return tuple(short) + tuple(to_ints(k)[None, :] for k in THEMATIC_KEYS)


def autokey_decrypt(keys: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Plaintext-autokey Vigenere: the primer keys the first len(primer)
    letters, then each plaintext letter keys the one len(primer) after it."""
    n_keys, primer_len = keys.shape
    p = np.full((n_keys, len(c)), -1, dtype=np.int64)
    for i in range(len(c)):
        k = keys[:, i] if i < primer_len else p[:, i - primer_len]
        known = (k >= 0) & (c[i] >= 0)
        p[:, i] = np.where(known, (c[i] - k) % 26, -1)
    return p


def autokey_encrypt(primer: np.ndarray, p: np.ndarray) -> np.ndarray:
    keystream = np.concatenate([primer, p])[:len(p)]
    return (p + keystream) % 26


def periodic_decrypt(keys: np.ndarray, c: np.ndarray, beaufort: bool) -> np.ndarray:
    """Vigenere p = c - k, or Beaufort p = k - c, with each key repeated."""
    k = keys[:, np.arange(len(c)) % keys.shape[1]]
    p = (k - c) % 26 if beaufort else (c - k) % 26
    return np.where(c >= 0, p, -1)


def periodic_encrypt(key: np.ndarray, p: np.ndarray, beaufort: bool) -> np.ndarray:
    k = key[np.arange(len(p)) % len(key)]
    return (k - p) % 26 if beaufort else (p + k) % 26


def best_over_keys(x: np.ndarray, decrypt: Callable) -> tuple[float, str, np.ndarray]:
    best, best_key = -np.inf, key_batches()[0][:1]
    for keys in key_batches():
        scores = score(decrypt(keys, x))
        i = int(scores.argmax())
        if scores[i] > best:
            best, best_key = float(scores[i]), keys[i:i + 1]
    return best, f"key '{to_text(best_key[0])}'", decrypt(best_key, x)[0]


def search_autokey(x: np.ndarray) -> tuple[float, str, np.ndarray]:
    # One missing letter blanks every later letter it would have keyed, so
    # search the longest gap-free run. A run that starts after a gap is keyed
    # by the lost letters before it, which the length 1-3 primers cover.
    return best_over_keys(longest_known_run(x), autokey_decrypt)


def search_vigenere(x: np.ndarray) -> tuple[float, str, np.ndarray]:
    return best_over_keys(x, functools.partial(periodic_decrypt, beaufort=False))


def search_beaufort(x: np.ndarray) -> tuple[float, str, np.ndarray]:
    return best_over_keys(x, functools.partial(periodic_decrypt, beaufort=True))


# ============================================================================
# SEARCH HARNESS: BEST-OF-BRUTE NULL AND PLANTED-KEY CONTROL
# ============================================================================

def plant(family: str, p: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, str]:
    """Encrypt plaintext p with a random key from inside the family's search."""
    if family == "transposition":
        order = tuple(int(v) for v in rng.permutation(5))
        return columnar_encrypt(p, order), f"period 5, column order {order}"
    if family == "hill":
        m = invertible_2x2()[rng.integers(len(invertible_2x2()))]
        return hill_apply(m[None, :], p)[0], f"key matrix {m.reshape(2, 2).tolist()}"
    key = rng.integers(26, size=3)
    if family == "autokey":
        return autokey_encrypt(key, p), f"primer '{to_text(key)}'"
    beaufort = family == "beaufort"
    return periodic_encrypt(key, p, beaufort), f"key '{to_text(key)}'"


def run_family(family: str, search: Search, letters: dict[str, np.ndarray],
               n_null: int, rng: np.random.Generator) -> dict:
    """Search each cipher, its shuffled-letter null and a planted control."""
    print(f"\n--- {family} ---")
    print(f"{'cipher':>6s}  {'best':>7s}  {'null mean':>9s}  {'null max':>8s}  "
          f"{'p':>6s}  {'control':>7s}  best key")
    results = {}
    for label, x in letters.items():
        best, key, decrypt = search(x)
        null = np.array([search(shuffle_known(x, rng))[0] for _ in range(n_null)])
        p = (1 + int((null >= best).sum())) / (1 + n_null)

        planted, planted_key = plant(family, to_ints(B2_PLAINTEXT[:len(x)]), rng)
        control, _, control_decrypt = search(masked_like(planted, x))

        results[label] = {"best": best, "key": key, "null_mean": float(null.mean()),
                          "null_max": float(null.max()), "p": p, "control": control}
        print(f"{label:>6s}  {best:7.3f}  {null.mean():9.3f}  {null.max():8.3f}  "
              f"{p:6.3f}  {control:7.3f}  {key}")
        print(f"{'':>6s}  best decrypt: {to_text(decrypt[:50])}")
        print(f"{'':>6s}  control ({planted_key}) recovers: {to_text(control_decrypt[:50])}")
    return results


# ============================================================================
# 4. INDEX OF COINCIDENCE BY PERIOD
# ============================================================================

def column_ioc(x: np.ndarray, period: int) -> float:
    """Mean index of coincidence over the period's columns, ignoring unknowns."""
    iocs = []
    for col in range(period):
        v = x[col::period]
        counts = np.bincount(v[v >= 0], minlength=26)
        n = counts.sum()
        iocs.append((counts * (counts - 1)).sum() / (n * (n - 1)))
    return float(np.mean(iocs))


def ioc_profile(x: np.ndarray, max_period: int = 25) -> np.ndarray:
    return np.array([column_ioc(x, period) for period in range(1, max_period + 1)])


def ioc_test(x: np.ndarray, n_null: int, rng: np.random.Generator) -> dict:
    """Column IoC per period against shuffles of the same letters. The decode's
    IoC inherits the DoI's first-letter skew, so English's 0.067 is no baseline."""
    observed = ioc_profile(x)
    null = np.array([ioc_profile(shuffle_known(x, rng)) for _ in range(n_null)])
    z = (observed - null.mean(0)) / null.std(0)
    flagged = [period for period, (o, col) in enumerate(zip(observed, null.T), 1)
               if o > col.max()]
    return {"observed": observed, "z": z, "flagged": flagged}


def run_ioc(letters: dict[str, np.ndarray], n_null: int, rng: np.random.Generator) -> dict:
    """IoC profile for each cipher and for a period-7 Vigenere planted on B2."""
    print("\n--- index of coincidence by period ---")
    print("(flagged = periods whose IoC beats every shuffle)")
    key = rng.integers(26, size=7)
    controls = {f"control for {label}":
                masked_like(periodic_encrypt(key, to_ints(B2_PLAINTEXT[:len(x)]), False), x)
                for label, x in letters.items()}
    results = {}
    for label, x in {**letters, **controls}.items():
        r = ioc_test(x, n_null, rng)
        top = int(np.argmax(r["z"]))
        results[label] = r
        print(f"{label:>16s}: IoC(1)={r['observed'][0]:.4f}  max z={r['z'][top]:+.2f} "
              f"at period {top + 1}  flagged={r['flagged'] or 'none'}")
    print(f"(controls use Vigenere key '{to_text(key)}', period 7)")
    return results


# ============================================================================
# SUMMARY
# ============================================================================

def verdict(r: dict) -> str:
    if r["control"] < ENGLISH_THRESHOLD:
        return "CONTROL FAILED"
    if r["p"] < 0.01 and r["best"] >= ENGLISH_THRESHOLD:
        return "HIT"
    return "no second layer"


def print_summary(family_results: dict[str, dict], ioc_results: dict | None) -> None:
    print("\n" + "=" * 72)
    print("PHASE 12 SUMMARY: SECOND-LAYER CIPHER TESTS")
    print("=" * 72)
    print(f"A hit needs p < 0.01 against the shuffle null and a score of at least "
          f"{ENGLISH_THRESHOLD} (English).")
    print(f"\n{'family':>14s}  {'cipher':>6s}  {'best':>7s}  {'null max':>8s}  "
          f"{'p':>6s}  {'control':>7s}  verdict")
    for family, by_cipher in family_results.items():
        for label, r in by_cipher.items():
            print(f"{family:>14s}  {label:>6s}  {r['best']:7.3f}  {r['null_max']:8.3f}  "
                  f"{r['p']:6.3f}  {r['control']:7.3f}  {verdict(r)}")
    if ioc_results:
        print("\nIoC by period (flagged periods beat every shuffle):")
        for label, r in ioc_results.items():
            print(f"  {label:>16s}: {r['flagged'] or 'none'}")


# ============================================================================
# CLI
# ============================================================================

FAMILIES: dict[str, tuple[str, Search]] = {
    "transposition": ("transposition", search_transposition),
    "hill": ("hill", search_hill),
    "autokey": ("keyed", search_autokey),
    "vigenere": ("keyed", search_vigenere),
    "beaufort": ("keyed", search_beaufort),
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phase 12: second-layer cipher tests on B1/B3 DoI decodes")
    parser.add_argument("--transposition", action="store_true",
                        help="Test 1: columnar transposition")
    parser.add_argument("--hill", action="store_true", help="Test 2: Hill 2x2")
    parser.add_argument("--keyed", action="store_true",
                        help="Test 3: autokey, Vigenere and Beaufort keys")
    parser.add_argument("--ioc", action="store_true",
                        help="Test 4: index of coincidence by period")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--n-null", type=int, default=100,
                        help="Shuffles per null distribution (default: 100; IoC uses 10x)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    args = parser.parse_args()

    selected = {flag for flag in ("transposition", "hill", "keyed", "ioc")
                if getattr(args, flag) or args.all}
    if not selected:
        parser.print_help()
        sys.exit(1)

    t0 = time.time()
    rng = np.random.default_rng(args.seed)
    letters = cipher_letters()
    family_results = {family: run_family(family, search, letters, args.n_null, rng)
                      for family, (flag, search) in FAMILIES.items() if flag in selected}
    ioc_results = run_ioc(letters, 10 * args.n_null, rng) if "ioc" in selected else None

    if args.all:
        print_summary(family_results, ioc_results)

    print(f"\nCompleted in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
