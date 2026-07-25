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


def execute_sql_file(
    sql_file: str,
    profile_name: str,
    target_name: str,
) -> None:
    target = load_dbt_target(profile_name, target_name)

    sql_path = Path(sql_file)

    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    connection = snowflake.connector.connect(
        account=target["account"],
        user=target["user"],
        password=target["password"],
        warehouse=target["warehouse"],
        database=target["database"],
        schema=target["schema"],
        role=target["role"],
    )

    try:
        with connection.cursor() as cursor:
            sql = sql_path.read_text()

            for statement in sql.split(";"):
                # Remove SQL comment lines
                lines = [
                    line
                    for line in statement.splitlines()
                    if not line.strip().startswith("--")
                ]

                statement = "\n".join(lines).strip()

                if not statement:
                    continue

                print(f"Executing: {statement[:100]}...")
                cursor.execute(statement)                    

    finally:
        connection.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--sql-file", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--target", required=True)

    args = parser.parse_args()

    execute_sql_file(
        sql_file=args.sql_file,
        profile_name=args.profile,
        target_name=args.target,
    )