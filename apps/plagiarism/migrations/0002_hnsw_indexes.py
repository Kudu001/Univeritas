from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('plagiarism', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE INDEX IF NOT EXISTS dissertationchunk_embedding_hnsw
                ON plagiarism_dissertationchunk
                USING hnsw (embedding vector_cosine_ops);

                CREATE INDEX IF NOT EXISTS dissertationchunk_code_embedding_hnsw
                ON plagiarism_dissertationchunk
                USING hnsw (code_embedding vector_cosine_ops);
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS dissertationchunk_embedding_hnsw;
                DROP INDEX IF EXISTS dissertationchunk_code_embedding_hnsw;
            """,
        ),
    ]
