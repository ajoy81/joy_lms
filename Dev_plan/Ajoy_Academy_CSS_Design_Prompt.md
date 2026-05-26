# 🎨 AJOY ACADEMY — COMPLETE CSS & UI DESIGN SYSTEM
# Consolidated Prompt for Gemini Agent
# ================================================================
# Target: Streamlit LMS App | Mobile-First | Light/Dark Mode
# Inspired by: PW (Physics Wallah), CuriousJr, Duolingo, Khan Academy Kids
# ================================================================

---

## SECTION 1: PREAMBLE & ROLE ASSIGNMENT

You are a **Senior UI/CSS Engineer** specializing in:
- Mobile-first responsive design systems for education apps
- Streamlit custom theming and CSS injection
- Kid-friendly UX (ages 5-16) with gamification UI patterns
- Accessibility (WCAG AA compliance)
- Light/Dark mode architecture with CSS custom properties

### YOUR MISSION:
Build a **complete, production-ready CSS design system** for **"Ajoy Academy"** — a Kids Learning Management System built with Streamlit. The design must feel as polished as **PW CuriousJr** and **Duolingo** — colorful, playful, touch-friendly, and professional.

### DESIGN REFERENCES & INSPIRATION:
- **PW CuriousJr**: Bright orange (#FF6B35) + teal accents, large touch targets, animated mascot interactions, progress-centric dashboard, rounded card UI
- **Physics Wallah (PW)**: Royal blue (#5A4BDA), deep violet (#140D52), clean card layouts, course grid, dark mode support
- **Duolingo**: Lime green (#58CC02), streak fire animation, gamification UI (XP bars, badges, leaderboards), celebratory confetti
- **Khan Academy Kids**: Soft pastels, large buttons, minimal text, illustration-heavy UI

### CRITICAL REQUIREMENTS:
1. **Mobile-first** — designed for phones/tablets FIRST, then scales up to laptop/desktop
2. **Light & Dark mode** — full dual-theme with smooth toggle transition
3. **Kid-friendly** — rounded corners, large text, emoji-rich, celebration animations
4. **Touch-optimized** — minimum 48px touch targets, generous spacing
5. **Performance** — CSS-only animations (no heavy JS libraries needed)
6. **Streamlit-compatible** — all CSS injected via st.markdown(unsafe_allow_html=True)

---

## SECTION 2: COLOR SYSTEM — DUAL THEME

### 2.1 LIGHT MODE PALETTE (Default Theme)

| Token                     | Hex Code   | Usage                                    |
|---------------------------|-----------|------------------------------------------|
| `--bg-primary`            | `#F8F9FE` | Page background                          |
| `--bg-secondary`          | `#FFFFFF` | Cards, panels, modals                    |
| `--bg-tertiary`           | `#F0F2F8` | Sidebar, input backgrounds               |
| `--bg-hover`              | `#E8EAF6` | Hover state backgrounds                  |
| `--text-primary`          | `#1A1A2E` | Headings, body text                      |
| `--text-secondary`        | `#5A5A7A` | Subtitles, captions, timestamps          |
| `--text-tertiary`         | `#8E8EA0` | Placeholders, disabled text              |
| `--text-inverse`          | `#FFFFFF` | Text on colored backgrounds              |
| `--accent-primary`        | `#FF6B35` | Primary CTA buttons (CuriousJr orange)   |
| `--accent-secondary`      | `#4361EE` | Links, secondary actions (PW blue)       |
| `--accent-tertiary`       | `#00C9A7` | Success accents, progress bars (Teal)    |
| `--accent-fun`            | `#FFD93D` | Badges, stars, highlights (Yellow)       |
| `--accent-pink`           | `#FF6B6B` | Hearts, streaks, alerts (Coral)          |
| `--accent-purple`         | `#7C3AED` | Premium badges, special features         |
| `--success`               | `#10B981` | Completed, passed, correct               |
| `--warning`               | `#F59E0B` | Due soon, medium priority                |
| `--error`                 | `#EF4444` | Failed, overdue, wrong answer            |
| `--info`                  | `#3B82F6` | Info banners, tooltips                   |
| `--border-light`          | `#E2E8F0` | Card borders, dividers                   |
| `--gradient-primary`      | `linear-gradient(135deg, #FF6B35, #FF8F65)` | Primary buttons   |
| `--gradient-streak`       | `linear-gradient(135deg, #FF6B35, #F59E0B)` | Streak fire       |
| `--gradient-sidebar`      | `linear-gradient(180deg, #1A1A2E, #16213E)` | Sidebar bg        |

### 2.2 DARK MODE PALETTE

| Token                     | Hex Code   | Usage                                    |
|---------------------------|-----------|------------------------------------------|
| `--bg-primary`            | `#0F0F1A` | Page background                          |
| `--bg-secondary`          | `#1A1A2E` | Cards, panels                            |
| `--bg-tertiary`           | `#16213E` | Sidebar, input backgrounds               |
| `--bg-hover`              | `#1E2A4A` | Hover state backgrounds                  |
| `--text-primary`          | `#E8E8F0` | Headings, body text                      |
| `--text-secondary`        | `#B8C1EC` | Subtitles, captions                      |
| `--text-tertiary`         | `#6B7280` | Placeholders, disabled text              |
| `--accent-primary`        | `#FF8F65` | Primary CTA (lighter orange for contrast)|
| `--accent-secondary`      | `#818CF8` | Links (lighter blue)                     |
| `--accent-tertiary`       | `#00E5FF` | Success/teal (neon glow)                 |
| `--accent-fun`            | `#FBBF24` | Stars, badges                            |
| `--accent-pink`           | `#FB7185` | Hearts, streaks                          |
| `--accent-purple`         | `#A78BFA` | Premium badges                           |
| `--success`               | `#34D399` | Completed, passed                        |
| `--warning`               | `#FBBF24` | Due soon                                 |
| `--error`                 | `#F87171` | Failed, overdue                          |
| `--info`                  | `#60A5FA` | Info banners                             |
| `--border-light`          | `#2D3748` | Card borders                             |
| `--gradient-primary`      | `linear-gradient(135deg, #FF8F65, #FFB088)` | Primary buttons   |
| `--gradient-streak`       | `linear-gradient(135deg, #FF8F65, #FBBF24)` | Streak fire       |

### 2.3 DIFFICULTY & CATEGORY COLORS

| Difficulty | Light BG  | Light Text | Dark BG   | Dark Text  |
|-----------|----------|-----------|----------|-----------|
| Easy      | #D1FAE5  | #065F46   | #064E3B  | #6EE7B7   |
| Medium    | #FEF3C7  | #92400E   | #78350F  | #FCD34D   |
| Hard      | #FEE2E2  | #991B1B   | #7F1D1D  | #FCA5A5   |

| Category     | Color   |
|-------------|---------|
| Mathematics | #4361EE |
| Science     | #10B981 |
| English     | #F59E0B |
| Coding      | #7C3AED |
| Art & Craft | #EC4899 |
| Music       | #06B6D4 |
| Life Skills | #FF6B35 |


---

## SECTION 3: TYPOGRAPHY SYSTEM

### 3.1 Font Stack

```css
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&family=Nunito:wght@400;500;600;700;800&display=swap');

:root {
    --font-heading: 'Fredoka', 'Comic Sans MS', cursive, sans-serif;
    --font-body: 'Nunito', 'Segoe UI', system-ui, -apple-system, sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
}
```

### 3.2 Type Scale (Mobile to Desktop)

| Token         | Mobile | Tablet | Desktop | Weight | Font    | Usage              |
|---------------|--------|--------|---------|--------|---------|--------------------|
| --text-hero   | 28px   | 36px   | 42px    | 700    | Heading | Welcome banners    |
| --text-h1     | 24px   | 28px   | 32px    | 700    | Heading | Page titles        |
| --text-h2     | 20px   | 22px   | 26px    | 600    | Heading | Section headings   |
| --text-h3     | 17px   | 18px   | 20px    | 600    | Heading | Card titles        |
| --text-body   | 14px   | 15px   | 16px    | 400    | Body    | Paragraphs         |
| --text-sm     | 12px   | 13px   | 14px    | 400    | Body    | Captions, times    |
| --text-xs     | 10px   | 11px   | 12px    | 400    | Body    | Badge labels       |
| --text-stat   | 32px   | 40px   | 48px    | 800    | Heading | Stat card numbers  |

### 3.3 Line Heights
- Headings: 1.2
- Body text: 1.6
- Small text: 1.4
- Stat numbers: 1.0

---

## SECTION 4: SPACING SYSTEM (4px Base Unit)

| Token    | Value | Usage                           |
|---------|-------|----------------------------------|
| --sp-1  | 4px   | Icon gaps, inline spacing        |
| --sp-2  | 8px   | Small padding, tight gaps        |
| --sp-3  | 12px  | Default padding, list items      |
| --sp-4  | 16px  | Card padding, section gaps       |
| --sp-5  | 20px  | Generous padding                 |
| --sp-6  | 24px  | Section separators               |
| --sp-8  | 32px  | Page section gaps                |
| --sp-10 | 40px  | Hero section padding             |
| --sp-12 | 48px  | Touch target minimum height      |

### Border Radius
| Token          | Value  | Usage                  |
|---------------|--------|-------------------------|
| --radius-sm   | 6px    | Badges, pills           |
| --radius-md   | 12px   | Buttons, inputs         |
| --radius-lg   | 16px   | Cards, panels           |
| --radius-xl   | 24px   | Large cards, modals     |
| --radius-full | 9999px | Circles, avatar frames  |

---

## SECTION 5: STREAMLIT CONFIG (.streamlit/config.toml)

```toml
[theme]
base = "light"
font = "sans serif"

[theme.light]
primaryColor = "#FF6B35"
backgroundColor = "#F8F9FE"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1A1A2E"

[theme.dark]
primaryColor = "#FF8F65"
backgroundColor = "#0F0F1A"
secondaryBackgroundColor = "#1A1A2E"
textColor = "#E8E8F0"

[server]
maxUploadSize = 50
enableCORS = false
headless = true

[browser]
gatherUsageStats = false
```

---

## SECTION 6: LIGHT / DARK MODE TOGGLE

### 6.1 Theme Toggle Component (components/theme_toggle.py)

```python
import streamlit as st

def render_theme_toggle():
    if 'theme' not in st.session_state:
        st.session_state['theme'] = 'light'

    current = st.session_state['theme']
    icon = "🌙" if current == 'light' else "☀️"
    label = "Dark" if current == 'light' else "Light"
    
    if st.button(f"{icon} {label}", key="theme_toggle", use_container_width=True):
        st.session_state['theme'] = 'dark' if current == 'light' else 'light'
        st.rerun()

def get_theme_class():
    return st.session_state.get('theme', 'light')
```

### 6.2 CSS Injection (in app.py)

```python
import streamlit as st
import os

def inject_styles():
    theme = st.session_state.get('theme', 'light')
    css_path = os.path.join("assets", "css", "styles.css")
    
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            css_content = f.read()
    
    st.markdown(f"""
    <style>{css_content}</style>
    <script>
        document.documentElement.setAttribute('data-theme', '{theme}');
        var app = document.querySelector('.stApp');
        if (app) app.setAttribute('data-theme', '{theme}');
    </script>
    """, unsafe_allow_html=True)
```


---

## SECTION 7: COMPLETE CSS FILE (assets/css/styles.css)

Generate this ENTIRE CSS file with complete, production-ready rules. The CSS must include:

### 7.1 CSS Custom Properties
- `:root` and `[data-theme="light"]` with ALL light mode tokens from Section 2.1
- `[data-theme="dark"]` with ALL dark mode tokens from Section 2.2
- Font variables, spacing variables, radius variables, transition variables

### 7.2 Global Resets & Base Styles
- `.stApp` background color, font family, color, transition
- `.block-container` responsive padding (mobile: 12px, tablet: 24px, desktop: 32px; max-width: 100%/960px/1200px)
- Heading styles (h1-h6) using --font-heading, responsive sizes
- Body text using --font-body

### 7.3 Sidebar Styles
- `section[data-testid="stSidebar"]` with gradient background (dark sidebar in both themes)
- Sidebar text color: white/light
- Sidebar radio labels: 15px font, 48px min-height, rounded, hover effect
- Sidebar dividers: subtle white opacity

### 7.4 Button Styles
- `.stButton > button` base: 48px min-height, rounded-md, font-body, 600 weight, transition
- Primary: gradient-primary background, white text, shadow, hover translateY(-2px)
- Secondary: transparent bg, accent-primary border, accent-primary text, hover fills light
- Active state: translateY(0)
- Success variant: gradient-success
- Danger variant: error color

### 7.5 Form Inputs
- Text inputs, text areas, selects, number inputs
- bg-tertiary background, border-light border, radius-md, 48px min-height
- Focus: border-focus color, box-shadow glow ring (3px), no outline
- Dark mode: appropriate dark colors

### 7.6 Stat Cards (4 variants: primary/success/warning/info)
- `.stat-card` class: bg-secondary, radius-lg, shadow-sm, border-light, center text
- Hover: translateY(-4px), shadow-md
- `.stat-icon`: 32px emoji
- `.stat-number`: font-heading, 32px mobile / 40px desktop, 800 weight
- `.stat-label`: 13px, text-secondary, uppercase, letter-spacing
- Color variants with left border: primary=accent-primary, success=success, etc.

### 7.7 Course Cards
- `.course-card`: bg-secondary, radius-lg, overflow hidden, shadow-sm, hover lift
- `.thumbnail`: 140px mobile / 160px desktop, object-fit cover, gradient fallback
- `.card-body`: padding 16px
- `.card-title`: font-heading, 16px, 600 weight, truncate
- `.card-meta`: flex, 12px, text-secondary
- Difficulty badges (.badge-easy/.badge-medium/.badge-hard): colored pills

### 7.8 Progress Bars
- `.progress-container`: bg-tertiary, radius-full, 12px height
- `.progress-bar`: gradient-success, animated shimmer effect (pseudo-element sliding)
- `.progress-label`: 12px, right-aligned, font-weight 700
- @keyframes shimmer animation

### 7.9 Badge Showcase
- `.badge-grid`: CSS grid, auto-fill minmax(75px mobile, 90px desktop)
- `.badge-item`: centered, padding 12px, radius-lg, border, hover scale(1.05) + golden glow
- `.badge-item.locked`: opacity 0.35, grayscale
- `.badge-emoji`: 36px mobile / 42px desktop
- `.badge-name`: 10px, uppercase, letter-spacing

### 7.10 Streak Display
- `.streak-card`: gradient-streak background, radius-xl, white text, relative, overflow hidden
- Radial glow animation (::before pseudo-element, scale pulsing)
- `.streak-number`: font-heading, 48px mobile / 56px desktop
- `.streak-fire`: inline-block with flame animation (rotate + scale alternating)
- @keyframes flame, @keyframes streak-glow

### 7.11 Leaderboard
- `.leaderboard-row`: flex, gap 12px, padding 12px 16px, radius-md, border-bottom, hover bg-hover
- `.leaderboard-row.current-user`: accent-primary-light bg, accent-primary border, bold
- `.leaderboard-rank`: font-heading, 20px, 40px width, centered
- `.leaderboard-points`: font-heading, 700 weight, accent-primary color

### 7.12 Timeline / Social Feed (Facebook-style)
- `.timeline-post`: bg-secondary, radius-lg, padding 16px, shadow-sm, border, hover shadow-md
- `.post-header`: flex, gap 12px, avatar (40px circle, gradient bg, emoji centered)
- `.post-author`: 14px, 700 weight
- `.post-time`: 12px, text-tertiary
- `.post-content`: 15px, line-height 1.6
- `.post-media`: radius-md, overflow hidden, max-height 400px, img object-fit cover
- `.post-actions`: flex, gap 16px, top-border separator
- `.reaction-btn`: no bg, no border, cursor pointer, hover bg-hover + accent-primary color
- `.reaction-btn.active`: accent-pink color
- `.timeline-post.achievement`: special border (accent-fun), gradient bg tint
- `.comment-item`: flex, gap 8px, bg-tertiary, radius-md, padding 8px

### 7.13 Video Player
- `.video-container`: relative, 56.25% padding-bottom (16:9), overflow hidden, radius-lg
- Absolutely positioned iframe/video: 100% width and height

### 7.14 Certificate Preview
- `.certificate-card`: golden border (3px #FFD700), radius-xl, gradient bg (warm), centered
- Dark mode variant with darker warm tones
- Decorative emoji (::before pseudo with 🎓, large, semi-transparent)

### 7.15 Homework Card
- `.homework-card`: flex, gap 16px, radius-lg, shadow-sm, hover translateX(4px)
- `.hw-icon`: 48px square, radius-md, centered emoji, info-light bg
- `.hw-title`: 15px, 700 weight, truncate
- `.hw-due`: 12px, text-secondary; `.hw-due.overdue`: error color, bold
- `.download-btn`: accent-secondary bg, white text, radius-md, 48px min-height, hover lift

### 7.16 Quiz Card & Timer
- `.quiz-card`: bg-secondary, radius-lg, shadow-sm, purple left-border (4px)
- `.quiz-timer`: inline-flex, error-light bg, error text, mono font, 16px, pulsing animation
- @keyframes timer-pulse

### 7.17 Toast Notifications
- `.toast`: fixed position, top-right, z-index 10000, radius-lg, shadow-lg, slide-in animation
- `.toast.success/.error/.warning/.info`: colored backgrounds
- @keyframes slide-in-right

### 7.18 Welcome Banner
- `.welcome-banner`: gradient-header bg, radius-xl, white text, decorative circle (::after)
- `.welcome-text`: font-heading, 22px mobile / 28px desktop
- `.welcome-sub`: 14px, opacity 0.9

### 7.19 Announcement Cards
- `.announcement-card`: bg-secondary, radius-lg, colored left-border (4px)
- Variants: .urgent (error), .high (warning), .medium (info), .low (tertiary)

### 7.20 Empty State
- `.empty-state`: centered, padded, tertiary color
- `.empty-icon`: 64px emoji, `.empty-title`: font-heading 18px, `.empty-desc`: 14px max-width 300px

### 7.21 Animations Library (all @keyframes)
- `confetti-fall`: translateY(-100vh to 100vh) + rotate + opacity fade
- `shimmer`: translateX sliding highlight
- `streak-glow`: scale pulsing radial gradient
- `flame`: scale + rotate alternating
- `pulse`: scale 1 to 1.08
- `bounce`: translateY with easing
- `fade-in`: opacity 0 to 1 + translateY(10px to 0)
- `slide-up`: opacity 0 to 1 + translateY(30px to 0)
- `slide-in-right`: translateX(100% to 0)
- `shake`: translateX(-4px to 4px)
- `spin`: rotate 0 to 360deg
- `timer-pulse`: opacity 1 to 0.7

### 7.22 Streamlit-Specific Overrides
- `div[data-testid="stMetric"]`: bg-secondary, border, radius-lg, shadow
- `.stTabs [data-baseweb="tab-list"]`: bg-tertiary, radius-full, small padding
- `.stTabs [data-baseweb="tab"][aria-selected="true"]`: accent-primary bg, white text
- `.streamlit-expanderHeader`: font-heading, bg-secondary, border, radius-lg
- `.stDataFrame`: radius-lg, overflow hidden, border
- `section[data-testid="stFileUploader"]`: dashed border, bg-tertiary, hover accent-primary

### 7.23 Custom Scrollbar
- `::-webkit-scrollbar`: 6px width
- `scrollbar-track`: bg-tertiary
- `scrollbar-thumb`: text-tertiary, radius-full, hover text-secondary

### 7.24 Accessibility
- `@media (prefers-reduced-motion: reduce)`: disable all animations
- `*:focus-visible`: 3px solid border-focus outline, 2px offset

### 7.25 Header Bar
- `.app-header`: gradient-header, flex between, radius bottom-xl, white text
- `.logo`: font-heading, 20px mobile / 24px desktop, flex with gap

### 7.26 Theme Toggle Button
- `.theme-toggle`: white/15% opacity bg, radius-full, 40px min size, hover rotate(20deg)

### 7.27 Weekly Goal Ring (SVG-based)
- `.goal-ring`: 120px square, relative
- `.ring-bg`: no fill, bg-tertiary stroke, 8px width
- `.ring-progress`: accent-tertiary stroke, rounded cap, animated dashoffset
- `.ring-text`: absolute centered, font-heading 24px

### 7.28 Print Styles
- `@media print`: white bg, hide sidebar/buttons/header, certificate card no shadow

### 7.29 Daily Reward Button
- `.daily-reward-btn`: gradient-streak, radius-xl, font-heading 18px, pulse animation, glow shadow

### 7.30 Responsive Breakpoints Summary
- Mobile (<768px): Single column, 12px side padding, smaller type, stacked cards
- Tablet (768-1024px): 2 columns, 24px padding, medium type
- Desktop (>1024px): Sidebar + main, 32px padding, full type, max-width 1200px

---

## SECTION 8: PYTHON COMPONENT HELPERS

Generate these reusable Python functions that produce HTML using st.markdown():

### 8.1 render_stat_card(icon, number, label, variant)
- Produces a `.stat-card` div with icon, number, label
- variant: 'primary' | 'success' | 'warning' | 'info'

### 8.2 render_progress_bar(percentage, label)
- Produces `.progress-container` with `.progress-bar` at given width percentage
- Shows label with percentage text

### 8.3 render_welcome_banner(name, streak, points)
- Produces `.welcome-banner` with greeting, streak fire emoji, points display

### 8.4 render_timeline_post(author, avatar, time_ago, content, reactions, comments, is_achievement)
- Produces full `.timeline-post` card with header, content, reactions bar, comments

### 8.5 trigger_confetti()
- Generates 40 `.confetti-piece` divs with random colors, positions, delays
- Uses colors: #FF6B35, #4361EE, #00C9A7, #FFD93D, #FF6B6B, #7C3AED

### 8.6 render_badge_item(emoji, name, is_locked)
- Produces a single `.badge-item` div, with `.locked` class if not earned

### 8.7 render_streak_card(current_streak, longest_streak)
- Produces `.streak-card` with fire emoji, current number, longest record

### 8.8 render_homework_card(title, due_date, hw_type, is_overdue)
- Produces `.homework-card` with icon, title, due date, download button

---

## SECTION 9: IMPLEMENTATION CHECKLIST

```
[ ] Create assets/css/styles.css with ALL CSS rules from Section 7
[ ] Create .streamlit/config.toml with dual theme from Section 5
[ ] Create components/theme_toggle.py from Section 6.1
[ ] Add inject_styles() to app.py from Section 6.2
[ ] Create all component helper functions from Section 8
[ ] Test light mode on mobile (Chrome DevTools 375px width)
[ ] Test dark mode toggle — smooth, no FOUC
[ ] Test all stat cards, course cards, progress bars render correctly
[ ] Test streak animation plays smoothly
[ ] Test confetti triggers on achievement events
[ ] Test sidebar menu items have 48px+ touch targets
[ ] Test form inputs have visible focus states
[ ] Test text contrast meets WCAG AA (4.5:1 body, 3:1 large text)
[ ] Test badge grid wraps on small screens
[ ] Test timeline posts with and without media
[ ] Test video container 16:9 ratio on all screens
[ ] Test certificate card prints cleanly
[ ] Test reduced-motion media query disables animations
[ ] Verify no horizontal scroll on mobile
[ ] Verify Google Fonts load (Fredoka + Nunito)
```

---

## SECTION 10: FINAL INSTRUCTION TO AI AGENT

Generate the COMPLETE `assets/css/styles.css` file implementing EVERY rule from Section 7 (all 30 sub-sections). Every CSS rule, every animation, every responsive breakpoint must be present and functional.

Generate the COMPLETE `components/theme_toggle.py` from Section 6.1.
Generate the COMPLETE `inject_styles()` function from Section 6.2.
Generate ALL 8 component helper functions from Section 8.
Generate the COMPLETE `.streamlit/config.toml` from Section 5.

The CSS file must be self-contained — no external dependencies except Google Fonts.
Every color token must match the palettes in Section 2. Both light and dark themes must work.
The design must look professional, kid-friendly, and match the quality of PW CuriousJr and Duolingo.

**No placeholders. No TODOs. Production-ready. Every line of CSS must be present.**
