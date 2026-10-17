# Note for Claude Fable: switched from Unsloth Studio to Ollama (2026-10-17)

Nir switched his local model server from Unsloth Studio to Ollama. Here's
what changed and why, so you can decide if the Bible needs updating.

## What happened

1. Unsloth Studio's chat-based server worked for a single real test (Iran,
   run_round.py, ~487s/call) but Nir wanted something more reliable/
   reusable, so we tried Ollama instead.
2. First attempt: imported Nir's exact GGUF file (from HuggingFace,
   huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF) directly into Ollama via
   a Modelfile. FAILED: "unknown model architecture: qwen35" — Ollama's
   engine at the time (v0.18.2) didn't support this newer hybrid Qwen
   architecture at all, no matter how it was imported.
3. Discovered Ollama's OWN library has the same abliterated model, properly
   packaged: `huihui_ai/Qwen3.8-abliterated:27b` (18GB, Q4_K_M). Pulled it
   directly — still failed with the same architecture error, because the
   problem was Ollama's outdated engine, not the file.
4. Upgraded Ollama from v0.18.2 to v0.40.5 (official install script). After
   the upgrade, the exact same library model loaded and worked correctly.
5. Context window: Ollama defaults to num_ctx=4096 per model unless told
   otherwise. We set OLLAMA_CONTEXT_LENGTH=32768 via a systemd service
   override (`/etc/systemd/system/ollama.service.d/override.conf`), to
   match the Bible's own stated recommendation (Part 04 line 359, Part 07
   line 6: "at least 32768"). This is a machine-wide setting (affects every
   model Ollama loads on this machine), not per-model.
6. GPU offload mattered a lot: Unsloth Studio's OWN old chat process was
   still running in the background and had NOT released ~9.5GB of VRAM
   even after Nir thought he'd "stopped" it earlier in the session — this
   silently starved Ollama down to 1% GPU / 99% CPU. Once Nir properly
   closed Unsloth Studio, Ollama jumped to 41% GPU / 59% CPU for the same
   model and context size. LESSON: always check `nvidia-smi
   --query-compute-apps` for stray VRAM holders before judging a slow
   result as "this is just how slow it is."

## Real numbers (after the fix, real --llm-test run, Iran)

- llm_ping: 2.4s
- position call: 231.0s (prompt_tokens=5851, completion_tokens=1920)
- display call: 169.4s (prompt_tokens=2138, completion_tokens=1705)
- Both validated correctly on the first attempt, no retries needed.
- For comparison, the OLD Unsloth Studio single real test (2026-10-16,
  --only IR) took: position 7m08s, naive_forecast 7m13s, crystal_forecast
  10m42s (with one retry), display 4m28s — so Ollama's position+display
  combined (400s) is already faster than Unsloth's position+display alone
  (7m08s + 4m28s = 696s), though this isn't a perfectly controlled
  comparison (different days, different headline counts, different load).

## Current settings (config/settings.env)

```
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=huihui_ai/Qwen3.8-abliterated:27b
LLM_API_KEY=not-needed-for-local
LLM_CONTEXT_BUDGET=12000   (unchanged — this is OUR prompt-size budget,
                             separate from Ollama's num_ctx, Bible 4.13)
```

## Open question for you, Fable

Should the Bible's language change from "Unsloth Studio, fall back to
Ollama" (current wording in Part 07 line 6) to the reverse — recommend
Ollama FIRST, since it turned out to be the one that actually needed a
real engine-version fix (not just a slider), and once fixed, was reliably
scriptable (survives reboots via systemd, no GUI chat window needed,
doesn't compete for VRAM with a leftover chat session)? Nir's call to make
with you, not mine — I'm just reporting what actually happened so you two
can decide if Part 07 section 7.1 (or wherever the model-server setup step
lives) needs a rewrite.

Also worth considering: should the Bible mention the
OLLAMA_CONTEXT_LENGTH systemd override explicitly, since the model-loading
screen Part 07 line 6 describes ("set the context window in the model
loading screen to at least 32768") doesn't exist for Ollama running
headless as a systemd service — there's no loading screen at all once it's
running as a daemon.

## IMPORTANT UPDATE (same day, 2026-10-17): the real maximum context, verified from official sources

Nir pushed back hard on "32768 because the Bible says so" and demanded the
REAL maximum this specific hardware can support, verified from actual
documentation (Unsloth's own docs + llama.cpp docs), not guesses, not
"matching a minimum."

**Verified facts, straight from Unsloth's official documentation
(unsloth.ai/docs/models/qwen3.8):**

> "Maximum context window: 262,144 (can be extended to 1M via YaRN)"
>
> "Best rule of thumb: RAM+VRAM ≈ the quant size; otherwise it'll still
> work, just much slower due to disk offloading."

Nir's machine: 12GB VRAM (RTX 4070 Ti) + 62GB system RAM = **~74GB total**.
The model's quant size (Q4_K_M): ~16-19GB. That's **~4x more total memory
than the quant size** — comfortably inside Unsloth's own stated rule of
thumb for smooth operation, with huge headroom left over specifically for
context/KV cache.

**The actual math (from the model's own architecture, read via `ollama
show`/journalctl, not guessed):** this is a hybrid architecture
(qwen35/Qwen3-Next style) where only 1 layer in every 4
(`full_attention_interval=4`) needs the expensive, context-growing kind of
memory; the rest are cheap constant-memory SSM/Mamba-style layers. Real
KV-cache math for this specific model (head_count_kv=4, key/value
length=256 each, ~16 attention layers out of 65 total):
- Model weights: ~16GB
- KV cache at the model's FULL native max (262,144 tokens): ~15GB more
- Total needed for FULL native max context: **~31GB**
- Nir's total available (RAM+VRAM combined): **~74GB**

**Conclusion: 262,144 (the model's own full native maximum) comfortably
fits Nir's actual combined hardware (GPU+CPU together, which is exactly
how he wants to use it — not GPU-only).** The crash/restart-loop
instability observed when testing this in Ollama directly was very likely
an Ollama-specific rough edge at extreme context sizes (possibly made worse
by testing it mid-loop while other processes/restarts were still settling),
NOT a real hardware memory limit — the math and Unsloth's own official
numbers both say it should fit.

**Correction to Bible guidance:** "at least 32768" was treated as a floor
to match, but it is NOT the real ceiling for this hardware, and should not
be presented to Nir as "the number" without the fuller picture above. The
real, hardware-justified number for this specific setup is the model's own
native max: 262,144. Whether to actually RUN at that size (vs. a smaller
size for speed) is a separate tradeoff — more context slows down
generation because it eats into the VRAM budget used for GPU-offloaded
model weight layers — but that is a SPEED tradeoff, not a "can it fit at
all" limit. Fable and Nir should decide together whether the Bible should
recommend running at the full 262,144 by default, or at a smaller size
for speed, now that the actual ceiling is known and documented here.
