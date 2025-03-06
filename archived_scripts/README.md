# Archived Migration Scripts

This directory contains archived migration scripts that were used for migrating the database to use pgvector for embedding storage.

## Purpose of These Scripts

- `migrate_to_vector.py`: Initial migration script to convert ARRAY(FLOAT) columns to vector type
- `complete_vector_migration.py`: Script to complete the migration that was interrupted
- `fix_vector_dimensions.py`: Script to fix vector dimensions, initially using 1536 dimensions
- `fix_vectors_384.py`: Final script that fixed vector columns to use 384 dimensions

These scripts are kept for reference purposes only and are no longer needed for normal operation.
