-- Delete items with invalid component types
-- Allowed: 'ERC', 'Rail Pad', 'Liner', 'Sleeper'
-- Current Invalid (based on seed script): 'Rail Clip', 'Concrete Sleeper', 'Fishplate', 'Bolt', 'Pad'
-- Note: 'Rail Clip' should be 'ERC', 'Concrete Sleeper' -> 'Sleeper', 'Pad' -> 'Rail Pad'.
-- We will delete ALL so we can re-seed cleanly with perfect distribution.

BEGIN;

DELETE FROM items WHERE component_type NOT IN ('ERC', 'Rail Pad', 'Liner', 'Sleeper');

-- Optional: If we want to clean everything to strictly enforce distribution, we might just TRUNCATE.
-- But user asked to "Delete invalid types".
-- Given the previous seed was random, likely EVERYTHING is invalid based on strict naming.
-- e.g. "Rail Clip" != "ERC"

COMMIT;
