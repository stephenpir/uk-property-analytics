from pathlib import Path

from python.utils.snowflake_connection import create_snowflake_connection


def execute_sql_file(
    sql_file: str,
    profile_name: str,
    target_name: str,
    year: int,
) -> None:
    sql_path = Path(sql_file)

    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    connection = create_snowflake_connection(
        profile_name=profile_name,
        target_name=target_name,
    )

    try:
        with connection.cursor() as cursor:
            sql = sql_path.read_text()

            sql = sql.replace("{{ YEAR }}", str(year))

            for statement in sql.split(";"):
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

                if cursor.rowcount is not None and cursor.rowcount >= 0:
                    print(f"Rows affected: {cursor.rowcount}")

    finally:
        connection.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--sql-file", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--year", required=True, type=int)

    args = parser.parse_args()

    execute_sql_file(
        sql_file=args.sql_file,
        profile_name=args.profile,
        target_name=args.target,
        year=args.year,
    )