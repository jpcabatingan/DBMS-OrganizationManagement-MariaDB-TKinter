**Group No.** Group 4 <br/>
**Section** CMSC 127 ST1-4L <br/>
**Member** Banasihan, Angela <br/>
**Member** Cabatingan, Joanne Maryz <br/>
**Member** Doroja, Kristina <br/>

# Installation Guide
1. Install Python
2. Install pip
3. Install mysqlconnect `pip install mysql-connector-python`

# How to Use
In MariaDB Terminal
1. Locate `welove127.sql`
2. Log in to root user
3. Create new user `CREATE USER admin IDENTIFIED BY 'admin';`
4. Reset Terminal
5. Log in to `mysql -uadmin -padmin`
6. Enter `source welove127.sql`

In Python Terminal
1. Locate databaseapp.py
2. Type `python main.py` to open GUI

# File Organization
1. main.py
    - authentication page
    - App call
2. shared_variables.py
    - base page
    - database configuration
    - database connection calls
    - query fetching
3. memberpov.py
4. orgpov.py
    - org menu
    - view members table with filters
5. orgpov_modifymembers.py
    - add member
    - edit member
6. orgpov_fees.py
