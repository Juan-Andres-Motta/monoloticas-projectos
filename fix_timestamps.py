#!/usr/bin/env python3
"""
Fix all timestamp fields in Avro schemas to use Long() instead of Integer()
"""
import os
import re


def fix_timestamps_in_file(file_path):
    """Fix timestamp = Integer() to timestamp = Long() in a file"""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Replace timestamp = Integer() with timestamp = Long()
        updated_content = re.sub(
            r"timestamp = Integer\(\)(\s*#[^\n]*)?",
            r"timestamp = Long()  # Use Long for Unix timestamps in milliseconds",
            content,
        )

        if updated_content != content:
            with open(file_path, "w") as f:
                f.write(updated_content)
            print(f"✅ Updated timestamps in: {file_path}")
            return True
        else:
            print(f"⚪ No changes needed in: {file_path}")
            return False

    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def main():
    """Fix timestamps in all avro_schemas.py files"""
    base_dir = "/Users/juan/Desktop/uniandes/monoliticas"

    avro_schema_files = [
        "campaingn/messaging/schemas/avro_schemas.py",
        "tracking/messaging/schemas/avro_schemas.py",
        "comission/messaging/avro_schemas.py",
        "payment/messaging/schemas/avro_schemas.py",
    ]

    print("🔧 Fixing timestamp fields in Avro schemas...")
    print("=" * 50)

    total_updated = 0
    for file_path in avro_schema_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            if fix_timestamps_in_file(full_path):
                total_updated += 1
        else:
            print(f"⚠️  File not found: {full_path}")

    print("=" * 50)
    print(f"🎉 Updated {total_updated} files with Long timestamp fields")
    print("✅ All timestamp fields now use Long() for Unix millisecond timestamps")


if __name__ == "__main__":
    main()
