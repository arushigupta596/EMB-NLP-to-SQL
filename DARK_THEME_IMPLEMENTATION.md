# Dark Theme Implementation

## Summary
Converted the Streamlit NLP-to-SQL app to a dark theme with clean, enterprise styling.

## Changes Made

### 1. Streamlit Theme Config (`.streamlit/config.toml`)

Created `.streamlit/config.toml` with dark theme settings:

```toml
[theme]
base = "dark"
primaryColor = "#47bf72"
backgroundColor = "#0c2114"
secondaryBackgroundColor = "#102a1c"
textColor = "#ffffff"
font = "sans serif"
```

### 2. CSS Dark Theme (app.py)

Replaced all CSS with dark theme using these color tokens:

**Backgrounds:**
- `--bg-base: #0c2114` - Main app background
- `--bg-surface: #102a1c` - Cards, chat containers, panels
- `--bg-surface-2: #0f2419` - System response background
- `--bg-info: #123524` - Info banners

**Borders:**
- `--border: #1f3d2b` - All borders

**Colors:**
- `--primary-green: #47bf72` - Primary brand color
- `--secondary-green: #346948` - Secondary accents

**Text:**
- `--text-primary: #ffffff` - Main text
- `--text-secondary: #cfe7db` - Secondary text
- `--text-muted: #8fb3a2` - Muted/placeholder text
- `--text-link: #47bf72` - Links and interactive elements

### 3. Component Styling

**Sidebar:**
- Background: `#0c2114`
- Section containers: `#102a1c` with `#1f3d2b` border
- Sample question buttons: Transparent with green border, fill on hover

**Chat Messages:**
- User messages: `#102a1c` background, green left border
- System messages: `#0f2419` background, secondary green border
- All messages have `#1f3d2b` borders

**Input Box:**
- Background: `#102a1c`
- Border: `#1f3d2b`, changes to green on focus
- Text: White, placeholder: muted

**Expanders:**
- Background: `#102a1c`
- Border: `#1f3d2b`
- Header text: Green link color

**Buttons:**
- Background: Green (`#47bf72`)
- Text: Dark (`#0c2114`)
- Hover: Slight opacity change

**Data Tables & Code Blocks:**
- Background: `#102a1c`
- Border: `#1f3d2b`

### 4. Logo Removal

Removed the EMB Global logo display code from the main function.

## Design Principles

- **No glow/neon effects** - Clean, enterprise look
- **Minimal shadows** - Uses borders instead
- **Consistent spacing** - 8px border-radius throughout
- **Readable contrast** - White text on dark backgrounds
- **Green accents** - Brand color for interactive elements

## Usage

Restart the Streamlit app to see the dark theme:

```bash
streamlit run app.py
```

The app will now feature:
- Dark background (#0c2114)
- Clean card-based layout
- Green accents for branding
- Excellent readability
- Professional, enterprise appearance
