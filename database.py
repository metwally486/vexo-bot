# أضف هذه الدوال في نهاية ملف database.py

# ==================== إدارة الأعمال (Portfolio) ====================

async def add_portfolio_item(
    title: str,
    project_type: str,
    description: str = "",
    preview_link: str = "",
    image_url: str = ""
) -> Optional[int]:
    """إضافة مشروع جديد لمعرض الأعمال"""
    try:
        async with pool.acquire() as conn:
            item_id = await conn.fetchval(
                """
                INSERT INTO portfolio (
                    title, type, description, preview_link, 
                    image_url, created_at
                ) VALUES ($1, $2, $3, $4, $5, NOW())
                RETURNING id
                """,
                title, project_type, description, preview_link, image_url
            )
            return item_id
    except Exception as e:
        print(f"❌ Error in add_portfolio_item: {e}")
        return None

async def get_portfolio(project_type: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """الحصول على مشاريع معرض الأعمال"""
    try:
        async with pool.acquire() as conn:
            if project_type:
                rows = await conn.fetch(
                    """
                    SELECT * FROM portfolio 
                    WHERE type = $1 
                    ORDER BY created_at DESC
                    LIMIT $2
                    """,
                    project_type, limit
                )
            else:
                rows = await conn.fetch(
                    """
                    SELECT * FROM portfolio 
                    ORDER BY created_at DESC
                    LIMIT $1
                    """,
                    limit
                )
            return [dict(r) for r in rows]
    except Exception as e:
        print(f"❌ Error in get_portfolio: {e}")
        return []

async def delete_portfolio_item(item_id: int) -> bool:
    """حذف مشروع من المعرض"""
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM portfolio WHERE id = $1",
                item_id
            )
            return True
    except Exception as e:
        print(f"❌ Error in delete_portfolio_item: {e}")
        return False

async def update_portfolio_item(
    item_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    preview_link: Optional[str] = None
) -> bool:
    """تحديث مشروع في المعرض"""
    try:
        async with pool.acquire() as conn:
            if title:
                await conn.execute(
                    "UPDATE portfolio SET title = $1 WHERE id = $2",
                    title, item_id
                )
            if description:
                await conn.execute(
                    "UPDATE portfolio SET description = $1 WHERE id = $2",
                    description, item_id
                )
            if preview_link:
                await conn.execute(
                    "UPDATE portfolio SET preview_link = $1 WHERE id = $2",
                    preview_link, item_id
                )
            return True
    except Exception as e:
        print(f"❌ Error in update_portfolio_item: {e}")
        return False
