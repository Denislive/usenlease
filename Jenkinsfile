pipeline {
    agent {
        docker {
            image 'python:3.9' // Use the Python 3.9 image
            args '-u root' // Optional: If you need root access inside the container
        }
    }
    stages {
        stage('Build') {
            steps {
                // Clone the repository or checkout the code
                checkout scm
                
                // Build the Docker image
                sh 'docker build -t equiprenthub_image .'
            }
        }

        stage('Run Tests') {
            steps {
                // Run tests using pytest or your test runner
                sh 'docker run --rm equiprenthub_image python manage.py test'
            }
        }

        stage('Deploy') {
            steps {
                // Add your deployment steps here
                // For example, run the container in the background
                sh 'docker run -d --name equiprenthub_container -p 8000:8000 equiprenthub_image'
                echo 'Deploying application...'
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
            // Optional cleanup steps, e.g., stopping/removing containers
            sh 'docker stop equiprenthub_container || true'
            sh 'docker rm equiprenthub_container || true'
        }
    }
}
