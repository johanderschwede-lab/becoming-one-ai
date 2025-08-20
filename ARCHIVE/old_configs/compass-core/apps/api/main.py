from fastapi import FastAPI, HTTPException, Response, Header
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Tuple, Any
import os, hashlib, yaml
import psycopg
from psycopg.types.json import Json
from semver import VersionInfo as SemVer

class Settings(BaseSettings):
    SUPABASE_DB_URL: str
    COMPASS_PROJECT_PREFIX: str = "compass-2025-08-v1"
    ADMIN_TOKEN: str = "replace-me"
    class Config:
        env_file = ".env"

S = Settings()
app = FastAPI(title="Compass Core API")

# ── DB helper ────────────────────────────────────────────────────────────────

def pg_conn():
    return psycopg.connect(S.SUPABASE_DB_URL)

def _parse_semver_suffix(version: str) -> SemVer:
    """Expecting version like PREFIX.<semver> e.g., compass-2025-08-v1.0.0"""
    prefix = S.COMPASS_PROJECT_PREFIX + "."
    if not version.startswith(prefix):
        raise ValueError(f"Version '{version}' does not start with prefix '{prefix}'")
    return SemVer.parse(version[len(prefix):])

def _compose_version(semver_obj: SemVer) -> str:
    return f"{S.COMPASS_PROJECT_PREFIX}.{semver_obj}"

def _active_version(conn) -> Tuple[str, str]:
    """Return (version, version_id) for highest active semver matching prefix."""
    with conn.cursor() as cur:
        cur.execute("""
            select version, id from compass.versions
            where status='active' and version like %s
        """, (f"{S.COMPASS_PROJECT_PREFIX}%",))
        rows = cur.fetchall()
        if not rows:
            raise HTTPException(404, "No active version found")
        rows_sorted = sorted(rows, key=lambda r: _parse_semver_suffix(r[0]))
        return rows_sorted[-1][0], rows_sorted[-1][1]

def _sections_for_version(conn, version: str) -> Tuple[Dict[str,str], str]:
    with conn.cursor() as cur:
        cur.execute("""
            select v.id, s.name, s.body
            from compass.versions v
            join compass.sections s on s.version_id = v.id
            where v.version = %s
            order by s.name asc
        """, (version,))
        rows = cur.fetchall()
        if not rows:
            raise HTTPException(404, f"No sections found for version {version}")
        version_id = rows[0][0]
        sections = {name: body for _, name, body in rows}
        return sections, version_id

def _assemble_yaml(prefix: str, version: str, sections: Dict[str,str]) -> str:
    data = {
        "id": prefix,
        "version": version,
        "sections": sections
    }
    return yaml.safe_dump(data, sort_keys=True)

def _checksum(yaml_text: str) -> str:
    return "sha256:" + hashlib.sha256(yaml_text.encode("utf-8")).hexdigest()

# ── Models ───────────────────────────────────────────────────────────────────

class ProposalIn(BaseModel):
    submitted_by: str
    source: str
    raw_idea: str
    normalized: dict  # {target_section, change_type, patch, impact}

# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/compass/active.yaml")
def get_active_yaml():
    with pg_conn() as conn:
        active_version, _ = _active_version(conn)
        sections, _ = _sections_for_version(conn, active_version)
        yml = _assemble_yaml(S.COMPASS_PROJECT_PREFIX, active_version, sections)
        return Response(content=yml, media_type="text/yaml")

@app.post("/proposals")
def submit_proposal(p: ProposalIn):
    with pg_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            insert into compass.proposals (submitted_by, source, raw_idea, normalized)
            values (%s, %s, %s, %s) returning id
        """, (p.submitted_by, p.source, p.raw_idea, Json(p.normalized)))
        pid = cur.fetchone()[0]
        conn.commit()
        return {"id": str(pid), "status": "queued"}

def _apply_additive_patch(sections: Dict[str,str], target: str, patch: Dict[str,Any]) -> Dict[str,str]:
    text = patch.get("text", "")
    if not text:
        raise HTTPException(400, "Patch missing 'text'")
    existing = sections.get(target, "")
    new_body = (existing + ("\n" if existing and not existing.endswith("\n") else "") + text + "\n").lstrip()
    s2 = dict(sections)
    s2[target] = new_body
    return s2

def _clone_with_bump(conn, from_version: str, sections: Dict[str,str], created_by: str, notes: str) -> str:
    # bump patch version
    sv = _parse_semver_suffix(from_version).bump_patch()
    new_version = _compose_version(sv)
    yml = _assemble_yaml(S.COMPASS_PROJECT_PREFIX, new_version, sections)
    chksum = _checksum(yml)
    with conn.cursor() as cur:
        # archive previous active
        cur.execute("update compass.versions set status='archived' where version = %s", (from_version,))
        # create new active version
        cur.execute("""
            insert into compass.versions (version, status, checksum, created_by, notes)
            values (%s, 'active', %s, %s, %s) returning id
        """, (new_version, chksum, created_by, notes))
        new_vid = cur.fetchone()[0]
        # insert sections
        for name, body in sections.items():
            cur.execute("""
                insert into compass.sections (version_id, name, body)
                values (%s, %s, %s)
            """, (new_vid, name, body))
        return new_version

@app.post("/admin/approve/{proposal_id}")
def approve_and_merge(proposal_id: str, x_admin_token: Optional[str] = Header(default=None)):
    if x_admin_token != S.ADMIN_TOKEN:
        raise HTTPException(401, "Unauthorized")

    with pg_conn() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("select submitted_by, source, raw_idea, normalized, status from compass.proposals where id = %s", (proposal_id,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404, "Proposal not found")
                submitted_by, source, raw_idea, normalized, status = row
                if status not in ("queued", "approved"):
                    raise HTTPException(400, f"Proposal status is '{status}', cannot merge")

                target = normalized.get("target_section")
                change_type = normalized.get("change_type")
                patch = normalized.get("patch", {})
                impact = normalized.get("impact", "low")

                active_version, _ = _active_version(conn)
                sections, _vid = _sections_for_version(conn, active_version)

                if change_type == "add":
                    merged_sections = _apply_additive_patch(sections, target, patch)
                else:
                    raise HTTPException(400, f"Unsupported change_type '{change_type}' in MVP")

                # Prepare diff
                old_body = sections.get(target, "")
                new_body = merged_sections.get(target, "")
                diff = {"section": target, "old": old_body, "new": new_body, "change_type": change_type, "impact": impact}

                # Create new version (patch bump)
                new_version = _clone_with_bump(conn, active_version, merged_sections, created_by="admin", notes=f"merge proposal {proposal_id}")

                # Mark proposal merged
                cur.execute("update compass.proposals set status='merged', rationale=%s where id=%s",
                            (f"Merged into {new_version}", proposal_id))
                # Record merge
                cur.execute("""
                    insert into compass.merges (proposal_id, from_version, to_version, diff, merged_by)
                    values (%s, %s, %s, %s, %s)
                """, (proposal_id, active_version, new_version, Json(diff), "admin"))

        conn.commit()
        return {"ok": True, "merged_version": new_version}

