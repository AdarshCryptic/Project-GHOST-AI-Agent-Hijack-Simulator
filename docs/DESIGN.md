# GHOST — Design System

Theme: **Ghost Terminal** — dark, forensic, terminal-first.
Only design. No code changes in this pass.

## Colours

| Role | Hex | Use |
|---|---|---|
| Background | `#0B0F0E` | Page / terminal |
| Surface | `#121816` | Cards |
| Surface 2 | `#1A221F` | Hover / code blocks |
| Text | `#E8FFF4` | Primary text |
| Muted | `#8AA698` | Secondary text |
| Ghost green (accent) | `#00E5A0` | Logo, links, safe / REFUSED |
| Danger red | `#FF3B5C` | FOLLOWED / critical |
| Amber | `#FFB020` | PARTIAL / medium |
| Border | `#243129` | Dividers, card borders |

## Fonts

- **Display / headings:** Space Grotesk, 600–700, tight tracking (-0.02em)
- **Body:** Inter, 400–500
- **Code / mono:** JetBrains Mono, 400–600 — all canaries, tool calls, IDs

Fallback stack if web fonts are unavailable:
`Space Grotesk, Inter, system-ui, sans-serif` /
`JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, monospace`

## Type scale

- H1: 40px / 1.05, Space Grotesk 700
- H2: 24px / 1.2, Space Grotesk 600
- Body: 16px / 1.6, Inter 400
- Label / eyebrow: 12px, uppercase, letter-spacing 0.14em, JetBrains Mono
- Code: 13–14px, JetBrains Mono

## Verdict badges

- `FOLLOWED` — red bg `#FF3B5C22`, red text, red border
- `PARTIAL` — amber bg `#FFB02022`, amber text
- `IGNORED` — muted grey
- `REFUSED` — green bg `#00E5A022`, green text

## Rules

- Dark only. No light theme.
- One accent at a time: green for safe, red for hijacked.
- Terminal blocks: `#0B0F0E` bg, green prompt `ghost$`, mono font.
- Cards: 12px radius, 1px `#243129` border, no shadows.
- No gradients, no stock photos, no emoji in UI.
