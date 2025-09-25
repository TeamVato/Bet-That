"""Check ingestion contract end-to-end for Bet-That odds processing."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import List

import pandas as pd

from .base import BaseCommand


class CheckIngestionContractCommand(BaseCommand):
    """Verify odds ingestion contract end-to-end."""

    name = "check-ingestion-contract"
    description = "Verify odds ingestion contract: normalize book names, infer pos, guarantee season"

    def run(self, *args, **kwargs) -> int:
        """Run the ingestion contract verification."""
        self.log("Starting ingestion contract verification")

        # Run the extended integrity tests
        test_result = self.run_pytest("tests/test_importer_integrity.py", verbose=True)
        if test_result != 0:
            self.error("Integrity tests failed")
            return test_result

        # Run make commands to verify end-to-end
        self.log("Running end-to-end workflow verification")

        import_result = self.run_make_target("import-odds")
        if import_result != 0:
            self.error("Import odds failed")
            return import_result

        edges_result = self.run_make_target("edges")
        if edges_result != 0:
            self.error("Compute edges failed")
            return edges_result

        # Verify contract compliance
        contract_result = self._verify_contract_compliance()
        if contract_result != 0:
            return contract_result

        self.success("Ingestion contract verification completed successfully")
        return 0

    def _verify_contract_compliance(self) -> int:
        """Verify that the ingestion contract is properly satisfied."""
        self.log("Verifying contract compliance in database")

        db_path = Path("storage/odds.db")
        if not db_path.exists():
            self.error("Database not found - run import-odds first")
            return 1

        try:
            with sqlite3.connect(db_path) as con:
                # Check that odds_csv_raw table exists and has data
                cursor = con.execute("SELECT COUNT(*) FROM odds_csv_raw")
                row_count = cursor.fetchone()[0]

                if row_count == 0:
                    self.error("No data found in odds_csv_raw table")
                    return 1

                self.log(f"Found {row_count} rows in odds_csv_raw")

                # Verify book name normalization
                cursor = con.execute("""
                    SELECT DISTINCT book FROM odds_csv_raw
                    WHERE book IN ('draftkings', 'dk', 'fanduel', 'fd', 'CAESARS', 'betmgm')
                """)
                unnormalized_books = [row[0] for row in cursor.fetchall()]

                if unnormalized_books:
                    self.error(f"Found unnormalized book names: {unnormalized_books}")
                    return 1

                self.log("✓ Book names are properly normalized")

                # Verify position inference
                cursor = con.execute("""
                    SELECT COUNT(*) FROM odds_csv_raw
                    WHERE market LIKE '%pass%' AND pos != 'QB'
                """)
                bad_qb_pos = cursor.fetchone()[0]

                cursor = con.execute("""
                    SELECT COUNT(*) FROM odds_csv_raw
                    WHERE market LIKE '%rush%' AND pos != 'RB'
                """)
                bad_rb_pos = cursor.fetchone()[0]

                if bad_qb_pos > 0:
                    self.error(f"Found {bad_qb_pos} passing markets without QB position")
                    return 1

                if bad_rb_pos > 0:
                    self.error(f"Found {bad_rb_pos} rushing markets without RB position")
                    return 1

                self.log("✓ Position inference is working correctly")

                # Verify season is present
                cursor = con.execute("SELECT COUNT(*) FROM odds_csv_raw WHERE season IS NULL")
                missing_season = cursor.fetchone()[0]

                if missing_season > 0:
                    self.error(f"Found {missing_season} rows without season information")
                    return 1

                self.log("✓ Season information is present in all rows")

                # Check for proper season values (should be reasonable NFL seasons)
                cursor = con.execute("""
                    SELECT DISTINCT season FROM odds_csv_raw
                    WHERE season < 2020 OR season > 2030
                """)
                invalid_seasons = [row[0] for row in cursor.fetchall()]

                if invalid_seasons:
                    self.error(f"Found invalid season values: {invalid_seasons}")
                    return 1

                self.log("✓ Season values are within expected range")

                return 0

        except sqlite3.Error as e:
            self.error(f"Database error during contract verification: {e}")
            return 1
        except Exception as e:
            self.error(f"Unexpected error during contract verification: {e}")
            return 1