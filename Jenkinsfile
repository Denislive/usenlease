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
        stage('Setup') {
            steps {
                echo "Creating .env file"
                sh '''
                echo "GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}" > .env
                echo "GOOGLE_CLOUD_ZONE=${GOOGLE_CLOUD_ZONE}" >> .env
                echo "GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}" >> .env
                echo "FRONTEND_IMAGE=${FRONTEND_IMAGE}" >> .env
                echo "BACKEND_IMAGE=${BACKEND_IMAGE}" >> .env
                '''
            }
        }
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
        stage('Verify docker-compose.yaml Path') {
            steps {
                script {
                    if (!fileExists('/home/nelson-ngumo/DevOps07/usenlease/docker-compose.yaml')) {
                        error 'docker-compose.yaml not found at /home/nelson-ngumo/DevOps07/usenlease!'
                    } else {
                        echo 'docker-compose.yaml found at specified path.'
                    }
                }
            }
        }

        // Stage to build and push the Docker images to Docker Hub
        stage('Push Frontend Image to Docker Hub') {
            steps {
                script {
                    echo 'Pushing frontend Docker image to Docker Hub...'
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh '''#!/bin/bash
                            docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}
                            docker build -t ${FRONTEND_IMAGE}:latest ./frontend
                            docker push ${FRONTEND_IMAGE}:latest
                        '''
                    }
                }
            }
        }

        stage('Push Backend Image to Docker Hub') {
            steps {
                script {
                    echo 'Pushing backend Docker image to Docker Hub...'
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh '''#!/bin/bash
                            docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}
                            docker build -t ${BACKEND_IMAGE}:latest ./backend
                            docker push ${BACKEND_IMAGE}:latest
                        '''
                    }
                }
            }
        }

        // Docker Compose Build and Push stage to handle images for both frontend and backend
        stage('Build and Push Docker Images') {
            steps {
                script {
                    echo 'Building and pushing Docker images using Docker Compose...'
                    sh '''#!/bin/bash
                    docker-compose -f /home/nelson-ngumo/DevOps07/usenlease/docker-compose.yaml build
                    docker-compose -f /home/nelson-ngumo/DevOps07/usenlease/docker-compose.yaml push
                    '''
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
        stage('Deploy to Google Cloud') {
            steps {
                script {
                    echo 'Deploying to Google Cloud...'
                    sh '''#!/bin/bash
                    INSTANCE_NAME="usenlease-site"
                    gcloud compute instances delete $INSTANCE_NAME --project=${GOOGLE_CLOUD_PROJECT} --zone=${GOOGLE_CLOUD_ZONE} --quiet || true
                    gcloud compute instances create $INSTANCE_NAME \
                        --project=${GOOGLE_CLOUD_PROJECT} \
                        --zone=${GOOGLE_CLOUD_ZONE} \
                        --image-family=debian-11 \
                        --image-project=debian-cloud \
                        --tags=http-server,https-server \
                        --metadata=startup-script='#!/bin/bash
                        apt-get update
                        apt-get install -y docker.io
                        systemctl enable docker
                        systemctl start docker
                        docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}
                        docker-compose -f /home/nelson-ngumo/DevOps07/usenlease/docker-compose.yaml up -d'
                    '''
                }
            }
        }

        // Build and Run should come after the deployment
        stage('Build and Run') {
            steps {
                script {
                    echo 'Building and running the Django application using Docker Compose...'
                    sh '''#!/bin/bash
                    docker-compose up --build -d
                    docker-compose exec web python manage.py migrate
                    docker-compose exec web python manage.py runserver 0.0.0.0:8000
                    '''
                }
            }
        }

        stage('Clean Up') {
            steps {
                echo "Cleaning up..."
                // Add any necessary cleanup commands here
            }
        }

        stage('Post Actions') {
            steps {
                echo "Pipeline finished successfully!"
                // Add any notifications or alerts here
            }
        }
    }
}
