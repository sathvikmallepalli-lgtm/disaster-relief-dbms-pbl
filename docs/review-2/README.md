# Review 2 · MySQL Database Prototype

This review turns the [Review 1 design](../review-1/README.md) into a working MySQL database. It includes the [3NF explanation](normalization.md), [data dictionary](data-dictionary.md), [DDL](../../database/schema.sql), [fictional data](../../database/seed.sql), [report queries](../../database/reports.sql), and [sample query output](sample-output.md).

## Set up a local demonstration database

Use a local MySQL account with permission to create a database. The commands ask for the password interactively; do not put a real password in the repository.

```bash
mysql -u root -p -e "CREATE DATABASE disaster_relief CHARACTER SET utf8mb4"
mysql -u root -p disaster_relief < database/schema.sql
mysql -u root -p disaster_relief < database/seed.sql
mysql -u root -p disaster_relief < database/reports.sql
```

Use a Python virtual environment for the small command-line prototype:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
export DB_HOST=127.0.0.1 DB_PORT=3306 DB_NAME=disaster_relief DB_USER=root
export DB_PASSWORD='your-local-password'
.venv/bin/python -m scripts.prototype report unmet
```

For a MySQL server using a Unix socket, set `DB_SOCKET` to its socket path. The `.env.example` file lists all supported settings. The application does not automatically read `.env` files; values must be exported in the terminal.

## Demonstration sequence

1. Run `report camps`, `report unmet`, and `report stock`. The sample has three families, seven people, four item needs, and three kinds of stock.
2. Run `distribute --need 1 --warehouse 1 --assignment 1 --quantity 3 --token demo-issue-1`. Family `F-001` now needs two more water kits, and warehouse stock falls by three.
3. Repeat the exact command. It is rejected because the token has already been used.
4. Try `distribute --need 1 --warehouse 1 --assignment 1 --quantity 3`. It is rejected because only two kits remain in that assessed need.
5. Run `report ledger`: each stock balance must equal its movement total.
6. Run `report volunteers` and choose start/end times inside volunteer 1's existing assignment. Try `assign --volunteer 1 --camp 2 --start YYYY-MM-DDTHH:MM --end YYYY-MM-DDTHH:MM` with those overlapping times. It is rejected.

The sample assignment starts one day before the seed is loaded and ends 30 days later, so the distribution example can be tried immediately after setup.

## How the rules are enforced

| Rule | Enforcement |
| --- | --- |
| One family/item/round assessment | `UNIQUE (family_id, item_id, relief_round)` |
| Repeated donation or distribution request | Unique receipt/request token |
| Positive quantities, valid statuses and times | MySQL `CHECK`, `NOT NULL`, and Python input validation |
| Distributed item matches assessed need | Item is read from the locked need row, then the matching warehouse stock row is locked |
| Total issued does not exceed need | A `READ COMMITTED` transaction locks the need row, then checks the latest committed total |
| Stock never becomes negative | Transaction locks the stock row and decrements only when enough remains; `CHECK` is a second guard |
| No overlapping volunteer assignments | Transaction locks the volunteer row, then checks overlapping intervals |
| Stock history remains traceable | Receipt/issue and movement are committed together; movement source is unique |

`CHECK` constraints cannot compare sums of several distribution rows or detect overlapping intervals across rows. The prototype keeps those decisions in transaction-safe Python functions in [`app/services.py`](../../app/services.py). The web app in Review 3 will use the same functions.

## Review evidence

- [x] Functional dependencies and 3NF explanation
- [x] Concise data dictionary
- [x] MySQL DDL with primary keys, foreign keys, unique keys, checks, defaults, and search indexes
- [x] Fictional sample data
- [x] Queries with joins, subqueries, aggregation, and views
- [x] Command-line database prototype and rejection examples
