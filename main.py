import os
import requests
import json

from elasticsearch import Elasticsearch

def main():
    
    #Execution context variables
    GITHUB_REF = os.environ["GITHUB_REF"]          
    GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]        
    GITHUB_RUN_ID = os.environ["GITHUB_RUN_ID"]         
    GITHUB_API_URL = os.environ["GITHUB_API_URL"]
    
    #User provided variables
    INPUT_JOB = os.environ.get("INPUT_JOB")
    GITHUB_TOKEN = os.environ.get("INPUT_GITHUB-TOKEN")
    ELASTIC_USER = os.environ.get("INPUT_ELASTIC-USER")
    ELASTIC_PSW = os.environ.get("INPUT_ELASTIC-PSW")
    ELASTIC_HOST = os.environ.get("INPUT_ELASTIC-HOST")
    ELASTIC_PORT = os.environ.get("INPUT_ELASTIC-PORT")                    
    ELASTIC_INDEX = os.environ.get("INPUT_ELASTIC-INDEX")        

    try:
        assert (INPUT_JOB not in(None, '') and 
            GITHUB_TOKEN not in(None, '') and 
            ELASTIC_USER not in(None, '') and 
            ELASTIC_PSW not in(None, '') and 
            ELASTIC_HOST not in(None, '') and
            ELASTIC_PORT not in(None, '') and
            ELASTIC_INDEX not in(None, ''))
    except:
        output = f"Some required variables are not set"       
        
        print(f"Error: {output}")

        print(f"::set-output name=result::{output}")        

        return
           
    url = "{url}/repos/{repo}/actions/runs/{run_id}/jobs".format(url=GITHUB_API_URL,repo=GITHUB_REPOSITORY,run_id=GITHUB_RUN_ID)    
    
    try:

        r = requests.get(url, auth=('username',GITHUB_TOKEN))

    except requests.exceptions.HTTPError as errh:
        output = "GITHUB API Http Error:" + str(errh)
        print(f"Error: {output}")        
        print(f"::set-output name=result::{output}")        
        return        
    except requests.exceptions.ConnectionError as errc:
        output = "GITHUB API Error Connecting:" + str(errc)        
        print(f"Error: {output}")        
        print(f"::set-output name=result::{output}")        
        return                
    except requests.exceptions.Timeout as errt:
        output = "Timeout Error:" + str(errt)        
        print(f"Error: {output}")        
        print(f"::set-output name=result::{output}")        
        return                
    except requests.exceptions.RequestException as err:
        output = "GITHUB API Non catched error conecting:" + str(err)    
        print(f"Error: {output}")            
        print(f"::set-output name=result::{output}")        
        return                       
   
    response = json.loads(r.text)

    try:      
        es = Elasticsearch(
            [ELASTIC_HOST],
            http_auth=(ELASTIC_USER, ELASTIC_PSW),
            scheme="https",
            port=ELASTIC_PORT,
        )

    except ValueError as e:
        output = f"Error connecting to Elastic: {str(e)}"       
        print(f"Error: {output}")
        print(f"::set-output name=result::{output}")        
        return
          
    for job in response['jobs']:
        if job['name'] == INPUT_JOB:
            try:
                res = es.index(index=ELASTIC_INDEX, id=job['id'], body=job)
            except ValueError as e:
                output = f"Error inserting to Elastic {str(e)}"       
                print(f"Error: {output}")            
                print(f"::set-output name=result::{output}")        
                return            

            print("Job " + str(job['name']) + " inserted with result: " + str(res['result']))           
                
    output = f"Process completed!"       

    print(f"::set-output name=result::{output}")


if __name__ == "__main__":
    main()
