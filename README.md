# SQL Server to Snowflake DWH Data Migration via Python

Migrate data from SQL Server into Snowflake warehouse.

## Assumptions:
* You have some knowledge of
  * Python
  * Linux/macOS
* Your computer runs Linux/macOS
* Your computer is connected to the internet
* You have a Snowflake account
    * Sign up for a Snowflake account if you do not already have one
    * Visit [this page]([https://signup.snowflake.com/) to sign up 
* You have python v3.8+ installed
  * To check run the following, and verify
```commandline
python3 --version
```

## Dependencies
* Microsoft ODBC driver for SQL server
* Snowflake Connector for Python
* others<sup>1</sup>

## Setup
Run the following commands from the terminal
### Create a virtual environment 
```commandline
python3 -m venv venv
```
### Activate the virtual environment
```commandline
source venv/bin/activate
```
### Install required packages
```commandline
pip install -r requirements.txt
```
### Set environment variable(s) 
```commandline
export PYODBC_DRIVER=<Variabel Here>
export PYODBC_SERVER=<Variabel Here>
export PYODBC_TRUSTED_CONNECTION=<Variabel Here> #Either "yes" or "no" (without the Quotation marks)
export PYODBC_UID=<Variabel Here> #Required if PYODBC_TRUSTED_CONNECTION is no
export PYODBC_PWD=<Variabel Here> #Required if PYODBC_TRUSTED_CONNECTION is no
export SNOWFLAKE_ACCOUNT=<Variabel Here>
export SNOWFLAKE_USER=<Variabel Here>
export SNOWFLAKE_PASSWORD=<Variabel Here>
export SNOWFLAKE_DATABASE=<Variabel Here>
```

### Install the Microsoft ODBC driver for SQL Server (Linux)

#### Ubuntu
Begin by running the following:

```bash
sudo su
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

```

Download appropriate package for the OS version
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


### Install the Python requirments
To install the Python libraries, run the following command:
```bash
pip install -r requirements.txt
```

## Execute
1. Run the following commands from the terminal
```bash
python3 main.py
```


## Footnotes
1. Full list can be found in the [requirements.txt](requirements.txt) file


<img src="https://us-central1-trackgit-analytics.cloudfunctions.net/token/ping/kwna4gs9gbwxovaj5zjk" height="1" width="1"/>
