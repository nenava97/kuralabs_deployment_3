# kuralabs_deployment_3
Deploying a flask application with two EC2s on two different VPCs utilizing a Jenkins server on one to build and test code from the GitHub repository and on the other utilizing a jenkins agent and node to deploy code with nginx and gunicorn.

<img width="680" alt="Screen Shot 2022-10-15 at 8 48 53 AM" src="https://user-images.githubusercontent.com/108698688/195987273-ebaf97bc-eefd-4941-9c68-01cfc4217f22.png">

## Configure 2 Amazon EC2s with Jenkins server and agent respectfully

1. Create first EC2 in public subnet on default VPC with Jenkins server

- run the following script to install packages needed for Jenkins (including java)

```
#!/bin/bash
sudo apt update
sudo apt install python3.10-venv
sudo apt -y install openjdk-11-jre
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee \ /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \ https://pkg.jenkins.io/debian-stable binary/ | sudo tee \ /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get -y install jenkins
sudo systemctl enable jenkins
sudo systemctl start jenkins
```

- Configure nginx file to ensure it will listen to port 5000 for gunicorn and then run it on http://127.0.0.1:8000

```
sudo nano /etc/nginx/sites-enabled/default
```

```diff
- Issues:
- needed to restart nginx after edit nginx file for changes to apply
- needed to install python3.10-venv as environment on Jenkins server EC2 as was receiving error in test stage
```

<img width="536" alt="Screen Shot 2022-10-15 at 8 45 02 AM" src="https://user-images.githubusercontent.com/108698688/195987192-f364101e-81ac-49cb-9f55-ad757d06d3e4.png">

- configure jenkins by navigating to http://PublicIPv4:8080

```diff
- Issue:
- make sure to not do https as will look for encryption and verification that have not configured and therefore will not load 
```

- create a new node awsDeploy and add permanent agent which will be launched on EC2 made in public subnet of Kura VPC via SSH and private RSA kay (aka pem file)

```diff
- Issue:
- after creating Jenkins SSH username with private key credential make sure to select it when configuring the awsDeploy node 
```

- add Pipleline Keep Running Step plugin

2. Create second EC2 in public subnet of Kura VPC with Jenkins agent

- ports 22 must be open to ssh from other EC2 instance and 5000 must be open for nginx to find gunicorn 

```diff
- Issue:
- when configuring the EC2 instance make sure to enable auto-assign public IP address creation as it will default to disable when changing your VPC from default to Kura VPC
```

- run the following script to install packages needed for Jenkins agent (including programming languages java and python; nginx, gunicorn and the flask app provide the web server gateway interface and framework for the application to run on the webpage)

```
#!/bin/bash
sudo apt update
sudo apt install default-jre
sudo apt install python3-pip
sudo apt install python3.10-venv
sudo apt install nginx
```

## Add slack notification system and additional testing

1. Add slack notification system plugin to Jenkins 
Navigate to manage Jenkins and configure system to add Slack workspace (https://kura-labs.slack.com) and add secret text credential which is Slack integration token credential ID 

<img width="574" alt="Screen Shot 2022-10-15 at 8 51 14 AM" src="https://user-images.githubusercontent.com/108698688/195987353-834e6907-a5c7-4ca5-8c51-eae2a3afa07a.png">

```diff
- Issue:
- need to grab user id (starting with U) from slack profile of member would like notifications be sent to, just a username will not work
- add Global notifications checking off what parts of pipeline would like to be notified on (build success, build fail, etc)
```

2. Add test in code stored in GitHub repository that will check if a get request to the application web page returns a status code HTTP 200 OK (success) and if a post request returns a HTTP 405 Method Not Allowed (error)

```
from application import app
#test
def test_home_page():
    response = app.test_client().get('/')
    assert response.status_code == 200

def test_home_page():
    response = app.test_client().post('/')
    assert response.status_code == 405
```

<img width="615" alt="Screen Shot 2022-10-15 at 8 52 07 AM" src="https://user-images.githubusercontent.com/108698688/195987382-fb483712-4f68-47d7-ae9e-adbcf8aa402c.png">

## Improvements
- to amplify security of application it would be best practice to have a private subnet and private route table added to ensure there is no unwanted inbound traffic reaching the backend of the application directly 
- for the sake of repetition and risk management it would be best to have two availability zones where the application was hosted on in case on region goes down 
