# Project 60 video presentation: ready-to-speak script

**Presenter:** M SHREEVENKAT SATHVIK · **Register number:** 25WU0101168

**Course:** 25TU03MJM0 Database Management Systems · **Semester:** III · **Section:** CSE Panthers

**Faculty guide:** Dr Sahithi · **Visual track:** 5 minutes 25 seconds

## Easiest recording path

The [silent visual track](../presentations/Project_60_Silent_Visual_Track.mp4) is already assembled in speaking order. It includes the presentation, selected lines from the actual SQL and Python files, and screenshots from a verified MySQL demo. It has **no voice audio**; add your own narration. The screenshots are evidence of the tested app, while the separate Safari app tab is available for a live demonstration.

1. In Safari, leave the video at **0:00, paused**. The other tabs contain the slide show, live app, SQL schema, Python service code, and printable report.
2. Press **Shift–Command–5**. Choose **Record Entire Screen** (or a selected area containing Safari). Under **Options**, choose your microphone and a save location. Start recording.
3. Click **Play** on the silent track and speak the lines below as each visual appears. You can pause if needed. The track advances automatically.
4. Stop screen recording from the menu bar. Play the recorded file once to check voice volume and screen clarity. Submit **that narrated recording**, not the silent source track. [Apple's screen recording guide](https://support.apple.com/en-gb/102618) shows the controls.

The [editable PowerPoint](../presentations/Project_60_Video_Presentation.pptx), [slide PDF](../presentations/Project_60_Video_Slides.pdf), and [Safari slideshow](../presentations/slideshow.html) are available if your professor asks for slides separately.

## Speak along with the visual track

| Time | Visual | What to say |
| --- | --- | --- |
| 0:00–0:15 | Title | “Hello. I am M Shreevenkat Sathvik, registration number 25WU0101168. This is my DBMS Project 60: Disaster Relief Resource and Camp Management System, guided by Dr Sahithi.” |
| 0:15–0:40 | Problem | “In a relief camp, family registration, needs, donations and issues may be kept in separate registers. Then it is difficult to know what each family still needs. My system connects those records in a MySQL database and shows the current answer in a small Python application.” |
| 0:40–1:05 | Three reviews | “The project has three review stages. In Review 1 I defined the problem, requirements and ER design. Review 2 implemented the tables, keys, constraints, sample records, views and queries. Review 3 added the working application, reports, integration tests and final report. Each stage is documented on GitHub.” |
| 1:05–1:35 | Database design | “A camp has families; a family has people and assessed needs. Each need names an item, quantity, urgency and relief round. Distributions refer to needs and volunteer assignments. Primary and foreign keys preserve the links. Repeated facts are separated into related tables so the main design follows third normal form.” |
| 1:35–2:05 | Practical innovation | “The useful addition is an explainable unmet-needs queue. It calculates assessed quantity minus issued quantity, then puts high urgency first and older assessments first within the same urgency. A distribution is one transaction: it checks remaining need, available stock and the volunteer assignment, then updates the issue and stock movement together.” |
| 2:05–2:20 | SQL table code | “Here is the real needs table. Its primary key identifies a need, foreign keys connect family and item, checks restrict quantity and urgency, and a unique key prevents the same family, item and relief round from being assessed twice.” |
| 2:20–2:35 | SQL view code | “The unmet-needs SQL view adds previous distributions and subtracts their total from the assessed quantity. That calculated result powers the queue and reports.” |
| 2:35–2:50 | Python row locks | “The Python service locks the selected need and stock rows with FOR UPDATE. This lets the transaction check the latest values before issuing supplies.” |
| 2:50–3:05 | Python validation | “It rejects an issue if the total would exceed the family’s assessed need. The error is shown to the user and the transaction rolls back.” |
| 3:05–3:20 | Python stock update | “For a valid issue, the same transaction subtracts warehouse stock and writes a negative stock movement. That movement gives the balance an audit trail.” |
| 3:20–3:45 | App overview | “These screenshots come from a verified MySQL run with fictional sample data. The overview shows two camps, three active families, seven registered people and four unmet item needs. The queue shows F-001’s high-urgency water-kit need of five.” |
| 3:45–4:30 | Distribution result | “In the verified demo, I selected F-001’s water kits, Central Relief Store and the assigned Riverside volunteer. I issued three kits. The assessed need was five and the store had twenty. After the transaction, the remaining need is two and stock is seventeen. The history identifies the family, item, warehouse and volunteer. An attempted issue above the remaining two is rejected.” |
| 4:30–5:00 | Reports | “The reports confirm the same numbers from joined database records: five required, three issued, two still needed, and seventeen water kits in stock. The distribution history and stock movement explain where the three kits went. This makes the result checkable, not just a display number.” |
| 5:00–5:25 | Conclusion | “Eight MySQL integration tests passed, including duplicate and excess issue checks, volunteer overlap and stock reconciliation. This is a local educational project using fictional data. It shows how basic relational design, SQL views and transactions can support a practical relief workflow. Thank you.” |

## If your professor asks for a live demo

The Safari **Overview · Project 60** tab runs against a fresh, isolated MySQL database at `http://127.0.0.1:5055/`. The app starts with F-001 needing **5** water kits and Central Relief Store holding **20**. Click **Distribute**, select **F-001 · Water kit**, **Central Relief Store**, and **Arun Mehta · Riverside School Camp**, enter **3**, and select **Record issue**. Then open **Overview** and **Reports**: the remaining need is **2** and stock is **17**. A second issue of **3** against the same need should show a rejection. The public GitHub SQL and Python tabs are ready to show the exact source.

If the live app has stopped, run `bash scripts/start_video_demo.sh` from the repository folder in Terminal. It starts a new, disposable MySQL instance on a private local socket; **your forgotten MySQL root password is not needed**. Keep that Terminal open while demonstrating and press Ctrl+C when finished. This separate demo does not change your existing MySQL database.
