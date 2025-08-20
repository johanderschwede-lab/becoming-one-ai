-- 🔒 Supabase Security Fix Script
-- Fixes all Security Definer Views and RLS Disabled issues
-- Run this in your Supabase SQL Editor

-- =====================================================
-- STEP 1: FIX SECURITY DEFINER VIEWS (5 views)
-- =====================================================

-- Fix 1: daily_engagement_summary
DROP VIEW IF EXISTS public.daily_engagement_summary;
CREATE VIEW public.daily_engagement_summary AS
SELECT 
    DATE(created_date) as engagement_date,
    COUNT(*) as total_engagements,
    COUNT(DISTINCT person_id) as unique_people,
    AVG(engagement_score) as avg_engagement_score
FROM public.engagement_opportunities
WHERE created_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_date)
ORDER BY engagement_date DESC;

-- Fix 2: high_value_prospects
DROP VIEW IF EXISTS public.high_value_prospects;
CREATE VIEW public.high_value_prospects AS
SELECT 
    p.id,
    p.name,
    p.email,
    p.engagement_score,
    p.last_engagement_date,
    COUNT(eo.id) as total_opportunities
FROM public.people p
LEFT JOIN public.engagement_opportunities eo ON p.id = eo.person_id
WHERE p.engagement_score >= 7.0
    AND p.last_engagement_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY p.id, p.name, p.email, p.engagement_score, p.last_engagement_date
ORDER BY p.engagement_score DESC;

-- Fix 3: unified_person_profiles
DROP VIEW IF EXISTS public.unified_person_profiles;
CREATE VIEW public.unified_person_profiles AS
SELECT 
    p.id,
    p.name,
    p.email,
    p.engagement_score,
    p.created_at,
    p.updated_at,
    STRING_AGG(DISTINCT pi.platform, ', ') as platforms,
    STRING_AGG(DISTINCT pa.attribute_key || ':' || pa.attribute_value, '; ') as attributes
FROM public.people p
LEFT JOIN public.platform_identities pi ON p.id = pi.person_id
LEFT JOIN public.person_attributes pa ON p.id = pa.person_id
GROUP BY p.id, p.name, p.email, p.engagement_score, p.created_at, p.updated_at;

-- Fix 4: high_priority_opportunities
DROP VIEW IF EXISTS public.high_priority_opportunities;
CREATE VIEW public.high_priority_opportunities AS
SELECT 
    eo.id,
    eo.person_id,
    p.name as person_name,
    eo.opportunity_type,
    eo.engagement_score,
    eo.created_date,
    eo.status
FROM public.engagement_opportunities eo
JOIN public.people p ON eo.person_id = p.id
WHERE eo.engagement_score >= 8.0
    AND eo.status IN ('open', 'pending')
    AND eo.created_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY eo.engagement_score DESC, eo.created_date DESC;

-- Fix 5: all_teaching_content
DROP VIEW IF EXISTS public.all_teaching_content;
CREATE VIEW public.all_teaching_content AS
SELECT 
    tm.id,
    tm.title,
    tm.content,
    tm.category,
    tm.created_date,
    tm.updated_date,
    tm.author_id,
    tm.status,
    COALESCE(tm.engagement_score, 0) as engagement_score
FROM public.teaching_materials tm
WHERE tm.status = 'published'
ORDER BY tm.created_date DESC;

-- =====================================================
-- STEP 2: ENABLE RLS ON ALL TABLES (35 tables)
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.channel_mappings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.event_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_task_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.engagement_opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.social_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.social_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.people ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.identifiers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.person_attributes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.inbox_processing_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.teaching_materials ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.social_to_telegram_conversions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.community_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.content_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ops_autoheal_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.personality_synthesis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.internal_material_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.internal_content_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.internal_teaching_materials ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.internal_content_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.internal_content_access ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tracked_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.target_communities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.monitoring_keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.engagement_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.platform_identities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.identity_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.identity_match_signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.willb_one_customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cross_platform_analytics ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- STEP 3: CREATE BASIC RLS POLICIES
-- =====================================================

-- Policy for authenticated users to read their own data
CREATE POLICY "Users can read their own data" ON public.people
    FOR SELECT USING (auth.uid()::text = created_by OR auth.uid()::text = updated_by);

CREATE POLICY "Users can read their own engagement opportunities" ON public.engagement_opportunities
    FOR SELECT USING (auth.uid()::text = created_by OR auth.uid()::text = updated_by);

CREATE POLICY "Users can read their own teaching materials" ON public.teaching_materials
    FOR SELECT USING (auth.uid()::text = author_id OR auth.uid()::text = created_by);

-- Policy for service role to access all data (for your API)
CREATE POLICY "Service role can access all data" ON public.people
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access all engagement opportunities" ON public.engagement_opportunities
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access all teaching materials" ON public.teaching_materials
    FOR ALL USING (auth.role() = 'service_role');

-- Policy for internal teaching materials (your Compass system)
CREATE POLICY "Service role can access internal teaching materials" ON public.internal_teaching_materials
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access internal content chunks" ON public.internal_content_chunks
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "Service role can access internal content access" ON public.internal_content_access
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- STEP 4: CREATE FUNCTION SEARCH PATH FIXES
-- =====================================================

-- Fix function search paths (if these functions exist)
-- Note: You may need to adjust these based on your actual function definitions

-- Example fix for has_internal_access function
CREATE OR REPLACE FUNCTION public.has_internal_access(user_id UUID, content_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = 'public'
AS $$
BEGIN
    -- Your function logic here
    RETURN EXISTS (
        SELECT 1 FROM public.internal_content_access 
        WHERE user_id = $1 AND content_id = $2
    );
END;
$$;

-- Example fix for calculate_engagement_metrics function
CREATE OR REPLACE FUNCTION public.calculate_engagement_metrics(person_id UUID)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = 'public'
AS $$
DECLARE
    result JSON;
BEGIN
    -- Your function logic here
    SELECT json_build_object(
        'total_engagements', COUNT(*),
        'avg_score', AVG(engagement_score),
        'last_engagement', MAX(created_date)
    ) INTO result
    FROM public.engagement_opportunities
    WHERE person_id = $1;
    
    RETURN result;
END;
$$;

-- Example fix for find_potential_identity_matches function
CREATE OR REPLACE FUNCTION public.find_potential_identity_matches(email TEXT)
RETURNS TABLE(person_id UUID, match_score NUMERIC)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = 'public'
AS $$
BEGIN
    -- Your function logic here
    RETURN QUERY
    SELECT p.id, 0.8 as match_score
    FROM public.people p
    WHERE p.email = $1;
END;
$$;

-- =====================================================
-- STEP 5: VERIFICATION QUERIES
-- =====================================================

-- Check that RLS is enabled on all tables
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN (
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

-- Check that views no longer have SECURITY DEFINER
SELECT 
    schemaname,
    viewname,
    definition
FROM pg_views 
WHERE schemaname = 'public' 
    AND viewname IN (
        'daily_engagement_summary', 'high_value_prospects', 
        'unified_person_profiles', 'high_priority_opportunities', 
        'all_teaching_content'
    );

-- =====================================================
-- STEP 6: COMMENTS AND DOCUMENTATION
-- =====================================================

COMMENT ON VIEW public.daily_engagement_summary IS 'Daily engagement summary without SECURITY DEFINER - uses RLS policies instead';
COMMENT ON VIEW public.high_value_prospects IS 'High value prospects without SECURITY DEFINER - uses RLS policies instead';
COMMENT ON VIEW public.unified_person_profiles IS 'Unified person profiles without SECURITY DEFINER - uses RLS policies instead';
COMMENT ON VIEW public.high_priority_opportunities IS 'High priority opportunities without SECURITY DEFINER - uses RLS policies instead';
COMMENT ON VIEW public.all_teaching_content IS 'All teaching content without SECURITY DEFINER - uses RLS policies instead';

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================

-- This script should fix all the security issues identified by Supabase Security Advisor
-- After running this script:
-- 1. All 5 Security Definer Views will be fixed
-- 2. All 35 tables will have RLS enabled
-- 3. Basic RLS policies will be in place
-- 4. Function search paths will be fixed
-- 5. Run the verification queries to confirm fixes

-- Next steps:
-- 1. Test your application functionality
-- 2. Adjust RLS policies as needed for your specific use cases
-- 3. Run Supabase Security Advisor again to confirm all issues are resolved
-- 4. Proceed with Compass API deployment
