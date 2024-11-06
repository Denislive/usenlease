pipeline {
    agent any

    environment {
        FRONTEND_IMAGE = 'ngumonelson123/frontend-image'
        BACKEND_IMAGE = 'ngumonelson123/backend-image'
        GOOGLE_CLOUD_PROJECT = 'burnished-ether-439413-s1'
        GOOGLE_CLOUD_ZONE = 'us-central1-a'
        GOOGLE_APPLICATION_CREDENTIALS = credentials('google-cloud-service-account-json') // Use the credential ID from Jenkins
    }

    stages {
        stage('Check Shell') {
            steps {
                script {
                    echo "Checking shell being used..."
                    // Explicitly call bash to ensure we are using bash for this command
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

        stage('Build Frontend Image') {
            steps {
                script {
                    echo 'Building the frontend Docker image...'
                    sh '''#!/bin/bash
                        docker build -t ${FRONTEND_IMAGE}:latest ./frontend
                    '''
                }
            }
        }

        stage('Build Backend Image') {
            steps {
                script {
                    echo 'Building the backend Docker image...'
                    sh '''#!/bin/bash
                        docker build -t ${BACKEND_IMAGE}:latest ./backend
                    '''
                }
            }
        }

        stage('Push Frontend Image to Docker Hub') {
            steps {
                script {
                    echo 'Pushing frontend Docker image to Docker Hub...'
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh '''#!/bin/bash
                            docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}
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
                            docker push ${BACKEND_IMAGE}:latest
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
                    echo 'Running Terraform plan to see the changes...'
                    // Make sure to properly escape variables in bash syntax
                    sh '''#!/bin/bash
                        terraform plan -var="frontend_image=${FRONTEND_IMAGE}" -var="backend_image=${BACKEND_IMAGE}" -var="GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}" -var="GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}" -var="GOOGLE_CLOUD_ZONE=${GOOGLE_CLOUD_ZONE}"
                    '''
                }
            }
        }

        stage('Set Up Infrastructure with Terraform') {
            steps {
                script {
                    echo 'Setting up infrastructure with Terraform...'
                    def retries = 3
                    def success = false
                    def attempt = 1
                    while (attempt <= retries && !success) {
                        try {
                            sh '''#!/bin/bash
                                terraform apply -auto-approve -var="frontend_image=${FRONTEND_IMAGE}" -var="backend_image=${BACKEND_IMAGE}" -var="GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}" -var="GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}" -var="GOOGLE_CLOUD_ZONE=${GOOGLE_CLOUD_ZONE}"
                            '''
                            success = true
                        } catch (Exception e) {
                            if (attempt == retries) {
                                currentBuild.result = 'FAILURE'
                                echo "Terraform failed after ${retries} attempts."
                                throw e
                            }
                            echo "Attempt #${attempt} failed. Retrying..."
                            attempt++
                            sleep(time: 10, unit: 'SECONDS')  // Retry delay
                        }
                    }
                }
            }
        }

        stage('Authenticate with GCloud') {
            steps {
                withCredentials([file(credentialsId: 'google-cloud-service-account-json', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        sh '''#!/bin/bash
                            gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                            gcloud config set project ${GOOGLE_CLOUD_PROJECT}
                        '''
                    }
                }
            }
        }

        stage('Deploying to Google Cloud') {
            steps {
                script {
                    echo 'Deploying Docker containers to Google Cloud...'
                    sh '''#!/bin/bash
                        gcloud compute instances describe usenlease-docker-vm --zone=${GOOGLE_CLOUD_ZONE} || exit 1
                        gcloud compute ssh usenlease-docker-vm --zone=${GOOGLE_CLOUD_ZONE} --command="docker pull ${FRONTEND_IMAGE}:latest && docker pull ${BACKEND_IMAGE}:latest && docker run -d -p 8000:8000 ${FRONTEND_IMAGE}:latest && docker run -d -p 3000:3000 ${BACKEND_IMAGE}:latest"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!!'
        }
        failure {
            echo 'Pipeline failed.'
            emailext(
                subject: "Build Failure: ${currentBuild.fullDisplayName}",
                body: "The pipeline has failed at stage ${env.STAGE_NAME}. Please check the logs for details.",
                to: 'nelsonmbui88@gmail.com'
            )
        }
    }
}
