# AEGIS — Counter-Swarm Defense Platform
## Design System & Color Scheme
### Version 1.0

---

> **Design Philosophy:** AEGIS is a defense-grade command and control interface. The visual language must communicate authority, precision, and urgency. It draws from real military C2 systems (like ATAK and Link 16 displays), air traffic control interfaces, and modern cybersecurity dashboards (Cloudflare, Datadog). Dark backgrounds reduce operator eye strain during sustained use. Every color choice is functional — color encodes information, not decoration.

---

## 1. Core Palette

### Background Scale

```
┌─────────────────────────────────────────────────────────┐
│  NAME              HEX         RGB              ROLE     │
├─────────────────────────────────────────────────────────┤
│  Deep Space        #080C14     8, 12, 20        App BG   │
│  Void              #0D1220     13, 18, 32       Panel BG │
│  Abyss             #111827     17, 24, 39       Card BG  │
│  Surface           #1A2235     26, 34, 53       Elevated │
│  Overlay           #1F2A40     31, 42, 64       Hover BG │
└─────────────────────────────────────────────────────────┘
```

**Visual:**
- `#080C14` ████████ Deep Space — the absolute darkest layer. Root background.
- `#0D1220` ████████ Void — sidebar, panel backgrounds.
- `#111827` ████████ Abyss — cards, modals.
- `#1A2235` ████████ Surface — elevated elements, dropdowns.
- `#1F2A40` ████████ Overlay — hover states, active rows.

---

### Primary — Tactical Blue

The system's primary interactive color. Draws from radar screens and military HUD displays.

```
┌──────────────────────────────────────────────────────────────┐
│  NAME              HEX         RGB               ROLE         │
├──────────────────────────────────────────────────────────────┤
│  Blue Dim          #0A2A4A     10, 42, 74        Subtle BG    │
│  Blue Dark         #0E3A6E     14, 58, 110       Pressed      │
│  Blue Core         #1565C0     21, 101, 192      Primary      │
│  Blue Bright       #1E88E5     30, 136, 229      Interactive  │
│  Blue Glow         #42A5F5     66, 165, 245      Highlight    │
│  Blue Light        #90CAF9     144, 202, 249     Text on Dark │
└──────────────────────────────────────────────────────────────┘
```

**Visual:**
- `#1565C0` ████████ Blue Core — primary buttons, active nav.
- `#1E88E5` ████████ Blue Bright — links, interactive elements.
- `#42A5F5` ████████ Blue Glow — hover states, pulsing radar arcs.
- `#90CAF9` ████████ Blue Light — secondary text, labels.

---

### Threat Level Colors — The Critical Scale

This scale is the most important part of the design system. Every operator decision is mediated through these colors. They must be instantly distinguishable under stress.

```
┌──────────────────────────────────────────────────────────────────────┐
│  LEVEL     NAME          HEX        RGB               MEANING        │
├──────────────────────────────────────────────────────────────────────┤
│  0         Cleared       #10B981    16, 185, 129      Benign / Safe  │
│  1         Monitoring    #F59E0B    245, 158, 11      Unknown        │
│  2         Caution       #F97316    249, 115, 22      Possible Threat│
│  3         Hostile       #EF4444    239, 68, 68       Confirmed      │
│  4         Critical      #DC2626    220, 38, 38       Impact Imminent│
│  —         Engaged       #8B5CF6    139, 92, 246      Being Engaged  │
│  —         Destroyed     #6B7280    107, 114, 128     Neutralized    │
└──────────────────────────────────────────────────────────────────────┘
```

**Visual:**
- `#10B981` ████████ Cleared Green — safe objects.
- `#F59E0B` ████████ Amber — unknown objects being tracked.
- `#F97316` ████████ Orange — elevated threat, monitoring closely.
- `#EF4444` ████████ Red — confirmed hostile, unengaged.
- `#DC2626` ████████ Deep Red — impact in <30s. Pulsing animation.
- `#8B5CF6` ████████ Violet — hostile currently being engaged.
- `#6B7280` ████████ Gray — neutralized / destroyed.

---

### Accent — Neon Green (Radar / Active Systems)

Draws from classic radar cathode ray tube green. Used sparingly for active sensor sweeps, live indicators, and uptime status.

```
┌─────────────────────────────────────────────────────────┐
│  NAME              HEX         RGB              ROLE     │
├─────────────────────────────────────────────────────────┤
│  Radar Dark        #064E3B     6, 78, 59        BG tint  │
│  Radar Core        #059669     5, 150, 105      Active   │
│  Radar Bright      #10B981     16, 185, 129     Pulse    │
│  Radar Glow        #34D399     52, 211, 153     Glow     │
└─────────────────────────────────────────────────────────┘
```

**Usage:** Radar sweep animations. "SYSTEMS ONLINE" indicator. Track dots for benign objects. Active sensor beacons.

---

### Typography Colors

```
┌──────────────────────────────────────────────────────────────┐
│  NAME              HEX         RGB               ROLE         │
├──────────────────────────────────────────────────────────────┤
│  Text Primary      #F1F5F9     241, 245, 249     Headings     │
│  Text Secondary    #94A3B8     148, 163, 184     Body text    │
│  Text Muted        #475569     71, 85, 105       Metadata     │
│  Text Disabled     #334155     51, 65, 85        Inactive     │
│  Text Accent       #42A5F5     66, 165, 245      Highlighted  │
└──────────────────────────────────────────────────────────────┘
```

---

### Border & Divider Colors

```
┌─────────────────────────────────────────────────────────┐
│  NAME              HEX         ROLE                      │
├─────────────────────────────────────────────────────────┤
│  Border Subtle     #1E293B     Dividers between panels   │
│  Border Default    #2D3F5E     Card borders              │
│  Border Active     #1E88E5     Focused / selected state  │
│  Border Danger     #EF4444     Error states              │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Complete Palette — CSS Variables

Paste this into your global CSS or Tailwind config. All components reference these variables, never hardcoded hex values.

```css
:root {
  /* ── Backgrounds ─────────────────────────────── */
  --color-bg-deep:       #080C14;
  --color-bg-void:       #0D1220;
  --color-bg-abyss:      #111827;
  --color-bg-surface:    #1A2235;
  --color-bg-overlay:    #1F2A40;

  /* ── Primary Blue ────────────────────────────── */
  --color-blue-dim:      #0A2A4A;
  --color-blue-dark:     #0E3A6E;
  --color-blue-core:     #1565C0;
  --color-blue-bright:   #1E88E5;
  --color-blue-glow:     #42A5F5;
  --color-blue-light:    #90CAF9;

  /* ── Threat Scale ────────────────────────────── */
  --color-threat-0:      #10B981;   /* Cleared */
  --color-threat-1:      #F59E0B;   /* Monitoring */
  --color-threat-2:      #F97316;   /* Caution */
  --color-threat-3:      #EF4444;   /* Hostile */
  --color-threat-4:      #DC2626;   /* Critical */
  --color-threat-engaged:#8B5CF6;   /* Being Engaged */
  --color-threat-dead:   #6B7280;   /* Destroyed */

  /* ── Radar Green ─────────────────────────────── */
  --color-radar-dark:    #064E3B;
  --color-radar-core:    #059669;
  --color-radar-bright:  #10B981;
  --color-radar-glow:    #34D399;

  /* ── Typography ──────────────────────────────── */
  --color-text-primary:  #F1F5F9;
  --color-text-secondary:#94A3B8;
  --color-text-muted:    #475569;
  --color-text-disabled: #334155;
  --color-text-accent:   #42A5F5;

  /* ── Borders ─────────────────────────────────── */
  --color-border-subtle: #1E293B;
  --color-border-default:#2D3F5E;
  --color-border-active: #1E88E5;
  --color-border-danger: #EF4444;

  /* ── Glow Effects ────────────────────────────── */
  --glow-blue:    0 0 12px rgba(30, 136, 229, 0.4);
  --glow-red:     0 0 12px rgba(239, 68, 68, 0.5);
  --glow-green:   0 0 12px rgba(16, 185, 129, 0.4);
  --glow-violet:  0 0 12px rgba(139, 92, 246, 0.4);
}
```

---

## 3. Typography System

### Font Stack

```css
/* Primary — Interface */
font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;

/* Secondary — Readability */
font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
```

**Why monospace primary?** AEGIS is a real-time data display. Track IDs, coordinates, latency numbers, timestamps — monospace ensures columns align perfectly and data reads cleanly. It also visually communicates that this is a technical system, not a consumer app.

**Why Inter secondary?** Best legibility at small sizes. Free (Google Fonts). Used for body text, descriptions, and labels where monospace would be too dense.

### Type Scale

```
┌────────────────────────────────────────────────────────────┐
│  TOKEN         SIZE     WEIGHT   FONT         USAGE        │
├────────────────────────────────────────────────────────────┤
│  --type-xs     10px     400      Mono         Metadata     │
│  --type-sm     12px     400      Mono         Labels       │
│  --type-base   13px     400      Mono         Body data    │
│  --type-md     14px     500      Inter        Panel titles │
│  --type-lg     16px     600      Inter        Section head │
│  --type-xl     20px     700      Inter        Panel header │
│  --type-2xl    24px     700      Inter        Page title   │
│  --type-display 32px   800      Inter        Alert/Danger │
└────────────────────────────────────────────────────────────┘
```

### Load Fonts (Google Fonts — Free)

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

---

## 4. Component Visual Specifications

### Threat Dot (Map Marker)

```css
/* Base dot */
.threat-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 1.5px solid currentColor;
}

/* Hostile — pulsing animation */
.threat-dot--hostile {
  background: #EF4444;
  box-shadow: var(--glow-red);
  animation: pulse-red 1.5s ease-in-out infinite;
}

/* Critical — fast pulse */
.threat-dot--critical {
  background: #DC2626;
  animation: pulse-red 0.6s ease-in-out infinite;
}

@keyframes pulse-red {
  0%, 100% { box-shadow: 0 0 4px rgba(239, 68, 68, 0.4); }
  50%       { box-shadow: 0 0 20px rgba(239, 68, 68, 0.9); }
}

/* Radar sweep ring */
.radar-sweep {
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 50%;
  animation: expand-fade 2s ease-out infinite;
}

@keyframes expand-fade {
  0%   { transform: scale(1); opacity: 0.6; }
  100% { transform: scale(3); opacity: 0; }
}
```

---

### Panel Card

```css
.panel-card {
  background: var(--color-bg-void);
  border: 1px solid var(--color-border-subtle);
  border-radius: 6px;
  padding: 16px;
}

.panel-card__header {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  border-bottom: 1px solid var(--color-border-subtle);
  padding-bottom: 8px;
  margin-bottom: 12px;
}
```

---

### Threat Row (in ThreatPanel)

```css
.threat-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  cursor: pointer;
  transition: background 0.15s;
}

.threat-row:hover {
  background: var(--color-bg-overlay);
}

.threat-row--critical {
  border-left: 3px solid var(--color-threat-4);
  animation: row-pulse 1s ease-in-out infinite;
}

@keyframes row-pulse {
  0%, 100% { background: transparent; }
  50%       { background: rgba(220, 38, 38, 0.08); }
}
```

---

### Status Badge

```css
/* Usage: <span class="badge badge--hostile">HOSTILE</span> */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 3px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.badge--cleared  { background: rgba(16, 185, 129, 0.15); color: #10B981; }
.badge--unknown  { background: rgba(245, 158, 11, 0.15);  color: #F59E0B; }
.badge--caution  { background: rgba(249, 115, 22, 0.15);  color: #F97316; }
.badge--hostile  { background: rgba(239, 68, 68, 0.15);   color: #EF4444; }
.badge--critical { background: rgba(220, 38, 38, 0.25);   color: #DC2626; }
.badge--engaged  { background: rgba(139, 92, 246, 0.15);  color: #8B5CF6; }
```

---

### System Health Indicator

```css
.health-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.health-dot--online  { background: #10B981; box-shadow: 0 0 6px #10B981; }
.health-dot--degraded{ background: #F59E0B; box-shadow: 0 0 6px #F59E0B; }
.health-dot--offline { background: #EF4444; animation: pulse-red 1s infinite; }
```

---

## 5. Layout Grid

```
┌─────────────────────────────────────────────────────────────────────┐
│  TOPBAR (48px) — Alert Timeline + System Health + AEGIS Wordmark   │
├──────────────┬──────────────────────────────────┬───────────────────┤
│              │                                  │                   │
│  LEFT NAV    │     TACTICAL MAP (PRIMARY)        │   THREAT PANEL    │
│  (200px)     │     Three.js + Mapbox             │   (280px)         │
│              │     70% of viewport               │                   │
│  - Overview  │                                  │  Ranked threats   │
│  - Tracks    │                                  │  Click to focus   │
│  - Sensors   │                                  │  Threat scores    │
│  - Defenders │                                  │  ETA countdown    │
│  - History   │                                  │                   │
│  - Settings  │                                  │                   │
│              │                                  │                   │
├──────────────┴──────────────────────────────────┴───────────────────┤
│  ASSIGNMENT PANEL (160px) — Current engagement assignments          │
│  [INTERCEPTOR_01] → [TRK-00042]  ETA: 23s  STATUS: ENGAGING        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 6. Three.js Map — Color Mapping

Colors used in the 3D tactical map in Three.js / WebGL:

```javascript
// THREE.js color constants for AEGIS map
export const MAP_COLORS = {
  // Ground / terrain
  terrain:          0x0D1A2D,
  terrain_grid:     0x1A2D4A,
  water:            0x0A1628,

  // Protected zones
  zone_fill:        0x1565C020,  // Blue, 12% opacity
  zone_border:      0x1E88E5,

  // Track colors by threat level
  track_cleared:    0x10B981,
  track_unknown:    0xF59E0B,
  track_caution:    0xF97316,
  track_hostile:    0xEF4444,
  track_critical:   0xDC2626,
  track_engaged:    0x8B5CF6,
  track_destroyed:  0x6B7280,

  // Trajectory arcs
  trajectory_hostile: 0xEF4444,
  trajectory_safe:    0x42A5F5,

  // Interceptor engagement envelope
  envelope_active:  0x8B5CF633,  // Violet, 20% opacity
  envelope_border:  0x8B5CF6,

  // Radar sweep
  radar_sweep:      0x10B98140,  // Green, 25% opacity

  // Interception beam
  interception_line: 0xA78BFA,
};
```

---

## 7. Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Backgrounds
        'bg-deep':    '#080C14',
        'bg-void':    '#0D1220',
        'bg-abyss':   '#111827',
        'bg-surface': '#1A2235',
        'bg-overlay': '#1F2A40',
        // Blues
        'blue': {
          dim:    '#0A2A4A',
          dark:   '#0E3A6E',
          core:   '#1565C0',
          bright: '#1E88E5',
          glow:   '#42A5F5',
          light:  '#90CAF9',
        },
        // Threat levels
        'threat': {
          0:       '#10B981',
          1:       '#F59E0B',
          2:       '#F97316',
          3:       '#EF4444',
          4:       '#DC2626',
          engaged: '#8B5CF6',
          dead:    '#6B7280',
        },
        // Radar green
        'radar': {
          dark:   '#064E3B',
          core:   '#059669',
          bright: '#10B981',
          glow:   '#34D399',
        },
      },
      fontFamily: {
        mono:  ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans:  ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'pulse-red':    'pulse-red 1.5s ease-in-out infinite',
        'pulse-fast':   'pulse-red 0.6s ease-in-out infinite',
        'radar-expand': 'expand-fade 2s ease-out infinite',
        'blink':        'blink 1s step-end infinite',
      },
    },
  },
};
```

---

## 8. Brand Mark

### Wordmark
`AEGIS` — all caps, JetBrains Mono, weight 700, color `#42A5F5` (Blue Glow), letter-spacing 0.2em.

Sub-label: `COUNTER-SWARM DEFENSE` — 10px, weight 400, color `#475569` (Text Muted), letter-spacing 0.25em.

### Visual Identity
No logo/icon for MVP. The wordmark with the glowing blue color and monospace font is the brand. Clean, technical, credible.

Post-MVP: A stylized shield icon — hexagonal, minimal, in Tactical Blue. The hexagon references both the software architecture (microservices/nodes) and swarm geometry.

---

## 9. Motion Design Principles

**Functional motion only.** Every animation communicates state, not decoration.

| Animation | Duration | Easing | Purpose |
|---|---|---|---|
| Threat dot pulse (hostile) | 1.5s | ease-in-out | Draws operator attention |
| Threat dot pulse (critical) | 0.6s | ease-in-out | Urgency escalation |
| Radar sweep expand | 2s | ease-out | Active sensor visualization |
| New threat appear | 200ms | ease-out | Track creation event |
| Track destroy | 400ms | ease-in | Visual confirmation of neutralization |
| Panel data update | 100ms | linear | State refresh at 10Hz (imperceptible) |
| Alert slide in | 250ms | ease-out | New alert notification |

**No decorative transitions.** No page transition animations. No hover bounce effects. The UI must feel like a tool, not an app.

---

*Document Version: 1.0 | AEGIS Founding Team*
