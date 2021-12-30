# SQL Server to Snowflake DWH Data Migration
Migrate data from SQL Server into Snowflake using python.


## Assumptions
* You have some knowledge of
  * Python
  * Linux/macOS
* Your computer runs Linux/macOS
* Your computer is connected to the internet
* You have a Snowflake account
    * Sign up for a Snowflake account if you do not already have one
    * Visit [this page](https://signup.snowflake.com) to sign up 
* You have python v3.8+ installed
  * To check run the following, and verify
```bash
python3 --version
```


## Dependencies
* Microsoft ODBC driver for SQL server
* Snowflake Connector for Python
* others<sup>1</sup>


## Setup
Run the following commands from the terminal
### Create a virtual environment 
```bash
python3 -m venv venv
```


### Activate the virtual environment
```bash
source venv/bin/activate
```


### Install the Microsoft ODBC driver for SQL Server (Linux)


#### Ubuntu
Begin by running the following:


```bash
sudo su
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
```

Download the appropriate package for the OS version
Choose only ONE of the following, corresponding to your OS version

```bash
#Ubuntu 18.04
curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

#Ubuntu 20.04
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

#Ubuntu 21.04
curl https://packages.microsoft.com/config/ubuntu/21.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
```

Then run the following:
```bash
exit
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```


#### macOS
To install Microsoft ODBC driver 17 for SQL Server on macOS, run the following commands:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew install msodbcsql17 mssql-tools
```


### Install the Snowflake Connector
To install the connector, run the following command:
```bash
pip install snowflake-connector-python
```


### Install the Python requirements
To install the Python libraries, run the following command:
```bash
pip install -r requirements.txt
```


## Configuration


### Environment Variables
Replace < ... > with your config, and run the following:

```bash
export PYODBC_DRIVER=<YOUR CONFIG HERE>
export PYODBC_SERVER=<YOUR CONFIG HERE>
export PYODBC_TRUSTED_CONNECTION=<YOUR CONFIG HERE>  #Either "yes" or "no" (without the quotation marks)
export PYODBC_UID=<YOUR CONFIG HERE>  #Required if PYODBC_TRUSTED_CONNECTION is no
export PYODBC_PWD=<YOUR CONFIG HERE>  #Required if PYODBC_TRUSTED_CONNECTION is no
export SNOWFLAKE_ACCOUNT=<YOUR CONFIG HERE>
export SNOWFLAKE_USER=<YOUR CONFIG HERE>
export SNOWFLAKE_PASSWORD=<YOUR CONFIG HERE>
export SNOWFLAKE_DATABASE=<YOUR CONFIG HERE>
```


### [Job List](job_list.json)
List of select statements (SELECT * FROM MY_TABLE) and the target tables you want to create. Replace the < ... > placeholders. To allow for multiple SQL Servers instances and many Snowflake databases simply replace the ${PYODBC_SERVER} and ${SNOWFLAKE_DATABASE} placeholders with the server names and database names respectively. Also, columns or rows can be excluded via the query, and essentially any SELECT query can be used as a source. 


### [Type Conversion](type_conversion.json)
PYODBC returns typed data. This file maps that type to the Snowflake type. 


## Execute
Run the following commands from the terminal:
```bash
python3 main.py
```


## Footnotes
1. The full list can be found in the [requirements.txt](requirements.txt) file


<img src="https://us-central1-trackgit-analytics.cloudfunctions.net/token/ping/kwna4gs9gbwxovaj5zjk" height="1" width="1"/>
