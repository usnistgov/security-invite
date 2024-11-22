# Homework assignments

## Configuration Task 1:
### VM setup
1. Create and configure a VirtualBox VM and set up an SSH forwarding port
2. Install Python (or any other preferred programming language/runtime/infrastructure)
3. Test the VM's ability to SSH with a password
4. Generate and install a public/private key-pair for SSH use
5. Use scp from the host to copy files to and from the VM

## Configuration Task 2:
1. Install DB Browser for SQLite
2. Investigate the database structure using DB Browser for SQLite or any other preferred method of viewing SQLite databases (e.g. SQlite CLI tool).
3. Use db_base.py and db_create.py to create the TopicsDB.dbf



## 
## ```Homework 1``` (Objectives: reading user input and using regular expressions for input validation):
### Present the user with options. Use Regular Expressions to validate User Name and Table Name inputs
- Upon startup, the application must print this menu ```0.[E]xit 1.[U]ser 2.[T]able:``` verbatim and then safely read the user's input
- #### Allowed user inputs are:
    - 0, E, or Exit (typed in any case combination, e.g. ExiT) switches app into the ```EXIT MODE```
        - When the EXIT MODE is chosen the application 
            - Prints ```Bye!```
            - Exits
    - 1, U, or User (typed in any case combination e.g. UsEr) switches the app into the ```USER MODE```
        - In ```USER MODE```, the application performs a regular expression verification (pattern matching) of a typed user name:
            - Prompts user for input of ```User Name:```
            - Validates the input provided to the application on matching or not matching the pattern
            - ```(+)``` Prints ```OK``` if the user name matches the pattern
            - ```(-)``` Prints ```FAILED!``` if the user name doesn't match the pattern
    - 2, T, or Table (typed in any case combination e.g. tAbLe)  switches app into the ```TABLE MODE```
        - In ```TABLE MODE```, the application performs a regular expression verification (pattern matching) of a typed **table name**:
            - Prompts user for input of ```Table Name:```
            - Validates the input provided to the application on matching or not matching the pattern
            - ```(+)``` Prints ```OK``` if the table name matches the pattern
            - ```(-)``` Prints ```FAILED!``` if the table name doesn't match the pattern
    - For any other input, the application prints ```Input 'Value-of-the-Input' is unknown!```, where ```Value-of-the-Input``` is the value provided by the user.
    - After above actions return back and display the menu ```0.[E]xit 1.[U]ser 2.[T]able:``` and safely read the user's input, unless ```EXIT MODE``` was chosen as explained above.



## 
## ```Homework 2``` (Objectives: reading files, validating data, catching errors and exceptions, logging the errors and exceptions):
### Read a file that is provided as a command-line input parameter. Resolve path shortcuts. Log data validation failures into a file
- The application begins by **safely** reading the YAML config file (if a parameter was provided) in the parameter named ```-config``` or ```--ConfigFile```. The application then displays the menu choices listed below (2c), responds to user inputs, logs exceptions and  errors into either a read-in or default log file, displays the data read from file, or exits.
#### Config file reading rules (2a):
- The YAML-formatted config file may contain values of any or all of the following: ```LOG_FILE```, ```TABLE_NAME```, and ```USER_NAME```
    - If the value ```LOG_FILE``` is missing from the config file, if there was an error reading the file, or if a config file was not provided, the default log file should be located at ```~/si/logs/default-log.log``` 
    - When writing to the log file, use the overwrite mode instead of the append mode log files would typically use.
#### Config file error handling (2b):    
- Any errors encountered while reading the config file or due to validation failure should not be printed to the terminal, but instead be LOGGED into the log file (using the log file path from 2a)
    - If the config file was not found at the location specified, then log the following error message in this format: ```Config file SETTINGS_FILE_NAME does not exist```. Replace `SETTINGS_FILE_NAME` with the attempted config file path.
    - If an unexpected YAML error or exception happens when reading the config file, then log the error or exception and fall back to using the default values
- Include the following information for validation faults, errors and exceptions:
    - Config file could not be parsed (invalid YAML) - log this as an error object
    - If any other exception occurs - log it as an exception object
    - ```TABLE_NAME``` failed regular expression validation - log this as an error with the message: ```"Config-file Table Name: 'table_name_value_from_config' failed validation"```
    - ```USER_NAME``` failed regular expression validation - log this as an error with the message: ```"Config-file User Name: 'table_name_value_from_config' failed validation"```
    - All log messages should be formatted as follows:
        - The message begins with no empty lines ('\n')
        - The message marker line begins with 3 exclamations '!', which are followed by 80 '=' (e.g. '!!!================================================================================')
        - The next line lists date-time in the ISO standard format (no microseconds) (e.g. 2023-10-10T23:23:10-0400)
        - The line after that  is indented with a tab ('\t') followed by  @Line No: lineNumberInYourCode
        - The following line is indented with a tab ('\t') followed by the error/exception description. 
            - E.g. if a failure occurs when parsing the table name and/or user name (if and only if either was present in the config-file) the following error messages should follow:
                - For the failed match of TABLE_NAME value: ```Config-file Table Name: 'table_name_value_from_config' failed validation``` 
                - Or for failed USER_NAME value:  ```"Config-file User Name: 'user_name_value_from_config' failed validation"```
#### Menu and actions (2c):
- After the config file is read, the application must print the text MAIN-MENU ```0.[E]xit 1.[S]ettings:``` verbatim and safely read the user's input
- #### Allowed user inputs are:
    - 0, E, or Exit (typed in any case combination, e.g. ExiT) switches app into the ```EXIT MODE```
        - When the EXIT MODE is chosen the application 
            - Prints ```Bye!```
            - Exits
    - 1, S, or Settings (typed in any case combination e.g. sEtTiNgS)  switches app into the ```SETTINGS MODE```
        - When the ```SETTINGS MODE``` is chosen - the application does the following:
            - Prints all of the settings using the text format: ```Entry-Name: Entry-Value```
            - After the list is printed - the application returns to the main menu as described in (2b)
    - For any other input, the application prints ```Input 'Value-of-the-Input' is unknown!``` where ```Value-of-the-Input``` is the value supplied by the user, and then returns back to print the MAIN-MENU (2b)

### Example:

- Provided ```conf_data.yaml``` settings file with the  content listed below
```
MAX_FAILED: 15
ABRACADABRA: 100 
TABLE_NAME: sqlite_AUTH_USERS
ZULU: 2023-10-10 23:23:23-00:04
DB_NAME: ~/Databases/SecInVITE-DB/MyDb.db
ABACUS: In this day and age we use computers
USER_NAME: 123456some_-_user!@#
```

- The program should produce the following interactions (inputs and outputs):
```
python3 hw2.py -conf ./conf_data.yaml
0.[E]xit 1.[S]ettings:set
Input 'set' is unknown!
0.[E]xit 1.[S]ettings:test
Input 'test' is unknown!
0.[E]xit 1.[S]ettings:s
MAX_FAILED: 15
ABRACADABRA: 100
TABLE_NAME: sqlite_AUTH_USERS
ZULU: 2023-10-10 23:23:23-00:04
DB_NAME: ~/Databases/SecInVITE-DB/MyDb.db
ABACUS: In this day and age we use computers
USER_NAME: 123456some_-_user!@#
LOG_FILE: /Users/dac4/si/logs/default-log.log
0.[E]xit 1.
```

- Also the following log file /Users/TE/si/logs/default-log.log (where TE is the Testing Environment user name in our case) would be created and shaped like this:
```

!!!================================================================================
2023-10-24T15:17:32-0400
	@Line No: 105
	Config-file Table Name: 'sqlite_AUTH_USERS' failed validation
!!!================================================================================


!!!================================================================================
2023-10-24T15:17:32-0400
	@Line No: 107
	Config-file User Name: '123456some_-_user!@#' failed validation
!!!================================================================================
```

#### Also note that: 
1. The line specified in the config file was not processed with the 'expanduser' function 
```
DB_NAME: ~/Databases/SecInVITE-DB/MyDb.db
```
2. If the LOG_FILE line is not present in the config file, the default value is used, but is resolved with the 'expanduser' function since it comes from a safe source. The default value of
```~/si/logs/default-log.log``` 
becomes
```LOG_FILE: /Users/dac4/si/logs/default-log.log```
in the output.


## 
## ```Homework 3```:
### Read/Interpret/Complement Config File and Provide a way to see the information read and complemented:
- The application begins by reading the config file. It can be provided as a parameter named ```-config``` or ```--ConfigFile```, or, if not specified, falls back to the default config values in (3a). Then, the application displays the menu choices listed below, responds to user inputs, or exits. These actions occur according to the rules of interpreting file and user input as described below. 
#### Config file reading rules (3a):
- All the rules of the previous homework about reading the config file (2a) apply. Now, the settings present in the default configuration must be read, validated (TABLE_NAME), resolved (LOG_FILE, DB_FILE) and arranged in alphabetical order when viewed.
- The YAML format config file may contain values for some or all of ```DB_NAME```, ```LOG_FILE```, ```TABLE_NAME```, and ```MAX_FAILED```, as well as any other entries.
- If any of the required default parameters are not provided in the config file  - the default values to be assumed are as follows:
``` 
DB_FILE: ~/si/db/SI_DBF.db 
LOG_FILE: ~/si/logs/SI_Log.txt 
MAX_FAILED: 6
TABLE_NAME: Users_Top50 
```
- If any of the values for ```DB_FILE```, ```LOG_FILE```, ```TABLE_NAME```, or ```MAX_FAILED``` are missing from the config file read at application startup, they should be replaced with the corresponding default value(s) listed above.
- ```ERROR CONDITION:``` If the file reading fails **for any reason** the application prints and logs the error ```Corrupt config file!``` as well as the actual error or exception, and then exits.
- ```ERROR CONDITION:``` If the TABLE_NAME value did not pass regular expression validation, the application logs the error as described in Homework 2.
#### Menu and actions (3b):
- After the config is read, the application must print the text MAIN-MENU ```0.[E]xit 1.[S]ettings 2.[D]ata:``` verbatim and safely read the user's input.
- #### Allowed user inputs are: 
    - 0, E, or Exit (typed in any case combination, e.g. ExiT) switches the app into the ```EXIT MODE```
        - When the EXIT MODE is chosen, the application simply 
            - Prints ```Bye!```
            - Exits
    - 1, S, or Settings (typed in any case combination e.g. sEtTiNgS) switches the app into the ```SETTINGS MODE```
        - When in the ```SETTINGS MODE```, the application does the following:
            - Sorts read, filtered, and complemented settings in alphabetic order of the keys
            - Prints all of the settings using the text format: ```Entry-Name: Entry-Value```
            - After the list is printed, the application returns to the main menu as described in (3b)
    - 2, D, d, or Data (typed in any case combination e.g. dAtA)  switches app into the ```DATA MODE```
        - When in the ```DATA MODE```, the application does the following:
            - Prompts for user input with ```Highest Id:``` and then safely reads the value in the range from 1 to 10
            - If the input is outside of the range, then it displays the error ```"User entered Highest Id: 'value-entered'"```
            - Prints a simple data sample of ALL the columns in ```TABLE_NAME``` (specified in the config file) with the id lesser than the value entered as the ```Highest Id```
            - Each table row's values should be separated by tabs, with white-spaces before and after the values removed, and each new row should begin with a new line
            - After the row data is printed, the application returns to the main menu as described in (3b)

    - For any other input, the application prints ```Input 'Value-of-the-Input' is unknown!``` and returns back to print the MAIN-MENU 

### Example:

- Provided ```conf_data.yaml``` settings file with the content listed below
```
MAX_FAILED: 15
ABRACADABRA: 100 
TABLE_NAME: Users_Top50
ZULU: 2023-10-10 23:23:23Z
DB_NAME: ~/si/db/SI_DB.db
ABACUS: In this day and age we use computers 
```
- Using the homework application would produce output similar to the following:
```
0.[E]xit 1.[S]ettings 2.[D]ata:Tada!
Input 'Tada!' is unknown!
0.[E]xit 1.[S]ettings 2.[D]ata:data
Highest Id:3
1       dummy1  123456  0
2       dummy2  password        0
0.[E]xit 1.[S]ettings 2.[D]ata:e
Bye!
>
```
- For the malformed YAML file it would be the following:
```
>python3 ./hw3.py -config conf_wrong.yaml
Corrupt config file!
>
```

## 
## Homework 4:
### Secure SQL Operations emulating user Login
Create a login application based on queries constructed from simple string concatenation
#### Config file operations (4a):
- The application reads and interprets the config file as in Homework 3, implementing all the features specified in (3a) and (3b)
- The application begins and reads the config file with he DB_NAME, TABLE_NAME, and MAX_FAILED limits
#### Menu and actions (4b):
- On startup, the application has to produce ```MAIN-MENU``` text ```0.[E]xit 1.[S]ettings: 2.[L]ogin:``` and then read user input
    - Options 0. and 1. in the menu have to respond according to (3b).
    - If the user inputs 2, L, or Login (typed in any case combination e.g. LogIN), the application enters the ```LOGIN MODE```: 
        - In ```LOGIN MODE```, the application performs the following:
            - Prompts the user to input a user name ```User Name:```
            - Prompts the user to input a password  ```Password:```
            - Reads both inputs and attempts to authenticate against the SQLite database
            - For the authentication process, use the table ```TABLE_NAME``` and the SQLite database file ```DB_NAME```, which are both read from the config file
            - ```(+)```If the user is authenticated successfully, print the following lines:
                - ```User-Id: $user-id``` where the value of ```$user-id``` is filled from the ```id``` column of the authentication table
                - ```User: $user-name``` where the value of ```$user-name``` is filled from the ```user_name``` column of the authentication table
                - ```Failed-Count: $failed-count``` where the value of ```$failed-count``` is filled from the ```failed_count``` column of the Authentication table before this authentication
                - ```Entries-Count: $entries-count``` where the value of ```$entries-count``` is filled from the extra data column added to the query with ```Count(*)``` column of the Authentication table before this authentication
                - Reset the ```failed_count``` value for the authenticated account in the table ```TABLE_NAME``` to ```0```
                - Return back to the ```MAIN-MENU```
            - ```(-)```If the user's authentication succeeded, but ```failed_count > MAX_FAILED``` - perform the following:
                - Print ```Account locked or either user name, password, or both are incorrect!```
                - Return back to the ```MAIN-MENU```
            - ```(-)```If the user's authentication failed - perform the following:
                - Increment the ```failed_count``` column of the Authentication table for the user name provided
                - Increment ```session_failed_count``` 
                    - Compare ```session_failed_count``` to ```MAX_FAILED``` read from the config file
                    - If ```session_failed_count > MAX_FAILED``` print ```Session MAX_FAILED exceed!``` and exit the application
                - Print ```Either user name, password, or both are incorrect!```
                - Return back to the ```MAIN-MENU```
            - ```(-)```If any unexpected situation (exception or not explicitly specified error) happens during the user input, file reading, or database operations log the message in the config-specified log file as follows:
                - Use the ISO datetime format with time zone as ```timestamp``` (e.g. in Python ```datetime.now().astimezone().isoformat(sep=" ")```)
                - Use the exception or error class information if available (e.g. sqlite3.Error as error: ```error.__class__```)



- Allowed inputs are either 1, L, l, or Login for switching into the LOGIN MODE and 2, E, e, or Exit for the EXIT MODE
- When the EXIT MODE is chosen - application simply prints "Bye!" and exits
- In login mode application authenticates against table Users_Topic_1a requesting for USER NAME and passwords in sequence by using Prompts "User:" and "Password:" to read the user input. 
- If the user has state that exceeded failed login MAX_FAILED counts value read from the config file in 1. Application prints "Failed Login Counts Exceeded!"
- If user reached the MAX_FAILED count while trying to login - application prints "Exceeded Login Attempts Allowed!" and exits
- If user successfully submitted credentials - application returns to the original prompt described in 3.


- In login mode, the application authenticates against the Users_Topic_1a table requesting both a user name and a password in sequence with the prompts "User:" and "Password:" to read the user input. 
- If the user causes a state where the failed login MAX_FAILED counts exceeds the value read from the config file in 1. the application prints "Failed Login Counts Exceeded!"
- If the user reached the MAX_FAILED count while trying to login, the application prints "Exceeded Login Attempts Allowed!" and exits
- If user successfully submitted credentials - application returns to the original prompt described in 3.
