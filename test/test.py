from sqlalchemy import create_engine

engine = create_engine('postgresql+psycopg2://postgres:team123@localhost:5432/')
