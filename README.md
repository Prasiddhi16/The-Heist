# The Heist:Detective Intelligence System

A web-based case management and detective simulation platform built on a
normalized relational schema, where every case, suspect, and piece of
evidence is tied together through enforced foreign key relationships.

## Demo Pictures

![Active Cases](The%20Heist%20images/Active%20Cases%20Page.png)


![Evidence Investigation](The%20Heist%20images/Evidence%20Investigation%20Page.png)
 **For more screenshots and application pages, please visit the `The Heist Images` folder in this repository.**


## Demo Video

https://github.com/Prasiddhi16/The-Heist/raw/main/The-Heist1.mp4
<video src="the-heist/heist.mp4" controls width="600"></video>



## Deployed Version
https://the-heist.onrender.com/

## Linked Report
[Click here to view the PDF](The-Heist.pdf)

<!-- Link to the full project report PDF, e.g.: [Project Report](./docs/project-report.pdf) -->

## Overview

The Heist (*Heist Solver: Detective Intelligence System*) is a web
application that lets investigators manage multiple active criminal cases like
heists, homicides, missing person cases , from a single structured
environment, rather than scattered spreadsheets and paper files. Every
suspect, piece of evidence, and case outcome is stored in a relational
database and explicitly linked back to its parent case through foreign key
constraints.

Investigators sign up, land on a dashboard of active cases, drill into a
specific case to review evidence and suspect profiles, and file a final
verdict and accusing a suspect and citing supporting evidence , which the
system checks against a hidden solution and scores.

Built as a group effort for **COMP 232 (Database Management Systems)** at
Kathmandu University, the project is a working demonstration of core
relational database concepts: normalization, primary/foreign key design,
one-to-many relationships, cascading deletes, and referential integrity.

## Core Workflow

```
START → LOGIN → DASHBOARD → CASES MODULE (master list)
      → SELECT ACTIVE CASE → INVESTIGATE
      → EVIDENCE MODULE ⇄ SUSPECTS MODULE
      → CASE RESOLUTION & REPORTING → END
```

## Architecture

| Layer | Technology |
|---|---|
| Frontend / Application | Django |
| Database | PostgreSQL, hosted on Supabase |
| Auth | Supabase `auth.users`, referenced by the app's `users` table |

## Setup / Installation

```bash
git clone <https://github.com/Prasiddhi16/The-Heist.git>
cd the-heist

# Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Apply schema / migrations
python manage.py migrate

# Run the app
python manage.py runserver
```

## Team

Built by a four-member team as a COMP 232 group project at Kathmandu
University, Department of Computer Science and Engineering, submitted to
Mr. Bipesh Subedi.

| Name | Student ID |Git Profiles|
|---|---|---|
| Prapti Dhamala | 037967-24 |https://github.com/PraptiDhamala|
| Prasiddhi Dumre | 037970-24 |https://github.com/Prasiddhi16|
| Ushma Sapkota | 037999-24 |https://github.com/Ushma-Sapkota|
| Anusha Khatri | 036130-24 |https://github.com/AnushaKhatri5|


