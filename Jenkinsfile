pipeline {
  agent any

  environment {
    IMAGE_NAME     = "lab2-app"
    CONTAINER_NAME = "lab2-app"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        sh 'git rev-parse --short HEAD || true'
      }
    }

    // 1) Télécharger les wheels (hors Docker build)
    stage('Vendor deps (download wheels)') {
      agent {
        docker {
          image 'python:3.11-slim'
          // si tu es derrière un proxy, remplace par les variables proxy au lieu de --network host
          args  '--network host'
          reuseNode true
        }
      }
      steps {
        sh '''
          echo "📦 Downloading wheels..."
          python -m venv venv
          . venv/bin/activate
          mkdir -p wheels
          pip download -r requirements.txt -d wheels --retries 5 --timeout 120
          echo "✅ Wheels ready:"
          ls -lh wheels
        '''
      }
    }

    // 2) Construire l'image en installant depuis /wheels (offline)
    stage('Build Docker Image (offline)') {
      steps {
        sh '''
          echo "🐳 Building image (offline deps)..."
          # Astuce: s'assurer que wheels/ est bien dans le contexte
          test -d wheels && test "$(ls -A wheels)" || { echo "❌ Aucun wheel téléchargé"; exit 1; }

          docker build -t ${IMAGE_NAME}:latest .
          docker images | grep ${IMAGE_NAME} || true
        '''
      }
    }

    // 3) Déployer sans rebuild (compose n'essaie pas de reconstruire)
	stage('Deploy') {
    steps {
        sh '''
        echo "🚀 Deploying with docker compose..."
        # Stop and remove all old containers for this project
        docker compose down --remove-orphans || true
        # Force remove any existing containers named lab2-app, prometheus, grafana
        docker rm -f lab2-app prometheus grafana 2>/dev/null || true
        # Bring up the stack fresh
        docker compose up -d --build
        '''
    }
}


  }

  post {
    success { echo "✅ Pipeline completed successfully!" }
    failure { echo "❌ Pipeline failed. Check logs." }
    always  { cleanWs() }
  }
}
