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
                        docker build -t ${env.FRONTEND_IMAGE}:latest ./frontend
                    '''
                }
            }
        }

        stage('Build Backend Image') {
            steps {
                script {
                    echo 'Building the backend Docker image...'
                    sh '''#!/bin/bash
                        docker build -t ${env.BACKEND_IMAGE}:latest ./backend
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
                            docker login -u ${env.DOCKER_USERNAME} -p ${env.DOCKER_PASSWORD}
                            docker push ${env.FRONTEND_IMAGE}:latest
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
                            docker login -u ${env.DOCKER_USERNAME} -p ${env.DOCKER_PASSWORD}
                            docker push ${env.BACKEND_IMAGE}:latest
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
                    // Run terraform plan to preview the changes, passing the GOOGLE_APPLICATION_CREDENTIALS variable
                    sh '''#!/bin/bash
                        terraform plan -var="GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}" \
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
                    // Apply the Terraform plan to provision the resources
                    sh '''#!/bin/bash
                        terraform apply -auto-approve \
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
                    echo 'Authenticating with GCloud...'
                    // Authenticate with Google Cloud using the service account key
                    sh '''#!/bin/bash
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GOOGLE_CLOUD_PROJECT}
                    '''
                }
            }
        }

        stage('Deploy to Google Cloud') {
            steps {
                script {
                    echo 'Deploying to Google Cloud...'
                    // Assuming you're deploying Docker images or resources, like the Compute instance
                    sh '''#!/bin/bash
                        # Example: Deploying a Docker container to a Google Compute Engine VM
                        # This could involve gcloud commands, docker run, or any other required steps
                        gcloud compute instances create ${env.FRONTEND_IMAGE}-vm \
                            --image-family debian-11 --image-project debian-cloud \
                            --zone ${GOOGLE_CLOUD_ZONE} \
                            --tags http-server,https-server \
                            --metadata startup-script="#!/bin/bash
                            docker pull ${env.FRONTEND_IMAGE}:latest
                            docker run -d -p 80:80 ${env.FRONTEND_IMAGE}:latest"
                    '''
                }
            }
        }

        stage('Clean Up') {
            steps {
                script {
                    echo 'Cleaning up...'
                    // Example cleanup steps, if necessary, like removing temporary files or resources
                    sh '''#!/bin/bash
                        docker system prune -f
                    '''
                }
            }
        }

        stage('Post Actions') {
            steps {
                echo 'Sending email notification on failure...'
                emailext(
                    to: 'nelsonmbui88@gmail.com',
                    subject: "Jenkins Pipeline: ${currentBuild.currentResult}",
                    body: "The Jenkins pipeline has finished with status: ${currentBuild.currentResult}."
                )
            }
        }
    }

    post {
        failure {
            echo "Pipeline failed!"
            // More failure handling or notifications can go here
        }
        success {
            echo "Pipeline succeeded!"
        }
    }
}
