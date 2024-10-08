pipeline {
    agent {
        docker {
            image 'python:3.2'  // Use the appropriate Python version
            args '-v /var/run/docker.sock:/var/run/docker.sock' // If you need to run Docker inside the container
        }
    }

    environment {
        VIRTUAL_ENV = '.venv'
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/Denislive/usenlease'
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh 'python -m venv $VIRTUAL_ENV'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                source $VIRTUAL_ENV/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Migrations') {
            steps {
                sh '''
                source $VIRTUAL_ENV/bin/activate
                python manage.py migrate
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                source $VIRTUAL_ENV/bin/activate
                python manage.py test
                '''
            }
        }

        stage('Run Server') {
            steps {
                sh '''
                source $VIRTUAL_ENV/bin/activate
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
