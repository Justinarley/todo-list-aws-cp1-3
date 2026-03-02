pipeline { 
    agent any 
    stages { 
        stage('Checkout Code') { 
            steps { 
              git(
                branch: 'develop',
                url: 'https://github.com/Justinarley/todo-list-aws-cp1-3.git',
                credentialsId: 'GITHUB-CP1.4'
              )
            } 
        } 
        stage('Tests'){
            steps {
                catchError(
                    buildResult: 'UNSTABLE',
                    stageResult: 'FAILURE'
                ) {
                    sh ''' 
                        export PYTHONPATH=.
                        flake8 --exit-zero --format=pylint src > flake8.out
                    ''' 
                    recordIssues(
                        qualityGates: [
                            [criticality: 'NOTE', integerThreshold: 8, threshold: 8.0, type: 'TOTAL'],
                            [criticality: 'ERROR', integerThreshold: 10, threshold: 10.0, type: 'TOTAL']
                        ],
                        tools:[
                            flake8(pattern: 'flake8.out')
                        ]
                    )
                }
            }
        }
        stage('Security') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE'){ 
                sh '''
                    bandit -r src -f custom -o bandit.out --msg-template "{abspath}:{line}: [{test_id}] {msg}"
                '''
                    recordIssues(
                        qualityGates: [
                            [criticality: 'NOTE', integerThreshold: 2, type: 'TOTAL'],
                            [criticality: 'FAILURE', integerThreshold: 4, type: 'TOTAL'] ],
                        tools:[
                            pyLint(pattern: 'bandit.out')
                        ]
                    )
                }
            }
        }
        stage('SAM deploy') {
           steps {
                script{
                    sh '''
                        set -e
                            STACK_NAME="todo-list-aws-staging"
                            REGION="us-east-1"
                        echo "===== AWS Identity ====="
                        aws sts get-caller-identity

                                    echo "===== Checking existing stack ====="

                                    STACK_STATUS=$(aws cloudformation describe-stacks \
                                        --stack-name $STACK_NAME \
                                        --region $REGION \
                                        --query "Stacks[0].StackStatus" \
                                        --output text 2>/dev/null || echo "NOT_FOUND")

                                    echo "Stack status: $STACK_STATUS"

                                    # 🔥 Si el stack quedó roto, eliminarlo
                                    if [ "$STACK_STATUS" = "ROLLBACK_COMPLETE" ] || \
                                       [ "$STACK_STATUS" = "CREATE_FAILED" ] || \
                                       [ "$STACK_STATUS" = "UPDATE_ROLLBACK_COMPLETE" ]; then

                                        echo "Deleting broken stack..."

                                        aws cloudformation delete-stack \
                                            --stack-name $STACK_NAME \
                                            --region $REGION

                                        echo "Waiting stack deletion..."
                                        aws cloudformation wait stack-delete-complete \
                                            --stack-name $STACK_NAME \
                                            --region $REGION

                                        echo "Stack deleted."
                                    fi

                                    echo "===== SAM Build ====="
                                    sam build

                                    echo "===== SAM Validate ====="
                                    sam validate --region $REGION

                                    echo "===== SAM Deploy ====="
                        sam deploy --config-env staging --no-fail-on-empty-changeset
        '''
        
        env.BASE_URL = sh(
                script: '''
                    aws cloudformation describe-stacks \
                      --stack-name todo-list-aws-staging \
                      --region us-east-1 \
                      --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
                      --output text
                ''',
                returnStdout: true
            ).trim()

            echo "BASE_URL = ${env.BASE_URL}"
        }
    }
        }
        stage('API Tests (pytest)') {
            environment {
                BASE_URL = "${env.BASE_URL}"
            }
            steps{
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    
                    pip install pytest requests

                    pytest -v test/integration/todoApiTest.py --junitxml=result_unit.xml
                '''
                 junit 'result_unit.xml'
            }
        }
        
        stage('***PROMOTE (MERGE MASTER)**') {
            steps {
                echo "🚀 Promoviendo versión a Release..."
                  withCredentials([usernamePassword(
                      credentialsId: 'GITHUB-CP1.4',
                      usernameVariable: 'GITHUB_USER',
                      passwordVariable: 'GITHUB_TOKEN'
                  )]) {
                  sh '''
                    

                    git fetch origin
                    git checkout main
                    git pull origin main
                    git merge origin/develop
                    git push https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/todo-list-aws-cp1-3.git
                  '''
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}