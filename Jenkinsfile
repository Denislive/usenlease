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
        stage('Check Docker Installation') {
            steps {
                script {
                    // Verify Docker installation
                    sh 'docker --version || exit 1'
                    echo 'Docker is installed. Proceeding with the build...'
                }
            }
        }

        stage('Check GCloud Installation') {
            steps {
                script {
                    // Define Google Cloud SDK path
                    def gcloudPath = '/home/nelson-ngumo/google-cloud-sdk/bin'
                    def currentPath = sh(script: 'echo $PATH', returnStdout: true).trim()

                    // Only append if it's not already in the PATH
                    if (!currentPath.contains(gcloudPath)) {
                        withEnv(["PATH=${gcloudPath}:${env.PATH}"]) {
                            // Ensure gcloud has execute permissions
                            sh "chmod +x ${gcloudPath}/gcloud"
                            sh 'gcloud --version || exit 1'
                            echo 'Google Cloud SDK is installed. Proceeding with the deployment...'
                        }
                    } else {
                        echo 'Google Cloud SDK path already set. Proceeding...'
                        // Ensure gcloud has execute permissions if path is already set
                        sh "chmod +x ${gcloudPath}/gcloud"
                        sh 'gcloud --version || exit 1'
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
                    sh "docker build -t ${FRONTEND_IMAGE}:latest ./frontend"
                }
            }
        }

        stage('Build Backend Image') {
            steps {
                script {
                    echo 'Building the backend Docker image...'
                    sh "docker build -t ${BACKEND_IMAGE}:latest ./backend"
                }
            }
        }

        stage('Push Frontend Image to Docker Hub') {
            steps {
                script {
                    echo 'Pushing frontend Docker image to Docker Hub...'
                    sh "docker push ${FRONTEND_IMAGE}:latest"
                }
            }
        }

        stage('Push Backend Image to Docker Hub') {
            steps {
                script {
                    echo 'Pushing backend Docker image to Docker Hub...'
                    sh "docker push ${BACKEND_IMAGE}:latest"
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
                            // Apply Terraform to create the infrastructure
                            sh 'terraform apply -auto-approve -var="frontend_image=${FRONTEND_IMAGE}" -var="backend_image=${BACKEND_IMAGE}"'
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

        stage('Deploy to Google Cloud') {
            steps {
                script {
                    echo 'Deploying Docker containers to Google Cloud...'
                    // Assuming Terraform has set up the VM and firewall
                    sh '''
                        gcloud compute instances describe my-docker-vm --zone=${GOOGLE_CLOUD_ZONE} || exit 1
                        gcloud compute ssh my-docker-vm --zone=${GOOGLE_CLOUD_ZONE} --command="
                            docker pull ${FRONTEND_IMAGE}:latest
                            docker pull ${BACKEND_IMAGE}:latest
                            docker run -d -p 8000:8000 ${FRONTEND_IMAGE}:latest
                            docker run -d -p 3000:3000 ${BACKEND_IMAGE}:latest"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
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
