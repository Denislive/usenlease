pipeline {
    agent any

    stages {
        stage('Install Docker') {
            steps {
                script {
                    def dockerInstalled = sh(script: 'command -v docker', returnStatus: true) == 0
                    if (!dockerInstalled) {
                        echo "Docker is not installed. Installing Docker..."
                        sh '''
                        if [ -x "$(command -v apt-get)" ]; then
                            sudo apt-get update
                            sudo apt-get install -y docker.io
                            sudo systemctl start docker
                        elif [ -x "$(command -v yum)" ]; then
                            sudo yum install -y docker
                            sudo systemctl start docker
                        else
                            echo "Unsupported package manager. Please install Docker manually."
                            exit 1
                        fi
                        '''
                    } else {
                        echo "Docker is already installed."
                    }
                }
            }
        }
        
        stage('Run Docker Commands') {
            steps {
                echo "Pulling Docker image..."
                sh 'docker pull python:3.9'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                sh 'docker build -t usenlease-app .'
            }
        }

        stage('Run Docker Container') {
            steps {
                echo "Running Docker container..."
                sh 'docker run -d -p 8000:8000 --name usenlease-container usenlease-app'
            }
        }

        stage('Run Tests in Docker') {
            steps {
                echo "Running tests inside Docker..."
                sh 'docker exec usenlease-container python manage.py test'
            }
        }
    }

    post {
        always {
            echo "Stopping and cleaning up Docker container..."
            sh 'docker stop usenlease-container || echo "No running container to stop"'
            sh 'docker rm usenlease-container || echo "No container to remove"'
        }
    }
}
