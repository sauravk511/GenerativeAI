#!/usr/bin/env python3
from db import init_database
from config import Config

def main():
	print("="*60)
	print("DATABASE SETUP AND VERIFICATION")
	print("="*60)

	print("\nConfiguration:")
	print(f"   SQLite DB Path: {Config.DB_PATH}\n")

	try:
		success = init_database()
		if success:
			print("\n[SUCCESS] Database setup completed successfully.")
	except Exception as e:
		print(f"\n[ERROR] Setup failed: {e}")


if __name__ == "__main__":
	main()
