pipeline {
    agent any
    stages {
        stage('Install dependencies') {
            steps {
                sh 'uv sync'
            }
        }

        stage('Run tests') {
            steps {
                sh 'uv test'
            }
        }

        stage('Build') {
            steps {
                sh 'uv build'
            }
        }
    }
}