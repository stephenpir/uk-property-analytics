from pathlib import Path

from python.utils.snowflake_connection import create_snowflake_connection


def execute_sql_file(
    sql_file: str,
    profile_name: str,
    target_name: str,
    parameters: list[str] | None = None,
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
            for parameter in parameters or []:
                name, value = parameter.split("=", 1)
                sql = sql.replace(f"{{{{ {name} }}}}", value)

            ### ADD THIS EXACT LINE HERE ###
            print(f"\n=== FULL SQL ===\n{sql}\n================")  # Single debug line
            
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
    parser.add_argument(
        "--param",
        action="append",
        default=[],
    )
    args = parser.parse_args()

    execute_sql_file(
        sql_file=args.sql_file,
        profile_name=args.profile,
        target_name=args.target,
        parameters=args.param,
    )