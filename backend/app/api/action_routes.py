"""API routes for action management."""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.database.connection import Database, get_db
from app.repositories.action_repository import ActionRepository

router = APIRouter(prefix="/api/actions", tags=["actions"])


# ========================================
# REQUEST/RESPONSE MODELS
# ========================================

class ActionAssignment(BaseModel):
    """Request model for assigning an action."""
    assigned_to: Optional[str] = None
    assigned_team: Optional[str] = None
    assigned_by: str = "demo_user"
    due_date: Optional[date] = None
    notes: Optional[str] = None


class ActionStatusUpdate(BaseModel):
    """Request model for updating action status."""
    status: str = Field(..., pattern="^(pending|in_progress|completed|snoozed|cancelled)$")
    progress_percent: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = None
    updated_by: str = "demo_user"


class ActionCommentCreate(BaseModel):
    """Request model for creating a comment."""
    comment: str = Field(..., min_length=1)
    author: str = "demo_user"


class ActionComment(BaseModel):
    """Response model for a comment."""
    id: UUID
    action_id: UUID
    comment: str
    author: str
    created_at: datetime
    updated_at: datetime
    is_edited: bool


class ActionDetail(BaseModel):
    """Detailed action response."""
    id: UUID
    priority: str
    category: str
    action_type: str
    title: str
    description: str
    impact: Optional[str]
    expected_impact: Optional[str]
    estimated_cost: Optional[float]
    deadline: Optional[date]
    due_date: Optional[date]
    affected_products: List[str]
    status: str
    assigned_to: Optional[str]
    assigned_team: Optional[str]
    assigned_at: Optional[datetime]
    assigned_by: Optional[str]
    progress_percent: int
    confidence_score: Optional[float]
    notes: Optional[str]
    action_items: dict
    created_at: datetime
    updated_at: datetime


class ActionSummary(BaseModel):
    """Action statistics summary."""
    total: int
    pending: int
    in_progress: int
    completed: int
    overdue: int
    by_priority: dict
    by_team: dict


# ========================================
# ENDPOINTS
# ========================================

@router.get("/", response_model=List[ActionDetail])
async def get_actions(
    status: Optional[str] = None,
    assigned_team: Optional[str] = None,
    assigned_to: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 100,
    db: Database = Depends(get_db),
):
    """Get all actions with optional filters."""
    repo = ActionRepository(db.pool)
    
    # Build filter conditions
    filters = []
    if status:
        filters.append(f"status = '{status}'")
    if assigned_team:
        filters.append(f"assigned_team = '{assigned_team}'")
    if assigned_to:
        filters.append(f"assigned_to = '{assigned_to}'")
    if priority:
        filters.append(f"priority = '{priority}'")
    
    where_clause = " AND ".join(filters) if filters else "1=1"
    
    query = f"""
        SELECT 
            id, priority, category, action_type, title, description, 
            impact, expected_impact, estimated_cost, deadline, due_date,
            affected_products, status, assigned_to, assigned_team,
            assigned_at, assigned_by, progress_percent, confidence_score,
            notes, action_items, created_at, updated_at
        FROM action_recommendations
        WHERE {where_clause}
        ORDER BY 
            CASE priority
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
            END,
            due_date ASC NULLS LAST
        LIMIT $1
    """
    
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, limit)
        return [dict(row) for row in rows]


@router.get("/summary", response_model=ActionSummary)
async def get_action_summary(db: Database = Depends(get_db)):
    """Get action statistics summary."""
    query = """
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE status = 'pending') as pending,
            COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
            COUNT(*) FILTER (WHERE status = 'completed') as completed,
            COUNT(*) FILTER (WHERE due_date < CURRENT_DATE AND status != 'completed') as overdue
        FROM action_recommendations
    """
    
    priority_query = """
        SELECT priority, COUNT(*) as count
        FROM action_recommendations
        WHERE status IN ('pending', 'in_progress')
        GROUP BY priority
    """
    
    team_query = """
        SELECT 
            assigned_team, 
            COUNT(*) as count,
            AVG(progress_percent) as avg_progress
        FROM action_recommendations
        WHERE assigned_team IS NOT NULL AND status IN ('pending', 'in_progress')
        GROUP BY assigned_team
    """
    
    async with db.pool.acquire() as conn:
        summary_row = await conn.fetchrow(query)
        priority_rows = await conn.fetch(priority_query)
        team_rows = await conn.fetch(team_query)
        
        by_priority = {row["priority"]: row["count"] for row in priority_rows}
        by_team = {
            row["assigned_team"]: {
                "count": row["count"],
                "avg_progress": float(row["avg_progress"]) if row["avg_progress"] else 0
            }
            for row in team_rows
        }
        
        return ActionSummary(
            total=summary_row["total"],
            pending=summary_row["pending"],
            in_progress=summary_row["in_progress"],
            completed=summary_row["completed"],
            overdue=summary_row["overdue"],
            by_priority=by_priority,
            by_team=by_team,
        )


@router.get("/{action_id}", response_model=ActionDetail)
async def get_action(action_id: UUID, db: Database = Depends(get_db)):
    """Get a specific action by ID."""
    query = """
        SELECT 
            id, priority, category, action_type, title, description, 
            impact, expected_impact, estimated_cost, deadline, due_date,
            affected_products, status, assigned_to, assigned_team,
            assigned_at, assigned_by, progress_percent, confidence_score,
            notes, action_items, created_at, updated_at
        FROM action_recommendations
        WHERE id = $1
    """
    
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(query, action_id)
        if not row:
            raise HTTPException(status_code=404, detail="Action not found")
        return dict(row)


@router.patch("/{action_id}/assign")
async def assign_action(
    action_id: UUID,
    assignment: ActionAssignment,
    db: Database = Depends(get_db),
):
    """Assign an action to a team or individual."""
    query = """
        UPDATE action_recommendations
        SET 
            assigned_to = $1,
            assigned_team = $2,
            assigned_by = $3,
            assigned_at = CURRENT_TIMESTAMP,
            due_date = $4,
            notes = COALESCE($5, notes),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = $6
        RETURNING id
    """
    
    # Log to history
    history_query = """
        INSERT INTO action_history (action_id, changed_field, new_value, changed_by, comment)
        VALUES ($1, 'assignment', $2, $3, $4)
    """
    
    async with db.pool.acquire() as conn:
        result = await conn.fetchrow(
            query,
            assignment.assigned_to,
            assignment.assigned_team,
            assignment.assigned_by,
            assignment.due_date,
            assignment.notes,
            action_id,
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Action not found")
        
        # Log assignment to history
        assignment_text = f"Assigned to {assignment.assigned_to or 'team'}: {assignment.assigned_team or 'N/A'}"
        await conn.execute(
            history_query,
            action_id,
            assignment_text,
            assignment.assigned_by,
            assignment.notes,
        )
        
        return {"success": True, "action_id": str(action_id)}


@router.patch("/{action_id}/status")
async def update_action_status(
    action_id: UUID,
    status_update: ActionStatusUpdate,
    db: Database = Depends(get_db),
):
    """Update action status and progress."""
    # Set completion timestamp if completed
    completed_at = "CURRENT_TIMESTAMP" if status_update.status == "completed" else "NULL"
    
    query = f"""
        UPDATE action_recommendations
        SET 
            status = $1,
            progress_percent = COALESCE($2, progress_percent),
            notes = COALESCE($3, notes),
            completed_at = {completed_at},
            completed_by = CASE WHEN $1 = 'completed' THEN $4 ELSE completed_by END,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = $5
        RETURNING id, status, progress_percent
    """
    
    # Log to history
    history_query = """
        INSERT INTO action_history (action_id, changed_field, new_value, changed_by, comment)
        VALUES ($1, 'status', $2, $3, $4)
    """
    
    async with db.pool.acquire() as conn:
        result = await conn.fetchrow(
            query,
            status_update.status,
            status_update.progress_percent,
            status_update.notes,
            status_update.updated_by,
            action_id,
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Action not found")
        
        # Log status change to history
        await conn.execute(
            history_query,
            action_id,
            f"{status_update.status} ({status_update.progress_percent}%)",
            status_update.updated_by,
            status_update.notes,
        )
        
        return {"success": True, "action_id": str(action_id), "new_status": result["status"]}


@router.post("/{action_id}/comments", response_model=ActionComment)
async def add_comment(
    action_id: UUID,
    comment: ActionCommentCreate,
    db: Database = Depends(get_db),
):
    """Add a comment to an action."""
    query = """
        INSERT INTO action_comments (action_id, comment, author)
        VALUES ($1, $2, $3)
        RETURNING id, action_id, comment, author, created_at, updated_at, is_edited
    """
    
    async with db.pool.acquire() as conn:
        # Check if action exists
        action_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM action_recommendations WHERE id = $1)",
            action_id,
        )
        if not action_exists:
            raise HTTPException(status_code=404, detail="Action not found")
        
        row = await conn.fetchrow(query, action_id, comment.comment, comment.author)
        return dict(row)


@router.get("/{action_id}/comments", response_model=List[ActionComment])
async def get_comments(action_id: UUID, db: Database = Depends(get_db)):
    """Get all comments for an action."""
    query = """
        SELECT id, action_id, comment, author, created_at, updated_at, is_edited
        FROM action_comments
        WHERE action_id = $1
        ORDER BY created_at DESC
    """
    
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, action_id)
        return [dict(row) for row in rows]


@router.get("/{action_id}/history")
async def get_action_history(action_id: UUID, db: Database = Depends(get_db)):
    """Get change history for an action."""
    query = """
        SELECT 
            id, changed_field, old_value, new_value, 
            changed_by, changed_at, comment
        FROM action_history
        WHERE action_id = $1
        ORDER BY changed_at DESC
    """
    
    async with db.pool.acquire() as conn:
        rows = await conn.fetch(query, action_id)
        return [dict(row) for row in rows]


# ========================================
# TEAM/USER ENDPOINTS
# ========================================

@router.get("/teams/list")
async def get_teams():
    """Get list of available teams (mock data for demo)."""
    return {
        "teams": [
            {"id": "production", "name": "Production Team", "description": "Manufacturing and production planning"},
            {"id": "supply_chain", "name": "Supply Chain Team", "description": "Logistics and supplier management"},
            {"id": "warehouse", "name": "Warehouse Team", "description": "Inventory and warehouse operations"},
            {"id": "sales", "name": "Sales Team", "description": "Sales, pricing, and customer relations"},
            {"id": "quality", "name": "Quality Assurance", "description": "Quality control and compliance"},
            {"id": "operations", "name": "Operations Team", "description": "General operations and coordination"},
        ]
    }


@router.get("/teams/{team_name}/actions", response_model=List[ActionDetail])
async def get_team_actions(team_name: str, db: Database = Depends(get_db)):
    """Get all actions assigned to a specific team."""
    return await get_actions(assigned_team=team_name, db=db)
