# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pyyaml",
# ]
# ///

# ==============================================================================
# Script: assemble_prompt.py
#
# Description:
# This script assembles a complete AVS (Agentic Value Stream) Value Story YAML
# file. It reads a Logic File (YAML/MD) that contains the Goal, Instructions,
# and a 'context_manifest'. It then dynamically loads all files listed in the
# manifest and embeds them into the final YAML output.
#
# This allows the Logic File to act as the "Master Controller," defining exactly
# what data constitutes the context for that specific Value Story.
#
# Usage:
#   To run this script with `uv` (recommended):
#     uv run assemble_prompt.py [OPTIONS]
#
# Options:
#   --logic PATH      Path to the logic (Goal/Instructions) file.
#                     (Default: illustrative-example/VS-001-logic-analysis.md)
#   --output PATH     Path to the output YAML file.
#                     (Default: illustrative-example/VS-001-assembled.yaml)
#
# Dependencies:
#   PyYAML (automatically managed by `uv run` if using `uv`)
# ==============================================================================

import yaml
import os
import argparse
import sys

def read_file(filename):
    """Reads content from a file, handling potential path issues."""
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Could not find file at '{filename}'")
        sys.exit(1)

def main():
    # Get the directory where the script is located to resolve relative defaults
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # The project root is one level up (assuming script is in illustrative-example/)
    project_root = os.path.dirname(script_dir)

    parser = argparse.ArgumentParser(description="Assemble an AVS Value Story from logic and context files.")
    parser.add_argument("--logic", default=os.path.join(script_dir, "VS-001-logic-analysis.md"), 
                        help="Path to the logic (Goal/Instructions) MD/YAML file.")
    # The --output argument will now represent just the filename, not the full path
    parser.add_argument("--output", default="VS-001-assembled.yaml", 
                        help="The filename for the assembled YAML output. The path will be determined by product.output_path in the logic file.")
    
    args = parser.parse_args()

    print(f"--- AVS Assembly Script ---")
    print(f"1. Loading Logic from '{args.logic}'...")
    
    # 1. Load the Logic File
    logic_content = read_file(args.logic)
    try:
        logic_data = yaml.safe_load(logic_content)
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML in logic file: {exc}")
        sys.exit(1)

    # 2. Process Context Manifest
    context_assets = []
    manifest = logic_data.get('context_manifest', [])
    
    if not manifest:
        print("Warning: No 'context_manifest' found in logic file. No context assets will be loaded.")
    else:
        print(f"2. Processing Context Manifest ({len(manifest)} items)...")
        
        for item in manifest:
            key = item.get('key')
            description = item.get('description', 'No description provided.')
            default_path = item.get('default_path')
            
            if not default_path:
                print(f"  - Skipping '{key}': No default_path provided.")
                continue

            # Resolve path: 
            # If path is absolute, use it. 
            # If relative, treat it as relative to the PROJECT ROOT.
            if os.path.isabs(default_path):
                file_path = default_path
            else:
                file_path = os.path.join(project_root, default_path)

            print(f"  - Loading '{key}' from: {file_path}")
            file_content = read_file(file_path)
            
            # Add to assets list
            context_assets.append({
                "name": key,
                "description": description,
                "source_file": default_path,
                "content": file_content
            })

    # 3. Assemble the Value Story
    print("3. Assembling final structure...")
    value_story = {
        "metadata": {
            "version": "1.0",
            "story_id": logic_data.get('metadata', {}).get('story_id', 'VS-Assembled'),
            "status": "active",
            "generated_by": "assemble_prompt.py"
        },
        "goal": logic_data.get('goal', {}),
        "instructions": logic_data.get('instructions', {}),
        "context": {
            "description": "Assembled context based on manifest.",
            "assets": context_assets,
            "implicit_knowledge_overrides": logic_data.get('context', {}).get('implicit_knowledge_overrides', [])
        },
        "product": logic_data.get('product', {
            "type": "Document",
            "format": "Markdown"
        })
    }

    # 4. Determine output path and filename
    output_dir = value_story['product'].get('output_path')
    if not output_dir:
        print("Warning: 'product.output_path' not found in logic file. Outputting to script's directory.")
        final_output_path = os.path.join(script_dir, args.output)
    else:
        # Resolve output_dir relative to project root
        if os.path.isabs(output_dir):
            resolved_output_dir = output_dir
        else:
            resolved_output_dir = os.path.join(project_root, output_dir)
        
        os.makedirs(resolved_output_dir, exist_ok=True)
        final_output_path = os.path.join(resolved_output_dir, args.output)

    print(f"4. Writing output to '{final_output_path}'...")
    with open(final_output_path, 'w') as f:
        f.write("# ==============================================================================\n")
        f.write("# AUTO-GENERATED VALUE STORY\n")
        f.write("# This file was assembled by 'assemble_prompt.py'\n")
        f.write("# It contains the Goal, Instructions, and FULL CONTEXT needed by the Agent.\n")
        f.write("# ==============================================================================\n\n")
        yaml.dump(value_story, f, sort_keys=False, indent=2, width=80)

    print(f"✅ Success! Assembled Value Story saved to: {final_output_path}")

if __name__ == "__main__":
    main()
