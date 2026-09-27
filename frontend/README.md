# PocketSmart — Frontend

This directory contains the user interface and presentation layer for **PocketSmart**.

---

## 📁 Directory Structure

```
frontend/
├── static/
│   ├── css/
│   │   └── styles.css          # Design system stylesheet (Inter typography, #2563EB primary)
│   ├── js/
│   │   └── main.js             # Client-side interactions (modals, steppers, drag-and-drop)
│   └── uploads/                # User uploaded outfit reference photos
└── templates/
    ├── base.html               # Master layout template (navigation, modals, footer)
    ├── index.html              # Landing page (hero, budget simulator, testimonials)
    ├── dashboard.html          # User dashboard with spending KPIs
    ├── home_planner.html       # Home Interior budget planner
    ├── party_planner.html      # Party & Event budget planner
    ├── jewelry_planner.html    # Fine Jewelry budget planner with outfit photo upload
    ├── recommendations.html    # Curated recommendations breakdown & verified retailer links
    ├── history.html            # Historical planning records
    ├── login.html              # User authentication sign-in
    └── register.html           # User account creation
```

---

## 🎨 UI/UX Design System Standards

- **Typography**: Inter (400, 500, 600, 700)
- **Palette**:
  - Primary Blue: `#2563EB`
  - Accent / Hover: `#1D4ED8`
  - Surface: `#FFFFFF`
  - Background: `#F8FAFC`
  - Border: `#E5E7EB`
- **Zero Gradients**: Solid, clean, enterprise SaaS aesthetic.
- **Component Modals**: Instant product preview and direct retailer redirect.
