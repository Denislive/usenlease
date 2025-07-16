// pipeline {
//     agent any
//     environment {
//         IMAGE = 'ngumonelson123/combined-image'
//         GOOGLE_CLOUD_PROJECT = 'buoyant-song-448609-h9'
//         GOOGLE_CLOUD_ZONE = 'europe-west2-a'
//         GOOGLE_APPLICATION_CREDENTIALS = credentials('google-cloud-service-account-json')
//         POSTGRES_USER = credentials('postgres-user')
//         POSTGRES_PASSWORD = credentials('postgres-password')
//         POSTGRES_DB = 'usenlease_db'
//         HEROKU_API_KEY = credentials('heroku-backend-api-key')
//         HEROKU_APP_NAME = 'usenleaseprod'
//     }
//     stages {
//         stage('Setup') {
//             steps {
//                 echo "Creating .env file"
//                 sh '''
//                 echo "GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}" > .env
//                 echo "GOOGLE_CLOUD_ZONE=${GOOGLE_CLOUD_ZONE}" >> .env
//                 echo "GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}" >> .env
//                 echo "IMAGE=${IMAGE}" >> .env
//                 echo "POSTGRES_USER=${POSTGRES_USER}" >> .env
//                 echo "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" >> .env
//                 echo "POSTGRES_DB=${POSTGRES_DB}" >> .env
//                 '''
//             }
//         }
//         stage('Check Prerequisites') {
//             steps {
//                 script {
//                     echo "Checking shell and Docker installation..."
//                     sh '''
//                     echo "Current shell: $SHELL"
//                     docker --version || exit 1
//                     '''
//                 }
//             }
//         }
//         stage('Clone Repository') {
//             steps {
//                 echo "Cloning the repository..."
//                 git url: 'https://github.com/Denislive/usenlease.git'
//             }
//         }
//         stage('Build and Push Docker Image') {
//             steps {
//                 script {
//                     echo 'Building and pushing Docker image to Docker Hub...'
//                     withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
//                         withEnv(["SECRET_KEY=django-insecure-^5zv2&aef@n*hi0icmu7lji6bqf0r&d@!x)%*gq-e^w)2e^kl!"]) {
//                             sh '''
//                             docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}
//                             docker build --build-arg SECRET_KEY=${SECRET_KEY} -t ${IMAGE}:v1.1.0 -f Dockerfile .
//                             docker push ${IMAGE}:v1.1.0
//                             '''
//                         }
//                     }
//                 }
//             }
//         }
//         stage('Deploy to Heroku') {
//             steps {
//                 script {
//                     echo 'Deploying to Heroku...'
//                     withEnv(["HEROKU_API_KEY=${HEROKU_API_KEY}", "HEROKU_APP_NAME=${HEROKU_APP_NAME}"]) {
//                         sh '''
//                         echo "$HEROKU_API_KEY" | docker login --username=_ --password-stdin registry.heroku.com
//                         docker tag ${IMAGE}:v1.1.0 registry.heroku.com/$HEROKU_APP_NAME/web
//                         docker push registry.heroku.com/$HEROKU_APP_NAME/web
//                         heroku container:release web --app $HEROKU_APP_NAME
//                         '''
//                     }
//                 }
//             }
//         }
//         stage('Deploy to Google Cloud') {
//     steps {
//         script {
//             echo 'Deploying to Google Cloud...'
//             sh '''
//             # Check if the instance already exists
//             INSTANCE_NAME="usenlease-instance"
//             INSTANCE_EXISTS=$(gcloud compute instances list --filter="name=${INSTANCE_NAME}" --format="value(name)" --project=${GOOGLE_CLOUD_PROJECT})

//             if [ "$INSTANCE_EXISTS" = "$INSTANCE_NAME" ]; then
//                 echo "Instance ${INSTANCE_NAME} already exists. Skipping creation..."
//             else
//                 echo "Instance ${INSTANCE_NAME} does not exist. Creating it..."
//                 gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
//                 gcloud compute instances create ${INSTANCE_NAME} \
//                     --project=${GOOGLE_CLOUD_PROJECT} \
//                     --zone=${GOOGLE_CLOUD_ZONE} \
//                     --tags=http-server,https-server \
//                     --metadata=startup-script='#!/bin/bash
//                     apt-get update
//                     apt-get install -y docker.io
//                     systemctl start docker
//                     docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}
//                     docker pull ${IMAGE}:v1.1.0
//                     docker-compose up -d'
//             fi
//             '''
//         }
//     }
// }

//     }
//     post {
//         success {
//             echo "Pipeline completed successfully!"
//         }
//         failure {
//             echo "Pipeline failed."
//         }
//     }
// }