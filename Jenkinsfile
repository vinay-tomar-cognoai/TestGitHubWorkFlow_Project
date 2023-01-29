pipeline {
        agent any
	parameters {
        	string(defaultValue: "v6.4-dev", description: 'pulling branch', name: 'BRANCH')
        }

        stages {    
                stage('Auto pull code and deploy') {
                   steps{
                         script {
                                sh '''  
					#!/bin/bash
					TAG=$BRANCH
					ssh ubuntu@3.7.80.99 "cd /home/ubuntu/EasyChatDev/EasyChat && git stash"	
					
					if ssh ubuntu@3.7.80.99 "cd /home/ubuntu/EasyChatDev/EasyChat && git pull origin $TAG | grep 'Automatic merge failed; fix conflicts and then commit the result'"
					then
						echo "ERROR: conflict issue. Please resolve the conflict"
    						exit 1
					else
						echo "successfully pull"	
					fi
					
					ssh ubuntu@3.7.80.99 "source /home/ubuntu/EasyChatDev/venv_3_9/bin/activate && pip install -r /home/ubuntu/EasyChatDev/EasyChat/requirements.txt"

					ssh ubuntu@3.7.80.99 "sudo chown -R ubuntu:ubuntu /home/ubuntu/EasyChatDev/EasyChat/log"

					ssh ubuntu@3.7.80.99 "source /home/ubuntu/EasyChatDev/venv_3_9/bin/activate && python /home/ubuntu/EasyChatDev/EasyChat/manage.py makemigrations --noinput"

					ssh ubuntu@3.7.80.99 "sudo chown -R ubuntu:ubuntu /home/ubuntu/EasyChatDev/EasyChat/log"

					ssh ubuntu@3.7.80.99 "source /home/ubuntu/EasyChatDev/venv_3_9/bin/activate && python /home/ubuntu/EasyChatDev/EasyChat/manage.py migrate --noinput"

					ssh ubuntu@3.7.80.99 "sudo apt install nodejs -y"

					ssh ubuntu@3.7.80.99 "cd /home/ubuntu/EasyChatDev/EasyChat/LiveChatApp && npm install && npm run build"

					ssh ubuntu@3.7.80.99 "source /home/ubuntu/EasyChatDev/venv_3_9/bin/activate && python /home/ubuntu/EasyChatDev/EasyChat/manage.py collectstatic --noinput"

					ssh ubuntu@3.7.80.99 "sudo systemctl restart gunicorn-dev.service"

					ssh ubuntu@3.7.80.99 "source /home/ubuntu/EasyChatDev/venv_3_9/bin/activate && python /home/ubuntu/EasyChatDev/EasyChat/manage.py crontab remove"

					ssh ubuntu@3.7.80.99 "source /home/ubuntu/EasyChatDev/venv_3_9/bin/activate && python /home/ubuntu/EasyChatDev/EasyChat/manage.py crontab add"

                    ssh ubuntu@3.7.80.99 "sudo systemctl restart scheduler_dev.service"

                    ssh ubuntu@3.7.80.99 "sudo systemctl restart scheduler_livechat_dev.service"

					ssh ubuntu@3.7.80.99 "sudo systemctl restart campaign_analytics_scheduler.service"

                                '''
                        }
                  }
                }
		
        }
	post {
		// success{
		// 	mail to: 'tech@allincall.in',
  //            		subject: "Jenkins auto-deployment successful: v6.4-dev : easychat-dev.allincall.in",
  //            		body: "Dear team, \n\n v6.4-dev branch latest code is hosted on easychat-dev.allincall.in. You can start testing of latest code. In case, you face any issue related to code deployment, please send email at hitesh.kumawat@allincall.in"
		// }
    		failure {
        		mail to: 'engineering-team@getcogno.ai',
             		subject: "Jenkins auto-deployment failed: v6.4-dev : easychat-dev.allincall.in",
             		body: "Dear team, \n\n Auto-deployment of v6.4-dev branch is failed on easychat-dev.allincall.in. Please send email at hitesh.kumawat@getcogno.ai"
    		}
	}

}