pipeline {
  agent any
  options { timestamps() }

  environment {
    IMAGE = 'thefallak/lab-fastapi-arith'
    TRIVY_CACHE = "${env.WORKSPACE}/.trivy"
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Tests + SAST (container Python)') {
      steps {
        sh '''
          set -eux
          mkdir -p reports
          docker run --rm -v "$PWD":"$PWD" -w "$PWD" python:3.11-slim bash -lc '
            pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt &&
            pytest -q --junitxml=reports/junit.xml &&
            bandit -r src -ll -f txt -o reports/bandit.txt &&
            pip freeze --exclude-editable > requirements.lock &&
            safety check -r requirements.lock --full-report --exit-code > reports/safety.txt
          '
        '''
      }
      post {
        always {
          junit 'reports/junit.xml'
          archiveArtifacts artifacts: 'reports/**', fingerprint: true
        }
      }
    }

    stage('Build image') {
      steps {
        sh 'docker build -t $IMAGE:latest -t $IMAGE:$BUILD_NUMBER .'
      }
    }

    stage('Scan image (Trivy)') {
      steps {
        sh '''
          set -eux
          mkdir -p "$TRIVY_CACHE"
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "$TRIVY_CACHE":/root/.cache/ \
            aquasec/trivy:latest image --severity HIGH,CRITICAL --exit-code 1 $IMAGE:latest
        '''
      }
    }

    stage('Déploiement local') {
      steps {
        sh '''
          set -eux
          if [ -f docker-compose.yml ] || [ -f docker-compose.yaml ] || [ -f compose.yml ] || [ -f compose.yaml ]; then
            docker compose up -d
          else
            docker rm -f lab1 || true
            docker run -d --name lab1 -p 8000:8000 $IMAGE:latest
          fi
          sleep 2
          curl -fsS http://localhost:8000/health
        '''
      }
    }
  }
}
