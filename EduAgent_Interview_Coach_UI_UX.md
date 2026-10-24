# EduAgent Interview Coach
## UI/UX Design System & Theme Specification

**File name:** `EduAgent_Interview_Coach_UI_UX.md`  
**Version:** 1.0  
**Status:** LOCKED — Design baseline  
**Date:** 21 October 2026  
**Applies to:** All screens, components, states, and future UI extensions in version 1.

---

# 1. Design Identity

## 1.1 Theme name: Focused Intelligence

EduAgent Interview Coach uses a professional, light-first interface built around clarity, focused learning, and trustworthy feedback.

The visual identity should communicate:

- **Intelligence:** Structured information and clear hierarchy.
- **Focus:** Minimal distractions while answering interview questions.
- **Trust:** Transparent scores and understandable feedback.
- **Progress:** Visible learning milestones without excessive gamification.
- **Professionalism:** A polished environment suitable for students, mentors, and hackathon judges.

## 1.2 Design principles

1. Content is more important than decoration.
2. One primary action should dominate each screen.
3. Questions and answers must be easy to read.
4. Feedback must distinguish strengths, gaps, and corrections.
5. Scores must never rely on color alone.
6. AI activity must be transparent and accurately labelled.
7. Spacing, alignment, and typography must remain consistent.
8. Avoid unnecessary animation, gradients, glassmorphism, and decorative elements.

## 1.3 Locked visual direction

<box gap={3}>
  <row align=start gap={3}>
    <AsyncImage query="minimal professional SaaS dashboard light ivory white background dark navy typography cobalt blue accent clean cards" aspectRatio="4:3" width="124px" />
    <box flex="1" gap={1}>
      **Primary appearance**

      Light theme, warm off-white background, white content surfaces, dark navy text, and cobalt blue interactive accents.
    </box>
  </row>
  <divider color="subtle" />
  <row align=start gap={3}>
    <AsyncImage query="minimal education dashboard interface progress indicator assessment feedback cards green success amber warning clean typography" aspectRatio="4:3" width="124px" />
    <box flex="1" gap={1}>
      **Learning experience**

      Calm feedback cards, subtle progress indicators, clear status labels, and restrained semantic colors.
    </box>
  </row>
  <divider color="subtle" />
  <row align=start gap={3}>
    <AsyncImage query="modern minimal coding interview practice interface centered question panel large readable text clean white navy blue design" aspectRatio="4:3" width="124px" />
    <box flex="1" gap={1}>
      **Interview workspace**

      A centered question area, generous reading space, a clear answer editor, and an obvious submit action.
    </box>
  </row>
</box>

These images are visual references for the general direction, not pixel-perfect product mockups. The specifications below define the actual design.

# 2. Locked Color System

All colors must use the following tokens. Do not introduce additional ad hoc colors into individual screens.

## 2.1 Brand palette

<grid columns={2} gap={3}>
  <grid-item>
    <box background="#172554" radius="lg" padding={3} gap={2}>
      <box background="#172554" height="42px" radius="md" />
      <text color="#FFFFFF" weight="medium">Deep Navy</text>
      <text color="#FFFFFF" size="sm">#172554</text>
      <text color="#FFFFFF" size="xs">Brand identity, headings, primary text accents</text>
    </box>
  </grid-item>
  <grid-item>
    <box background="#315EFB" radius="lg" padding={3} gap={2}>
      <box background="#315EFB" height="42px" radius="md" />
      <text color="#FFFFFF" weight="medium">Cobalt Blue</text>
      <text color="#FFFFFF" size="sm">#315EFB</text>
      <text color="#FFFFFF" size="xs">Primary buttons, links, focus indicators</text>
    </box>
  </grid-item>
  <grid-item>
    <box background="#E9EEFF" radius="lg" padding={3} gap={2}>
      <box background="#E9EEFF" height="42px" radius="md" />
      <text color="#172554" weight="medium">Pale Blue</text>
      <text color="#172554" size="sm">#E9EEFF</text>
      <text color="#172554" size="xs">Selected items, subtle brand surfaces</text>
    </box>
  </grid-item>
  <grid-item>
    <box background="#0F172A" radius="lg" padding={3} gap={2}>
      <box background="#0F172A" height="42px" radius="md" />
      <text color="#FFFFFF" weight="medium">Ink</text>
      <text color="#FFFFFF" size="sm">#0F172A</text>
      <text color="#FFFFFF" size="xs">Main text and high-emphasis content</text>
    </box>
  </grid-item>
</grid>

## 2.2 Surface and text tokens

| Token | Hex | Usage |
|---|---|---|
| `canvas` | `#F6F7FB` | Main application background |
| `surface` | `#FFFFFF` | Cards, panels, input backgrounds |
| `surface-subtle` | `#F1F4F9` | Secondary sections and neutral panels |
| `surface-selected` | `#E9EEFF` | Selected navigation and active items |
| `border` | `#E2E8F0` | Card borders and dividers |
| `border-strong` | `#CBD5E1` | Input borders and emphasized outlines |
| `text-primary` | `#0F172A` | Main content |
| `text-secondary` | `#475569` | Descriptions and secondary information |
| `text-muted` | `#64748B` | Supporting metadata and timestamps |
| `text-on-brand` | `#FFFFFF` | Text on primary brand surfaces |

## 2.3 Semantic status colors

These colors communicate meaning and must not be used merely for decoration.

<box gap={2}>
  <row align="center" gap={3}>
    <box background="#15803D" radius="md" size="44px" align="center" justify="center">
      <icon name="check" color="#FFFFFF" size="xl" />
    </box>
    <box flex="1" gap={1}>
      **Success — `#15803D`**

      <text color="secondary" size="sm">Correct points, completed steps, demonstrated concepts.</text>
    </box>
    <text color="secondary" size="sm">Green</text>
  </row>
  <row align="center" gap={3}>
    <box background="#B45309" radius="md" size="44px" align="center" justify="center">
      <icon name="alert-triangle" color="#FFFFFF" size="xl" />
    </box>
    <box flex="1" gap={1}>
      **Warning — `#B45309`**

      <text color="secondary" size="sm">Missing concepts, partial answers, cautionary feedback.</text>
    </box>
    <text color="secondary" size="sm">Amber</text>
  </row>
  <row align="center" gap={3}>
    <box background="#B91C1C" radius="md" size="44px" align="center" justify="center">
      <icon name="x-circle" color="#FFFFFF" size="xl" />
    </box>
    <box flex="1" gap={1}>
      **Error — `#B91C1C`**

      <text color="secondary" size="sm">Invalid submissions, critical errors, failed operations.</text>
    </box>
    <text color="secondary" size="sm">Red</text>
  </row>
  <row align="center" gap={3}>
    <box background="#0369A1" radius="md" size="44px" align="center" justify="center">
      <icon name="info" color="#FFFFFF" size="xl" />
    </box>
    <box flex="1" gap={1}>
      **Information — `#0369A1`**

      <text color="secondary" size="sm">Hints, explanatory messages, neutral guidance.</text>
    </box>
    <text color="secondary" size="sm">Blue</text>
  </row>
</box>

Use tinted backgrounds for semantic cards:

| Status | Background | Text |
|---|---|---|
| Success | `#F0FDF4` | `#166534` |
| Warning | `#FFFBEB` | `#92400E` |
| Error | `#FEF2F2` | `#991B1B` |
| Information | `#EFF6FF` | `#1E40AF` |

## 2.4 Color usage rules

- Cobalt blue is the only primary action color.
- Deep navy is the main brand and heading color.
- Green indicates a positive state, not a high score by itself.
- Amber indicates an incomplete or cautionary state, not a failure.
- Red is reserved for errors and significant misconceptions.
- Gray is used for neutral information.
- Never color an entire page with a semantic status color.
- Never communicate correctness through color alone; always include text or an icon.
- Avoid gradients in the interface, including the main header and buttons.

# 3. Typography System

## 3.1 Locked fonts

<box border radius="xl" padding={4} gap={3}>
  <box gap={1}>
    <text color="secondary" size="xs">PRIMARY UI FONT</text>
    <title size="2xl">Inter</title>
    <text color="secondary" size="sm">Interface, navigation, buttons, forms, labels, feedback and reports.</text>
  </box>
  <divider color="subtle" />
  <box gap={1}>
    <text color="secondary" size="xs">TECHNICAL CONTENT FONT</text>
    <title size="xl">JetBrains Mono</title>
    <text color="secondary" size="sm">Code snippets, operation names, complexity expressions, and technical examples.</text>
  </box>
</box>

Font stacks:

- Interface: `Inter, ui-sans-serif, system-ui, sans-serif`
- Technical content: `JetBrains Mono, ui-monospace, monospace`

Use Inter as the default. Use the technical font sparingly, only when it improves readability.

## 3.2 Type scale

| Element | Size | Weight | Line height |
|---|---:|---:|---:|
| Main page title | 30 px | 700 | 38 px |
| Section title | 24 px | 650 | 32 px |
| Card title | 18 px | 600 | 26 px |
| Question text | 22 px | 500–600 | 34 px |
| Body text | 15 px | 400 | 24 px |
| Button text | 14 px | 600 | 20 px |
| Form label | 14 px | 600 | 20 px |
| Supporting text | 13 px | 400 | 19 px |
| Metadata | 12 px | 500 | 16 px |
| Technical text | 13–14 px | 400–500 | 21 px |

### Typography rules

1. Do not use more than four text sizes in a single content section.
2. Use sentence case, not all-uppercase headings.
3. Use bold for emphasis, not entire paragraphs.
4. Keep question text comfortably readable.
5. Avoid light font weights for essential information.
6. Do not use decorative or handwritten fonts.
7. Avoid long lines of text; aim for approximately 60–80 characters per line in reading-heavy areas.

# 4. Spacing and Layout System

## 4.1 Base spacing scale

Use an **8 px base rhythm** with 4 px for compact adjustments.

| Token | Value | Intended use |
|---|---:|---|
| `space-1` | 4 px | Icon-to-label spacing, tiny adjustments |
| `space-2` | 8 px | Compact internal gaps |
| `space-3` | 12 px | Input label spacing and tight groups |
| `space-4` | 16 px | Standard component gaps |
| `space-5` | 20 px | Card content separation |
| `space-6` | 24 px | Standard card padding |
| `space-8` | 32 px | Section separation |
| `space-10` | 40 px | Major content separation |
| `space-12` | 48 px | Page section spacing |
| `space-16` | 64 px | Large desktop-only separation |

Use these values consistently. Avoid arbitrary spacing values unless required by a specific component.

## 4.2 Page layout

- Main page background: `#F6F7FB`.
- Desktop content maximum width: `1200 px`.
- Standard page horizontal padding: `32 px`.
- Tablet horizontal padding: `24 px`.
- Mobile horizontal padding: `16 px`.
- Header height: `64 px`.
- Standard card padding: `24 px`.
- Compact card padding: `16 px`.
- Major section gap: `32 px`.
- Standard component gap: `16 px`.

## 4.3 Grid and columns

- Desktop: use a centered content container with a maximum width of 1200 px.
- Tablet: reduce horizontal padding and keep content readable.
- Mobile: use a single-column layout.
- The main interview question should receive more space than secondary information.
- Never force the answer editor into a narrow sidebar.
- On small screens, stack the question, answer editor, feedback, and supporting panels vertically.

# 5. Shape, Borders, and Shadows

## 5.1 Border-radius scale

| Component | Radius |
|---|---:|
| Small labels and chips | 6 px |
| Input fields | 8 px |
| Buttons | 8 px |
| Standard cards | 12 px |
| Main content panels | 16 px |
| Dialogs and large overlays | 16 px |
| Circular icons or avatars | 50% |

**Locked rule:** Do not use pill-shaped buttons throughout the application. Use rounded rectangles to maintain a professional software-product appearance.

## 5.2 Borders

- Standard border: `1 px solid #E2E8F0`.
- Emphasized border: `1 px solid #CBD5E1`.
- Selected border: `1 px solid #315EFB`.
- Avoid thick decorative borders.
- Use borders to define structure, not to highlight every element.

## 5.3 Shadows

Use very subtle shadows only for floating elements, dropdowns, and dialogs.

- Cards: no shadow by default.
- Hovered interactive cards: a subtle shadow and/or border change.
- Dialogs and dropdowns: soft shadow.
- Do not use strong shadows around every card.
- Do not use glassmorphism or glowing effects.

# 6. Icon System

## 6.1 Icon library

Use **Lucide-style outline icons** consistently.

All icons must follow the same visual style. Do not mix outline icons with colorful emoji, filled cartoon icons, and unrelated icon libraries.

## 6.2 Icon sizes

| Context | Size |
|---|---:|
| Inline status | 14–16 px |
| Button icon | 16 px |
| Navigation icon | 20 px |
| Card illustration icon | 24 px |
| Empty-state illustration | 32 px |

Default stroke width: approximately 2 px.

## 6.3 Approved icon mapping

| Meaning | Icon |
|---|---|
| Application identity | `brain-circuit` |
| Dashboard or home | `layout-dashboard` |
| Interview | `messages-square` |
| Question | `circle-help` |
| Submit answer | `arrow-up` |
| Hint | `lightbulb` |
| Progress | `chart-no-axes-column-increasing` |
| Correct answer | `check-circle-2` |
| Missing concept | `alert-circle` |
| Error | `x-circle` |
| Information | `info` |
| Time | `clock-3` |
| Settings | `settings-2` |
| Report | `file-text` |
| Restart | `rotate-ccw` |
| Next question | `arrow-right` |
| AI evaluation | `sparkles` |
| Local evaluation | `shield-check` |
| External service | `cloud` |
| Expand details | `chevron-down` |
| Collapse details | `chevron-up` |

Use the nearest available Lucide icon if a named icon is unavailable, but maintain the same outline style and meaning.

## 6.4 Icon rules

- Every icon-only button must have an accessible label.
- Do not use an icon to replace an unclear text label.
- Do not use emojis as application controls.
- Use semantic status icons alongside text.
- Do not decorate every heading with an icon.

# 7. Buttons and Actions

## 7.1 Primary button

Used for the most important action on a screen.

Examples: `Start interview`, `Submit answer`, `View report`.

- Background: `#315EFB`
- Text: `#FFFFFF`
- Height: 44 px
- Horizontal padding: 16 px
- Radius: 8 px
- Font: Inter, 14 px, weight 600

Hover: `#254DE5`

Pressed: `#1D43CB`

Disabled: `#DCE3F5` background with `#64748B` text.

## 7.2 Secondary button

Used for helpful but non-primary actions.

- Background: `#FFFFFF`
- Text: `#172554`
- Border: `1 px solid #CBD5E1`
- Height: 44 px
- Radius: 8 px

Hover: `#F1F4F9`

## 7.3 Tertiary button

Used for low-emphasis actions such as `Cancel`, `Back`, or `Skip`.

- Background: transparent.
- Text: `#475569`.
- No prominent border.
- Height: 40–44 px.

## 7.4 Destructive button

Use only for actions that discard or clear meaningful information.

- Background: `#B91C1C`.
- Text: `#FFFFFF`.
- Require confirmation when an action could discard an active session.

## 7.5 Button behavior

- Only one visually dominant primary action per screen.
- Buttons must have clear hover, focus, pressed, disabled, and loading states.
- Show a loading indicator when an operation is genuinely in progress.
- Prevent duplicate submission while an answer is being evaluated.
- Never display a successful state before the action has actually succeeded.

# 8. Form and Answer Editor

## 8.1 Text input styling

- Background: `#FFFFFF`.
- Border: `1 px solid #CBD5E1`.
- Radius: 8 px.
- Padding: 12 px.
- Text size: 15 px.
- Minimum height for single-line inputs: 44 px.

Focus state:

- Border: `#315EFB`.
- Visible focus ring: `0 0 0 3px rgba(49, 94, 251, 0.16)`.

Error state:

- Border: `#B91C1C`.
- Error text: `#991B1B`.
- Include a short message explaining how to resolve the error.

## 8.2 Interview answer editor

The answer editor is one of the most important components in the product.

- Full width of the primary question panel.
- Minimum height: 180 px on desktop.
- Minimum height: 160 px on mobile.
- Text size: 15 px.
- Line height: 24 px.
- Padding: 16 px.
- Background: `#FFFFFF`.
- Border: `#CBD5E1`.
- Radius: 12 px.

Placeholder:

> Explain your answer step by step. Include the key concepts and reasoning.

The placeholder must disappear or become unobtrusive when the student begins typing.

## 8.3 Input interaction rules

- Preserve the answer during normal interface reruns.
- Display a clear message for empty submissions.
- Avoid unnecessary character restrictions.
- Keep the submit action near the editor.
- If evaluation fails, preserve the answer so the student does not need to retype it.
- Do not clear the answer before a successful submission has been recorded.

# 9. Card System

## 9.1 Standard content card

- Background: `#FFFFFF`.
- Border: `1 px solid #E2E8F0`.
- Radius: 12 px.
- Padding: 24 px.
- Gap between internal elements: 16 px.

Use standard cards for questions, progress summaries, and reports.

## 9.2 Question card

- Background: `#FFFFFF`.
- Border: `1 px solid #E2E8F0`.
- Radius: 16 px.
- Padding: 32 px on desktop and 20 px on mobile.
- Question text: 22 px.
- Metadata appears above the question, not mixed into its main text.
- Avoid decorative illustrations inside the question area.

## 9.3 Feedback card

Use separate sections for:

- What was correct.
- What was missing.
- What needs correction.
- Recommended next step.

Each section should have a short heading and concise content.

Avoid placing all feedback into one large block of undifferentiated text.

## 9.4 Card interaction

Only cards that actually perform an action should look clickable.

Clickable cards must have a hover state and keyboard focus state. Static information cards must not imitate buttons.

# 10. Status Labels and Badges

Use compact badges for question difficulty, evaluation mode, and progress state.

| Badge | Appearance |
|---|---|
| Easy | Pale green background, dark green text |
| Medium | Pale amber background, dark amber text |
| Hard | Pale red background, dark red text |
| Local evaluation | Neutral gray background, dark navy text |
| AI evaluation | Pale blue background, dark blue text |
| Completed | Pale green background, dark green text |
| In progress | Pale blue background, dark blue text |

Badge height: approximately 24 px.

Horizontal padding: 8 px.

Radius: 6 px.

Text: 12 px, medium weight.

Do not use badges for every piece of metadata. Use plain text when a badge does not improve understanding.

# 11. Navigation and Header

## 11.1 Header

Height: 64 px.

Background: `#FFFFFF`.

Bottom border: `1 px solid #E2E8F0`.

Contents:

- Brand icon and product name on the left.
- Current topic or session status where useful.
- Evaluation mode indicator.
- Settings or secondary actions only if implemented.

Product name: **EduAgent Interview Coach**

Do not add navigation items for features that do not exist.

## 11.2 Brand treatment

- Icon: `brain-circuit`, 24 px.
- Icon background: `#E9EEFF`.
- Icon foreground: `#315EFB`.
- Wordmark: `#172554`, Inter, 16 px, weight 700.

Do not create different logos or color variants for different screens.

## 11.3 Navigation behavior

For the first version, keep navigation minimal. The student should be able to start, continue, and finish an interview without navigating through a complex sidebar.

If a sidebar is introduced later, use:

- Width: 240 px on desktop.
- Background: `#FFFFFF`.
- Selected item: `#E9EEFF`.
- Selected text and icon: `#315EFB`.
- Unselected text: `#475569`.

On mobile, replace the persistent sidebar with a compact navigation pattern only if the application actually needs additional destinations.

# 12. Screen-by-Screen Theme

## 12.1 Start screen

**Purpose:** Explain the product and begin a session.

Layout:
- Centered content area, maximum width approximately 880 px.
- Brand header at the top.
- Clear page title.
- Short supporting description.
- One primary interview card.
- A visible topic label: `DSA · Stacks & Queues`.
- Role label: `Junior Software Developer`.
- Evaluation mode indicator.
- Primary button: `Start interview`.

Use a white card against the `#F6F7FB` canvas.

Do not use a large animated hero, a rotating carousel, or an oversized decorative AI illustration.

## 12.2 Interview screen

**Purpose:** Keep the student's attention on the current question.

Desktop layout:
- Main content width: approximately 760–840 px.
- Progress and session metadata at the top.
- Question card.
- Answer editor directly below the question.
- Hint and submit controls underneath the editor.

Order:

1. Progress indicator.
2. Topic and difficulty.
3. Question text.
4. Answer editor.
5. Hint action.
6. Primary submit action.

The submit button should be the most visually prominent control in the answer area.

## 12.3 Feedback state

**Purpose:** Make the evaluation understandable.

Display:

1. Score and short interpretation.
2. Correct points.
3. Missing concepts.
4. Possible misconceptions, if present.
5. Recommended next step.
6. Reason for the selected follow-up.
7. Continue action.

Use semantic colors only on the relevant feedback sections. Keep the surrounding screen neutral.

A score should be displayed as `7/10`, not as a large decorative circular gauge that consumes unnecessary space.

## 12.4 Final report

**Purpose:** Help the student understand performance and what to revise.

Layout:
- Page title: `Interview report`.
- Overall score and attempts summary.
- Demonstrated concepts.
- Concepts to revisit.
- Important misconceptions.
- Recommended revision actions.
- Evaluation mode disclosure.
- Primary action: `Start new interview`.

The report must reflect actual session data. Do not show empty charts or fabricated statistics simply to make the page look more advanced.

## 12.5 Error and empty states

Error states must be calm, specific, and actionable.

Example:

**Unable to evaluate this answer**

The evaluation service did not return a valid result. Your answer is still available. You can retry or continue using local evaluation if it is available.

Buttons:
- `Retry evaluation`
- `Use local evaluation` — only if the fallback is implemented.

Do not display raw stack traces or technical credentials to the student.

# 13. Progress Indicators and Scoring

## 13.1 Progress bar

- Track session progress only when a meaningful denominator is available.
- Height: 6 px.
- Track: `#E2E8F0`.
- Fill: `#315EFB`.
- Radius: 999 px.

If the total number of questions is adaptive and unknown, show `Question 4` or `4 questions answered` rather than claiming that the session is 60% complete.

## 13.2 Score presentation

- Main score: 28–32 px, weight 700.
- Maximum score: displayed beside the score.
- Interpretation: short text beneath the score.
- Correct, incomplete, and incorrect points must be explained in text.

Do not classify students with stigmatizing labels such as “bad candidate” or “failure.”

## 13.3 Mastery status

Use these labels:

- `Demonstrated`
- `Needs practice`
- `Not yet assessed`

Do not mark a concept as mastered simply because it has been displayed or attempted.

# 14. Motion and Interaction

## 14.1 Motion policy

The interface should feel responsive but not animated for decoration.

- Button hover: 120–160 ms.
- Card hover: 150 ms.
- Small state transition: 150–200 ms.
- Avoid large page transitions.
- Avoid bouncing, pulsing, spinning decorative elements, and animated backgrounds.

A spinner is permitted only while an actual operation is in progress.

## 14.2 Loading states

During evaluation:

- Preserve the student's answer.
- Disable duplicate submission.
- Show a small spinner.
- Use status text such as `Evaluating your answer…`.
- Do not imply that an external AI call is occurring when local evaluation is running.

## 14.3 Reduced motion

If the user prefers reduced motion, avoid non-essential transitions and animations.

# 15. Responsive Design Rules

## 15.1 Breakpoints

| Device class | Width |
|---|---:|
| Mobile | Up to 639 px |
| Tablet | 640–1023 px |
| Desktop | 1024 px and above |

## 15.2 Mobile

- One-column layout.
- 16 px page padding.
- 20 px question-card padding.
- Full-width primary button where appropriate.
- Answer editor at least 160 px high.
- No horizontal scrolling.
- Stack report cards vertically.
- Keep all controls usable with touch.

## 15.3 Tablet

- 24 px page padding.
- Main content width constrained for readability.
- Two columns allowed only for compact summary sections.
- Keep the interview question and editor in the primary column.

## 15.4 Desktop

- Maximum content width: 1200 px.
- 32 px horizontal page padding.
- Question and answer area centered.
- Optional supporting panels may sit beside the main area, but must not compete with the question.

# 16. Accessibility Requirements

Target WCAG 2.2 AA principles where practical.

- Maintain readable contrast for text and controls.
- Provide visible keyboard focus.
- Ensure buttons and fields have meaningful accessible names.
- Do not communicate status through color alone.
- Use labels for input fields rather than relying only on placeholders.
- Ensure interactive targets are comfortably sized; aim for at least 44 × 44 px for primary touch controls.
- Maintain logical heading order.
- Avoid excessive motion.
- Keep feedback readable at normal browser zoom.
- Support keyboard navigation for the core interview flow.

# 17. Empty States and Microcopy

Use short, respectful, student-friendly language.

| Situation | Recommended copy |
|---|---|
| No session yet | Ready to practice? Start your Stacks and Queues interview. |
| Empty answer | Write an answer before submitting. |
| Evaluation in progress | Evaluating your answer… |
| Weak answer | Let's strengthen the fundamentals with a focused follow-up. |
| Missing concept | Your answer is partly correct. Let's revisit one important concept. |
| Strong answer | Good explanation. Let's move to the next concept. |
| Session complete | Interview complete. Review your strengths and topics to revisit. |
| Service unavailable | Evaluation is unavailable right now. Your answer has been preserved. |
| Local mode active | Using local evaluation. Feedback may be less reliable for paraphrased answers. |
| AI mode active | AI-assisted evaluation is enabled. Review feedback critically. |

Do not promise that a student's next answer will be correct or that the application will guarantee interview success.

# 18. Theme Consistency Rules

These rules are mandatory for every screen.

1. Use the locked color tokens only.
2. Use Inter for interface text and JetBrains Mono for technical snippets.
3. Use the defined spacing scale.
4. Use the approved outline icon style.
5. Keep cards white with subtle borders.
6. Keep the main background light and neutral.
7. Use cobalt blue for primary actions.
8. Use semantic colors only for meaningful states.
9. Keep the question and answer editor as the primary visual focus.
10. Use consistent component sizes across all screens.
11. Do not introduce dark mode in version 1.
12. Do not add glassmorphism, neon effects, excessive gradients, or decorative charts.
13. Do not introduce a new font, icon pack, or unrelated accent color without formally revising this document.
14. Any design revision must update this file before the revised style is implemented across the product.

# 19. Final Design Lock

The following decisions are frozen for version 1:

| Category | Locked decision |
|---|---|
| Theme name | Focused Intelligence |
| Theme mode | Light only |
| Primary brand | Deep Navy `#172554` |
| Primary action | Cobalt Blue `#315EFB` |
| Background | `#F6F7FB` |
| Card surface | `#FFFFFF` |
| Main text | `#0F172A` |
| Secondary text | `#475569` |
| Font | Inter |
| Technical font | JetBrains Mono |
| Icon style | Lucide-style outline |
| Spacing system | 4 px adjustment + 8 px base rhythm |
| Standard card radius | 12 px |
| Main question card radius | 16 px |
| Standard control height | 44 px |
| Primary layout | Centered, single-column interview workspace |
| Desktop content maximum | 1200 px |
| Motion | Subtle and functional |
| Design personality | Calm, precise, professional, student-friendly |

## Final instruction

Treat this document as the single source of truth for the application's visual design. Implement the design consistently rather than redesigning individual screens independently.

Any proposed change to the palette, typography, spacing system, icon family, or overall visual direction must be reviewed as a design-system change—not introduced as an isolated styling adjustment.