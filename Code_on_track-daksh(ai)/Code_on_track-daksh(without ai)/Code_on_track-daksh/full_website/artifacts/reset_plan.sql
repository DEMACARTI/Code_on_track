-- Dry-Run Reset Plan
-- DEPENDENCY ORDER: Child tables first, then parents (though CASCADE handles it, explicit is safer/cleaner)
-- Tables:
-- items (refs vendors)
-- item_events (refs items)
-- lot_health (refs items by lot_no? No, refs vendors? Need to check dependency)
-- lot_quality (refs lot_health? need to check)
-- engraving_queue (refs items)
-- engraving_history (refs engraving_queue)
-- notifications (independent)
-- users (independent)
-- job_schedules (independent)

-- RESET COMMANDS:
TRUNCATE TABLE 
    item_events,
    engraving_history, 
    engraving_queue,
    lot_quality, 
    lot_health, 
    notifications,
    items, -- refs vendors
    vendors,
    users, -- if we want to reset users? Prompt said "delete ALL existing data... tables: items, vendors...". Usually users are kept, but prompt said ALL. I will include users but recreate admin in seed.
    job_schedules 
    RESTART IDENTITY CASCADE;

-- Note: 'alembic_version' is PRESERVED.
