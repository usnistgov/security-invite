# Improving the safety of relational databases

## Prerequisites for practice:

* [Installed SQLite DB Browser](https://sqlitebrowser.org/)
* [Local Python installation](https://www.python.org/downloads/)

## General rules to protect data:
* ### How to protect data from unintended information leaks
    - #### Manage data handling exceptions correctly
    - #### Return data, messages, and exception information separately 
    - #### Separate ID and Personally Identifiable Information (PII) handling
* ### How to protect data from SQL Injection attacks
    - #### ALWAYS sanitize user input
    - #### ALWAYS avoid string concatenation for query building
    - #### USE Stored Procedures and SQL/DB Querying Frameworks
* ### How to protect data from internal threats
    - #### NEVER store open-text passwords 
    - #### Protect users regardless of password strength
    - #### Periodically check user passwords against the most popular passwords list (rainbow tables)
* ### How to protect passwords from persistent threats
    - #### Use "salted hashes" to avoid rainbow-table password reverse engineering
    - #### Consider using an application-level secret (pepper) for better password protection
