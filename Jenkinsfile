pipeline {
    agent {
        docker {
            image 'python:3.11'
            args '-u root' // Run as root if necessary
        }
    }

    stages {
        stage('Check Docker Installation') {
            steps {
                sh 'docker --version || exit 1'
                echo 'Docker is installed. Proceeding with the build...'
            }
        }

        stage('Clone repo') {
            steps {
                echo "Clone this repository..."
                git credentialsId: 'gitconnect-jenkins', url: 'https://github.com/Denislive/usenlease.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                // Build the Docker image
                sh 'docker build -t equiprenthub_image .'
                echo 'Docker image built successfully.'
            }
        }

        stage('Run Tests') {
            steps {
                // Run tests using Docker
                sh 'docker run --rm equiprenthub_image python manage.py test'
                echo 'Tests completed successfully.'
            }
        }

        stage('Deploy') {
            steps {
                // Deploy the application by running the Docker container in detached mode
                sh 'docker run -d --name equiprenthub_container -p 8000:8000 equiprenthub_image'
                echo 'Application deployed successfully.'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed.'
        }
        always {
            // Cleanup: Stop and remove the container if it exists
            sh 'docker stop equiprenthub_container || true'
            sh 'docker rm equiprenthub_container || true'
        }
    }
}