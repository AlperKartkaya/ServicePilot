# Local reference coding

[XERJ](https://xerj.org/llms.txt) v1.0.0-rc.100 installed with the upstream installer and SHA-256 verification. Lexical retrieval, not neural search. Node: loopback `http://127.0.0.1:9327`; storage: `~/.cache/servicepilot/xerj-node`, outside this repository. No share, tunnel, feedback submission or uploaded project sources.

## Corpora
- Project: `xerj autoindex . --url http://127.0.0.1:9327 --prefix servicepilot --no-graph`. Initial result: 21 files, 346 records; empty `app/__init__.py` classified as junk, all 8 code files indexed. `.env`, `.git`, `.venv`, data/ and hidden skills excluded by normal rules.
- https://github.com/frappe/helpdesk at `d496b4dc187fa36a66695125b2e8df77f1c438d0` (2026-10-29). AGPL-3.0: approach only, no copied implementation. Clone: `~/.cache/servicepilot/references/helpdesk`, index prefix `refhelpdesk`. Result: 1,069 files / 6,398 records, all 488 code files indexed.
- https://github.com/langchain-ai/langgraph at `6f2df053f4487ce6ea8decc0d7482c8e46e0f132` (2026-10-29). MIT. Clone: `~/.cache/servicepilot/references/langgraph`, index prefix `reflanggraph`. Result: 599 files / 14,438 records, all 465 code files indexed. No LangGraph dependency introduced.

## Searches before implementation
```sh
xerj search --url http://127.0.0.1:9327 --prefix servicepilot 'renderCaseDetail nextAction' -k 2
xerj search --url http://127.0.0.1:9327 --prefix refhelpdesk 'TicketActions status priority assign' -k 2
xerj search --url http://127.0.0.1:9327 --prefix reflanggraph 'interrupt resume human approval' -k 2
xerj search --url http://127.0.0.1:9327 --prefix reflanggraph 'interrupt human_review approval' -k 3
```

Retrieved and read:
- Helpdesk `studio/helpdesk/composables/useTicketDetails.ts:22–86`: separate identity, nonempty metadata and timeline; highlight the next pending step rather than repeat all pending states. Applied as compact case context and a single next action.
- LangGraph `libs/prebuilt/langgraph/prebuilt/interrupt.py:8`: allowed human actions are explicit. `libs/sdk-py/langgraph_sdk/schema.py:915`: resume and state updates are distinct. Applied as state-dependent controls; human-reviewed assignment and machine recommendation stay distinct. The deprecated API is not adopted.

## Five project-local skills
Installed using the official Codex skill-installer script into `.agents/skills/` and read during this run. Skill discovery is available on the next turn; their instructions were applied directly now.

| Skill | Upstream | Application |
|---|---|---|
| frontend-design | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/frontend-design) | Compact token/layout plan in DESIGN.md; keep technical-desk identity |
| impeccable | [pbakaus/impeccable](https://github.com/pbakaus/impeccable/tree/main/.agents/skills/impeccable) | distill/clarify/polish: delete repeated panels, progressive disclosure, rendered QA |
| web-design-guidelines | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines) | Frontend accessibility/responsive/focus/error review |
| webapp-testing | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) | Browser inspection before interaction, screenshots and reproducible browser tests |
| systematic-debugging | [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/systematic-debugging) | Reproduce lifecycle/presentation defects, add a regression, fix root cause |

The first three are frontend skills. No upstream code is executed as application code. No global Codex config or AGENTS.md was changed.

## Resume
Start only this project's node when port 9327 is free:
```sh
XERJ_DISABLE_FEEDBACK=true xerj --insecure --port 9327 --data-dir "$HOME/.cache/servicepilot/xerj-node"
```
Reindex project changes with the same command above, without `--fresh`; the committed journal reconciles changes incrementally. `--fresh` refuses to discard an already committed generation. Use separate prefixes for each reference. Query before editing an unfamiliar path; inspect retrieved source and license. Do not index secrets or case data. Stop only the node you started.

Both reference imports completed with junk warnings only (binary/empty files); no code files were omitted. Impeccable context and detector were run locally; the application does not depend on its engine. Installed skill contents are versioned in this repo, so upstream drift does not silently change them.

## Scroll landing reference session — 2026-10-31

The earlier setup above is retained as history. The landing session uses loopback node data `~/.local/share/servicepilot-xerj` and independent prefix `splanding` (39 files / 408 records at the pre-implementation snapshot). The old `servicepilot` resume journal failed read-back validation against this node, so it was not overwritten.

Clones are outside the project at `~/.local/share/servicepilot-references/`:
- Lenis 1.3.27, `e01eefb1f55cd08bc051521d74f5f8182b71ee9d`, packages indexed as `reflenis`: 39 files / 185 records.
- GSAP 3.15.0, `13e2b790546426a1a2e0e9b409f3f8dc6d6611f2`, src indexed as `refgsap`: 34 files / 1,166 records.

Retrieved before implementation: Lenis `core/src/lenis.ts` options/RAF/touch behavior, GSAP `ScrollTrigger.js` scrub timing and matchMedia revert. The implementation follows [Lenis GSAP integration](https://github.com/darkroomengineering/lenis#gsap-scrolltrigger), [ScrollTrigger](https://gsap.com/docs/v3/Plugins/ScrollTrigger/), and [GSAP's standard license](https://gsap.com/standard-license/). GSAP is not described as MIT. Local vendored files and license notices are documented in `static/vendor/README.md`.

```sh
XERJ_DISABLE_FEEDBACK=true xerj --insecure --bind 127.0.0.1 --port 9327 --data-dir "$HOME/.local/share/servicepilot-xerj"
XERJ_DISABLE_FEEDBACK=true xerj search --url http://127.0.0.1:9327 --prefix refgsap 'pin scrub scrollTrigger'
XERJ_DISABLE_FEEDBACK=true xerj search --url http://127.0.0.1:9327 --prefix reflenis 'raf scroll smoothWheel'
```

Corpus Hub catalogue refresh returned 508 corpora; broad landing/GSAP/Lenis lookup reported `no_coverage`. It was not treated as a gallery of premium websites. No project sources, secrets or telemetry were uploaded.

Post-implementation reindex: 50 files / 488 records; all 22 code files indexed. Exit 3 is completed-with-junk for the empty `app/__init__.py`, not a code-indexing failure. Vendored runtimes, fonts, raster files and secrets are excluded by normal rules. Counts describe that source snapshot, not future edits.
