# debug_database.py - Enhanced to check all places in database
import sqlite3
import pandas as pd
import os
import json


def debug_database():
    db_path = 'database/college_data.db'

    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return

    print(f"📊 Database found at: {db_path}")
    print("=" * 80)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("📋 Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    print("=" * 80)

    # Define the tables to check
    college_tables = ['mca_colleges', 'mba_colleges', 'mtech_colleges']

    for table_name in college_tables:
        print(f"\n🔍 Checking table: {table_name}")
        print("-" * 60)

        try:
            # Check if table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not cursor.fetchone():
                print(f"❌ Table {table_name} does not exist!")
                continue

            # Get table structure
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"📝 Table columns ({len(columns)} columns):")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")

            # Get count of records
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_records = cursor.fetchone()[0]
            print(f"📊 Total records: {total_records}")

            # Check for NULL or empty place values
            print(f"\n🔎 Checking for NULL/empty place values:")
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM {table_name} 
                WHERE place IS NULL OR place = '' OR TRIM(place) = ''
            """)
            null_places = cursor.fetchone()[0]
            print(f"  - Records with NULL/empty place: {null_places}")

            # Get all distinct places
            print(f"\n📍 Distinct places in {table_name}:")
            cursor.execute(f"""
                SELECT DISTINCT place, COUNT(*) as college_count
                FROM {table_name}
                WHERE place IS NOT NULL AND place != '' AND TRIM(place) != ''
                GROUP BY place
                ORDER BY place
            """)

            places_data = cursor.fetchall()
            print(f"  - Total distinct places: {len(places_data)}")

            if len(places_data) > 0:
                # Print places in a formatted way
                print("\n  Places (with college count):")
                for place, count in places_data:
                    print(f"    - '{place}' ({count} colleges)")

                # Find common place name variations
                print(f"\n🔍 Analyzing place name patterns:")
                place_variations = {}
                for place, count in places_data:
                    place_lower = str(place).lower().strip()
                    if place_lower not in place_variations:
                        place_variations[place_lower] = []
                    place_variations[place_lower].append(place)

                # Report variations
                variations_found = False
                for base_name, variations in place_variations.items():
                    if len(variations) > 1:
                        print(f"    ⚠️  Multiple variations for '{base_name}': {variations}")
                        variations_found = True

                if not variations_found:
                    print("    ✅ No place name variations found")

            # Check specific problematic queries
            print(f"\n🔬 Testing specific queries for {table_name}:")

            # Test 1: Bengaluru variations
            test_queries = [
                ("Bengaluru", f"SELECT COUNT(*) FROM {table_name} WHERE place = 'Bengaluru'"),
                ("Bangalore", f"SELECT COUNT(*) FROM {table_name} WHERE place = 'Bangalore'"),
                ("Bangalore (case-insensitive)", f"SELECT COUNT(*) FROM {table_name} WHERE LOWER(place) = 'bengaluru'"),
                ("Bangalore (like)",
                 f"SELECT COUNT(*) FROM {table_name} WHERE place LIKE '%Bengaluru%' OR place LIKE '%Bangalore%'")
            ]

            for test_name, query in test_queries:
                try:
                    cursor.execute(query)
                    count = cursor.fetchone()[0]
                    print(f"  - {test_name}: {count} colleges")
                except Exception as e:
                    print(f"  - {test_name}: Error - {e}")

            # Test 2: Check category distribution
            print(f"\n📊 Category distribution in {table_name}:")
            cursor.execute(f"""
                SELECT category, COUNT(*) as count
                FROM {table_name}
                GROUP BY category
                ORDER BY category
            """)
            categories = cursor.fetchall()
            for category, count in categories:
                print(f"  - {category}: {count} colleges")

            # Test 3: Sample data with specific rank range
            print(f"\n🔍 Sample colleges (GM category, rank range 300-500):")
            cursor.execute(f"""
                SELECT college_name, place, opening_cutoff_rank, closing_cutoff_rank, category
                FROM {table_name}
                WHERE category = 'GM'
                  AND opening_cutoff_rank <= 500
                  AND closing_cutoff_rank >= 300
                ORDER BY opening_cutoff_rank
                LIMIT 5
            """)

            sample_colleges = cursor.fetchall()
            if sample_colleges:
                for college in sample_colleges:
                    print(f"    - {college[0]} ({college[1]}): {college[2]}-{college[3]} ({college[4]})")
            else:
                print("    No colleges found in rank range 300-500")

                # Show what ranks are available
                cursor.execute(f"""
                    SELECT MIN(opening_cutoff_rank), MAX(closing_cutoff_rank), AVG(opening_cutoff_rank), AVG(closing_cutoff_rank)
                    FROM {table_name}
                    WHERE category = 'GM'
                """)
                min_open, max_close, avg_open, avg_close = cursor.fetchone()
                print(f"    Rank range available: {min_open} to {max_close}")
                print(f"    Average range: {avg_open:.0f} to {avg_close:.0f}")

            # Test 4: Check specific place queries
            print(f"\n🔍 College counts by place (GM category):")
            top_places_query = f"""
                SELECT place, COUNT(*) as count
                FROM {table_name}
                WHERE category = 'GM'
                GROUP BY place
                ORDER BY count DESC
                LIMIT 10
            """

            try:
                df_places = pd.read_sql(top_places_query, conn)
                if len(df_places) > 0:
                    print(df_places.to_string(index=False))
                else:
                    print("    No data found")
            except Exception as e:
                print(f"    Error: {e}")

            # Test 5: Year distribution
            print(f"\n📅 Year distribution in {table_name}:")
            cursor.execute(f"""
                SELECT year, COUNT(*) as count
                FROM {table_name}
                GROUP BY year
                ORDER BY year
            """)
            years = cursor.fetchall()
            for year, count in years:
                print(f"  - {year}: {count} colleges")

        except Exception as e:
            print(f"❌ Error analyzing {table_name}: {e}")
            import traceback
            traceback.print_exc()

        print("=" * 80)

    # Additional analysis: Check for potential issues
    print("\n🔧 ADDITIONAL DATABASE ANALYSIS")
    print("=" * 80)

    # Check data consistency across tables
    print("\n📊 Comparing data across all college tables:")
    for table in college_tables:
        try:
            # Check if table exists
            cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone()[0] == 0:
                continue

            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(DISTINCT place) FROM {table} WHERE place IS NOT NULL")
            place_count = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(DISTINCT category) FROM {table}")
            category_count = cursor.fetchone()[0]

            print(f"  {table}:")
            print(f"    - Total records: {count}")
            print(f"    - Distinct places: {place_count}")
            print(f"    - Distinct categories: {category_count}")

        except Exception as e:
            print(f"  {table}: Error - {e}")

    # Check for common issues
    print("\n🔍 Checking for common data issues:")

    # 1. Check for invalid rank ranges (opening > closing)
    for table in college_tables:
        try:
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM {table} 
                WHERE opening_cutoff_rank > closing_cutoff_rank
            """)
            invalid_ranges = cursor.fetchone()[0]
            if invalid_ranges > 0:
                print(f"  ⚠️  {table}: {invalid_ranges} records have opening rank > closing rank")
        except:
            pass

    # 2. Check for negative ranks
    for table in college_tables:
        try:
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM {table} 
                WHERE opening_cutoff_rank < 0 OR closing_cutoff_rank < 0
            """)
            negative_ranks = cursor.fetchone()[0]
            if negative_ranks > 0:
                print(f"  ⚠️  {table}: {negative_ranks} records have negative ranks")
        except:
            pass

    # 3. Check for zero seats
    for table in college_tables:
        try:
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM {table} 
                WHERE seats <= 0
            """)
            zero_seats = cursor.fetchone()[0]
            if zero_seats > 0:
                print(f"  ⚠️  {table}: {zero_seats} records have zero or negative seats")
        except:
            pass

    # Create summary report
    print("\n📋 SUMMARY REPORT")
    print("=" * 80)

    summary = []
    for table in college_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone()[0] == 0:
                summary.append(f"{table}: Table does not exist")
                continue

            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(DISTINCT place) FROM {table}")
            places = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(DISTINCT category) FROM {table}")
            categories = cursor.fetchone()[0]

            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM {table} 
                WHERE place IS NULL OR place = '' OR TRIM(place) = ''
            """)
            null_places = cursor.fetchone()[0]

            summary.append(
                f"{table}: {total} records, {places} places, {categories} categories, {null_places} null places")

        except Exception as e:
            summary.append(f"{table}: Error - {e}")

    for item in summary:
        print(f"  - {item}")

    print("\n💡 RECOMMENDATIONS:")
    print("  1. Ensure place names are consistent (e.g., use 'Bengaluru' instead of 'Bangalore')")
    print("  2. Check for NULL or empty place values")
    print("  3. Verify rank ranges are valid (opening <= closing)")
    print("  4. Check category names match expected values (GM, OBC, SC, ST)")
    print("  5. Ensure all required tables exist and have data")

    conn.close()
    print("\n✅ Debug complete!")


def test_specific_prediction():
    """Test specific prediction scenarios"""
    print("\n🎯 TESTING SPECIFIC PREDICTION SCENARIOS")
    print("=" * 80)

    db_path = 'database/college_data.db'
    if not os.path.exists(db_path):
        print("Database not found for testing")
        return

    conn = sqlite3.connect(db_path)

    # Test cases
    test_cases = [
        {
            "name": "MCA in Bengaluru with rank 400 (GM)",
            "table": "mca_colleges",
            "place": "Bengaluru",
            "category": "GM",
            "rank": 400,
            "year": 2024
        },
        {
            "name": "MBA in Bengaluru with rank 1000 (GM)",
            "table": "mba_colleges",
            "place": "Bengaluru",
            "category": "GM",
            "rank": 1000,
            "year": 2024
        },
        {
            "name": "MTech in Bengaluru with rank 500 (GM)",
            "table": "mtech_colleges",
            "place": "Bengaluru",
            "category": "GM",
            "rank": 500,
            "year": 2024
        },
        {
            "name": "MCA in Mysore with rank 800 (GM)",
            "table": "mca_colleges",
            "place": "Mysore",
            "category": "GM",
            "rank": 800,
            "year": 2024
        }
    ]

    for test in test_cases:
        print(f"\n🔍 Testing: {test['name']}")

        try:
            query = f"""
                SELECT college_name, place, opening_cutoff_rank, closing_cutoff_rank, category, year
                FROM {test['table']}
                WHERE place = ? 
                  AND category = ?
                  AND opening_cutoff_rank <= ?
                  AND closing_cutoff_rank >= ?
                  AND year = ?
                ORDER BY opening_cutoff_rank
                LIMIT 5
            """

            params = (test['place'], test['category'], test['rank'], test['rank'], test['year'])

            df = pd.read_sql(query, conn, params=params)

            if len(df) > 0:
                print(f"✅ Found {len(df)} matching colleges:")
                for idx, row in df.iterrows():
                    print(f"   {idx + 1}. {row['college_name']} ({row['place']})")
                    print(f"      Rank: {row['opening_cutoff_rank']} - {row['closing_cutoff_rank']}")
            else:
                print(f"❌ No exact matches found")

                # Show what's available
                alt_query = f"""
                    SELECT college_name, place, opening_cutoff_rank, closing_cutoff_rank, category, year
                    FROM {test['table']}
                    WHERE place = ? 
                      AND category = ?
                      AND year = ?
                    ORDER BY opening_cutoff_rank
                    LIMIT 3
                """
                alt_params = (test['place'], test['category'], test['year'])
                alt_df = pd.read_sql(alt_query, conn, params=alt_params)

                if len(alt_df) > 0:
                    print(f"   Available colleges in {test['place']} ({test['category']}):")
                    for idx, row in alt_df.iterrows():
                        print(
                            f"   - {row['college_name']}: {row['opening_cutoff_rank']} - {row['closing_cutoff_rank']}")
                else:
                    print(f"   No colleges found for {test['place']} ({test['category']}) in {test['year']}")

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == '__main__':
    print("🔍 COLLEGE PREDICTOR DATABASE DEBUGGER")
    print("=" * 80)

    # Run main debug
    debug_database()

    # Run specific prediction tests
    test_specific_prediction()

    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("\n📝 NEXT STEPS:")
    print("1. Check the logs above for any warnings or errors")
    print("2. Look for 'null places' or inconsistent place names")
    print("3. Verify that all expected tables and columns exist")
    print("4. Check if sample queries return expected results")
    print("5. If issues found, update your CSV files and re-run init_db.py")