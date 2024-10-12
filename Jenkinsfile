pipeline {
    agent {
        docker { 
            image 'python:3.9' 
            args '-u root' // Optional: If you need root access inside the container
        }
    }
    stages {
        stage('Run in Docker Container') {
            steps {
                // Run commands inside the Docker container
                sh 'python --version'
                sh 'pip install -r requirements.txt'
                sh 'python manage.py test'
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
    }
}
