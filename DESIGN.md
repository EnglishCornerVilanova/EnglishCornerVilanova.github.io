---
name: English Corner
description: Website of a small English school in Vilanova del Camí, in Catalan, Spanish and British English.
colors:
  union-red: "#E8192C"
  union-red-ink: "#B8121F"
  union-navy: "#012169"
  ink: "#12151C"
  ink-soft: "#3D4351"
  ink-muted: "#646B78"
  hairline: "#E8E4DE"
  paper: "#FFFFFF"
  pearl: "#F2F2F0"
  pearl-deep: "#E6E6E2"
  marker-pink: "#FFCBD1"
  red-soft: "#FF6B7A"
  open-green: "#4ADE80"
  level-a2: "#5CC98F"
  level-b1: "#5B8DEF"
  level-b2: "#F5A623"
  tone-mint: "#E6F6EC"
  tone-mint-ink: "#1E7A4C"
  tone-sun: "#FFF3D9"
  tone-sun-ink: "#8A5B00"
  tone-sky: "#E3F4FB"
  tone-sky-ink: "#0B5C7A"
  tone-rose: "#FCE8F1"
  tone-rose-ink: "#9B1F55"
typography:
  display:
    fontFamily: "Bricolage Grotesque, sans-serif"
    fontSize: "clamp(2.05rem, 3.4vw, 2.9rem)"
    fontWeight: 800
    lineHeight: 0.98
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "Bricolage Grotesque, sans-serif"
    fontWeight: 800
    lineHeight: 1.06
    letterSpacing: "-0.03em"
  title:
    fontFamily: "Bricolage Grotesque, sans-serif"
    fontSize: "clamp(1.25rem, 2.1vw, 1.65rem)"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.025em"
  body:
    fontFamily: "Instrument Sans, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Instrument Sans, sans-serif"
    fontSize: "0.78rem"
    fontWeight: 700
    letterSpacing: "-0.005em"
  logotype:
    fontFamily: "Special Elite, serif"
    fontSize: "0.9rem"
    lineHeight: 1.1
rounded:
  polaroid: "5px"
  step: "20px"
  panel: "36px"
  pill: "100px"
spacing:
  gutter: "clamp(1.5rem, 5vw, 5.5rem)"
  section: "clamp(5rem, 11vh, 9rem)"
components:
  button-primary:
    backgroundColor: "{colors.union-red}"
    textColor: "{colors.paper}"
    rounded: "{rounded.pill}"
    padding: "11px 11px 11px 20px"
  button-navy:
    backgroundColor: "{colors.union-navy}"
    textColor: "{colors.paper}"
    rounded: "{rounded.pill}"
    padding: "11px 11px 11px 20px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "12px 22px"
  chip-level:
    backgroundColor: "{colors.tone-sky}"
    textColor: "{colors.tone-sky-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "6px 13px"
  card-step:
    backgroundColor: "{colors.paper}"
    rounded: "{rounded.step}"
    padding: "1.5rem 1.4rem"
  photo-polaroid:
    backgroundColor: "{colors.paper}"
    rounded: "{rounded.polaroid}"
    padding: "9px 9px 26px"
---

# Design System: English Corner

## Overview

**Creative North Star: "La libreta ordenada" (The Tidy Notebook)**

The site reads like a well-kept school notebook: everything has its place, levels follow one another in order, and nothing is improvised. Structure comes first. Sections are clearly separated, the exam path climbs step by step, and each course has its row. Warmth comes from what is stuck into the notebook: real photos mounted as polaroid "cromos", a pink marker stroke under the key phrase, and the red and navy of the Union Jack on pale paper.

Density is calm and generous. Most of the page is white or pearl-grey paper with dark ink, and colour is saved for meaning: red for the one action that matters, navy for trust, and soft paired tones to tell courses and levels apart. Motion is playful but controlled: a gentle bounce on buttons, cromos that lift and straighten, and content that settles into place once.

**Key Characteristics:**
- Order first: clear rows, sections and a rising staircase for the exams.
- Real photos, always whole, mounted on white card like polaroids and slightly tilted.
- Union Jack red and navy on pale paper; colour carries meaning, not decoration.
- One bold display face with a friendly, readable text face.
- A springy, tactile touch on everything you can press.

## Colors

A British-flag pair on quiet paper, with soft paired tones that label courses and levels.

### Primary
- **Union Red** (union-red): the single call to action (red buttons), the accent line of the hero claim and the C1 step. **Union Red Ink** is its darker partner, used for red text on light tones.

### Secondary
- **Union Navy** (union-navy): trust and structure: the numbers band, the navy button on the map, the B1 accent and focus rings.

### Tertiary
- **Paired Tones** (tone-mint, tone-sun, tone-sky, tone-rose, each with its ink): light background plus dark ink of the same hue for course icons, age chips and Young Learners tags. Never use a tone without its ink.
- **Level Colours** (level-a2, level-b1, level-b2, with Union Red for C1): the top edge of each step of the exam staircase.
- **Marker Pink** (marker-pink): only the hand-drawn stroke behind the last line of the hero claim.
- **Open Green** (open-green): only the dot of "Obert ara" on the dark contact panel.

### Neutral
- **Ink** (ink): headings and body text; also the dark contact panel.
- **Soft Ink** (ink-soft) and **Muted Ink** (ink-muted): secondary text and descriptions. Muted Ink is the lightest text allowed on white (4.5:1).
- **Paper** (paper) and **Pearl** (pearl, pearl-deep): page backgrounds; sections alternate between white and pearl.
- **Hairline** (hairline): 1px dividers, card borders and ghost-button outlines.

### Named Rules
**The One Red Button Rule.** Each view has one red button, and it is the action that leads to contact.

**The Tone-and-Ink Rule.** A light tone always carries text in its own dark ink, never grey or black.

## Typography

**Display Font:** Bricolage Grotesque (with sans-serif)
**Body Font:** Instrument Sans (with system-ui)
**Logotype Font:** Special Elite, only for "English Corner" next to the round brand mark

**Character:** a chunky, confident grotesque for headings paired with a clear, modern sans for reading: the headline of a school notice board over the tidy handwriting of a notebook.

### Hierarchy
- **Display** (800, clamp(2.05rem, 3.4vw, 2.9rem), 0.98): the hero claim ("Totes les àrees. Tots els nivells. Res a mitges.").
- **Headline** (800, 1.06): section headings, two or three lines with `text-wrap: balance`.
- **Title** (700, clamp(1.25rem, 2.1vw, 1.65rem), 1.1): course names and step names.
- **Body** (400, 16px, 1.6): all running text; legal pages keep lines to about 35rem.
- **Label** (700, 0.78rem): age chips and small tags.

### Named Rules
**The Balanced Heading Rule.** Headings break into balanced lines; manual line breaks are only used where the copy was written for them.

## Layout

Content sits in a centred column of up to 1180px with fluid side gutters (gutter) and generous vertical rhythm between sections (section). Sections alternate between white and pearl paper; two soft waves mark the transitions after the hero and before the contact panel. The hero stacks a brand band (logo and tagline) above a two-column grid of claim and cromo collage. Courses are full-width rows; the exam staircase is five equal columns that rise step by step on desktop and becomes an indented vertical list on phones.

Breakpoints: 600px (phone), 940/941px (tablet to desktop: burger menu below, full menu above), 1280px and 1400px for wider refinements. Nothing may scroll horizontally from 320px upwards, even with text enlarged to 200 %.

## Elevation & Depth

Depth is soft and physical, as if paper items were resting on a desk. Shadows are low-opacity, wide and pulled down (negative spread), never hard or dark. Photos and cromos cast the deepest shadows; cards cast a faint one; flat rows and dividers carry none.

### Shadow Vocabulary
- **Polaroid** (`0 2px 5px rgba(20,20,18,.07), 0 22px 42px -20px rgba(20,20,18,.4)`): mounted photos and cromos.
- **Floating bar** (`0 1px 2px rgba(18,21,28,.04), 0 8px 28px -12px rgba(18,21,28,.14)`): the navigation capsule and the Instagram follow pill.
- **Red glow** (`0 2px 4px rgba(232,25,44,.16), 0 10px 28px -10px rgba(232,25,44,.6)`): red buttons on light paper only; on the dark panel it becomes a plain dark drop shadow.

### Named Rules
**The Resting Paper Rule.** Only things that feel like paper (photos, cromos, cards) float; text blocks and rows stay flat.

## Shapes

Two families of corners. Everything you press is a full pill (100px). Everything you read inside is a soft rounded card (20px for steps and cards, up to 36px for the large contact panel). Photos break the rule on purpose: small 5px corners on a white card with a thicker bottom edge, tilted a few degrees, like a polaroid.

## Components

### Buttons
- **Shape:** full pill (100px).
- **Primary:** Union Red with white text, bold 0.84rem label and a small round arrow chip on the right.
- **Navy:** the same shape in Union Navy, for secondary actions on light panels (loading the map).
- **Ghost:** transparent with a 1.5px hairline border; on the dark panel the border is translucent white.
- **Hover / Press:** lifts 2px with a springy ease on hover, shrinks to 0.96 when pressed; focus shows a 2.5px navy outline.

### Chips
- **Style:** pill with a light tone background and its dark ink (age chips of the courses, Young Learners tags).

### Cards / Containers
- **Exam steps:** white, 20px corners, 1px hairline border and a 3px top edge in the level colour. On desktop all steps have the same height and rise evenly; the age sits at the foot of each step as a plain caption line.
- **Contact panel:** Ink background, 36px corners, white text, soft red and navy glows in the corners; on phones it flattens into a single panel with full-width buttons.

### Navigation
- **Style:** a floating white capsule with blur, round London brand mark on the left, text links in the centre, round phone and WhatsApp icons and a language menu on the right. On phones it starts transparent (only icons and burger) and becomes the capsule after scrolling; the menu opens as a full-screen sheet with compact links and four contact tiles.

### Polaroid cromos (signature component)
Real photos mounted on white card (9px sides, 26px bottom), slightly rotated. In the hero, four cromos from the original banner overlap diagonally, move with the pointer on desktop and straighten while scrolling on phones. In "Sobre nosaltres" the two school photos move at different depths when scrolling, and on desktop the one under the pointer comes to the front.

### Exam staircase (signature component)
Young Learners, A2, B1, B2 and C1 as five equal steps rising from left to right, each with its level colour on top.

## Do's and Don'ts

### Do:
- **Do** show photos whole, at their own proportions, mounted as polaroids.
- **Do** keep one red button per view and point it towards contact.
- **Do** pair every light tone with its own dark ink.
- **Do** keep the springy bounce on pressable elements; with reduced motion, replace movement with short fades.
- **Do** keep every language (Catalan, Spanish, British English) at the same visual quality; long words must be able to wrap.

### Don't:
- **Don't** crop, zoom or fill-crop photos.
- **Don't** use grey or black text on a coloured tone.
- **Don't** introduce new accent colours outside the flag pair, the paired tones and the level colours.
- **Don't** add fake testimonials, stock "happy students" imagery or invented figures.
- **Don't** call the school a shop or show it as one.
