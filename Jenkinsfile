pipeline {
    agent {
        docker { 
            image 'python:3.9'  // Specify the Docker image
            args '-v /path/to/cache:/root/.cache'  // Optional: Caching dependencies
        }
    }

    stages {
        stage('Checkout') {  // Step to clone the repository
            steps {
                git 'https://github.com/Denislive/usenlease'  // Replace with your repository URL
            }
        }

        stage('Install Dependencies') {  // Installing the required Python packages
            steps {
                sh 'python --version'  // Checking Python version
                sh 'pip install --upgrade pip'  // Upgrading pip
                sh 'pip install -r requirements.txt'  // Installing the dependencies
            }
        }

        stage('Run Tests') {  // Running Django tests
            steps {
                sh 'python manage.py test'  // Running the test suite
            }
        }
    }

    post {
        success {
            echo 'Build succeeded!'  // Notify success
        }
        failure {
            echo 'Build failed.'  // Notify failure
        }
    }
}
