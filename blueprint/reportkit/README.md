# reportkit (vendored)

- `check.py`, `POLICY.md`: copied unchanged from `cogito5170/se_new` (`reportkit/`). They are the "청사진" report policy and its machine check.
- `vendor/katex`: KaTeX (MIT License, see `vendor/katex/LICENSE`), copied from the same repository.

The Holo blueprint build (`blueprint/build.py`) runs `check.검사` on the final HTML. If the check finds any violation, the PDF is not written.
If the upstream policy changes, re-copy these files rather than editing them here.
