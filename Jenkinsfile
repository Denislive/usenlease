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

        stage('Run Docker Commands') {
            steps {
                sh 'docker pull python:3.9'
            }
        }

        // Add additional stages for your pipeline as needed
        stage('Checkout') {
            steps {
                git 'https://github.com/Denislive/usenlease'
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh 'python -m venv .venv'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                source .venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Migrations') {
            steps {
                sh '''
                source .venv/bin/activate
                python manage.py migrate
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                source .venv/bin/activate
                python manage.py test
                '''
            }
        }

        stage('Run Server') {
            steps {
                sh '''
                source .venv/bin/activate
                gunicorn usenlease.wsgi:application --bind 0.0.0.0:8000 --daemon
                '''
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
