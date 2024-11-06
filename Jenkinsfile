pipeline {
    agent any

    environment {
        FRONTEND_IMAGE = 'ngumonelson123/frontend-image'  // Frontend Docker image
        BACKEND_IMAGE = 'ngumonelson123/backend-image'    // Backend Docker image
        DOCKER_USERNAME = credentials('docker-username')  // Docker Hub username (ensure this is set up in Jenkins credentials)
        DOCKER_PASSWORD = credentials('docker-password')  // Docker Hub password (ensure this is set up in Jenkins credentials)
    }

    stages {
        stage('Build Frontend Image') {
            steps {
                script {
                    echo "Building the frontend Docker image..."
                    sh """
                        docker build -t ${env.FRONTEND_IMAGE}:latest ./frontend
                    """
                }
            }
        }

        stage('Build Backend Image') {
            steps {
                script {
                    echo "Building the backend Docker image..."
                    sh """
                        docker build -t ${env.BACKEND_IMAGE}:latest ./backend
                    """
                }
            }
        }

        stage('Push Frontend Image to Docker Hub') {
            steps {
                script {
                    echo "Pushing frontend Docker image to Docker Hub..."
                    withCredentials([usernamePassword(credentialsId: 'docker-credentials', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh """
                            docker login -u ${env.DOCKER_USERNAME} -p ${env.DOCKER_PASSWORD}
                            docker push ${env.FRONTEND_IMAGE}:latest
                        """
                    }
                }
            }
        }

        stage('Push Backend Image to Docker Hub') {
            steps {
                script {
                    echo "Pushing backend Docker image to Docker Hub..."
                    withCredentials([usernamePassword(credentialsId: 'docker-credentials', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                        sh """
                            docker login -u ${env.DOCKER_USERNAME} -p ${env.DOCKER_PASSWORD}
                            docker push ${env.BACKEND_IMAGE}:latest
                        """
                    }
                }
            }
        }

        stage('Initialize Terraform') {
            steps {
                script {
                    echo "Initializing Terraform..."
                    sh "terraform init"
                }
            }
        }

        stage('Terraform Plan') {
            steps {
                script {
                    echo "Running Terraform plan to see the changes..."
                    sh """
                        terraform plan -var="frontend_image=${env.FRONTEND_IMAGE}" -var="backend_image=${env.BACKEND_IMAGE}"
                    """
                }
            }
        }

        stage('Terraform Apply') {
            steps {
                script {
                    echo "Applying Terraform configuration..."
                    sh """
                        terraform apply -auto-approve -var="frontend_image=${env.FRONTEND_IMAGE}" -var="backend_image=${env.BACKEND_IMAGE}"
                    """
                }
            }
        }

        stage('Authenticate with GCloud') {
            steps {
                script {
                    echo "Authenticating with Google Cloud..."
                    sh """
                        gcloud auth activate-service-account --key-file=${GOOGLE_CREDENTIALS}
                    """
                }
            }
        }

        stage('Deploy to Google Cloud') {
            steps {
                script {
                    echo "Deploying to Google Cloud..."
                    sh """
                        # Your deployment commands for Google Cloud here
                    """
                }
            }
        }

        stage('Clean Up') {
            steps {
                script {
                    echo "Cleaning up..."
                    // Add any necessary cleanup steps
                }
            }
        }

        stage('Post Actions') {
            steps {
                script {
                    echo "Post actions after deployment"
                    // Any post-deployment actions
                }
            }
        }
    }
}
