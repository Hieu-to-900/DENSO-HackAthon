-- Action Management Migration
-- Add assignment and tracking fields to action_recommendations table

-- ========================================
-- ALTER action_recommendations TABLE
-- ========================================

-- Add assignment fields
ALTER TABLE action_recommendations 
ADD COLUMN IF NOT EXISTS assigned_to VARCHAR(100),
ADD COLUMN IF NOT EXISTS assigned_team VARCHAR(100),
ADD COLUMN IF NOT EXISTS assigned_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS assigned_by VARCHAR(100);

-- Add progress tracking
ALTER TABLE action_recommendations
ADD COLUMN IF NOT EXISTS progress_percent INTEGER DEFAULT 0 CHECK (progress_percent >= 0 AND progress_percent <= 100),
ADD COLUMN IF NOT EXISTS due_date DATE;

-- Add notes/comments
ALTER TABLE action_recommendations
ADD COLUMN IF NOT EXISTS notes TEXT;

-- Add action type field (if not exists from original)
ALTER TABLE action_recommendations
ADD COLUMN IF NOT EXISTS action_type VARCHAR(50) DEFAULT 'optimization';

-- Add confidence score
ALTER TABLE action_recommendations
ADD COLUMN IF NOT EXISTS confidence_score DECIMAL(5, 2) DEFAULT 75.00 CHECK (confidence_score >= 0 AND confidence_score <= 100);

-- Add expected impact text
ALTER TABLE action_recommendations
ADD COLUMN IF NOT EXISTS expected_impact TEXT;

-- Create indexes for new fields
CREATE INDEX IF NOT EXISTS idx_actions_assigned_to ON action_recommendations (assigned_to);
CREATE INDEX IF NOT EXISTS idx_actions_assigned_team ON action_recommendations (assigned_team);
CREATE INDEX IF NOT EXISTS idx_actions_due_date ON action_recommendations (due_date);
CREATE INDEX IF NOT EXISTS idx_actions_progress ON action_recommendations (progress_percent);
CREATE INDEX IF NOT EXISTS idx_actions_type ON action_recommendations (action_type);

-- ========================================
-- CREATE ACTION HISTORY TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS action_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_id UUID NOT NULL REFERENCES action_recommendations(id) ON DELETE CASCADE,
    
    -- Change tracking
    changed_field VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    
    -- Who and when
    changed_by VARCHAR(100),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Optional comment
    comment TEXT
);

CREATE INDEX idx_action_history_action_id ON action_history (action_id);
CREATE INDEX idx_action_history_changed_at ON action_history (changed_at DESC);

-- ========================================
-- CREATE ACTION COMMENTS TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS action_comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_id UUID NOT NULL REFERENCES action_recommendations(id) ON DELETE CASCADE,
    
    -- Comment content
    comment TEXT NOT NULL,
    author VARCHAR(100) NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Edit tracking
    is_edited BOOLEAN DEFAULT FALSE,
    edited_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_action_comments_action_id ON action_comments (action_id);
CREATE INDEX idx_action_comments_created_at ON action_comments (created_at DESC);

-- Auto-update updated_at for comments
CREATE TRIGGER update_action_comments_updated_at 
    BEFORE UPDATE ON action_comments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- UPDATE VIEWS
-- ========================================

-- Update active_actions view to include assignment fields
DROP VIEW IF EXISTS active_actions;

CREATE OR REPLACE VIEW active_actions AS
SELECT 
    id, priority, category, action_type, title, description, impact,
    estimated_cost, deadline, due_date, affected_products, status,
    assigned_to, assigned_team, progress_percent, confidence_score,
    expected_impact, notes, created_at, updated_at
FROM action_recommendations
WHERE status IN ('pending', 'in_progress', 'snoozed')
    AND (snoozed_until IS NULL OR snoozed_until < CURRENT_TIMESTAMP)
ORDER BY 
    CASE priority
        WHEN 'high' THEN 1
        WHEN 'medium' THEN 2
        WHEN 'low' THEN 3
    END,
    due_date ASC NULLS LAST;

-- Create view for actions by team
CREATE OR REPLACE VIEW actions_by_team AS
SELECT 
    assigned_team,
    status,
    priority,
    COUNT(*) as action_count,
    AVG(progress_percent) as avg_progress,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_count,
    COUNT(*) FILTER (WHERE due_date < CURRENT_DATE AND status != 'completed') as overdue_count
FROM action_recommendations
WHERE assigned_team IS NOT NULL
GROUP BY assigned_team, status, priority
ORDER BY assigned_team, 
    CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END;

-- Create view for actions by assignee
CREATE OR REPLACE VIEW actions_by_assignee AS
SELECT 
    assigned_to,
    assigned_team,
    status,
    COUNT(*) as action_count,
    AVG(progress_percent) as avg_progress,
    COUNT(*) FILTER (WHERE status = 'completed') as completed_count,
    COUNT(*) FILTER (WHERE due_date < CURRENT_DATE AND status != 'completed') as overdue_count
FROM action_recommendations
WHERE assigned_to IS NOT NULL
GROUP BY assigned_to, assigned_team, status
ORDER BY assigned_to, status;

-- ========================================
-- SEED DATA FOR TEAMS
-- ========================================

-- Update existing actions with mock assignments for demo
UPDATE action_recommendations
SET 
    assigned_team = CASE 
        WHEN category = 'production' OR category = 'production_planning' THEN 'Production Team'
        WHEN category = 'supply_chain' OR category = 'logistics' THEN 'Supply Chain Team'
        WHEN category = 'inventory' THEN 'Warehouse Team'
        WHEN category = 'pricing' OR category = 'marketing' THEN 'Sales Team'
        ELSE 'Operations Team'
    END,
    assigned_at = CURRENT_TIMESTAMP - INTERVAL '1 day',
    assigned_by = 'System',
    due_date = CASE 
        WHEN priority = 'high' THEN CURRENT_DATE + INTERVAL '7 days'
        WHEN priority = 'medium' THEN CURRENT_DATE + INTERVAL '14 days'
        ELSE CURRENT_DATE + INTERVAL '30 days'
    END,
    progress_percent = CASE 
        WHEN status = 'completed' THEN 100
        WHEN status = 'in_progress' THEN FLOOR(RANDOM() * 50 + 25)::INTEGER
        ELSE 0
    END
WHERE assigned_team IS NULL;

-- ========================================
-- COMMENTS
-- ========================================

COMMENT ON TABLE action_history IS 'Tracks all changes made to action recommendations';
COMMENT ON TABLE action_comments IS 'Comments and discussions on action recommendations';
COMMENT ON VIEW actions_by_team IS 'Action statistics grouped by assigned team';
COMMENT ON VIEW actions_by_assignee IS 'Action statistics grouped by individual assignee';

COMMENT ON COLUMN action_recommendations.assigned_to IS 'Individual person assigned to the action';
COMMENT ON COLUMN action_recommendations.assigned_team IS 'Team/department responsible for the action';
COMMENT ON COLUMN action_recommendations.progress_percent IS 'Completion percentage (0-100)';
COMMENT ON COLUMN action_recommendations.due_date IS 'Target completion date';
COMMENT ON COLUMN action_recommendations.notes IS 'Internal notes and progress updates';
