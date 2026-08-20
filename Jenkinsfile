pipeline {
    agent any
    environment {
        IMAGE_NAME = "notes-vault-app"
        CONTAINER_NAME = "notes-vault-container"
        HOST_PORT = "8000"
    }

    stages {
        stage('checkout code'){
            steps{
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME} ."
                }
            }
        }
        stage('Deploy application') {
            steps {
                script {
                    //stop and remove old container if it exists
                    sh "docker stop ${CONTAINER_NAME} || true"
                    sh "docker rm ${CONTAINER_NAME} || true"

                    // Run the new container with a mounted volume for data persistence
                    sh "docker run -d -p ${HOST_PORT}:8000 --name ${CONTAINER_NAME} -v notes-data:/app ${IMAGE_NAME}"
                }
            }
        }
    }
}