#!/usr/bin/env python3
import csv,datetime,decimal,json,gzip,os,pyodbc,shutil,string,tempfile,uuid
import snowflake.connector as sf
import multiprocessing
#####################################################################
##  Pre-job
##    1) load job file
##      a) Load the file
##      b) Replace environment variables ${something} style
##      c) Convert to dict
##    2) validate connections
#####################################################################
def write_data(chunk):
    path = os.path.join(chunk[0],'')
    job_name = chunk[1]
    header = chunk[2]
    rows = chunk[3]
    num = multiprocessing.current_process().name[16:]
    filename = f'{path}{job_name}.{num}.csv.gz'
    if os.path.exists(filename) is False:
        with gzip.open(filename, 'at', encoding='utf-8', newline='') as f:
            csv_writer = csv.writer(f,
                quoting=csv.QUOTE_NONNUMERIC)
            csv_writer.writerows(header)
    with gzip.open(filename, 'at', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f,quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerows(rows)

if __name__  == '__main__':
    # Credentials
    os.environ['PYODBC_DRIVER']    =   '{ODBC Driver 13 for SQL Server}'
    os.environ['PYODBC_SERVER']    =   '<INSERT SQL SERVER NAME HERE>'
    os.environ['PYODBC_TRUSTED_CONNECTION']    = 'yes'                  
        # set to no, if not using AD Auth / Trusted Connection
    os.environ['SNOWFLAKE_ACCOUNT']     =   '<INSERT FULL ACCOUNT NAME HERE>'     
        # examples: xy12345.us-east-1, xy12345.canada-central.azure
    os.environ['SNOWFLAKE_USER']        =   '<INSERT SNOWFLAKE USER NAME HERE>'
        # Leave blank for AD Auth / Trusted Connection
    os.environ['SNOWFLAKE_PASSWORD']    =   '<INSERT SNOWFLAKE PASSWORD NAME HERE>'                          
    os.environ['SNOWFLAKE_DATABASE']    =   '<INSERT TARGET DATABASE NAME HERE>'

    if      os.environ.get('PYODBC_DRIVER') is not None                 \
        and  os.environ.get('PYODBC_SERVER') is not None                \
        and (    os.environ.get('PYODBC_TRUSTED_CONNECTION') == 'yes'   \
              or (      os.environ.get('PYODBC_UID') is not None        \
                   and  os.environ.get('PYODBC_PWD') is not None        \
                  )                                                     \
            )                                                           \
        and  os.environ.get('SNOWFLAKE_ACCOUNT') is not None            \
        and  os.environ.get('SNOWFLAKE_USER') is not None               \
        and  os.environ.get('SNOWFLAKE_PASSWORD') is not None           \
        and  os.environ.get('SNOWFLAKE_DATABASE') is not None           \
            :pass
    else:
        print('Environment Variables Not Set')
        raise SystemExit

    with open('job_list.json') as table_list_file:
        table_list_raw \
            =   table_list_file.read()
        table_list_template \
            =   string.Template(table_list_raw)
        job_list_json \
            =   table_list_template.substitute(
                    {x : os.environ[x] for x in os.environ})
        job_list \
            =   json.loads(job_list_json)[0]
     #2 test odbc connection
    odbc_dict = {x[7:]:os.environ[x]
                for x in os.environ
                    if x.startswith('PYODBC_')}
    odbc_connection_string \
        = ';'.join('{}={}'.format(k, v) for k, v in odbc_dict.items())

    odbc_cursor = pyodbc.connect(odbc_connection_string).cursor()
    odbc_cursor.execute("select 'PYODBC connection okay' as test")
    print(odbc_cursor.fetchone()[0])
    odbc_cursor.close()

    # test snowflake connection
    sf_dict = {x[10:].lower():os.environ[x]
                for x in os.environ
                    if x.startswith('SNOWFLAKE_')}
    sf_cursor = sf.connect(**sf_dict).cursor()
    sf_cursor.execute("select 'Snowflake connection okay' as test")
    print(sf_cursor.fetchone()[0])
    sf_cursor.close()
    #print()

#####################################################################
##  Extract
##    1) read source data definition, save for later
##    2) Create temp folder
##    3) Data
##        a) write header
##        b) Read
##        c) serialize
##        d) compress
##     ...repeat for each job
#####################################################################
    #1
    src_def = {}
    for job in job_list.keys():
        src_qry = job_list[job]['extract']['query']
        probe_qry=f"""select * from ({src_qry}) subquery WHERE 0=1"""
        odbc_cursor = pyodbc.connect(odbc_connection_string).cursor()
        odbc_cursor.execute(probe_qry)
        odbc_cursor.fetchone()
        src_def[job] = odbc_cursor.description
        odbc_cursor.close()
##  for item in src_def:
##  print(item, src_def[item], '\n')

    #2
    def get_rows(cursor):
        while True:
            row = cursor.fetchmany(500)
            if len(row) != 0:
                yield row
            else:
                break
    tgt_sql = {}
    with tempfile.TemporaryDirectory() as tempdir:
        for job_name in job_list.keys():
            print(f'Extracting {job_name}')
            src_qry = job_list[job_name]['extract']['query']
            header = []
            header.append( \
                tuple(x[0].upper() for x in src_def[job_name]))
            odbc_cursor = \
                pyodbc.connect(odbc_connection_string).cursor()
            odbc_cursor.execute(src_qry)

            with multiprocessing.Pool() as p:
                while True:
                    try:
                        rows = next(get_rows(odbc_cursor))
                        p.map(write_data,(
                            (tempdir,job_name,header,rows),))
                    except StopIteration:
                        break
    ## pauses the tempdir clean up
    ## can be used to inspect files
    ##os.system("pause")

#####################################################################
##  Transform
##    1) Covert source to target definition
##    2) Generate sql for later use
#####################################################################
            with open('type_conversion.json') as tc:
                tc2 = tc.read()
                tc3 = json.loads(tc2)[0]
                tc4 = dict([(eval(f'type({k})'),tc3[k]) for k in tc3.keys()])
                tgt_def = {}
                tgt_def[job_name]=[(col[0],tc4[col[1]]) for col in src_def[job_name]]
            col_name=','.join( \
                ['"'+i[0].upper()+'"'+' '+i[1]+'\n' for i in tgt_def[job_name]])
            col_num=','.join(\
                ['t.$'+str(n)+'\n' for n in range(1,len(tgt_def[job_name])+1)])
            database = job_list[job_name]['load']['database'].upper()
            schema = job_list[job_name]['load']['schema'].upper()
            table = job_list[job_name]['load']['table'].upper()
            path = os.path.join(tempdir,'').replace('\\','/')
            stage = job_name.upper()
            tgt_sql[job_name] = [
                f'CREATE DATABASE IF NOT EXISTS "{database}";',
                f'USE DATABASE "{database}";',
                f'CREATE SCHEMA IF NOT EXISTS "{schema}";',
                f'USE SCHEMA "{schema}";',
                r'''CREATE FILE FORMAT IF NOT EXISTS PYTHON_CSV
                        COMPRESSION = 'AUTO'
                        FIELD_DELIMITER = ','
                        RECORD_DELIMITER = '\n'
                        SKIP_HEADER = 1
                        FIELD_OPTIONALLY_ENCLOSED_BY = '\042'
                        TRIM_SPACE = FALSE
                        ERROR_ON_COLUMN_COUNT_MISMATCH = TRUE
                        ESCAPE = 'NONE'
                        ESCAPE_UNENCLOSED_FIELD = '\134'
                        DATE_FORMAT = 'AUTO'
                        TIMESTAMP_FORMAT = 'AUTO'
                        NULL_IF = ('');''',
                f'CREATE OR REPLACE STAGE "{stage}" FILE_FORMAT = PYTHON_CSV;',
                f"""PUT 'file://{path}{stage}.*.csv.gz' @"{stage}" parallel=8;""",
                f'USE DATABASE "{database}";',
                f'USE SCHEMA "{schema}";',
                f'USE WAREHOUSE LOAD_WH;',
                f'CREATE OR REPLACE TABLE "{schema}"."{table}"\n('+
                    col_name+
                    ') AS SELECT\n '+
                    col_num+
                    f'FROM @"{stage}" t;',
                f'DROP STAGE "{stage}";'
            ]
            #print(tgt_sql)

#####################################################################
##  Load
##    1) Upload files
##    2) Create tables on load
#####################################################################
        sf_cursor = sf.connect(**sf_dict).cursor()
        for job_name in job_list.keys():
            print(f'Uploading {job_name}')
            for stmt in tgt_sql[job_name][:7]:
                sf_cursor.execute(stmt)
        sf_cursor.close()
        
    sf_cursor = sf.connect(**sf_dict).cursor()
    for job_name in job_list.keys():
        print(f'Loading {job_name}')
        for stmt in tgt_sql[job_name][7:]:
            sf_cursor.execute(stmt)
    for job_name in job_list.keys():
        print(f'Completed {job_name}') 
    sf_cursor.close()
        
### END ###
