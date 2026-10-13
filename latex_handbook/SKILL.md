---
name: thai-academic-latex-formatting
description: "Format, audit, or refine Thai academic books and textbooks written in LaTeX. Use for Thai XeLaTeX typography, book cover design and art direction (3D Pixar / High-aesthetic illustration, full-bleed TikZ layout, transparent text / glassmorphism), chapter and section layout, paragraph indentation, figure and table captions, front matter, indexes, APA 7 references, pagination, or whole-document PDF layout checks."
argument-hint: "Describe the LaTeX book, formatting rule, cover design, or layout issue to address"
user-invocable: true
---

# Thai Academic LaTeX Book Formatting & Cover Architecture

Apply a consistent, publication-oriented style to Thai academic books, textbooks, and workshop handbooks written in XeLaTeX. Inspect the project and its existing conventions first; preserve established choices unless the user requests a change. Treat the settings below as the established profile for a 6 × 9 inch (Royal Octavo) Thai academic publication.

## Workflow

1. **Inspect before editing**
   - Find the main LaTeX entry point (`main.tex`), preamble modules (`preamble/`), chapter and appendix sources, front matter, build script (`build.sh`), bibliography configuration, and generated PDF.
   - Identify the engine (XeLaTeX for Thai), document class (`book`, `report`), loaded packages, caption and heading settings, and local macros.
   - Check worktree changes and do not overwrite unrelated or user-authored edits.
   - Search for existing one-off formatting overrides before introducing a global rule.

2. **Cover design & front matter orchestration**
   - Determine cover direction: High-aesthetic illustrated cover (e.g. 3D Pixar, modern digital art) or minimalist formal vector cover.
   - Generate or source artwork strictly matching the 2:3 aspect ratio for 6 × 9 inch publications.
   - Establish a **Dual-Cover Architecture**:
     - **Outer Cover (`frontmatter/cover.tex`):** Full-bleed high-impact illustration with elegant floating title and author hierarchy.
     - **Inner Title Page (`frontmatter/titlepage.tex`):** Formal academic front matter with university affiliation, project name, fiscal year, and vector motif.
   - Choose text overlay style:
     - **Transparent (No Background Box):** Clean floating typography directly over the art with subtle micro-drop-shadows for 100% legibility.
     - **Glassmorphism (Frosted Glass Cards):** Semi-transparent rounded cards (`colback=white!80` or `colback=black!65`) when a badge-structured layout is desired.
   - Isolate Thai typography on the cover with `\setlength{\XeTeXlinebreakskip}{0pt}` to prevent awkward syllable spacing in display titles.

3. **Confirm scope and style**
   - Apply the requested style globally when the user says “throughout the document”; prefer central preamble modules (`preamble/packages.tex`, `preamble/typography.tex`, `preamble/headings.tex`, `preamble/captions.tex`) over repeated local overrides.
   - Reuse the project's class, packages, font setup, and commands. Avoid duplicating packages or redefining an existing mechanism without checking its effects.
   - Ask a focused question only when a material choice is ambiguous.

4. **Make the smallest complete change**
   - Change the shared source of the style where possible.
   - Preserve content, labels, references, list behavior, and the appearance of unrelated elements.
   - Do not edit generated PDF/build artifacts by hand or add filler text merely to force page breaks.

5. **Build and audit**
   - Use the repository's build script (typically `./build.sh` running `xelatex -interaction=nonstopmode main.tex` twice).
   - Check the build log for fatal errors, unresolved citations/references, missing fonts, and overfull boxes.
   - Inspect the resulting PDF (including cover, inner titlepage, front matter, representative chapter pages, tables, figures, and bibliography).
   - Iterate if the PDF does not show the requested result. Report the exact build/check outcome.

---

## Style Profile

Use these established preferences when they match the user's request and no house style overrides them:

### 1. Book Cover Architecture (การออกแบบและจัดทำปก)

- **Cover Geometry:** 6 × 9 inch page, 2:3 aspect ratio, full-bleed (zero page margins on cover via `\begin{titlepage}\thispagestyle{empty}`).
- **Art Direction (3D Pixar / High-Aesthetic Style):**
  - Character/Subject: Expressive, friendly, high-tech character or AI companion interacting with the core subject (e.g. soil layers, glowing plant leaf, diagnostics).
  - Environment: Warm cinematic studio lighting, soft sunrise or golden hour, rolling natural landscape, subtle futuristic structures.
  - Negative Space: Composed with ample open sky at top (for title) and deep soil/ground at bottom (for author metadata).
  - Ratio: Strictly `2:3` matching 6 × 9 inches.
- **Cover Typography Layout (TikZ & XeLaTeX):**
  - Background Node:
    ```latex
    \node[anchor=center, inner sep=0pt] at (current page.center) {
        \includegraphics[width=\paperwidth,height=\paperheight]{figures/cover_art.jpg}
    };
    ```
  - **Transparent Text Mode (No Background Box):**
    To keep the artwork completely unblocked, omit all background rectangles and use layered micro-drop-shadows for contrast:
    ```latex
    % White shadow for dark text on bright sky
    \node[anchor=north, align=center, text width=5.2in] at ([xshift=0.6pt, yshift=-0.44in]current page.north) { ... };
    % Main dark text
    \node[anchor=north, align=center, text width=5.2in] at ([yshift=-0.45in]current page.north) { ... };
    ```
  - **Syllable Separation Fix:** Always wrap cover titles in `\begingroup\setlength{\XeTeXlinebreakskip}{0pt} ... \endgroup` so that centered Thai display titles do not spread into isolated syllables.
  - **Hierarchy:**
    1. Category Badge: `HANDS-ON WORKSHOP HANDBOOK \textbullet\ เอกสารประกอบการอบรม` (8.5pt bold)
    2. Main Title Line 1: `คู่มือการจัดเตรียมชุดข้อมูลและการฝึกอบรม` (18pt bold)
    3. Main Title Line 2: `ปัญญาประดิษฐ์เพื่อเกษตรดิจิทัลและสิ่งแวดล้อม` (20-22pt bold, accented color)
    4. English Subtitle: `SMART AGRICULTURE & SOIL-PLANT AI SYSTEM HANDBOOK` (8.5pt bold)
    5. Author & Affiliation: `ผู้ช่วยศาสตราจารย์ ดร.ชีวะ ทัศนา` (12-13pt bold white), Department, Faculty, University (8.5-9.5pt white), Fiscal Year (8pt gold).

### 2. Page & Typography Setup

- **Page & Text:** 6 × 9 inch book page (`geometry`: inner=1.0in, outer=0.75in, top/bottom=0.85in); Sarabun font (or TH Sarabun New) for Thai and English; about 1.18 line spacing (`\setstretch{1.18}`).
- **Self-Contained Fonts:** Place TTF font files directly in `fonts/` inside the project to ensure 100% portability without machine-specific font paths.
- **Thai Word Segmentation:** Enable native Thai line-breaking in XeLaTeX preamble:
  ```latex
  \XeTeXlinebreaklocale "th"
  \XeTeXlinebreakskip = 0pt plus 1pt
  ```
- **Paragraphs:** First-line indent of `3em`, no extra paragraph skip (`\parskip=0pt`). In this profile, 3em is an explicit user preference and deeper than conventional book styles.
- **First Paragraph after Headings:** Use `indentfirst` to ensure the first prose paragraph after sectioning commands follows the 3em indent. Do not force prose indentation onto lists, tables, captions, or boxed content.

### 3. Headings & Chapter Openings

- **Chapter Openings:** Chapter and appendix openers begin on odd/right-hand pages (`openright`). Right-align the chapter label and title (`\raggedleft`); make the chapter label visually prominent (`fontsize{18}{22}` bold "บทที่ \thechapter").
- **Heading Pagination:** Keep headings with a reasonable amount of following content using `\needspace{5\baselineskip}` before sections and `\needspace{4\baselineskip}` before subsections.
- **Running Headers:** Even pages show page number left, book title right. Odd pages show chapter title left, page number right.

### 4. Captions & Structured Elements

- **Figure & Table Captions:** Use Thai figure label `ภาพที่` and table label `ตารางที่`; separate label and caption text with a space, not a colon (`\DeclareCaptionLabelSeparator{space}{ }`).
- **Table Captions:** Left-aligned across the document (`\captionsetup[table]{singlelinecheck=false, justification=raggedright, position=top}`).
- **Lists & Callout Boxes:** Retain their own indentation (`leftmargin=2.8em`). Do not apply paragraph indentation a second time to `itemize`, `enumerate`, `description`, tables, or `tcolorbox`.

### 5. Academic Apparatus

- **Citations & Bibliography:** Formatted in APA 7th Edition with hanging indentation:
  ```latex
  \newcommand{\bibentry}[1]{\noindent\hangindent=2.5em\hangafter=1 #1\par\vspace{7pt}}
  ```
- **Appendices:** Grouped under `\appendix` using `\chapter{...}` for lettered appendices (ภาคผนวก ก, ข).

---

## Whole-Book & Cover Audit Checklist

- [ ] **Outer Cover:** 2:3 aspect ratio, full-bleed 6 × 9 in, artwork unblocked, zero text collisions with focal visual elements (characters, roots, sensor nodes).
- [ ] **Cover Text Legibility:** Titles and author details are 100% transparent (no clumsy background boxes) with subtle drop-shadows ensuring crisp readability.
- [ ] **Cover Syllable Continuity:** Thai display title does not have awkward syllable gaps (`\XeTeXlinebreakskip=0pt` inside cover).
- [ ] **Inner Title Page:** Matches full academic metadata (author, department, faculty, university, fiscal year) and fits completely on page without overflowing.
- [ ] **Running Headers:** Even pages show updated book title; odd pages show chapter title.
- [ ] **Prose Indentation:** 3em first-line indent applied to all prose, including first paragraphs after headings; lists and tables are not double-indented.
- [ ] **Chapter Openers:** Begin on odd/right-hand pages with bold right-aligned chapter label.
- [ ] **Captions:** `ภาพที่` and `ตารางที่` use space separator without colon; table captions align left.
- [ ] **PDF Verification:** Rebuilt PDF (`main.pdf`) visually confirms all layout, typography, and cover art rules.
