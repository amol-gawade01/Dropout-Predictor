import os
from datetime import date
from pathlib import Path

import pandas as pd

from backend.app.db.session import SessionLocal
from backend.app.db.models import (
    Student,
    StudentFeatureSnapshot,
)

from ml.predict import MODEL_FEATURES


DATASET_PATH = Path(
    os.getenv(
        "EWS_DATASET_PATH",
        "ml/dataset.xlsx",
    )
)

SHEET_NAME = os.getenv(
    "EWS_DATASET_SHEET",
    "ML_Dataset",
)

IMPORT_LIMIT = int(
    os.getenv(
        "EWS_IMPORT_LIMIT",
        "5000",
    )
)

WEEK_START = date.fromisoformat(
    os.getenv(
        "EWS_WEEK_START",
        "2026-08-24",
    )
)


BOOL_FEATURES = {
    "financial_support_requested",
    "support_requested",
}


def python_value(value):

    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


def main():

    print(
        f"Reading dataset: {DATASET_PATH}"
    )

    df = pd.read_excel(
        DATASET_PATH,
        sheet_name=SHEET_NAME,
    )

    if IMPORT_LIMIT > 0:
        df = df.head(
            IMPORT_LIMIT
        )

    required_columns = {
        "student_id",
        "semester",
        "program_stream",
        "institution_type",
        "residence_mode",
        "scholarship_holder",
        *MODEL_FEATURES,
    }

    missing = (
        required_columns
        - set(df.columns)
    )

    if missing:
        raise RuntimeError(
            "Dataset is missing columns: "
            + ", ".join(
                sorted(missing)
            )
        )

    df["student_id"] = (
        df["student_id"]
        .astype(str)
        .str.strip()
    )

    student_codes = (
        df["student_id"]
        .tolist()
    )

    db = SessionLocal()

    try:

        # -------------------------
        # 1. Fetch existing students
        # -------------------------

        existing_students = (
            db.query(Student)
            .filter(
                Student.student_code.in_(
                    student_codes
                )
            )
            .all()
        )

        existing_codes = {
            s.student_code
            for s
            in existing_students
        }

        students_to_create = []

        for _, row in df.iterrows():

            code = row["student_id"]

            if code in existing_codes:
                continue

            student = Student(
                student_code=code,

                display_name=(
                    f"Student {code}"
                ),

                program_stream=(
                    str(
                        row[
                            "program_stream"
                        ]
                    )
                ),

                institution_type=(
                    str(
                        row[
                            "institution_type"
                        ]
                    )
                ),

                residence_mode=(
                    str(
                        row[
                            "residence_mode"
                        ]
                    )
                ),

                scholarship_holder=bool(
                    int(
                        row[
                            "scholarship_holder"
                        ]
                    )
                ),

                preferred_language=(
                    "en-IN"
                ),

                is_synthetic=True,
            )

            students_to_create.append(
                student
            )

        if students_to_create:

            db.add_all(
                students_to_create
            )

            db.commit()

        print(
            "New students created:",
            len(
                students_to_create
            ),
        )

        # -------------------------
        # 2. Reload student mapping
        # -------------------------

        students = (
            db.query(Student)
            .filter(
                Student.student_code.in_(
                    student_codes
                )
            )
            .all()
        )

        student_map = {
            s.student_code: s
            for s in students
        }

        imported_student_ids = [
            s.student_id
            for s in students
        ]

        # -------------------------
        # 3. Existing snapshots
        # -------------------------

        existing_snapshot_rows = (
            db.query(
                StudentFeatureSnapshot.student_id
            )
            .filter(
                StudentFeatureSnapshot.student_id.in_(
                    imported_student_ids
                ),
                StudentFeatureSnapshot.week_start_date
                == WEEK_START,
            )
            .all()
        )

        existing_snapshot_ids = {
            row[0]
            for row
            in existing_snapshot_rows
        }

        # -------------------------
        # 4. Create snapshots
        # -------------------------

        snapshots = []

        created_snapshots = 0
        skipped_snapshots = 0

        for _, row in df.iterrows():

            code = row["student_id"]

            student = student_map[
                code
            ]

            if (
                student.student_id
                in existing_snapshot_ids
            ):

                skipped_snapshots += 1

                continue

            feature_values = {}

            for feature in MODEL_FEATURES:

                value = python_value(
                    row[feature]
                )

                if (
                    feature
                    in BOOL_FEATURES
                    and value is not None
                ):

                    value = bool(
                        int(value)
                    )

                feature_values[
                    feature
                ] = value

            snapshot = (
                StudentFeatureSnapshot(
                    student_id=(
                        student.student_id
                    ),

                    semester=int(
                        row["semester"]
                    ),

                    week_start_date=(
                        WEEK_START
                    ),

                    **feature_values,
                )
            )

            snapshots.append(
                snapshot
            )

            if len(snapshots) >= 250:

                db.add_all(
                    snapshots
                )

                db.commit()

                created_snapshots += len(
                    snapshots
                )

                print(
                    "Snapshots created:",
                    created_snapshots,
                )

                snapshots.clear()

        if snapshots:

            db.add_all(
                snapshots
            )

            db.commit()

            created_snapshots += len(
                snapshots
            )

        print()
        print(
            "Import complete."
        )

        print(
            "Students in file:",
            len(df),
        )

        print(
            "New students:",
            len(
                students_to_create
            ),
        )

        print(
            "New snapshots:",
            created_snapshots,
        )

        print(
            "Existing snapshots skipped:",
            skipped_snapshots,
        )

        print(
            "Snapshot week:",
            WEEK_START,
        )

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


if __name__ == "__main__":
    main()