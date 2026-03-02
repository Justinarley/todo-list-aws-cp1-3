pipeline {
    agent any

    stages {

        stage('Get Code') {
            steps {
                git(
                    branch: 'develop',
                    url: 'https://github.com/Justinarley/todo-list-aws-cp1-3.git',
                    credentialsId: 'GITHUB-CP1.4'
                )
            }
        }

        stage('Static Test') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {

                    sh '''
                        export PYTHONPATH=.
                        flake8 --exit-zero --format=pylint src > flake8.out
                    '''

                    recordIssues(
                        tools: [flake8(pattern: 'flake8.out')]
                    )

                    sh '''
                        bandit -r src -f custom -o bandit.out \
                        --msg-template "{abspath}:{line}: [{test_id}] {msg}"
                    '''

                    recordIssues(
                        tools: [pyLint(pattern: 'bandit.out')]
                    )
                }
            }
        }

        stage('Deploy') {
            steps {
                script {

                    sh '''
                        set -e

                        STACK_NAME="todo-list-aws-staging"
                        REGION="us-east-1"

                        echo "===== AWS Identity ====="
                        aws sts get-caller-identity

                        STACK_STATUS=$(aws cloudformation describe-stacks \
                            --stack-name $STACK_NAME \
                            --region $REGION \
                            --query "Stacks[0].StackStatus" \
                            --output text 2>/dev/null || echo "NOT_FOUND")

                        if [ "$STACK_STATUS" = "ROLLBACK_COMPLETE" ] || \
                           [ "$STACK_STATUS" = "CREATE_FAILED" ] || \
                           [ "$STACK_STATUS" = "UPDATE_ROLLBACK_COMPLETE" ]; then

                            aws cloudformation delete-stack \
                                --stack-name $STACK_NAME \
                                --region $REGION

                            aws cloudformation wait stack-delete-complete \
                                --stack-name $STACK_NAME \
                                --region $REGION
                        fi

                        sam build
                        sam validate --region $REGION
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

                    echo "API URL = ${env.BASE_URL}"
                }
            }
        }

        stage('Rest Test') {
            steps {
                sh """
                    export BASE_URL=${env.BASE_URL}
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install pytest requests
                    pytest -v test/integration/todoApiTest.py --junitxml=result_unit.xml
                """
                junit 'result_unit.xml'
            }
        }

        stage('Promote') {
            steps {
                echo "🚀 Promoting version to main..."

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