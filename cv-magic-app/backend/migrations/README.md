# Database Migrations

This directory contains all database migration scripts organized by feature and version.

## Structure

```
migrations/
├── README.md                           # This file
├── 001_user_management/                # User-related tables and enhancements
│   ├── 001_enhance_users_table.sql
│   └── 002_enhance_user_sessions.sql
├── 002_cv_management/                  # CV-related tables and enhancements
│   ├── 001_enhance_cv_table.sql
│   └── 002_create_cv_versions.sql
├── 003_job_management/                 # Job-related tables
│   ├── 001_create_job_descriptions.sql
│   └── 002_enhance_job_applications.sql
├── 004_skills_management/              # Skills-related tables
│   ├── 001_create_skills_master.sql
│   └── 002_create_user_skills.sql
├── 005_analysis_tracking/              # Analysis and audit tables
│   ├── 001_create_analysis_history.sql
│   └── 002_create_ai_usage_logs.sql
├── 006_notifications/                  # Notification system
│   └── 001_create_notifications.sql
├── 007_monitoring/                     # Monitoring and usage tracking
│   ├── 001_create_api_usage.sql
│   └── 002_create_performance_metrics.sql
└── 008_indexes/                        # Performance indexes
    ├── 001_create_core_indexes.sql
    └── 002_create_jsonb_indexes.sql
```

## Migration Order

Run migrations in this order:
1. User Management (001)
2. CV Management (002)
3. Job Management (003)
4. Skills Management (004)
5. Analysis Tracking (005)
6. Notifications (006)
7. Monitoring (007)
8. Indexes (008)

## Usage

```bash
# Run all migrations
psql -d your_database -f migrations/001_user_management/001_enhance_users_table.sql

# Or use Alembic (recommended)
alembic upgrade head
```
