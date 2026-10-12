# Project 60 live presentation script

**M SHREEVENKAT SATHVIK · 25WU0101168 · 25TU03MJM0 Database Management Systems**

**Semester III · CSE Panthers · Guide: Dr Sahithi**

This is the script for **your own screen recording and voice**. Safari is arranged left to right as: **Slides → live app → SQL schema → Python service → report**. The first slide is open. Aim for about **5–6 minutes**. Speak naturally; the wording below is a guide.

## Before pressing Record

- Check `http://127.0.0.1:5055/` in the second Safari tab. The overview should show **2 camps, 3 active families, 7 people and 4 unmet needs**. F-001's water-kit need should show **5**.
- Keep the live app on **Overview**. Do not issue the three kits before the recording; it needs to start from 5 required and 20 in stock.
- Put this script on your phone or a second screen. Turn on Do Not Disturb to keep notifications out of the recording.
- On Mac, press **Shift–Command–5**. Choose **Record Entire Screen** so tab switches are captured. In **Options**, choose your microphone and save location. Click **Record**. [Apple's instructions](https://support.apple.com/en-gb/102618) explain the recording toolbar.

## Say and show

### 1. Title slide — about 15 seconds

**Show:** Slide 1.

> Hello, I am M Shreevenkat Sathvik, registration number 25WU0101168. My DBMS PBL Project 60 is the Disaster Relief Resource and Camp Management System. I used MySQL and Python under the guidance of Dr Sahithi.

### 2. Problem — about 30 seconds

**Action:** Press **Space** for slide 2.

> In a disaster camp, families, supply needs, donations and item issues may be recorded in separate registers. That makes it hard to answer: which family still needs what? My project connects these records in one relational database and gives staff a current, checkable view of needs and stock. All data shown here is fictional.

### 3. Review stages — about 30 seconds

**Action:** Press **Space** for slide 3.

> We built the project in three reviews. Review 1 defined the problem, requirements and ER diagram. Review 2 implemented the MySQL schema, constraints, sample data and reports. Review 3 connected the Python application and added working forms, validation, tests and the final report. Each stage is documented in GitHub.

### 4. Database design — about 40 seconds

**Action:** Press **Space** for slide 4.

> A camp has families, and a family has people and item needs. A need contains the item, quantity, urgency and relief round. A distribution links to that need and to a volunteer assignment. Primary keys identify records, foreign keys connect them, and unique and check constraints reject invalid entries. I kept descriptive facts in their own tables instead of repeating them in every distribution.

### 5. Practical feature — about 35 seconds

**Action:** Press **Space** for slide 5.

> My practical innovation is an explainable unmet-needs queue. Remaining need equals assessed quantity minus total issued quantity. High urgency appears first, with older assessments first within each urgency level. To issue supplies, one transaction checks the remaining need, warehouse stock and volunteer assignment. A failed check rolls back the issue, and a stock movement records every successful change.

### 6. Show the code — about 50 seconds

**Action:** Click the **SQL schema** Safari tab. It opens on the `needs` table. Point to `PRIMARY KEY`, `FOREIGN KEY`, `CHECK`, and the unique key on family, item and relief round. Then click the **Python service** tab, which opens on `distribute()`.

> This is the actual source code in my public GitHub repository. The SQL table prevents duplicate or invalid assessments. In the Python distribution function, `FOR UPDATE` locks the need and stock rows while the current quantities are checked. If the requested issue exceeds need or stock, the function raises an error. Otherwise the same transaction inserts the distribution, reduces stock and writes a movement entry.

### 7. Live app overview — about 25 seconds

**Action:** Click the **Overview · Project 60** Safari tab. Point to the four count cards and F-001 in the queue.

> Here is the live application reading from MySQL. It shows two camps, three active families, seven people and four unmet item needs. F-001 needs five water kits. The queue is calculated from database records; it is not a manually typed dashboard number.

### 8. Issue three water kits — about 60 seconds

**Action:** Click **Distribute**. Select:

1. **Unmet need:** `F-001 · Water kit · 5 remaining · Riverside School Camp`
2. **Warehouse:** `Central Relief Store`
3. **Active volunteer assignment:** `Arun Mehta · Riverside School Camp`
4. **Quantity to issue:** `3`
5. Click **Record issue**.

> I will issue three water kits to F-001. The family was assessed for five, and the warehouse began with twenty. Arun Mehta is assigned to this camp. When I submit, the application checks all three rules and records the issue as one database transaction. The distribution history now shows the family, item, quantity, warehouse and volunteer.

### 9. Verify the result — about 40 seconds

**Action:** Click **Overview** to show F-001's remaining water kits as **2**. Then click **Reports** and point to water-kit stock **17**, F-001's issued quantity **3**, and remaining quantity **2**.

> The numbers reconcile. Five were required, three were issued, and two remain. Warehouse stock changed from twenty to seventeen. The reports join the family, need, distribution, warehouse and volunteer records, so the result can be checked from more than one screen.

### 10. Show a rejected issue — about 25 seconds

**Action:** Click **Distribute** again. Choose the same F-001 water-kit need, warehouse and Arun Mehta assignment. Enter **3** and click **Record issue**. It should show an error because only **2** remain. Do **not** resubmit the old form with the browser Back button.

> This second request asks for three, but only two remain. The system rejects it. Because the transaction rolls back, stock stays at seventeen and there is no second distribution. This demonstrates a DBMS rule rather than only a successful form submission.

### 11. Close — about 25 seconds

**Action:** Return to the **Slides** tab and press **End** to show slide 9.

> I ran eight MySQL integration tests covering excess and duplicate issues, volunteer overlap, stock reconciliation and the web workflow. The project uses basic DBMS ideas to solve a practical coordination problem with a clear needs queue and traceable stock. Thank you.

## Finish the recording

Click the **Stop** icon in the Mac menu bar, or press **Control–Command–Escape**. Open the saved recording and check that your **voice, code and app text** are clear. The Mac may save a `.mov` file; use that unless your submission instructions specifically require another format.

If the app is unavailable later, run `bash scripts/start_video_demo.sh` from this repository in Terminal. It creates a fresh, local-only MySQL demo without asking for the existing root password. Keep the Terminal open while presenting.
