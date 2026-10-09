pipeline {
    
    agent {
        docker {
            image 'ghcr.io/astral-sh/uv:python3.12-bookworm-slim'
        }
    }

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