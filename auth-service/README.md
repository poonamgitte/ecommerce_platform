# This is the auth-service 

# open the folder
cd ecommerce_platform/auth-service

# Step 1 — Create fresh venv
python3 -m venv venv
source venv/bin/activate

# Step 2 — Install dependencies
pip install -r requirements.txt

# Step 3 — Create .env file (not cloned, in .gitignore)

# Step 4 — Start PostgreSQL (via Docker)
docker start ecommerce-postgres
# or if not created yet
docker run --name ecommerce-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=auth_db \
  -p 5432:5432 -d postgres:16

# Step 5 — Run migrations
alembic upgrade head

# Step 6 — Start server
uvicorn app.main:app --reload