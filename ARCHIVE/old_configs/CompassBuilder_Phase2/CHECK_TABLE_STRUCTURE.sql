-- 🔍 Check Table Structure Before Security Fixes
-- Run this first to understand your actual schema

-- Check engagement_opportunities table structure
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name = 'engagement_opportunities'
ORDER BY ordinal_position;

-- Check people table structure
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name = 'people'
ORDER BY ordinal_position;

-- Check teaching_materials table structure
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
    AND table_name = 'teaching_materials'
ORDER BY ordinal_position;

-- Check which views currently exist (using information_schema)
SELECT 
    table_name as view_name,
    view_definition
FROM information_schema.views 
WHERE table_schema = 'public' 
    AND table_name IN (
        'daily_engagement_summary', 'high_value_prospects', 
        'unified_person_profiles', 'high_priority_opportunities', 
        'all_teaching_content'
    );

-- Check which functions currently exist (using information_schema)
SELECT 
    routine_name as function_name,
    routine_definition
FROM information_schema.routines 
WHERE routine_schema = 'public' 
    AND routine_name IN (
        'has_internal_access', 'calculate_engagement_metrics', 
        'find_potential_identity_matches'
    );

-- Check RLS status on all tables (using information_schema)
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_name IN (
        'orders', 'channel_mappings', 'event_log', 'agent_task_log',
        'engagement_opportunities', 'social_responses', 'social_comments',
        'people', 'identifiers', 'person_attributes', 'inbox_processing_log',
        'teaching_materials', 'social_to_telegram_conversions', 'community_content',
        'content_chunks', 'ops_autoheal_log', 'personality_synthesis',
        'internal_material_categories', 'internal_content_categories',
        'internal_teaching_materials', 'internal_content_chunks',
        'internal_content_access', 'tracked_content', 'target_communities',
        'monitoring_keywords', 'engagement_analytics', 'platform_identities',
        'identity_registry', 'identity_match_signals', 'willb_one_customers',
        'cross_platform_analytics'
    );

-- Simple check for RLS status (alternative approach)
SELECT 
    tablename,
    rowsecurity
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN (
        'engagement_opportunities', 'people', 'teaching_materials',
        'internal_teaching_materials', 'internal_content_chunks'
    );
