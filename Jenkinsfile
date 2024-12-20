pipeline {
    agent any
    environment {
        FRONTEND_IMAGE = 'ngumonelson123/frontend-image'
        BACKEND_IMAGE = 'ngumonelson123/backend-image'
        GOOGLE_CLOUD_PROJECT = 'burnished-ether-439413-s1'
        GOOGLE_CLOUD_ZONE = 'us-central1-a'
        GOOGLE_APPLICATION_CREDENTIALS = credentials('google-cloud-service-account-json')
        POSTGRES_USER = credentials('postgres-user')
        POSTGRES_PASSWORD = credentials('postgres-password')
        POSTGRES_DB = 'usenlease_db'
        HEROKU_BACKEND_API_KEY = credentials('heroku-backend-api-key')  // Backend Heroku API key
        HEROKU_FRONTEND_API_KEY = credentials('heroku-frontend-api-key')  // Frontend Heroku API key
        HEROKU_BACKEND_APP_NAME = 'usenlease'
        HEROKU_FRONTEND_APP_NAME = 'usenlease-v1'
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
                echo "POSTGRES_USER=${POSTGRES_USER}" >> .env
                echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" >> .env
                echo "POSTGRES_DB=${POSTGRES_DB}" >> .env
                '''
            }
        }
        stage('Check Shell and Docker Installation') {
            steps {
                script {
                    echo "Checking shell and Docker installation..."
                    sh '''#!/bin/bash
                    echo "Current shell: $SHELL"
                    docker --version || exit 1
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
        stage('Push Docker Images to Docker Hub') {
            parallel {
                stage('Push Frontend Image') {
                    steps {
                        script {
                            echo 'Pushing frontend Docker image to Docker Hub...'
                            withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                                sh '''
                                docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}
                                docker build -t ${FRONTEND_IMAGE}:v1.1.0 ./frontend
                                docker push ${FRONTEND_IMAGE}:v1.1.0
                                '''
                            }
                        }
                    }
                }
                stage('Push Backend Image') {
                    steps {
                        script {
                            echo 'Pushing backend Docker image to Docker Hub...'
                            withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                                withEnv(["SECRET_KEY=django-insecure-^5zv2&aef@n*hi0icmu7lji6bqf0r&d@!x)%*gq-e^w)2e^kl!"]) {
                                    sh '''
                                    docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}
                                    docker build --build-arg SECRET_KEY=${SECRET_KEY} -t ${BACKEND_IMAGE}:v1.1.0 -f backend/Dockerfile .
                                    docker push ${BACKEND_IMAGE}:v1.1.0
                                    '''
                                }
                            }
                        }
                    }
                }
            }
        }
        // stage('Build and Deploy with Docker Compose') {
        //     steps {
        //         script {
        //             echo 'Building and deploying Docker images using Docker Compose...'
        //             sh '''
        //             docker-compose down
        //             docker-compose pull
        //             docker-compose up --build -d
        //             '''
        //         }
        //     }
        // }
        stage('Initialize and Apply Terraform') {
            steps {
                script {
                    echo 'Initializing and applying Terraform configuration...'
                    sh '''
                    terraform init
                    terraform apply -auto-approve \
                    -var="frontend_image=${FRONTEND_IMAGE}" \
                    -var="backend_image=${BACKEND_IMAGE}" \
                    -var="GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}" \
                    -var="GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}" \
                    -var="GOOGLE_CLOUD_ZONE=${GOOGLE_CLOUD_ZONE}" \
                    -var="POSTGRES_USER=${POSTGRES_USER}" \
                    -var="POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" \
                    -var="POSTGRES_DB=${POSTGRES_DB}"
                    '''
                }
            }
        }
        stage('Heroku Backend Deployment') {
            steps {
                script {
                    echo 'Deploying backend to Heroku...'
                    withEnv(["HEROKU_API_KEY=${HEROKU_BACKEND_API_KEY}", "HEROKU_APP_NAME=${HEROKU_BACKEND_APP_NAME}"]) {
                        sh '''
                        echo "$HEROKU_API_KEY" | docker login --username=_ --password-stdin registry.heroku.com
                        docker tag ${BACKEND_IMAGE}:v1.1.0 registry.heroku.com/$HEROKU_APP_NAME/web
                        docker push registry.heroku.com/$HEROKU_APP_NAME/web
                        heroku container:release web --app $HEROKU_APP_NAME
                        '''
                    }
                }
            }
        }
        stage('Heroku Frontend Deployment') {
            steps {
                script {
                    echo 'Deploying frontend to Heroku...'
                    withEnv(["HEROKU_API_KEY=${HEROKU_FRONTEND_API_KEY}", "HEROKU_APP_NAME=${HEROKU_FRONTEND_APP_NAME}"]) {
                        sh '''
                        echo "$HEROKU_API_KEY" | docker login --username=_ --password-stdin registry.heroku.com
                        docker tag ${FRONTEND_IMAGE}:v1.1.0 registry.heroku.com/$HEROKU_APP_NAME/web
                        docker push registry.heroku.com/$HEROKU_APP_NAME/web
                        heroku container:release web --app $HEROKU_APP_NAME
                        '''
                    }
                }
            }
        }
        stage('Authenticate and Deploying to Google Cloud') {
            steps {
                script {
                    echo 'Authenticating and deploying to Google Cloud...'
                    sh '''
                    gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}

                    INSTANCE_NAME="usenlease-website"

                    INSTANCE_EXISTS=$(gcloud compute instances describe $INSTANCE_NAME --project=${GOOGLE_CLOUD_PROJECT} --zone=${GOOGLE_CLOUD_ZONE} --format="get(name)" || echo "not found")

                    if [[ "$INSTANCE_EXISTS" == "not found" ]]; then
                        echo "Instance $INSTANCE_NAME does not exist. Creating it..."
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
                            cd /home/nelson-ngumo/DevOps07/usenlease
                            docker-compose up -d'
                    else
                        echo "Instance $INSTANCE_NAME already exists. Skipping creation."
                        gcloud compute instances add-metadata $INSTANCE_NAME \
                            --project=${GOOGLE_CLOUD_PROJECT} \
                            --zone=${GOOGLE_CLOUD_ZONE} \
                            --metadata=startup-script='#!/bin/bash
                            apt-get update
                            apt-get install -y docker.io
                            systemctl enable docker
                            systemctl start docker
                            docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}
                            cd /home/nelson-ngumo/DevOps07/usenlease
                            docker-compose up -d'
                    fi
                    '''
                }
            }
        }
    }
    post {
        success {
            echo "Pipeline finished successfully!"
        }
        failure {
            echo "Pipeline failed."
        }
    }
}
