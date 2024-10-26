pipeline {
    agent {
        docker {
            image 'python:3.11'
            args '-u root' // Run as root if necessary
        }
    }

    environment {
        DOCKER_USERNAME = 'denislive'
    }

    stages {
        stage('Check Docker Installation') {
            steps {
                sh 'docker --version || exit 1'
                echo 'Docker is installed. Proceeding with the build...'
            }
        }

        stage('Clone Repo') {
            steps {
                echo "Cloning the repository..."
                git credentialsId: 'gitconnect', url: 'https://github.com/Denislive/usenlease.git'
            }
        }

        stage('Login to Docker') {
            steps {
                script {
                    def dockerPassword = credentials('dockerconnect')
                    sh "echo ${dockerPassword} | docker login -u ${DOCKER_USERNAME} --password-stdin"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t equiprenthub_image .'
                echo 'Docker image built successfully.'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'docker run --rm equiprenthub_image python manage.py test'
                echo 'Tests completed successfully.'
            }
        }

        stage('Deploy') {
            steps {
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
            script {
                sh 'docker stop equiprenthub_container || true'
                sh 'docker rm equiprenthub_container || true'
            }
        }
    }
}
