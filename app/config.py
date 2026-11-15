# lru_cache caches function results so the function doesn't need to recompute the same result every time.
from functools import lru_cache                
from pydantic_settings import BaseSettings , SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = ".env" , extra = "ignore")
    aws_region:str='us-east-1'
    aws_access_key_id:str=''
    aws_secret_access_key_id:str=''
    s3_bucket:str=''
    database_url:str=''  # Render PostgreSQL External Database URL
    bedrock_embed_model:str='amazon.titan-embed-text-v2:0'
    bedrock_chat_model:str='amazon.nova-lite-v1:0'
    embed_dim:int=1024
    max_upload_bytes:int=10485760
    pinecone_api_key:str=''
    pinecone_index_name:str='enterprise-rag-with-ci-cd-aws-actions-index'
    pinecone_cloud:str='aws'
    pinecone_region:str='us-east-1'
    pinecone_ready_timeout:int=180
    min_relevance:float=0.25
    hitl_enabled:bool=True
    memory_turns:int=6


def settings() -> Settings:
    return Settings()