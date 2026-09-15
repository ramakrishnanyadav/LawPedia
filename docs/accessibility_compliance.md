# Lawpedia — Accessibility Compliance & Usability Matrix (WCAG 2.2 & India RPWD Act 2016)

Lawpedia treats plain language, cognitive clarity, and screen-reader accessibility as core product capabilities, complying with international and regional accessibility standards.

---

## 1. Compliance Standard Alignment Matrix

| Standard / Framework | Requirement / Clause | Lawpedia Technical Implementation | Verifying Artifact / Test |
|---|---|---|---|
| **WCAG 2.2 AA / AAA** | **1.4.3 & 1.4.6 Contrast (Enhanced)** | Body text contrast ≥ 7:1 (AAA); AAA high contrast toggle in preferences. | `frontend/src/styles/tokens.css` |
| **WCAG 2.2 AA** | **1.4.4 Resize Text** | Text resizable up to 200% without clipping or layout breakage; user text scale setting. | `frontend/src/components/AccessibilityPreferences.tsx` |
| **WCAG 2.2 AA** | **1.4.11 Non-text Contrast** | Interactive icons and UI borders achieve ≥ 3:1 contrast against light background. | `frontend/src/index.css` |
| **WCAG 2.2 AA** | **2.1.1 Keyboard** | 100% of interactive components (command palette, graph table, sidepanels) are keyboard accessible. | `tests/test_accessibility.py` |
| **WCAG 2.2 AA** | **2.4.1 Skip Blocks** | `Skip to main content` link present on every page header (`#main-content`). | `frontend/src/components/Navbar.tsx` |
| **WCAG 2.2 AA** | **2.4.7 Focus Visible** | High-contrast 3px focus ring (`outline: 3px solid #1d4ed8`) on all focusable controls. | `frontend/src/styles/tokens.css` |
| **WCAG 2.2 AA** | **2.5.8 Target Size (Minimum)** | All mobile touch targets meet or exceed 44×44px minimum sizing. | `frontend/src/components/Navbar.tsx` |
| **WCAG 2.2 AA** | **3.1.5 Reading Level** | System copy and AI plain-language explanations target Flesch-Kincaid Grade 8–9. | `tests/test_accessibility.py` |
| **India RPWD Act 2016** | **Section 42 & Rule 15** | Accessibility standards for ICT products; text-to-speech screen reader compatibility. | `docs/accessibility_compliance.md` |
| **EN 301 549 / Sec 508** | **Chapter 9 Web** | Semantic HTML5 structure (`main`, `nav`, `button`, `table`, `dialog`) and ARIA live regions. | `frontend/src/App.tsx` |

---

## 2. Information Architecture Simplification

Top-level navigation is capped at **5 primary plain-language items**:
1. `My Documents` (Upload + document list + progressive disclosure to workspace)
2. `Ask a Question` (Grounded Q&A workspace)
3. `Compare` (Semantic contract comparison matrix)
4. `Important Dates` (Deadlines & amendment timeline)
5. `Get Help` (Lawyer Handoff Pack + legal counsel guidance + accessibility settings)

Advanced tools (Clause Explorer, 3D Evidence Graph, Risk Shift Analysis, Inconsistency Matrix) are progressively disclosed inside a document's workspace view (`DocumentWorkspaceView.tsx`).
