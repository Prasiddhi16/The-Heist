## The Heist — Detective Intelligence System
A web-based case management and detective simulation platform built on a normalized relational schema, where every case, suspect, and piece of evidence is tied together through enforced foreign key relationships.
## Demo Pictures
## Demo Video
## Deployed Version
## Linked  Report

## Overview
The Heist (Heist Solver: Detective Intelligence System) is a web application that lets investigators manage multiple active criminal cases like heists, homicides, missing person cases from a single structured environment rather than scattered spreadsheets and paper files every suspect, piece of evidence, and case outcome is stored in a relational database and explicitly linked back to its parent case through foreign key constraints.

Investigators sign up, land on a dashboard of active cases, drill into a specific case to review evidence and suspect profiles, and file a final verdict, accusing a suspect and citing supporting evidence, which the system checks against a hidden solution and scores.

The project built as a group effort  for COMP 232(Database Management Systems ) at Kathmandu University is  a working demonstration of core core relational database concepts: normalization, primary/foreign key design, one-to-many relationships, cascading deletes, and referential integrity.

## Core Workflow
START → LOGIN → DASHBOARD → CASES MODULE (master list)
      → SELECT ACTIVE CASE → INVESTIGATE
      → EVIDENCE MODULE ⇄ SUSPECTS MODULE
      → CASE RESOLUTION & REPORTING → END

## Architecture
Frontend / Application layer: Django
Database: PostgreSQL, hosted on Supabase
Auth: Supabase auth.users, referenced by the app's users table

## Setup/Installation
git clone <repo-url>
cd the-heist

# Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt


# Apply schema / migrations
python manage.py migrate

# Run the app
python manage.py runserver


## Team
Built by a four-member team
# Prapti Dhamala (037967-24) 
# Prasiddhi Dumre (037970-24 ) 
# Ushma Sapkota (037999-24 ) 
# Anusha Khatri ( 036130-24) 
as a COMP 232 group project at Kathmandu University, Department of Computer Science and Engineering, submitted to Mr. Bipesh Subedi.


