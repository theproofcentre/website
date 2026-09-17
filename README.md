# PROOF Centre Website

Welcome to the repository for the **PROOF Centre of Excellence** website ([proofcentre.github.io](https://proofcentre.github.io/)).

This website is built with [Hugo](https://gohugo.io/) and features an automated, native data ingestion pipeline that syncs content directly from a shared Google Spreadsheet.

---

## 📖 Table of Contents
1. [For Content Editors: Google Sheets Guide](#-for-content-editors-google-sheets-guide)
   - [Access & Permissions](#access--permissions)
   - [Things That Can Break The Website](#things-that-can-break-the-website)
   - [Tab-by-Tab Column Guide](#tab-by-tab-column-guide)
   - [Formatting & Styling Sheets Safely](#formatting--styling-sheets-safely)
   - [Filtering & Sorting Safely: Always Use "Filter Views"](#filtering--sorting-safely-always-use-filter-views)
   - [Guarding Against Deletion & Human Error](#guarding-against-deletion--human-error)
   - [When Do Edits Appear on the Website?](#when-do-edits-appear-on-the-website)
2. [For Developers & Site Maintainers](#-for-developers--site-maintainers)
   - [Architecture & Tech Stack](#architecture--tech-stack)
   - [Running Locally](#running-locally)
   - [How Ingestion Works](#how-ingestion-works)
   - [Fallback Resilience](#fallback-resilience)
   - [Deployment Pipeline](#deployment-pipeline)
   - [Troubleshooting: Missing or "Dropped" Content](#troubleshooting-missing-or-dropped-content)

---

## 📝 For Content Editors: Google Sheets Guide

Non-technical team members can manage publications, team bios, and patents entirely through Google Sheets without touching code, Git, or Markdown.

### Access & Permissions
- **Spreadsheet Link**: Contact the site administrator for the link to the *PROOF Centre - Web Content* master sheet.
- **Sharing Mode**:
  - The sheet must always remain set to **"Anyone with the link can view"** so Hugo can read the data.
  - Team members who need edit access should be added individually by email as **Editors**.

---

### Things That Can Break The Website

> [!CAUTION]
> The automated website build depends on exact tab names, column names, and unfiltered data views. Items 1–2 will trigger fallback to static backup data, while item 4 will cause rows to be **silently dropped from the website**.

1. **Never rename the tabs**: The tabs must remain named exactly:
   - `Publications`
   - `Team`
   - `Patents`
2. **Never rename or delete Row 1 (Header Row)**: The text in Row 1 (`year`, `title`, `lead`, etc.) must remain lowercase and exact.
3. **No completely blank rows between data**: Add new records in the next available empty row at the bottom (or insert rows directly between existing entries).
4. **Never leave active standard filters on the sheet**: Standard filters (`Data > Create a filter`) hide rows globally. Because Google's CSV export only downloads visible rows, any filtered-out rows will be **silently dropped from the live website**! Always use **Filter Views** instead (`Data > Filter views`) to sort or filter safely.

---

### Tab-by-Tab Column Guide

#### 1. `Publications` Tab
Controls both the interactive minimalist table and publication cards.

| Column Name | Required? | Type / Format | Description & Example |
| :--- | :---: | :--- | :--- |
| `year` | **Yes** | Number (`YYYY`) | Publication year (e.g. `2026`). Used for sorting and grouping. |
| `date` | Optional | Date (`YYYY-MM-DD`) | Exact publication date (e.g. `2026-08-15`). Used for chronological sort within a year. |
| `title` | **Yes** | Plain text | Full title of the paper. Avoid enclosing in quotes. |
| `journal` | **Yes** | Plain text | Name of the publishing journal (e.g. `European Heart Journal`). |
| `citations` | Optional | Number | Total citation count (e.g. `42` or `0`). Summed automatically to power the dynamic cumulative counter above the table. |
| `doi` | Optional | Plain text | Digital Object Identifier without prefix (e.g. `10.1093/eurheartj/ehag751`). |
| `link` | Optional | Web URL | Direct link to the publication or DOI (e.g. `https://doi.org/...`). |
| `lead` | **Yes** | `TRUE` or `FALSE` | Set to `TRUE` if PROOF-led, or `FALSE` if collaborative. (Controls the filter chips). |
| `tag` | **Yes** | Pick one | Publication category. Must be one of:<br>• `Original Research`<br>• `Editorial & Commentary`<br>• `Review` |
| `pillar` | Optional | Code (`1`–`4` or `01`–`04`) | Landmark theme identifier. Connects this publication directly to the **Our Research** featured cards:<br>• `1` or `01` = Heart & Cardiovascular<br>• `2` or `02` = Respiratory & Pulmonary<br>• `3` or `03` = Infection & Immunity<br>• `4` or `04` = Multi-Omics & Systems Biology<br>*(Google Sheets automatic numbers `1`, `2`, `3`, `4` are fully supported).*<br>Leave blank for regular publications. |
| `authors` | **Yes** | Plain text | Full list of authors for the search engine. (e.g. `Shannon CP, Assadian S, Tebbutt SJ.`). |
| `display_authors`| Optional | Plain text | Shortened citation for the card summary. (e.g. `Shannon CP, Assadian S, et al.`). |

---

#### 2. `Team` Tab
Controls the *Our Team* section, avatars, and expandable biographies.

| Column Name | Required? | Format | Description & Example |
| :--- | :---: | :--- | :--- |
| `name` | **Yes** | Plain text | Full name including title (e.g. `Dr. Scott Tebbutt`). |
| `role` | **Yes** | Plain text | Official title at PROOF (e.g. `CEO & CSO`). |
| `mini_bio` | **Yes** | Plain text | 1–2 sentence summary displayed on the card (e.g. `Professor in Dept. of Medicine at UBC...`). |
| `bio` | Optional | Multi-line text | Full expanded biography displayed when user clicks *Full bio*. Separate paragraphs with blank lines. |
| `orcid` | Optional | `XXXX-XXXX-XXXX-XXXX` | 16-character ORCID identifier (e.g. `0000-0002-7908-1581`). The website automatically links to `orcid.org`. |
| `image` | Optional | Path | Path to headshot photo (e.g. `images/headshots/scott.jpg`). |
| `img_position` | Optional | Percentage | Focus alignment for avatar thumbnail (e.g. `50% 10%` or `50% 50%`). |

---

#### 3. `Patents` Tab
Controls the intellectual property disclosure table.

| Column Name | Required? | Format | Description & Example |
| :--- | :---: | :--- | :--- |
| `year` | **Yes** | Number (`YYYY`) | Filing or grant year (e.g. `2026`). |
| `title` | **Yes** | Plain text | Patent or application title. |
| `jurisdiction` | **Yes** | Country code | Short jurisdiction badge (e.g. `CA`, `US`, `EU`, `PCT`). |
| `status` | **Yes** | Plain text | Filing identification or status (e.g. `US Patent 10,989,716 B2` or `Patent Pending`). |
| `link` | Optional | Web URL | Direct link to Google Patents or patent office record. |

---

### Formatting & Styling Sheets Safely

Feel free to format the Google Sheet however you like to make it easier for your team to use! The website's data ingestion reads **only the raw cell values** and completely ignores Google Sheets formatting.

You can safely:
- **Freeze Header Rows**: Click **View > Freeze > 1 row** so column names stay visible while scrolling.
- **Add Background Colors & Fonts**: Use brand colors, bold headers, and zebra striping (**Format > Alternating colors**).
- **Add Dropdown Menus (Data Validation)**:
  - Select the `lead` column, click **Data > Data validation**, and select **Checkbox** or **Dropdown** (`TRUE`, `FALSE`).
  - Select the `tag` column, click **Data > Data validation**, and enter dropdown items: `Original Research`, `Editorial & Commentary`, `Review`.
- **Add Comments & Hover Notes**: Right-click any header cell and click **Insert note** to write guidance for teammates (e.g., *"Enter full DOI link here"*).
- **Adjust Column Widths & Wrap Text**: Set text wrapping or widen columns to make long titles comfortable to read.

---

### Filtering & Sorting Safely: Always Use "Filter Views"

> [!WARNING]
> **Standard Filters Drop Content from the Website!**  
> If someone uses standard filtering (**Data > Create a filter** or the toolbar funnel icon) and filters rows (e.g., viewing only year 2025, or unchecking specific categories), Google Sheets hides all non-matching rows globally.  
> When the website builds, Hugo requests Google's CSV export endpoint (`gviz/tq?tqx=out:csv`). **Google's CSV export only includes currently visible rows.** Any rows hidden by an active standard filter are omitted from the export, causing them to **silently disappear from the live website**!

#### The Safe Solution: Use Filter Views

Google Sheets includes a powerful feature built specifically for this: **Filter Views**. Filter Views allow you to filter and sort data for your own personal viewing **without affecting any other collaborator and without hiding rows from the CSV export**.

##### How to Create a Safe Filter View:
1. Select your data (or click any cell inside the data).
2. In the Google Sheets menu, click **Data > Filter views > Create new filter view** (or click the dropdown arrow next to the funnel icon on the toolbar and choose **Create new filter view**).
3. The column headers and row numbers will turn **dark grey / black**. This confirms you are in a temporary, private Filter View.
4. You can now sort or filter any column (by year, tag, author, etc.) freely.
5. When you are done, close the filter view by clicking the **X** in the top-right corner of the black bar (or click **Data > Filter views > None**).

##### Why Filter Views are 100% Safe:
- **Zero Impact on the Website**: The master sheet remains completely unfiltered. The CSV export fetches all rows, so no publications, team members, or patents will ever be dropped.
- **Collaborator Friendly**: Other team members viewing the sheet at the same time will not see their view rearranged or hidden.
- **Saveable & Reusable**: You can name your filter view (e.g. *"2025 Publications"*) in the top-left box on the black bar, and easily switch back to it anytime under **Data > Filter views**.

#### What to Do If Content Has Disappeared from the Website

If publications, team members, or patents are missing on the live site:
1. Open the Google Sheet and check the column headers on each tab.
2. **Look for active standard filters**:
   - Are any column headers displaying a green funnel icon instead of the normal dropdown arrow?
   - Are the row numbers on the left displayed in green text or skipping numbers (e.g., jumping from row 12 to 34)?
3. **Turn off the filter**:
   - Click **Data > Remove filter** (or click the green funnel icon on the main toolbar to disable it).
   - Alternatively, click the funnel icon on the filtered column and choose **Select all > OK**.
4. **Trigger a website sync**:
   - Trigger an on-demand sync via [GitHub Actions](https://github.com/cashoes/proofcentre/actions/workflows/hugo.yml) (or wait for the nightly 11:00 PM PST sync). All content will immediately be restored!

---

### Guarding Against Deletion & Human Error

Google Sheets provides powerful built-in protections against accidental deletions:

1. **Protect the Header Row (Row 1)**:
   - Highlight Row 1.
   - Click **Data > Protect sheets and ranges**.
   - Select **Set permissions** and choose **"Only you"** (or administrators). Teammates can still edit all the data rows, but cannot accidentally rename or delete column headers!
2. **Enable Input Rejection on Dropdowns**:
   - When creating Data Validation rules (such as for `tag` or `lead`), check **"Reject input"** so invalid values cannot be saved.
3. **Restoring Accidental Deletions (Version History)**:
   - If someone accidentally deletes rows or pastes over data, don't panic!
   - Click **File > Version history > See version history**.
   - You can view earlier revisions minute-by-minute and click **"Restore this version"** with zero data loss.
   - You can also click **"Name current version"** to bookmark verified milestones (e.g., *"March 2026 Baseline"*).

---

### When Do Edits Appear on the Website?

When you make changes to the Google Sheet, they are published to the live website via two methods:

1. **Automatic Nightly Sync**:
   - Every night at **06:00 UTC (11:00 PM PST)**, GitHub Actions automatically fetches the latest data from Google Sheets, rebuilds the site, and deploys it to GitHub Pages.
2. **Instant On-Demand Sync**:
   - If you need changes published immediately without waiting overnight:
     1. Go to the [PROOF Centre GitHub Actions](https://github.com/cashoes/proofcentre/actions/workflows/hugo.yml).
     2. Click **Deploy Hugo site to Pages** on the left menu.
     3. Click the **Run workflow** dropdown on the right and click the green **Run workflow** button.
     4. Within ~60 seconds, your updates will be live!

---

## 💻 For Developers & Site Maintainers

### Architecture & Tech Stack
- **Framework**: Hugo v0.165+ (Extended)
- **Styling**: Tailwind CSS (CDN runtime configuration) with custom brand tokens
- **Typography**: Inter (Body) & Montserrat (Headings) via Google Fonts
- **Deployment**: GitHub Pages via GitHub Actions workflow [`.github/workflows/hugo.yml`](.github/workflows/hugo.yml)

### Running Locally

```bash
# Clone repository
git clone https://github.com/cashoes/proofcentre.git
cd website

# Start Hugo dev server with remote cache-busting
hugo server -D --ignoreCache
```
Access the site at `http://localhost:1313/`.

### How Ingestion Works
Data ingestion is 100% native to Hugo without external Python, Node, or build-time scripts:
1. `hugo.toml` specifies the Google Sheet ID and tab names under `[params.google_sheets]`.
2. Layout partials in [`layouts/partials/data/`](layouts/partials/data/) construct the CSV export URL:
   `https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={TAB_NAME}`
3. Hugo's `resources.GetRemote` downloads the live CSV into memory.
4. Hugo's `transform.Unmarshal` unpacks the CSV rows into a 2D slice (`[][]string`).
5. The partial matches header columns to row values, casts data types (`int`, `bool`), and returns a clean dictionary slice to the layout.

### Fallback Resilience
Hugo wraps all remote requests in the modern `try` template keyword (`with try (resources.GetRemote $url)`).
If:
- The spreadsheet link is broken,
- The network is disconnected during local offline development, or
- `params.google_sheets.enabled` is set to `false`,

Hugo automatically catches the condition, logs a warning, and immediately serves data from the local backup YAML files in [`data/`](data/):
- `data/publications.yml`
- `data/team.yml`
- `data/patents.yml`

The site build **never breaks** due to a remote network failure.

### Deployment Pipeline
The GitHub Actions workflow [`.github/workflows/hugo.yml`](.github/workflows/hugo.yml) triggers on:
- `push` to branch `main`
- `schedule` cron every night at `0 6 * * *` (06:00 UTC)
- `workflow_dispatch` manual trigger via GitHub web UI

---

### Troubleshooting: Missing or "Dropped" Content

If publications, team members, or patents are unexpectedly missing from the live website even though they exist in the Google Sheet:

1. **Check for Active Sheet Filters (Most Common Cause)**:
   - Google's CSV export endpoint (`/gviz/tq?tqx=out:csv&sheet={TAB}`) exports the spreadsheet in its current visual presentation state.
   - If any collaborator applied a standard filter (**Data > Create a filter**), Google omits all hidden rows from the returned CSV payload.
   - Because the HTTP request succeeds (`200 OK`) and the CSV still contains valid headers, Hugo parses the truncated dataset without error—meaning the fallback YAML files are **not** triggered.
   - **Remedy**: In Google Sheets, click **Data > Remove filter** and re-run the deployment workflow in GitHub Actions. Always encourage editors to use **Filter Views** instead.
2. **Check for Empty Rows**:
   - Ensure there are no entirely blank rows interrupting the table, which could prematurely terminate row processing.
3. **Verify Header Integrity**:
   - Ensure Row 1 column names match the exact lowercase names required (e.g., `year`, `title`, `lead`, `tag`, `pillar`). Renaming or removing Row 1 headers causes Hugo to fall back to the backup YAML data.
