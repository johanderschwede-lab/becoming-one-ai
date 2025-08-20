import os, hashlib, yaml, datetime, pathlib, psycopg
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_DB_URL: str
    COMPASS_PROJECT_PREFIX: str = "compass-2025-08-v1"
    class Config: env_file = ".env"

S = Settings()
SNAP_DIR = pathlib.Path("snapshots")

def active_version(conn):
    with conn.cursor() as cur:
        cur.execute("""
            select version from compass.versions
            where status='active' and version like %s
        """, (f"{S.COMPASS_PROJECT_PREFIX}%",))
        rows = [r[0] for r in cur.fetchall()]
        if not rows:
            raise RuntimeError("No active version found")
        from semver import VersionInfo as SemVer
        rows_sorted = sorted(rows, key=lambda v: SemVer.parse(v.split(S.COMPASS_PROJECT_PREFIX + ".")[-1]))
        return rows_sorted[-1]

def sections(conn, version):
    with conn.cursor() as cur:
        cur.execute("""
            select s.name, s.body
            from compass.versions v
            join compass.sections s on s.version_id = v.id
            where v.version = %s
            order by s.name asc
        """, (version,))
        return dict(cur.fetchall())

def main():
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    with psycopg.connect(S.SUPABASE_DB_URL) as conn:
        v = active_version(conn)
        secs = sections(conn, v)
        data = {"id": S.COMPASS_PROJECT_PREFIX, "version": v, "sections": secs}
        yml = yaml.safe_dump(data, sort_keys=True)

        # Write to DB
        with conn.cursor() as cur:
            cur.execute("""
                insert into compass.snapshots (version, yaml) values (%s, %s)
            """, (v, yml))
            conn.commit()

        # Write local file
        ts = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        path = SNAP_DIR / f"{v}-{ts}.yaml"
        path.write_text(yml, encoding="utf-8")
        print(f"Snapshot written: {path}")

if __name__ == "__main__":
    main()
