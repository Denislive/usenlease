pipeline {
    agent any

    stages {
        stage('Check Docker Installation') {
            steps {
                script {
                    def dockerInstalled = sh(script: 'command -v docker', returnStatus: true) == 0
                    if (!dockerInstalled) {
                        error "Docker is not installed on this system."
                    } else {
                        echo "Docker is already installed."
                    }
                }
            }
        }

        stage('Checkout') {
            steps {
                git 'https://github.com/Denislive/usenlease'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t usenlease-app .'
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    // Run the container in detached mode and map port 8000
                    sh 'docker run -d -p 8000:8000 --name usenlease-container usenlease-app'
                }
            }
        }

        stage('Run Tests in Docker') {
            steps {
                script {
                    // Run tests inside the Docker container
                    sh 'docker exec usenlease-container python manage.py test'
                }
            }
        }
    }

    post {
        success {
            echo 'Build succeeded!'
        }
        failure {
            echo 'Build failed.'
        }
        always {
            echo 'Stopping and cleaning up Docker container...'
            sh 'docker stop usenlease-container || echo "No running container to stop"'
            sh 'docker rm usenlease-container || echo "No container to remove"'
        }
    }
}
