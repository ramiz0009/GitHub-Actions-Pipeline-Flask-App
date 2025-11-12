pipeline {
  agent any

  parameters {
    string(name: 'DEPLOY_HOST', defaultValue: 'YOUR_EC2_IP_OR_HOST', description: 'EC2 host for deployment (ip or dns)')
  }

  environment {
    DEPLOY_USER = "ubuntu"
    DEPLOY_TARGET_BASE = "/var/www/html"
    SSH_CRED_ID = "ec2-ssh-key"    // create this SSH Username with private key credential in Jenkins (id: ec2-ssh-key)
  }

  options {
    skipStagesAfterUnstable()
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '30')) // keep last 30 builds
    ansiColor('xterm')
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
        echo "Checked out branch ${env.BRANCH_NAME}"
      }
    }

    stage('Build') {
      steps {
        sh label: 'Create venv & install deps', script: """
          bash -lc 'set -euo pipefail
          python3 -m venv .venv || true
          . .venv/bin/activate
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          deactivate'
        """
      }
    }

    stage('Test') {
      steps {
        sh label: 'Run pytest (if present)', script: """
          bash -lc 'set -euo pipefail
          if [ -d .venv ]; then . .venv/bin/activate; fi
          if [ -d tests ] || ls test_*.py >/dev/null 2>&1; then
            pytest -q || (echo "Pytest failed" && exit 1)
          else
            echo "No tests found - skipping pytest"
          fi
          if [ -d .venv ]; then deactivate; fi'
        """
      }
    }

    stage('Package') {
      steps {
        script {
          // Attempt packaging up to 2 times to avoid transient tar errors
          def rc = 1
          def attempts = 0
          while (rc != 0 && attempts < 2) {
            attempts++
            echo "Package attempt #${attempts}"
            rc = sh(script: """
              bash -lc 'set -euo pipefail
              rm -f build.tar.gz || true
              # tolerate file-changed warnings
              tar --warning=no-file-changed -czf build.tar.gz --exclude=".venv" --exclude=".git" .
              ls -lh build.tar.gz
              ' 
            """, returnStatus: true)
            if (rc != 0) {
              echo "tar failed with exit ${rc}; retrying..."
            }
          }
          if (rc != 0) {
            error "Packaging failed after ${attempts} attempts (rc=${rc})"
          }
        }
        archiveArtifacts artifacts: 'build.tar.gz', fingerprint: true
      }
    }

    stage('Deploy') {
      when {
        anyOf {
          branch 'staging'
          branch 'main'
        }
      }
      steps {
        script {
          env.APP_ENV = (env.BRANCH_NAME == 'main') ? "production" : "staging"
          env.TARGET_DIR = (env.BRANCH_NAME == 'main') ? "${env.DEPLOY_TARGET_BASE}" : "${env.DEPLOY_TARGET_BASE}/staging"
          echo "Deploying branch '${env.BRANCH_NAME}' to '${env.TARGET_DIR}' (APP_ENV=${env.APP_ENV})"
        }

        withCredentials([sshUserPrivateKey(credentialsId: "${env.SSH_CRED_ID}",
                                          keyFileVariable: 'SSH_KEY_FILE',
                                          usernameVariable: 'SSH_USER')]) {
          sh label: 'Upload and deploy to EC2', script: """
            bash -lc 'set -euo pipefail
            REMOTE=\"${SSH_USER}@${params.DEPLOY_HOST}\"
            KEY=\"${SSH_KEY_FILE}\"
            BUILD=\"build.tar.gz\"
            REMOTE_TMP=\"/home/${SSH_USER}/build.tar.gz\"
            TARGET_DIR=\"${env.TARGET_DIR}\"
            DEPLOY_BASE=\"${env.DEPLOY_TARGET_BASE}\"

            echo "Ensure parent exists on remote: \${DEPLOY_BASE}"
            ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i \"\${KEY}\" \"\${REMOTE}\" \\
              \"sudo mkdir -p '\${DEPLOY_BASE}' && sudo chown ${SSH_USER}:${SSH_USER} '\${DEPLOY_BASE}'\"

            echo "Copying package to remote..."
            scp -o BatchMode=yes -o StrictHostKeyChecking=no -i \"\${KEY}\" \"\${BUILD}\" \"\${REMOTE}:\${REMOTE_TMP}\"

            echo "Extracting package on remote into \${TARGET_DIR} and writing APP_ENV=${env.APP_ENV}"
            ssh -o BatchMode=yes -o StrictHostKeyChecking=no -i \"\${KEY}\" \"\${REMOTE}\" bash -lc \\
              \"sudo mkdir -p \\\"\\\${TARGET_DIR}\\\" \\
               && sudo tar -xzf \\\"\\\${REMOTE_TMP}\\\" -C \\\"\\\${TARGET_DIR}\\\" --strip-components=0 \\
               && echo APP_ENV=${env.APP_ENV} | sudo tee \\\"\\\${TARGET_DIR}/.env\\\" >/dev/null \\
               && sudo chown -R ${SSH_USER}:www-data \\\"\\\${TARGET_DIR}\\\" \\
               && if sudo systemctl list-unit-files | grep -q '^flaskapp.service'; then sudo systemctl daemon-reload || true; sudo systemctl restart flaskapp || true; fi \\
               && sudo systemctl restart nginx || true\"

            echo "Deploy finished."
            '
          """
        }
      }
    }
  }

  post {
    success {
      echo "BUILD SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER} (branch: ${env.BRANCH_NAME})"
      // Optional: use emailext here if configured
      // emailext to: 'you@example.com', subject: "...", body: "..."
    }
    failure {
      echo "BUILD FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER} (branch: ${env.BRANCH_NAME})"
      // Optional: send failure email with emailext if configured
    }
    cleanup {
      sh 'rm -f build.tar.gz || true'
    }
  }
}
