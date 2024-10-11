pipeline {
    agent any

    stages {
        stage('Install Docker if not found') {
            steps {
                sh '''
                if ! [ -x "$(command -v docker)" ]; then
                  echo "Docker not installed. Installing Docker..."
                  curl -fsSL https://get.docker.com -o get-docker.sh
                  sh get-docker.sh
                else
                  echo "Docker is already installed."
                fi
                '''
            }
        }

        stage('Run Docker Commands') {
            steps {
                sh 'docker pull python:3.9'
            }
        }

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
