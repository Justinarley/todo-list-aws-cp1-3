pipeline {
    agent any

    stages {

        stage('Source Retrieval') {
            steps {
                git branch: 'develop',
                    url: 'https://github.com/Justinarley/todo-list-aws-cp1-3.git'
            }
        }

        stage('Workspace Check') {
            steps {
                sh 'ls -lah'
            }
        }

        stage('Static Analysis') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    sh '''
                        export PYTHONPATH=.
                        flake8 --exit-zero --format=pylint src > lint-report.out
                    '''

                    recordIssues(
                        qualityGates: [
                            [criticality: 'NOTE', integerThreshold: 7, threshold: 7.0, type: 'TOTAL'],
                            [criticality: 'ERROR', integerThreshold: 9, threshold: 9.0, type: 'TOTAL']
                        ],
                        tools: [
                            flake8(pattern: 'lint-report.out')
                        ]
                    )
                }
            }
        }

        stage('Code Security Scan') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh '''
                        bandit -r src -f custom -o security-report.out --msg-template "{abspath}:{line}: [{test_id}] {msg}"
                    '''

                    recordIssues(
                        qualityGates: [
                            [criticality: 'NOTE', integerThreshold: 3, type: 'TOTAL'],
                            [criticality: 'FAILURE', integerThreshold: 5, type: 'TOTAL']
                        ],
                        tools: [
                            pyLint(pattern: 'security-report.out')
                        ]
                    )
                }
            }
        }

        stage('Serverless Deployment') {
            steps {
                script {
                    sh '''
                        set -e

                        DEPLOY_STACK="todo-list-aws-staging"
                        AWS_REGION="us-east-1"

                        echo "===== Verifying AWS Identity ====="
                        aws sts get-caller-identity

                        echo "===== Checking Stack Status ====="

                        CURRENT_STATUS=$(aws cloudformation describe-stacks \
                            --stack-name $DEPLOY_STACK \
                            --region $AWS_REGION \
                            --query "Stacks[0].StackStatus" \
                            --output text 2>/dev/null || echo "NOT_FOUND")

                        echo "Current status: $CURRENT_STATUS"

                        if [ "$CURRENT_STATUS" = "ROLLBACK_COMPLETE" ] || \
                           [ "$CURRENT_STATUS" = "CREATE_FAILED" ] || \
                           [ "$CURRENT_STATUS" = "UPDATE_ROLLBACK_COMPLETE" ]; then

                            echo "Removing failed stack..."

                            aws cloudformation delete-stack \
                                --stack-name $DEPLOY_STACK \
                                --region $AWS_REGION

                            aws cloudformation wait stack-delete-complete \
                                --stack-name $DEPLOY_STACK \
                                --region $AWS_REGION

                            echo "Stack successfully removed."
                        fi

                        echo "===== Building Application ====="
                        sam build

                        echo "===== Validating Template ====="
                        sam validate --region $AWS_REGION

                        echo "===== Deploying Application ====="
                        sam deploy --config-env staging --no-fail-on-empty-changeset
                    '''

                    env.APP_ENDPOINT = sh(
                        script: '''
                            aws cloudformation describe-stacks \
                              --stack-name todo-list-aws-staging \
                              --region us-east-1 \
                              --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" \
                              --output text
                        ''',
                        returnStdout: true
                    ).trim()

                    echo "Application URL = ${env.APP_ENDPOINT}"
                }
            }
        }

        stage('==========>PROMOTE (MERGE MAIN)<===========') {
            steps {
                echo "🚀 Promoviendo versión ..."

                withCredentials([
                    usernamePassword(
                        credentialsId: 'GITHUB-CP1.4',
                        usernameVariable: 'GITHUB_USER',
                        passwordVariable: 'GITHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        git fetch origin
                        git checkout main
                        git pull origin main
                        git merge origin/develop
                        git push https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/todo-list-aws-cp1-3.git main
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