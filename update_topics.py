#!/usr/bin/env python3
"""
Update all topic names from v0206 to v0216 to use Long timestamp schemas
"""
import os
import re


def update_topics_in_file(file_path):
    """Update topic versions from v0206 to v0216 in a file"""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Replace v0206 with v0216 in topic names
        updated_content = re.sub(r'-v0206"', r'-v0216"', content)

        if updated_content != content:
            with open(file_path, "w") as f:
                f.write(updated_content)
            print(f"✅ Updated topic versions in: {file_path}")
            return True
        else:
            print(f"⚪ No changes needed in: {file_path}")
            return False

    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False


def main():
    """Update topics in all avro_schemas.py files"""
    base_dir = "/Users/juan/Desktop/uniandes/monoliticas"

    avro_schema_files = [
        "campaingn/messaging/schemas/avro_schemas.py",
        "tracking/messaging/schemas/avro_schemas.py",
        "comission/messaging/avro_schemas.py",
        "payment/messaging/schemas/avro_schemas.py",
    ]

    print("🔧 Updating topic versions from v0206 to v0216...")
    print("=" * 50)

    total_updated = 0
    for file_path in avro_schema_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            if update_topics_in_file(full_path):
                total_updated += 1
        else:
            print(f"⚠️  File not found: {full_path}")

    print("=" * 50)
    print(f"🎉 Updated {total_updated} files with v0216 topic names")
    print("✅ All topics now use v0216 version for Long timestamp compatibility")


if __name__ == "__main__":
    main()
