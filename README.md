# Flask App CI/CD Pipeline with GitHub Actions

A complete CI/CD workflow implementation using GitHub Actions for a Python Flask application with automated deployment to staging and production environments on AWS EC2.

# Fork the repo into your github
create staging branch
-<img width="1172" height="627" alt="image" src="https://github.com/user-attachments/assets/79b670c7-9412-4deb-8a07-c71db2757b0a" />


```bash
####  Clone Repository Locally

```bash
git clone https://github.com/ramiz0009/GitHub-Actions-Pipeline-Flask-App.git
<img width="1100" height="346" alt="image" src="https://github.com/user-attachments/assets/1afd0c73-ca3e-4b7c-92d8-9189f9422bb6" />

cd flask_Practice
- <img width="1000" height="370" alt="image" src="https://github.com/user-attachments/assets/de86913a-9fcd-400d-b91d-24aa8b299275" />

# Create workflow directory
mkdir -p .github/workflows

# Add main.yml workflow file to .github/workflows/
- <img width="1100" height="346" alt="image" src="https://github.com/user-attachments/assets/70433f45-f2f9-4b31-be2d-d0a5a7dfce65" />

# Create `main.yml` file in `.github/workflows/` with the CI/CD pipeline configuration. Ensure the workflow file is committed to both `main` and `staging` branches.

**Create Staging Branch**

In your forked repository, create a new branch called `staging`:

```bash
git checkout -b staging
git push origin staging
```


```

### EC2 Configuration

#### Launch EC2 Instances

Launch 2 EC2 instances (Ubuntu):

| Instance | Purpose |
|----------|---------|
| Staging Server | Testing environment before production |
| Production Server | Live application environment |

#### Step 6: Configure Systemd Service

SSH into each EC2 instance and create the Flask app service:

```bash
## sudo nano /etc/systemd/system/flaskapp.service

Add the following configuration:
-<img width="1212" height="516" alt="image" src="https://github.com/user-attachments/assets/8275b4bc-0624-4258-8b53-6b83a2100f3b" />

Enable and start the service on both servers:

```bash
sudo systemctl daemon-reload
sudo systemctl enable flaskapp.service
sudo systemctl start flaskapp.service

# Verify the service is running
sudo systemctl status flaskapp.service
```

Repeat this configuration on both staging and production servers.

### MongoDB Setup

#### Create MongoDB Cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. Configure network access to allow connections from all IP addresses (`0.0.0.0/0`)
4. Create a database user with appropriate permissions
5. Obtain your connection string in the format: `mongodb+srv://user:password@cluster.mongodb.net/`


### GitHub Secrets Configuration

#### Add Repository Secrets

Navigate to your GitHub repository: **Settings > Secrets and variables > Actions > New repository secret**

GitHub Secrets Configuration
Step 8: Add Repository Secrets
Navigate to your GitHub repository: Settings > Secrets and variables > Actions > New repository secret
Add the following secrets one by one:
EC2_HOST_PROD
Description: Production EC2 public IP address
Value: 18.175.186.97

EC2_HOST_STAGING

Description: Staging EC2 public IP address
Value: 18.171.212.236

EC2_SSH_KEY

Description: Private SSH key for EC2 access
Value: Copy your entire private SSH key starting from -----BEGIN RSA PRIVATE KEY----- to -----END RSA PRIVATE KEY-----

EC2_USERNAME

Description: EC2 instance username
Value: ubuntu

MONGO_URI

Description: MongoDB Atlas connection string
Value: mongodb+srv://user:pass@cluster.mongodb.net/dbname

SECRET_KEY

Description: Flask secret key
Value: your-secure-random-key-here (Use a secure random string)

- <img width="1093" height="553" alt="image" src="https://github.com/user-attachments/assets/8596c2d4-094b-4609-95ac-b0ea3e0b0539" />


## GitHub Actions Workflow

The workflow file (`main.yml`) should automate the following steps:

1. **Code Checkout** - Pull latest code from the repository
2. **Environment Setup** - Install Python dependencies and set up virtual environment
3. **Testing** - Run unit tests and code validation
4. **Build Artifacts** - Create deployable artifacts (zip file)
5. **Deploy to EC2** - Copy artifacts and deploy to appropriate environment
6. **Service Restart** - Restart Flask application service
7. **Health Checks** - Verify application is running

**Workflow Triggers:**
- Staging branch: Deploys to staging server on every push
- Main branch: Deploys to production server when version tags (e.g., `v1.0.1`) are pushed

## Deployment Process

### Staging Deployment

####  Switch to Staging Branch

```bash
git switch staging
```

####  Make Code Changes

Edit your code in Visual Studio Code or your preferred editor.

#### Configure Personal Access Token (PAT)

Generate a Personal Access Token for secure Git operations:

1. Go to GitHub **Settings > Developer settings > Personal access tokens > Tokens (classic)**
2. Click **Generate new token**
3. Select scopes: `repo` and `workflow`
4. Copy the generated token

Configure in your local repository:

```bash
git remote set-url origin https://<your-PAT>@github.com/<your-username>/flask_Practice.git
```

####  Commit and Push Changes

```bash
git checkout staging
git add .
git commit -m "Staging Initial build"
git push origin staging
```

#### Monitor Workflow Execution

1. Go to your GitHub repository
2. Navigate to the **Actions** tab
3. Watch the workflow run in real-time
4. Verify the workflow completes successfully
   - <img width="1391" height="801" alt="image" src="https://github.com/user-attachments/assets/ca059900-4550-45b7-b8dc-b7543c275f8a" />


####  Verify Staging Artifacts

SSH into the staging server:

Check for the deployed application:

```bash
ls -la /home/ubuntu/
ls -la /home/ubuntu/app/
```
- <img width="651" height="301" alt="image" src="https://github.com/user-attachments/assets/86b4eea6-6b4b-4102-aea2-4590b6fa9720" />

####  Test Staging Application

Access the application in your browser:

```
http://http://18.171.212.236/:8000
```

Verify:
- Application loads correctly
- All features are functioning
- Data is being stored in MongoDB Atlas
-- <img width="1712" height="541" alt="image" src="https://github.com/user-attachments/assets/fec529b8-c736-49c1-9f00-369bb943bf6d" />

### Production Deployment

#### Deploy to Production

Once staging tests pass successfully, merge changes to production:

```bash
# Update local main branch
git fetch origin
git pull origin main

# Switch to main branch
git checkout main

# Merge staging branch into main
git merge origin/staging

# Create a version tag (this triggers production deployment)
git tag v1.0.1

# Push tag to trigger production workflow
git push origin v1.0.1
```

**Note:** The tag push automatically triggers the production deployment workflow.

####  Verify Production Deployment

Monitor the workflow in the **Actions** tab until it completes successfully.

- <img width="1570" height="778" alt="image" src="https://github.com/user-attachments/assets/33302dd0-3075-46a5-9bce-6d0559d67911" />


Access the production application:

```
http://18.175.186.97/:8000
```

Verify:
- Application is running correctly
- All features are functional

- <img width="1492" height="502" alt="image" src="https://github.com/user-attachments/assets/92fce48b-a3c0-4195-89a7-e977d996c41e" />








