# Formula Conversion Pitfalls

Lessons from attempting to auto-convert Unicode math symbols to LaTeX in LLM Wiki pages (2026-05-09 session).

## What We Tried

Script-based batch replacement of Unicode math characters (µ→\mu, Ω→\Omega, etc.) across all wiki pages.

## What Went Wrong

### 1. Subscript Splitting
**Problem:** The replacement script wrapped individual symbols in `$...$` but didn't handle subscripts.

```
Before: α_ip = 0
After:  $\alpha$_ip = 0    ← subscript disconnected!
Should: $\alpha_{ip} = 0$
```

### 2. Command Concatenation (粘连)
**Problem:** When `\pi` was followed by text without a space, it merged.

```
Before: 2πnt/τ
After:  2\pint/\tau          ← \pi absorbed the 'n'!
Should: $2\pi n t / \tau$
```

### 3. Multi-Symbol Fragmentation
**Problem:** Complex expressions were split into many tiny `$...$` blocks.

```
After:  $\partial$^k $\alpha$_ip / $\partial$$\omega$_p^k = 0   ← 5 fragments!
Should: $\partial^k \alpha_{ip} / \partial \omega_p^k = 0$       ← 1 expression
```

### 4. Mixed Content Loss
**Problem:** `$\mu$₀` — the Unicode subscript `₀` survived outside math mode.

```
After:  $\mu$₀           ← ₀ is bare Unicode
Should: $\mu_0$
```

## The Fix

**Stop automating. Rewrite manually.** For each affected page:

1. Read the entire page with `read_file`
2. Rewrite with `write_file`, constructing every `$...$` and `$$...$$` by hand
3. Verify with `read_file` after writing

The manual approach ensures:
- Subscripts stay inside `$...$`: `$\alpha_{ip}$` not `$\alpha$_ip`
- Multi-symbol expressions are grouped: `$g(t) = \Omega(t) \sin[\psi(t)]$`
- Function names are correct: `\sin` not bare `sin`
- No orphan Unicode characters remain

## When to Use Manual Rewrite

Any page containing more than ~3 math symbols should be fully rewritten rather than patched. The time saved by automation is lost in debugging fragmented LaTeX.
