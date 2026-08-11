---
name: dbx-create-table-sql
description: Inspect a PostgreSQL database through DBX and draft convention-aligned CREATE TABLE SQL for new MES2.0 tables. Use when a user requests a new table, Chinese table or column comments, field types or defaults, audit columns, selector data sources, table naming, keys, uniqueness, or query indexes; query the live schema before deciding and do not execute DDL unless explicitly requested.
---

# DBX 建表 SQL

通过 DBX 查询当前 PostgreSQL 数据库的连接、表、列、注释、约束和索引，按 MES2.0 的实际规范为新增业务表生成可执行 SQL。默认只查询并输出 SQL，不执行 DDL。

## Workflow

### 1. Clarify Scope

- Determine whether the user wants SQL only or authorizes executing DDL. Treat “use DBX” as authorization to inspect, not to create or alter objects.
- Ask only when a material decision cannot be derived safely: target database, table naming, duplicate-row policy, normalized versus text multi-select storage, or permission to execute DDL.
- Preserve the user's exact Chinese table and field semantics. Do not silently turn a filter condition into a uniqueness rule.

### 2. Inspect the Database

Use DBX MCP tools in this order:

- dbx_list_connections: identify the current PostgreSQL connection and database. Prefer the returned connection_id when a displayed connection name contains an emoji or other prefix.
- dbx_list_tables: list tables and comments in the relevant schema.
- dbx_get_schema_context or dbx_describe_table: inspect likely neighboring tables, the same module, the same business domain, selector source tables, and tables with similar audit fields.
- dbx_execute_query: run read-only metadata queries against information_schema, pg_catalog.pg_description, pg_indexes, pg_constraint, and extension catalogs.

Verify the proposed table name is unused with to_regclass('public.table_name'). Check existing index names before adding indexes.
Never hard-code environment-specific metadata IDs. Omit sequence-backed primary-key columns from inserts, use RETURNING to pass a newly generated table ID to column metadata, and resolve parent IDs through stable names or other environment-independent keys.

Before trusting a DBX result, verify the runtime target with `current_database()` and `current_user`. Match it to the API's active `ASPNETCORE_ENVIRONMENT` and connection string; in this repository, the IIS Express profile uses Development/MES2_DEV while the VOL.WebApi profile uses Staging/MES2_UAT. A table or metadata row verified in one database does not prove that the debugging API can see it in another.

When a physical table is created by an administrative role, inspect privileges for the API runtime role. PostgreSQL's `information_schema.columns` only exposes columns visible to the current role, so a missing table grant can make `SyncTable` return an empty structure without meaning the table is absent. Include environment-appropriate grants in deployment SQL when the table owner and API role differ:

~~~sql
GRANT USAGE ON SCHEMA public TO <runtime_role>;
GRANT SELECT, INSERT, UPDATE, DELETE
ON TABLE public.<table_name>
TO <runtime_role>;
~~~

### 3. Derive Conventions

Do not copy a convention from one table without comparing several tables. Report the evidence briefly and use the most common compatible pattern.

- **Module prefix**: follow nearby namespaces and table names. In MES2.0, ie_ is used for industrial-engineering/process features, mdm_ for master data, and qm_ for quality features; verify current usage before choosing.
- **Identifiers**: existing MES tables commonly use id uuid NOT NULL as the primary key and let application code provide the UUID. Do not add a UUID default unless neighboring tables use one or the user requests it.
- **Text**: use PostgreSQL text when the requirement says text or nearby tables use it.
- **Integer values**: use integer for IDs and explicit integer ordering fields. Use smallint for 0/1 flags when that matches the live schema, and enforce CHECK (flag IN (0, 1)) when the requirement defines the domain.
- **Timestamps**: use timestamp without time zone for audit timestamps when that is the dominant database type.
- **Audit columns**: the common MES pattern is create_id integer, creator text, create_time timestamp without time zone, modify_id integer, modifier text, modify_time timestamp without time zone. Prefer this over less common variants such as create_user or createor unless the neighboring module consistently uses them.
- **Metadata audit identity**: when inserting or updating rows in `sys_tableinfo`, `sys_tablecolumn`, `sys_menu`, `sys_dictionary`, `sys_dictionarylist`, or similar system metadata tables, set the creator/new-entry user and modifier/editor user to `曹亦鸣` as applicable. Do not leave these audit-user fields blank or substitute the database/API runtime user.
- **Defaults**: implement explicitly requested defaults such as order_no DEFAULT 0 and enable DEFAULT 1; do not invent defaults for audit fields.

### 4. Map Fields and Relationships

- Use clear lowercase snake_case names and keep each requested field represented once.
- Add COMMENT ON TABLE and COMMENT ON COLUMN statements for the Chinese table and field comments.
- For a multi-select operation field, first inspect existing storage. op_codes text is acceptable when the requested design is one table and the application already stores selected operation codes as text. Document that the value stores mdm_operation.code values; do not duplicate operation names unless required.
- Treat sys_tablecolumn.DropNo as a stable dictionary number, not as a place to store raw SQL. Inspect sys_dictionary and reuse an existing compatible dictionary number; if the requested source SQL needs a new or changed dictionary, call that out as a separate sys_dictionary change.
- When a requested page hierarchy contains a missing menu directory, inspect sys_menu and create the missing menu conditionally with its parent resolved by name. Do not assume sys_menu.Menu_Id equals sys_tableinfo.Table_Id. If the builder metadata also represents directories in sys_tableinfo, create a matching no-entity folder row with TableTrueName NULL and attach the real table metadata below that folder.
- When a requested page hierarchy contains a missing leaf menu, create the complete sys_menu row as well as the parent directory: resolve the parent Menu_Id dynamically, set the physical TableName and generated route Url, provide the Auth JSON and audit/menu fields, and make the insert idempotent. The sys_menu parent chain and sys_tableinfo parent chain use different ID spaces.
- If users must query by one selected operation frequently, recommend a normalized relation table with one row per (category_id, op_code) instead of claiming that a normal index on comma-separated text will solve the query.
- Do not add foreign keys to a multi-valued text field. Add a real foreign key only for a single-valued column whose target and delete/update behavior are clear.

### 5. Choose Keys and Indexes

- A table has one primary key. Keep id as the primary key unless the user explicitly requires a natural or composite primary key and the business semantics support it.
- A field being a filter does not make it unique. Add a UNIQUE constraint only when the user confirms duplicates are invalid or the existing business model proves it.
- Add B-tree indexes only for actual equality, prefix, join, or ordering patterns. Candidate filter indexes commonly include individual category fields and a composite (enable, order_no) for active ordered lists, but avoid indexing every column automatically.
- A leading-wildcard fuzzy query such as ILIKE '%keyword%' is not helped by a normal B-tree index. Check whether pg_trgm is installed before proposing a GIN trigram index; do not install extensions implicitly.
- A normal index on multi-select text is generally not useful for “contains one operation code”. Prefer the normalized relation-table design when that query matters.
- Match existing index naming, commonly <table>_<column>_idx, <table>_pk, and un_<table>_<column> for unique business keys.

### 6. Produce and Validate SQL

Produce one coherent PostgreSQL block containing, as applicable:

- CREATE TABLE public.<table_name> with the primary key, required fields, defaults, and domain checks.
- COMMENT ON TABLE and COMMENT ON COLUMN statements.
- Separate CREATE INDEX or ALTER TABLE ... ADD CONSTRAINT ... UNIQUE statements only when justified by query semantics and database evidence.

Before handing off:

- Check the candidate table name, column names, PostgreSQL types, nullability, defaults, comments, and constraint names for consistency.
- Check the physical table, metadata rows, runtime-role privileges, and `IsColumnData` values with the validation queries below; do not treat successful model or service generation as proof that Vue metadata is valid.
- State the selected connection/database and whether DDL was executed. If only metadata queries ran, say so explicitly.
- If an ambiguity remains, present the assumption and ask a focused question instead of embedding a risky business rule in SQL.

### SQL Output Style

- When the user requests a deployment script that creates menus, `sys_tableinfo`, and `sys_tablecolumn` together, output one complete `BEGIN; DO $$ ... END $$; COMMIT;` block or an equivalently complete transactional script. Resolve parent IDs by stable names and use `RETURNING` for newly generated IDs; never hard-code environment-specific IDs.
- Add necessary section comments in the SQL, especially before resolving menu parents, creating parent and leaf `sys_menu` rows, creating `sys_tableinfo` directory/entity rows, and inserting `sys_tablecolumn` metadata. Explain relationships and non-obvious values, but do not comment every ordinary assignment.
- A complete `sys_menu` insert includes `MenuName`, `Auth`, `Icon`, `Description`, `Enable`, `OrderNo`, `TableName`, `ParentId`, `Url`, `CreateDate`, `Creator`, `ModifyDate`, and `Modifier` when those columns exist. Use the generated page route in `Url` and attach a leaf menu to the resolved parent menu ID.
- A physical column inserted into `sys_tablecolumn` must explicitly set `IsColumnData = 1`, including audit columns and the primary-key column. Use `IsDisplay` to hide columns from the grid; do not use `IsColumnData = 0` for a hidden physical column.
- In `sys_tablecolumn`, a larger `OrderNo` value sorts earlier; assign ordering values with that descending-priority semantics and verify the resulting order in the read-only checks.
- When inserting or updating `sys_tableinfo`, `sys_tablecolumn`, `sys_menu`, `sys_dictionary`, `sys_dictionarylist`, or similar system metadata rows, set the new-entry/creator and edit/modifier user fields to `曹亦鸣` as applicable.
- Preserve safety checks for existing metadata. If the script raises on an existing business-table configuration, state that rerunning it in the same environment will roll back the whole transaction and provide or describe the incremental menu-only repair path when relevant.
- Finish with read-only verification queries for the menu parent-child relationship, table metadata parent-child relationship, column count, and `IsColumnData` count.

## MES2.0 Generator Validation

For a table intended for the MES2.0 code generator, validate the database state and the browser payload separately:

- Every physical column represented in `sys_tablecolumn` must have `IsColumnData = 1`. The Vue generator's `GetGridColumns` skips every row where `IsColumnData == 0`; if all rows are zero, it returns `未获取到数据!` even though the physical table and metadata rows exist.
- `IsColumnData` is different from `IsDisplay`: use `IsDisplay` to hide a column such as `id` or `create_id`, but keep real physical columns as data columns.
- `SyncTable` detects added, removed, and type/nullability changes, but existing-column synchronization does not repair `IsColumnData`. Repair that flag explicitly or recreate the metadata configuration.
- Model and business-class generation can still succeed when `IsColumnData` is zero because entity generation does not use the same grid-column filter. This is not evidence that Vue generation will succeed.
- `CreateVuePage` consumes the `Sys_TableInfo` object posted by the builder page; it does not reload `sys_tablecolumn` immediately before generation. After changing metadata with SQL, reload/reselect/reopen the builder configuration and verify the request payload contains `tableColumns[*].isColumnData = 1`. Do not save a stale page before refreshing, because it can write the old zero values back to the database.

~~~sql
SELECT
    tc."TableName",
    count(*) AS total_columns,
    count(*) FILTER (WHERE tc."IsColumnData" = 1) AS data_columns,
    count(*) FILTER (WHERE tc."IsColumnData" = 0) AS non_data_columns
FROM public.sys_tablecolumn tc
WHERE tc."TableName" = '<table_name>'
GROUP BY tc."TableName";
~~~

## Metadata Query Templates

Adapt the schema and table filters before executing these read-only queries.

~~~sql
-- Tables, table comments, and relevant columns
SELECT
    c.table_name,
    c.column_name,
    c.data_type,
    c.udt_name,
    c.is_nullable,
    c.column_default,
    pgd.description AS column_comment,
    obj_description(cls.oid, 'pg_class') AS table_comment
FROM information_schema.columns c
LEFT JOIN pg_catalog.pg_class cls
    ON cls.relname = c.table_name
LEFT JOIN pg_catalog.pg_namespace ns
    ON ns.oid = cls.relnamespace
   AND ns.nspname = c.table_schema
LEFT JOIN pg_catalog.pg_description pgd
    ON pgd.objoid = cls.oid
   AND pgd.objsubid = c.ordinal_position
WHERE c.table_schema = 'public'
  AND c.table_name IN ('neighbor_table_1', 'neighbor_table_2')
ORDER BY c.table_name, c.ordinal_position;
~~~

~~~sql
-- Audit-field frequency by name and type
SELECT column_name, data_type, udt_name, count(*) AS table_count
FROM information_schema.columns
WHERE table_schema = 'public'
  AND column_name IN (
      'creator', 'create_user', 'createor', 'create_id', 'create_time',
      'modifier', 'modify_user', 'modify_id', 'modify_time'
  )
GROUP BY column_name, data_type, udt_name
ORDER BY column_name, table_count DESC;
~~~

~~~sql
-- Candidate name and extension/index checks
SELECT to_regclass('public.<candidate_table_name>');

SELECT indexname, tablename, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('neighbor_table_1', 'neighbor_table_2')
ORDER BY tablename, indexname;

SELECT extname, extversion
FROM pg_extension
WHERE extname = 'pg_trgm';
~~~
