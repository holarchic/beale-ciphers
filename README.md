# Beale Ciphers

Nobody has cracked Beale ciphers B1 and B3 in 140 years. After the key search came up empty (9,500+ texts, four languages, nothing) we stopped hunting and modelled how you'd fake a book cipher at an 1880s desk instead. Both ciphers match the fake within 1σ on the two statistics that measure how the numbers were picked, and real English encoded the same way fits worse. Bayes factors for hoax over genuine come out at roughly 8 to 1,800 for B1 and 150 to 5,400 for B3, depending on the likelihood choices, which are all printed.

> **Status:** Complete (February 2026, corrected November 2026). All 12 phases are done. Reusable: `beale.py` (cipher data, book-cipher codecs, stats battery, English-likeness scoring) and `beale_doi_wordlist.py` (the 1,311-word Beale-variant Declaration of Independence).

<img src="phase8_multi_metric_b1.png" width="800" alt="Six histograms comparing B1's statistics with simulated ciphers from seven construction methods">

*B1 (red dashed line) against simulated ciphers from seven construction methods, none of them losing their place. None reaches B1's serial correlation. The fitted page-scanning model from phase 8 matches it within 1σ.*

## The approach

In 1885 a Virginia pamphlet published three number ciphers said to hide a treasure worth millions. B2 decodes with the Declaration of Independence as the key and describes the treasure. B1 (the vault's location) and B3 (the owners' names) have never decoded against anything.

Every analysis since has asked what key decrypts B1 and B3. We ran that search as due diligence and it came back empty, which gets you to "probably fake" on absence of evidence. That's where most analyses stop.

The real work assumed the ciphers were faked and asked a different question. Someone at a desk in the 1880s with a printed Declaration in front of them, making up a cipher that has to pass as real: what do their numbers look like? Model that person, generate the noise they'd produce, check whether B1 and B3 match it.

They do, within 1σ on serial correlation and distinct ratio. Then we ran the control: real English, encoded by the same forward scan. It fits worse, by a likelihood factor of roughly 7 to 550, so the numbers carry some trace of what was encoded as well as how. Two more patterns fit a person doing the job by hand. The Gillogly alphabet strings fall out of the method once the hoaxer lapses into the alphabet, and both ciphers get sloppier from start to finish.

## How do you fake a book cipher?

**A book cipher is a lookup against a shared text.** For each letter you find a word in the key text starting with that letter and write down its position. The Beale key is the Declaration of Independence, 1,311 numbered words. To encode "t" you could use word 3 (*the*), 14 (*to*) or 75 (*truths*) and all three decode back to "t". Every letter has a choice like that, and how the encoder makes it leaves a fingerprint. Pick favourites from memory and you reuse a small set of numbers. Run your finger down the page and your numbers climb.

**We simulated seven ways to produce one.**

1. Letters drawn at English frequencies, each encoded with a random matching word (the from-memory baseline)
2. Uniform random numbers from 1 to 1311 (the laziest fake)
3. Human-random numbers, with round-number bias and the other habits people have
4. Gibberish letters, each encoded by jumping to a random matching word
5. The same, with the gibberish following English vowel rates
6. Sequential gibberish: make up a letter, scan forward from where your finger is to the next word starting with it, write down its number, repeat
7. Sequential English: the same forward scan, with real English in place of gibberish (the control)

**Only sequential scanning produces serial correlation.** Scanning forward makes each number tend to be bigger than the last, until you reach the end of a page or lose your place and jump back. A genuine encoder working from memory shows none of it, and B2 sits at 0.04. B1 is at 0.25 and B3 at 0.62. The five methods that don't scan can't get there.

**The one free parameter is how often the hoaxer loses their place.** Run a finger along dense 1880s type for long enough and you lose track and jump back. We swept that reset probability from 0 (never) to 1 (every number). B3 fits at about 0.01 and B1 at about 0.65. Same method, very different discipline.

**The page limit does the rest for B3.** Reset rate barely moves distinct ratio (55% to 59% across the whole sweep for a B1-length cipher). What drives it is how much of the text the hoaxer was working from, since fewer words means fewer homophones per letter. Hold B3's model to the first 975 words and it lands within 1σ on serial correlation and distinct ratio at the same time. B1 fits on the full text:

| | B2 (genuine) | B3 (faked first) | B1 (faked second) |
|---|---|---|---|
| **Words the cipher uses** | 1-807, plus its x and y overrides | 1-975 (pages 1-3) | 1-1300 (pages 1-4) |
| **Reset probability** | n/a | ~0.01 | ~0.65 |
| **Serial correlation** | 0.04 | 0.62 | 0.25 |
| **Distinct ratio** | 24% | 43% | 57% |
| **Model fit (SC, DR)** | n/a | z = 0.3, 0.1 | z = 0.3, 0.9 |

## Does real English fit as well?

**We ran the control most analyses skip.** If a genuine encoder also scanned forward through a printed key, serial correlation alone says nothing about fakery. So method 7 encodes real English the same way, from two sources: windows of B2's own plaintext, and the Declaration's text. Each source gets the same reset grid as gibberish and the same page limit, and we compare how likely B1's and B3's statistics are under each. The ratio averages the fit over every reset probability on the grid rather than picking the best one.

| | Gibberish over English (B2's text) | Gibberish over English (the Declaration's text) |
|---|---:|---:|
| **B1** | 7× | 550× |
| **B3** | 56× | 91× |

**English fits worse, not impossibly worse.** For B1, English scanning matches the serial correlation but uses too many distinct numbers (61% from B2's text against B1's 57%). For B3, English can match both statistics within 1σ, but only at reset rates of 0.003 to 0.005, so it's much less likely across the range of reset rates the comparison allows. The gap depends a lot on which English you use, and it assumes the Declaration stands in for whatever key a genuine encoder would have scanned.

**The twelve-statistic classification says something different.** Human-made random numbers win the weighted vote for both ciphers. Counted metric by metric, they win 7 of 12 for B1, while sequential gibberish wins 3 of 12 for B3. For B1, five of human-random's seven wins are digit statistics (Benford and last digits), which can't see how homophones were chosen. Its other two, for both ciphers, are the bigram score and index of coincidence of the Declaration decode. Those point at a real misfit: B1's and B3's decoded letters mix like random draws from the Declaration's word initials (bigram −3.37 and −3.33), which uniform gibberish doesn't reproduce (−3.68). So the hoaxer's made-up letters weren't uniform, and the model doesn't capture how they were chosen. On distinct ratio the scanning methods are closest, and only scanning gives positive serial correlation, which the reset sweep then fits.

## What else fits a hand-made fake?

### The Gillogly strings

**The strongest argument for a real cipher falls out of the method.** In 1980 Jim Gillogly decoded B1 with the Declaration, the wrong key by the story's own account, and found `abcdefghiijklmmno` at positions 187-203. Seventeen near-alphabetical characters in a row, odds under 10⁻¹² by chance. Genuine-cipher proponents have played it as their ace since. If B1 is encoded gibberish, how does structure leak through the wrong key?

**Humans are bad at making up random letters.** The alphabet is the strongest letter sequence in memory, and a hoaxer generating hundreds of letters by hand lapses into a, b, c, d... now and then. Encode that through the Declaration (word 147 *alter* for a, 436 *bodies* for b, 195 *changed* for c) and the numbers look random. Decode them with the same text and the alphabet comes straight back. The Gillogly string is the hoaxer's alphabet brain fart, preserved through a round trip of encoding and decoding with the same key.

**The lapse rate is fitted, not predicted.** Pure random gibberish gives longest runs of 5-6. Lapsing into the alphabet 70% of the time gives runs of 17+ about 11% of the time, and that rate was chosen to reproduce the run. Serial correlation and distinct ratio stay within 1σ of B1 at every lapse rate. It's the strongest qualitative evidence for B1, but the repo has no likelihood for the strings under a genuine B1 encoded with some other key, so they carry no weight in the Bayes factor.

### Fatigue

**The hoaxer got lazier as each session went on.** Split each cipher into quarters and measure serial correlation in each. Consistent effort gives a flat line. Both ciphers rise from the first quarter to the last:

| Quarter | B3 | B1 |
|---|:---:|:---:|
| Q1 | 0.08 | -0.07 |
| Q2 | 0.57 | 0.26 |
| Q3 | 0.46 | 0.31 |
| Q4 | 0.69 | 0.36 |

Early on they jumped around the page for variety. By the end they grabbed the next available word every time. Permutation test over 10,000 shuffles: B1 p < 0.001, B3 p < 0.0001, combined p ≤ 4×10⁻⁸, and the slope holds with 3 to 8 segments.

**It's evidence of a tired human, not of a fake.** The model runs a constant reset probability, so it doesn't generate the gradient. We didn't go looking for it, it came out of the data. But a genuine encoder scanning a physical key for hours would tire the same way.

## Checks on the story

**B2 is real.** B2 uses 180 distinct numbers across 763 positions, a distinct ratio of 23.6%. Encode its plaintext 1,000 times with random homophone choice and the mean is 64%, so B2 sits 43σ below it. The encoder worked from a memorised index or a personal lookup table, and at a serial correlation of 0.04 they weren't scanning the page. B2's plaintext also needs x and y 13 times, and the Declaration has no word starting with either. Every x is number 1005 (*have*) and every y is 811 (*fundamentally*), 13 of 13. A hoaxer writing the plaintext would have avoided those letters. Per-letter positional correlation can't separate B2 from B1 or B3 (Mann-Whitney p = 0.78 and 0.20), so the split rests on distinct ratio and serial correlation.

**B3 looks too short for what B2 says it holds.** B2 says B3 lists the names, residences and next of kin of 30 people. B3 is 618 characters. Simulating that content 10,000 times with 1820s Virginia names and county-level residences gives a mean of 1,194 characters and zero fits under 618. Names alone fit at 380 though, and a terse "surname, county, kin" format gets close, so this is evidence and not proof.

**Our reconstruction of the order is B2, then B3, then B1.** It's a hypothesis that fits the evidence rather than something the statistics prove. B2 names B3's contents, which fits B3 existing first. B3 is the careful job: reset probability 0.01, pages 1-3 only, longest Gillogly run 7. B1 is the second attempt: reset probability 0.65, all 4 pages, the 17-character run and two of 11. Each starts near zero serial correlation (B3 0.08, B1 -0.07 in the first quarter), so separate sessions, and homophone preferences are independent between them (Jaccard z = -0.4), so no shared lookup table. Anyone who has done tedious manual work twice will recognise the drop from B3 to B1.

**A coincidence we can't weigh.** B3's highest number is 975, or 3 × 325, and B1's highest in-range number is 1,300, or 4 × 325. An 1880s octavo fits about 325 words of the Declaration per page, and 325 is the only page size from 250 to 400 that puts both ciphers on a boundary. But every cipher front-loads, the genuine one included:

| Words | 1-325 | 326-650 | 651-975 | 976-1300 | 1301-1311 | over 1311 |
|---|---:|---:|---:|---:|---:|---:|
| **B1** | 384 | 70 | 46 | 9 | 0 | 11 |
| **B2** | 656 | 75 | 28 | 4 | 0 | 0 |
| **B3** | 560 | 34 | 24 | 0 | 0 | 0 |

B2 only reaches page 4 through its fixed x override, so stopping short of the end isn't a sign of fabrication. The factor of 325 was also noticed after the fact. It stays a curiosity with no weight in the Bayes factor.

**Due diligence came first.** Before any of this we tested every serious case for a real cipher:

| Hypothesis | Test | Result |
|---|---|---|
| Published analyses hold up (phase 1) | B2 decode, Gillogly strings, Wase's base-dependence | Decode and Gillogly check out. Wase's last-digit signal holds for B3 and not B1 |
| Statistics alone can classify (phase 2) | Monte Carlo against genuine and fake populations | Fake-vote share B1 ~71%, B3 ~35%. Suggestive only |
| Another cipher scheme (phase 3) | Gillogly-as-Vigenère, Pelling's multi-layer with 13 keys, sliding window | No English |
| An unknown key text (phases 4-5) | 8,594 Gutenberg texts as word keys, 9,428 as letter-index keys | Zero hits |
| A variant Declaration (phase 6) | Offsets, insertions, deletions, hill-climbing | No single edit improves all the Gillogly runs |
| Non-English plaintext (phase 7) | Latin, French, Spanish bigram scoring | Noise in all four languages |
| A second cipher layer (phase 12) | Columnar transposition, all 157,248 Hill 2×2 matrices, autokey, Vigenère, Beaufort, index of coincidence to period 25 | Nothing beats shuffled letters (p ≥ 0.17). The same searches recover a key planted on B2 every time |

<a id="formal-bayesian-model-phase-11"></a>

## How sure?

**Each cipher gets its own Bayes factor, built from ranges.** A Bayes factor is how much more likely the data is under hoax than under genuine. Each line of evidence gets a likelihood-ratio range rather than a single number, with the reason for each end, and the factor is the range those multiply out to. It's a sensitivity analysis over judgement calls, apart from the scan fit, which comes from simulation.

| Evidence | Applies to | Likelihood ratio | Why the range |
|---|---|---:|---|
| No key in 9,500+ texts | both | 1.1-3.3 | A Lynchburg almanac, newspaper or private letter wouldn't be on Gutenberg |
| Scan fit, gibberish over English | B1 | 7-550 | Simulated. Low end B2's English, high end the Declaration's |
| Scan fit, gibberish over English | B3 | 56-91 | The same, held to pages 1-3 |
| B3 too short | B3 | 2.3-18 | Names alone fit, and a terse format nearly does |

| | Bayes factor | Midpoint | Start 99% sure it's real | Start 50/50 |
|---|---:|---:|---:|---:|
| **B1** | 8-1,800 | 120 | 8-55% hoax | 89-99% hoax |
| **B3** | 150-5,400 | 890 | 60-90% hoax | 99.3-99.9% hoax |

The posterior columns run from the factor's lower bound to its midpoint.

**B3 has the stronger case on paper.** Both scan fits assume the Declaration stands in for a genuine encoder's key, but B3 adds length evidence that needs no key at all. B1's strongest evidence is the Gillogly strings, and they carry no weight until someone builds a likelihood for them under a genuine B1.

**The scan fit carries most of the weight.** Drop it and B1's midpoint falls to about 2 and B3's to about 12. The shared factor of 325 and the fatigue gradient carry none in the headline. Count them as assumptions and the midpoints rise to about 15,000 for B1 and 110,000 for B3.

**Phase 11 checks the statistics too.** It runs the multiple-comparison correction (11 of 15 tests survive Bonferroni), recovers the model parameters in an open grid search, and checks how the six statistics correlate.

## Limits

**The statistics identify a method, not a person.** Ward, who published the 1885 pamphlet, is the most parsimonious candidate, and that's as far as the data goes.

**The Bayes factor was 2×10⁷ until November 2026.** That figure multiplied five point likelihoods described as conservative. They weren't, the scan fit had no English control, and the factor was joint across both ciphers. The ranges above replace it.

**Every range except the scan fit is a judgement call.** Multiplying the lines assumes they're independent given the hypothesis. The scan fit assumes the Declaration behaves like whatever key a genuine encoder would have scanned, uses a normal approximation to the simulated statistics, and depends on two short English texts.

**Known residuals.** A junction-effect residual of z ≈ 4 between the ciphers. B2's reuse of 180 numbers is described, not explained. The errors inside the Gillogly run (the *ii* and *mm*) aren't modelled at character level. Benford's law and last-digit tests don't separate the three ciphers (all fail Benford at p < 0.001) and carry no weight here.

**The printing is a prediction nobody has checked.** A 4-page octavo Declaration at about 325 words per page, reading "inalienable". The best lead is *The American's Guide* (Hogan & Thompson, 1840), digitised by the Library of Congress. Candidates in [`doi_printing_research.md`](doi_printing_research.md). Finding it would be physical corroboration.

## Reproduce

```
Python 3.10+
pip install numpy scipy matplotlib
```

```bash
# Quick verification (< 1 min): B2 decode, stats battery
python3 beale.py

# Hoax reconstruction and English scanning control (phase 8, ~7 min)
python3 phase8_hoax_construction.py --all --n-sims 1000

# B2 construction analysis (phase 9, ~2 min)
python3 phase9_b2_analysis.py --all --n-sims 1000

# B3 length + cross-cipher analysis (phase 10, ~1 min)
python3 phase10_b3_cross_cipher.py --all --n-sims 1000

# Bayes factors, multiple comparison, cross-validation (phase 11, ~2 min)
python3 phase11_methodology.py --all --n-sims 1000

# Fatigue gradient with high-resolution permutation test
python3 phase8_hoax_construction.py --fatigue-test --n-sims 10000
```

Due diligence phases:

```bash
python3 phase1_reproduce.py
python3 phase2_monte_carlo.py --n-sims 1000
python3 phase3_bigram.py

# Word-level corpus search: 8,594 texts (~4GB download, several hours)
python3 phase4_corpus.py --sweep --sweep-start 1 --sweep-end 10000

# Letter-index corpus search: 9,428 texts (~35 min on cached texts)
python3 phase5_letter_cipher.py --sweep

python3 phase6_doi_variant.py --all
python3 phase7_multilingual.py --build-tables && python3 phase7_multilingual.py --sweep

# Second-layer ciphers (~7 min)
python3 phase12_layered.py --all
```

The cipher numbers and the Beale-variant Declaration ship in the repo. Phases 4 and 7 download texts from Project Gutenberg into `.gutenberg_cache/`, and the phase 5 and 7 sweeps read phase 4's cache, so run phase 4 first. Nothing calls a paid service.

> [!NOTE]
> Phases 1, 2, 3 and 8 write their charts to the working directory by default, overwriting the committed PNGs. Pass `--no-plots` or `--save-dir` to keep them.

| Phase | Script | What |
|-------|--------|------|
| 1 | `phase1_reproduce.py` | Reproduce published analyses: B2 decode, Gillogly strings, Wase base-dependence |
| 2 | `phase2_monte_carlo.py` | Monte Carlo classification: genuine vs fake cipher populations |
| 3 | `phase3_bigram.py` | Bigram transitions, Gillogly-as-Vigenère, Pelling multi-layer hypothesis |
| 4 | `phase4_corpus.py` | Word-level corpus search: 8,594 Gutenberg texts as candidate keys |
| 5 | `phase5_letter_cipher.py` | Letter-index hypothesis: 9,428 texts as character-level keys |
| 6 | `phase6_doi_variant.py` | Declaration variant optimisation: can a close variant extend the Gillogly strings? |
| 7 | `phase7_multilingual.py` | Multi-language hypothesis: Latin/French/Spanish bigram scoring |
| 8 | `phase8_hoax_construction.py` | **The inversion**: 7 construction methods, page-constrained model, English scanning control, page census, Gillogly resolution, fatigue gradient |
| 9 | `phase9_b2_analysis.py` | B2 construction analysis: reset sweep, fabrication test, homophone fingerprint |
| 10 | `phase10_b3_cross_cipher.py` | B3 length feasibility, cross-cipher session analysis, construction ordering |
| 11 | `phase11_methodology.py` | Per-cipher Bayes factors from likelihood-ratio ranges, multiple comparison, cross-validation |
| 12 | `phase12_layered.py` | Second-layer ciphers: columnar transposition, Hill 2×2, autokey/Vigenère/Beaufort, IoC by period |

`beale.py` holds the three ciphers, word-level and letter-index codecs, the stats battery (Benford, last-digit, distinct ratio, letter frequency, Gillogly runs), English-likeness scoring and Gutenberg corpus utilities. `beale_doi_wordlist.py` is the Beale-variant Declaration as a 1,311-word tuple (eight changes from the standard text, plus three decode overrides).

Issues and replications are welcome, failed replications most of all.

## Prior art

- Gillogly, J.F. (1980). "Breaking the Beale Cipher: Not Yet." *Cryptologia* 4(3).
- Nickell, J. (1982). "Discovered: The Secret of Beale's Treasure." *Virginia Magazine of History and Biography* 90(3).
- Wase, P. (2013). "The Beale Ciphers: Number-Theoretic Analysis." *Cryptologia* 37(3).
- Pelling, N. *Cipher Mysteries* blog. Ongoing analysis of the multi-layer hypothesis.
- Hsieh, M.-Y. (2026). "A Reproducible Re-examination of Beale Ciphers B1 and B3: Systematically Closing the Composite-Cipher Hypotheses, with Methodological Cautions." *Cryptologia* 50(5), 550-561. [doi:10.1080/01611194.2026.2698071](https://doi.org/10.1080/01611194.2026.2698071). The source of phase 12's test families.

## Attribution

For those who care about such things, the majority of the analysis and code in this repo was produced by Claude Opus 4.6 (Anthropic), with david guiding Claude, providing insights, direction and critical review throughout the process.

## License

MIT. See [LICENSE](LICENSE).
