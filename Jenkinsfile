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
        stage('Check Docker Installation') {
            steps {
                script {
                    // Use bash explicitly to check if Docker is installed
                    sh 'bash -c "docker --version || exit 1"'
                    echo 'Docker is installed. Proceeding with the build...'
                }
            }
        }

        stage('Check GCloud Installation') {
            steps {
                script {
                    // Define Google Cloud SDK path
                    def gcloudPath = '/usr/local/bin/google-cloud-sdk/bin'
                    def currentPath = sh(script: 'echo $PATH', returnStdout: true).trim()

                    // Only append if it's not already in the PATH
                    if (!currentPath.contains(gcloudPath)) {
                        withEnv(["PATH=${gcloudPath}:${env.PATH}"]) {
                            // Ensure gcloud has execute permissions
                            sh "chmod +x ${gcloudPath}/gcloud"
                            // Use bash explicitly here
                            sh 'bash -c "gcloud --version || exit 1"'
                            echo 'Google Cloud SDK is installed. Proceeding with the deployment...'
                        }
                    } else {
                        echo 'Google Cloud SDK path already set. Proceeding...'
                        // Ensure gcloud has execute permissions if path is already set
                        sh "chmod +x ${gcloudPath}/gcloud"
                        // Use bash explicitly here
                        sh 'bash -c "gcloud --version || exit 1"'
                    }
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
                    // Use bash explicitly here to build the Docker image
                    sh "bash -c 'docker build -t ${FRONTEND_IMAGE}:latest ./frontend'"
                }
            }
        }

        stage('Build Backend Image') {
            steps {
                script {
                    echo 'Building the backend Docker image...'
                    // Use bash explicitly here to build the Docker image
                    sh "bash -c 'docker build -t ${BACKEND_IMAGE}:latest ./backend'"
                }
            }
        }

        stage('Push Frontend Image to Docker Hub') {
            steps {
                script {
                    echo 'Pushing frontend Docker image to Docker Hub...'
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh "docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}"
                        // Use bash explicitly here to push Docker image
                        sh "bash -c 'docker push ${FRONTEND_IMAGE}:latest'"
                    }
                }
            }
        }

        stage('Push Backend Image to Docker Hub') {
            steps {
                script {
                    echo 'Pushing backend Docker image to Docker Hub...'
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh "docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}"
                        // Use bash explicitly here to push Docker image
                        sh "bash -c 'docker push ${BACKEND_IMAGE}:latest'"
                    }
                }
            }
        }

        stage('Initialize Terraform') {
            steps {
                script {
                    echo 'Initializing Terraform...'
                    // Run terraform init to initialize the working directory
                    sh 'bash -c "terraform init"'
                }
            }
        }

        stage('Terraform Plan') {
            steps {
                script {
                    echo 'Running Terraform plan to see the changes...'
                    // Use bash explicitly to run terraform plan
                    sh 'bash -c "terraform plan -var=\\"frontend_image=${FRONTEND_IMAGE}\\" -var=\\"backend_image=${BACKEND_IMAGE}\\" -var=\\"GOOGLE_APPLICATION_CREDENTIALS=${env.GOOGLE_APPLICATION_CREDENTIALS}\\" -var=\\"GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}\\" -var=\\"GOOGLE_CLOUD_ZONE=${GOOGLE_CLOUD_ZONE}\\""'
                }
            }
        }

        stage('Set Up Infrastructure with Terraform') {
            steps {
                script {
                    def retries = 3
                    def success = false
                    def attempt = 1
                    while (attempt <= retries && !success) {
                        try {
                            echo "Attempt #${attempt} to apply Terraform..."
                            // Use bash explicitly here to run terraform apply
                            sh 'bash -c "terraform apply -auto-approve -var=\\"frontend_image=${FRONTEND_IMAGE}\\" -var=\\"backend_image=${BACKEND_IMAGE}\\" -var=\\"GOOGLE_APPLICATION_CREDENTIALS=${env.GOOGLE_APPLICATION_CREDENTIALS}\\" -var=\\"GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}\\" -var=\\"GOOGLE_CLOUD_ZONE=${GOOGLE_CLOUD_ZONE}\\""'
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
                        // Authenticate with gcloud using the service account key
                        sh 'bash -c "gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}"'
                        sh 'bash -c "gcloud config set project ${GOOGLE_CLOUD_PROJECT}"'
                    }
                }
            }
        }

        stage('Deploying to Google Cloud') {
            steps {
                script {
                    echo 'Deploying Docker containers to Google Cloud...'
                    // Assuming Terraform has set up the VM and firewall
                    sh '''
                        bash -c "gcloud compute instances describe usenlease-docker-vm --zone=${GOOGLE_CLOUD_ZONE} || exit 1"
                        bash -c "gcloud compute ssh usenlease-docker-vm --zone=${GOOGLE_CLOUD_ZONE} --command=\"
                            docker pull ${FRONTEND_IMAGE}:latest
                            docker pull ${BACKEND_IMAGE}:latest
                            docker run -d -p 8000:8000 ${FRONTEND_IMAGE}:latest
                            docker run -d -p 3000:3000 ${BACKEND_IMAGE}:latest\""
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
