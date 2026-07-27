from pathlib import Path

import snowflake.connector
import yaml


def load_dbt_target(profile_name: str, target_name: str) -> dict:
    profiles_path = Path.home() / ".dbt" / "profiles.yml"

    with profiles_path.open() as file:
        profiles = yaml.safe_load(file)

    try:
        profile = profiles[profile_name]
        target = profile["outputs"][target_name]
    except KeyError as exc:
        raise ValueError(
            f"dbt profile/target not found: {profile_name}/{target_name}"
        ) from exc

    return target


def create_snowflake_connection(
    profile_name: str,
    target_name: str,
):
    target = load_dbt_target(
        profile_name=profile_name,
        target_name=target_name,
    )

    return snowflake.connector.connect(
        account=target["account"],
        user=target["user"],
        password=target["password"],
        warehouse=target["warehouse"],
        database=target["database"],
        schema=target["schema"],
        role=target["role"],
    )