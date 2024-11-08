pipeline { 
    agent any 
    environment { 
        FRONTEND_IMAGE = 'ngumonelson123/frontend-image'
        BACKEND_IMAGE = 'ngumonelson123/backend-image'
        GOOGLE_CLOUD_PROJECT = 'burnished-ether-439413-s1'
        GOOGLE_CLOUD_ZONE = 'us-central1-a'
        GOOGLE_APPLICATION_CREDENTIALS = credentials('google-cloud-service-account-json')
    }
    stages {
        stage('Check Shell') { 
            steps { 
                script { 
                    echo "Checking shell being used..."
                    sh '''#!/bin/bash
                    echo "Current shell: $SHELL"
                    ''' 
                } 
            } 
        }
        stage('Check Docker Installation') { 
            steps { 
                script { 
                    echo 'Checking if Docker is installed...'
                    sh '''#!/bin/bash
                    docker --version || exit 1
                    ''' 
                } 
            } 
        }
        stage('Check Docker Compose Installation') { 
            steps { 
                script { 
                    echo 'Checking if Docker Compose is installed...'
                    sh '''#!/bin/bash
                    docker-compose --version || exit 1
                    ''' 
                } 
            } 
        }
        stage('Check GCloud Installation') { 
            steps { 
                script { 
                    echo 'Checking if GCloud is installed...'
                    sh '''#!/bin/bash
                    gcloud --version || exit 1
                    ''' 
                } 
            } 
        }
        stage('Clone Repo') { 
            steps { 
                echo "Cloning the repository..."
                git url: 'https://github.com/Denislive/usenlease.git'
            } 
        }
        stage('Build and Push Images') {
            steps {
                script {
                    echo 'Building and pushing Docker images using Docker Compose...'
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh '''#!/bin/bash
                        docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}
                        docker-compose -f docker-compose.yml build
                        docker-compose -f docker-compose.yml push
                        '''
                    }
                }
            }
        }
        stage('Initialize Terraform') { 
            steps { 
                script { 
                    echo 'Initializing Terraform...'
                    sh '''#!/bin/bash
                    terraform init
                    ''' 
                } 
            } 
        }
        stage('Terraform Plan') { 
            steps { 
                script { 
                    echo 'Running Terraform plan to see the changes.....'
                    sh '''#!/bin/bash
                    terraform plan \
                        -var="frontend_image=${FRONTEND_IMAGE}" \
                        -var="backend_image=${BACKEND_IMAGE}" \
                        -var="GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}" \
                        -var="GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}" \
                        -var="GOOGLE_CLOUD_ZONE=${GOOGLE_CLOUD_ZONE}"
                    ''' 
                } 
            } 
        }
        stage('Terraform Apply') { 
            steps { 
                script { 
                    echo 'Applying Terraform changes...'
                    sh '''#!/bin/bash
                    terraform apply -auto-approve \
                        -var="frontend_image=${FRONTEND_IMAGE}" \
                        -var="backend_image=${BACKEND_IMAGE}" \
                        -var="GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}" \
                        -var="GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}" \
                        -var="GOOGLE_CLOUD_ZONE=${GOOGLE_CLOUD_ZONE}"
                    ''' 
                } 
            } 
        }
        stage('Authenticate with GCloud') { 
            steps { 
                script { 
                    echo 'Authenticating with Google Cloud...'
                    sh '''#!/bin/bash
                    gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                    ''' 
                } 
            } 
        }
        stage('Deploy using Docker Compose on GCloud') {
            steps {
                script {
                    echo 'Deploying services to Google Cloud using Docker Compose...'
                    sh '''#!/bin/bash
                    INSTANCE_NAME="usenlease-website"
                    gcloud compute instances delete $INSTANCE_NAME --project=${GOOGLE_CLOUD_PROJECT} --zone=${GOOGLE_CLOUD_ZONE} --quiet || true
                    gcloud compute instances create $INSTANCE_NAME \
                        --project=${GOOGLE_CLOUD_PROJECT} \
                        --zone=${GOOGLE_CLOUD_ZONE} \
                        --image-family=debian-11 \
                        --image-project=debian-cloud \
                        --tags=http-server,https-server \
                        --metadata=startup-script='#!/bin/bash
                        apt-get update
                        apt-get install -y docker.io docker-compose
                        systemctl enable docker
                        systemctl start docker
                        cd /path/to/your/cloned/repo
                        docker-compose up -d
                        '''
                }
            }
        }
        stage('Clean Up') { 
            steps { 
                echo "Cleaning up..."
            } 
        }
        stage('Post Actions') { 
            steps { 
                echo "Pipeline finished successfully!"
            } 
        }
    }
}
