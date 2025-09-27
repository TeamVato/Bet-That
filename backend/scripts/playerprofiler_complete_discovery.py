#!/usr/bin/env python3
"""Complete discovery of ALL PlayerProfiler data assets"""

import os
import pandas as pd
import json
import csv
from pathlib import Path
from datetime import datetime
import chardet  # For encoding detection
import openpyxl  # For Excel files
import warnings
warnings.filterwarnings('ignore')

# PlayerProfiler root
PP_ROOT = Path("/Users/vato/work/Bet-That/storage/imports/PlayerProfiler")


class PlayerProfilerExplorer:
    def __init__(self):
        self.root = PP_ROOT
        self.inventory = {
            'folders': {},
            'data_files': {},
            'documentation': {},
            'total_size_mb': 0,
            'file_count': 0,
            'discovered_at': datetime.now().isoformat()
        }
        self.data_dictionary = {}
        self.column_mappings = {}

    def explore_all_folders(self):
        """Deep exploration of entire PlayerProfiler directory structure"""
        print("[DISCOVERY] PLAYERPROFILER COMPLETE DISCOVERY")
        print("=" * 80)

        # First pass: Map entire structure
        for root, dirs, files in os.walk(self.root):
            rel_path = Path(root).relative_to(self.root)
            folder_name = str(rel_path) if str(rel_path) != '.' else 'ROOT'

            # Track each folder
            self.inventory['folders'][folder_name] = {
                'path': str(root),
                'subfolders': dirs,
                'file_count': len(files),
                'files': []
            }

            # Analyze files in this folder
            for file in files:
                file_path = Path(root) / file
                file_info = self.analyze_file(file_path)
                self.inventory['folders'][folder_name]['files'].append(file_info)
                self.inventory['file_count'] += 1

        print(f"\n[METRICS] DISCOVERY SUMMARY:")
        print(f"   Total folders: {len(self.inventory['folders'])}")
        print(f"   Total files: {self.inventory['file_count']}")
        print(f"   Total size: {self.inventory['total_size_mb']:.2f} MB")

        return self.inventory

    def analyze_file(self, file_path):
        """Detailed analysis of individual file"""
        file_stats = file_path.stat()
        size_mb = file_stats.st_size / (1024 * 1024)
        self.inventory['total_size_mb'] += size_mb

        file_info = {
            'name': file_path.name,
            'type': file_path.suffix.lower(),
            'size_mb': round(size_mb, 3),
            'modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
        }

        # Special handling for different file types
        if file_path.suffix.lower() == '.csv':
            file_info.update(self.analyze_csv(file_path))
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            file_info.update(self.analyze_excel(file_path))
        elif file_path.suffix.lower() in ['.txt', '.md']:
            file_info.update(self.analyze_text(file_path))
        elif 'dictionary' in file_path.name.lower() or 'glossary' in file_path.name.lower():
            file_info['category'] = 'DOCUMENTATION'
            self.load_data_dictionary(file_path)

        return file_info

    def analyze_csv(self, file_path):
        """Deep dive into CSV structure"""
        csv_info = {'category': 'DATA', 'analysis': {}}

        try:
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read(100000)  # Read first 100KB
                result = chardet.detect(raw_data)
                encoding = result['encoding'] or 'utf-8'

            # Load sample
            df = pd.read_csv(file_path, encoding=encoding, nrows=1000)

            csv_info['analysis'] = {
                'rows_sample': len(df),
                'columns': len(df.columns),
                'column_list': list(df.columns),
                'dtypes': df.dtypes.value_counts().to_dict(),
                'null_counts': df.isnull().sum().to_dict() if len(df) < 100 else {},
                'date_columns': [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()],
                'player_columns': [col for col in df.columns if 'player' in col.lower() or 'name' in col.lower()],
                'stat_columns': self.categorize_columns(df.columns)
            }

            # Check for specific strategy-relevant columns
            csv_info['strategy_relevance'] = self.check_strategy_relevance(df.columns)

        except Exception as e:
            csv_info['error'] = str(e)

        return csv_info

    def analyze_excel(self, file_path):
        """Analyze Excel files which might contain multiple sheets"""
        excel_info = {'category': 'DATA', 'sheets': {}}

        try:
            xl = pd.ExcelFile(file_path)
            excel_info['sheet_count'] = len(xl.sheet_names)
            excel_info['sheet_names'] = xl.sheet_names

            # Analyze each sheet
            for sheet_name in xl.sheet_names[:3]:  # First 3 sheets
                df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=100)
                excel_info['sheets'][sheet_name] = {
                    'columns': len(df.columns),
                    'column_list': list(df.columns)[:20]  # First 20 columns
                }

        except Exception as e:
            excel_info['error'] = str(e)

        return excel_info

    def analyze_text(self, file_path):
        """Analyze text files for documentation"""
        text_info = {'category': 'DOCUMENTATION'}

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(5000)  # First 5KB
                text_info['preview'] = content[:500]
                text_info['lines'] = len(content.splitlines())

                # Check if it's a data dictionary
                if any(term in content.lower() for term in ['column', 'field', 'definition', 'glossary']):
                    text_info['type'] = 'DATA_DICTIONARY'
                    self.parse_text_dictionary(content)

        except Exception as e:
            text_info['error'] = str(e)

        return text_info

    def categorize_columns(self, columns):
        """Categorize columns by their likely purpose"""
        categories = {
            'passing': [],
            'rushing': [],
            'receiving': [],
            'defense': [],
            'fantasy': [],
            'advanced': [],
            'team': [],
            'game': []
        }

        for col in columns:
            col_lower = col.lower()

            # Passing stats
            if any(x in col_lower for x in ['pass', 'qb', 'comp', 'att', 'td_pass', 'int', 'sack']):
                categories['passing'].append(col)
            # Rushing stats
            elif any(x in col_lower for x in ['rush', 'carry', 'run', 'yards_rush', 'ypc']):
                categories['rushing'].append(col)
            # Receiving stats
            elif any(x in col_lower for x in ['rec', 'catch', 'tgt', 'target', 'yards_rec', 'ypr']):
                categories['receiving'].append(col)
            # Defense stats
            elif any(x in col_lower for x in ['def', 'allow', 'against', 'opp_', 'dvoa', 'pressure']):
                categories['defense'].append(col)
            # Fantasy stats
            elif any(x in col_lower for x in ['fantasy', 'fp', 'dk', 'fd', 'yahoo', 'proj']):
                categories['fantasy'].append(col)
            # Advanced metrics
            elif any(x in col_lower for x in ['epa', 'dvoa', 'qbr', 'pff', 'grade', 'war', 'vorp']):
                categories['advanced'].append(col)
            # Team/game info
            elif any(x in col_lower for x in ['team', 'opp', 'home', 'away', 'game', 'week']):
                categories['team'].append(col)
            elif any(x in col_lower for x in ['date', 'season', 'year']):
                categories['game'].append(col)

        return {k: v for k, v in categories.items() if v}  # Only return non-empty categories

    def check_strategy_relevance(self, columns):
        """Check which betting strategies this data supports"""
        relevance = {
            'qb_td_strategy': False,
            'rb_under_strategy': False,
            'wr_under_strategy': False,
            'totals_strategy': False,
            'defensive_stats': False
        }

        columns_lower = [col.lower() for col in columns]

        # QB TD Strategy needs
        if any('pass' in col and 'td' in col for col in columns_lower):
            relevance['qb_td_strategy'] = True

        # RB Under Strategy needs
        if any('rush' in col and ('yard' in col or 'carry' in col) for col in columns_lower):
            relevance['rb_under_strategy'] = True

        # WR Under Strategy needs
        if any('rec' in col and 'yard' in col for col in columns_lower):
            relevance['wr_under_strategy'] = True

        # Defensive stats
        if any('allow' in col or 'against' in col or 'def' in col for col in columns_lower):
            relevance['defensive_stats'] = True

        return relevance

    def load_data_dictionary(self, file_path):
        """Load and parse data dictionary files"""
        print(f"\n[DOCS] Loading Data Dictionary: {file_path.name}")

        try:
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
                for _, row in df.iterrows():
                    if 'column' in df.columns and 'description' in df.columns:
                        self.data_dictionary[row['column']] = row['description']

            elif file_path.suffix.lower() in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    self.parse_text_dictionary(f.read())

        except Exception as e:
            print(f"   Error loading dictionary: {e}")

    def parse_text_dictionary(self, content):
        """Parse text-based data dictionary"""
        lines = content.splitlines()
        for line in lines:
            # Look for patterns like "COLUMN_NAME: description" or "COLUMN_NAME - description"
            if ':' in line or '-' in line:
                parts = line.split(':') if ':' in line else line.split('-')
                if len(parts) == 2:
                    col_name = parts[0].strip()
                    description = parts[1].strip()
                    if col_name and description:
                        self.data_dictionary[col_name] = description

    def generate_comprehensive_report(self):
        """Generate actionable report with all findings"""
        report = {
            'discovery_timestamp': datetime.now().isoformat(),
            'root_path': str(self.root),
            'summary': {
                'total_folders': len(self.inventory['folders']),
                'total_files': self.inventory['file_count'],
                'total_size_mb': round(self.inventory['total_size_mb'], 2),
                'data_files': sum(1 for f in self.inventory['folders'].values()
                                 for file in f['files'] if file.get('category') == 'DATA'),
                'documentation_files': sum(1 for f in self.inventory['folders'].values()
                                          for file in f['files'] if file.get('category') == 'DOCUMENTATION')
            },
            'key_discoveries': {},
            'strategy_support': {},
            'data_dictionary_entries': len(self.data_dictionary),
            'recommended_files': [],
            'next_actions': []
        }

        # Identify key files for each strategy
        for folder_name, folder_info in self.inventory['folders'].items():
            for file_info in folder_info['files']:
                if file_info.get('category') == 'DATA' and 'strategy_relevance' in file_info:
                    relevance = file_info['strategy_relevance']
                    if any(relevance.values()):
                        report['recommended_files'].append({
                            'file': file_info['name'],
                            'folder': folder_name,
                            'size_mb': file_info['size_mb'],
                            'strategies': [k for k, v in relevance.items() if v]
                        })

        # Sort recommended files by relevance
        report['recommended_files'].sort(key=lambda x: len(x['strategies']), reverse=True)

        # Generate next actions
        if report['recommended_files']:
            report['next_actions'].append("Process recommended files for strategy implementation")
        if self.data_dictionary:
            report['next_actions'].append("Apply data dictionary mappings to column interpretation")

        return report


def main():
    print("\n" + "[PP]" * 30)
    print(" PLAYERPROFILER COMPLETE DATA DISCOVERY")
    print("[PP]" * 30 + "\n")

    explorer = PlayerProfilerExplorer()

    # Run complete discovery
    inventory = explorer.explore_all_folders()

    # Generate report
    report = explorer.generate_comprehensive_report()

    # Display findings
    print("\n" + "=" * 80)
    print("[METRICS] KEY FINDINGS")
    print("=" * 80)

    print(f"\n[FOLDERS] FOLDER STRUCTURE:")
    for folder_name in list(inventory['folders'].keys())[:10]:
        folder = inventory['folders'][folder_name]
        print(f"   {folder_name}: {folder['file_count']} files")
        if folder['subfolders']:
            print(f"      Subfolders: {', '.join(folder['subfolders'][:3])}")

    print(f"\n[DOCS] DATA DICTIONARY:")
    if explorer.data_dictionary:
        print(f"   Found {len(explorer.data_dictionary)} column definitions")
        for col, desc in list(explorer.data_dictionary.items())[:5]:
            print(f"   - {col}: {desc[:50]}...")
    else:
        print("   No data dictionary found - will need online research")

    print(f"\n[STRATEGY] STRATEGY-RELEVANT FILES:")
    for rec in report['recommended_files'][:5]:
        print(f"   {rec['file']} ({rec['size_mb']:.1f} MB)")
        print(f"      Supports: {', '.join(rec['strategies'])}")

    # Save complete inventory
    output_file = Path("/Users/vato/work/Bet-That/backend/data/playerprofiler_complete_inventory.json")
    output_file.parent.mkdir(exist_ok=True)

    # Save in chunks to avoid JSON serialization issues
    save_data = {
        'report': report,
        'data_dictionary': explorer.data_dictionary,
        'folder_summary': {k: {'file_count': v['file_count'], 'subfolders': v['subfolders']}
                          for k, v in inventory['folders'].items()}
    }

    with open(output_file, 'w') as f:
        json.dump(save_data, f, indent=2, default=str)

    print(f"\n[OUTPUT] Complete inventory saved to: {output_file}")

    # Create research questions file
    research_file = Path("/Users/vato/work/Bet-That/backend/data/research_questions.txt")
    with open(research_file, 'w') as f:
        f.write("PLAYERPROFILER TERMS REQUIRING CLARIFICATION\n")
        f.write("=" * 50 + "\n\n")
        f.write("Reference: https://www.playerprofiler.com/terms-glossary/\n\n")

        # Find unknown columns
        all_columns = set()
        for folder in inventory['folders'].values():
            for file_info in folder['files']:
                if 'analysis' in file_info and 'column_list' in file_info['analysis']:
                    all_columns.update(file_info['analysis']['column_list'])

        unknown_columns = all_columns - set(explorer.data_dictionary.keys())

        f.write("UNKNOWN COLUMN DEFINITIONS NEEDED:\n")
        for col in sorted(unknown_columns)[:50]:  # First 50 unknown
            f.write(f"- {col}\n")

        f.write("\n\nSPECIFIC QUESTIONS FOR STRATEGY IMPLEMENTATION:\n")
        f.write("1. What does 'Target Share' mean in PlayerProfiler context?\n")
        f.write("2. How is 'Opportunity Share' calculated?\n")
        f.write("3. What is 'Weighted Opportunities'?\n")
        f.write("4. How to interpret 'Game Script' metrics?\n")
        f.write("5. What defensive metrics best predict QB TD performance?\n")

    print(f"[NOTES] Research questions saved to: {research_file}")

    return explorer, report


if __name__ == "__main__":
    explorer, report = main()
